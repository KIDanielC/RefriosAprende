"""Gestión de la conexión a la base de datos SQLite (patrón Singleton)."""
import hashlib
import os
import shutil
import sqlite3
from datetime import datetime

from config.settings import SCHEMA_PATH, DATABASE_PATH

# Tablas con datos de negocio que una migración de estructura nunca debería alterar en
# cantidad. Se usa como red de seguridad adicional alrededor de la migración de cursos,
# la que el comité señaló con el mayor radio de impacto (contenidos, evaluaciones,
# progreso, inscripciones y talleres dependen de 'cursos' por clave foránea).
_TABLAS_CON_DATOS = (
    "usuarios", "categorias", "cursos", "cursos_prerrequisitos", "guias_aprendizaje",
    "inscripciones", "contenidos", "evaluaciones", "preguntas", "opciones", "resultados",
    "progreso", "simulaciones", "talleres", "entregas_taller", "tiempo_uso_curso",
    "contenidos_vistos",
)


class ConexionBD:
    """Provee una única conexión SQLite compartida por toda la aplicación."""

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self._conexion = sqlite3.connect(DATABASE_PATH)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")
        self._aplicar_esquema()

    def _aplicar_esquema(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as archivo_esquema:
            script_sql = archivo_esquema.read()
        self._conexion.executescript(script_sql)
        self._aplicar_migraciones()
        self._conexion.commit()

    def _aplicar_migraciones(self):
        """Ajustes incrementales sobre bases de datos ya existentes (creadas con un esquema anterior)."""
        columnas_evaluaciones = {fila["name"] for fila in self._conexion.execute("PRAGMA table_info(evaluaciones)")}
        if "id_contenido" not in columnas_evaluaciones:
            self._conexion.execute(
                """
                ALTER TABLE evaluaciones ADD COLUMN id_contenido INTEGER
                REFERENCES contenidos (id_contenido) ON UPDATE CASCADE ON DELETE CASCADE
                """
            )

        self._reconstruir_evaluaciones_si_falta_cascada()

        # Los dos índices de abajo dependen de la columna id_contenido, así que no pueden
        # vivir en schema.sql: ese script corre ANTES de que la línea de arriba la agregue
        # en una base antigua, y "no such column: id_contenido" tumbaría el arranque.
        self._conexion.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_evaluaciones_contenido_unico
            ON evaluaciones (id_contenido) WHERE id_contenido IS NOT NULL
            """
        )
        self._conexion.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_evaluaciones_final_unica_por_curso
            ON evaluaciones (id_curso) WHERE id_contenido IS NULL AND tipo_evaluacion = 'CUESTIONARIO'
            """
        )

        self._migrar_matricula_desde_progreso()
        self._migrar_cursos_borrador_categoria_secuencial()
        self._conexion.execute("CREATE INDEX IF NOT EXISTS idx_cursos_categoria ON cursos (id_categoria)")
        self._migrar_guia_aprendizaje_secciones_ampliadas()
        self._migrar_guia_aprendizaje_quitar_retroalimentar_reforzar_registrar()
        self._migrar_usuarios_foto_perfil()
        self._migrar_usuarios_bloqueo_login()

    def _migrar_usuarios_foto_perfil(self):
        columnas_usuarios = {fila["name"] for fila in self._conexion.execute("PRAGMA table_info(usuarios)")}
        if "foto_perfil" not in columnas_usuarios:
            self._conexion.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT")

    def _migrar_usuarios_bloqueo_login(self):
        """Soporte para el bloqueo temporal tras varios inicios de sesión fallidos
        (AutenticacionController)."""
        columnas_usuarios = {fila["name"] for fila in self._conexion.execute("PRAGMA table_info(usuarios)")}
        if "intentos_fallidos" not in columnas_usuarios:
            self._conexion.execute(
                "ALTER TABLE usuarios ADD COLUMN intentos_fallidos INTEGER NOT NULL DEFAULT 0"
            )
        if "bloqueado_hasta" not in columnas_usuarios:
            self._conexion.execute("ALTER TABLE usuarios ADD COLUMN bloqueado_hasta TEXT")

    def _migrar_matricula_desde_progreso(self):
        """La matrícula (tabla inscripciones) se agregó después de que ya existían cursos con
        aprendices avanzando en ellos. Para no dejarlos "fuera" del curso que ya venían tomando,
        se matricula automáticamente a todo usuario que ya tenga registro de progreso en un curso.
        Se ejecuta una sola vez (registrada en migraciones_aplicadas) para no revivir matrículas
        que el administrador haya quitado manualmente después."""
        self._conexion.execute(
            "CREATE TABLE IF NOT EXISTS migraciones_aplicadas (nombre TEXT PRIMARY KEY)"
        )
        ya_aplicada = self._conexion.execute(
            "SELECT 1 FROM migraciones_aplicadas WHERE nombre = 'matricula_desde_progreso'"
        ).fetchone()
        if ya_aplicada:
            return

        self._conexion.execute(
            """
            INSERT OR IGNORE INTO inscripciones (id_usuario, id_curso)
            SELECT id_usuario, id_curso FROM progreso
            """
        )
        self._conexion.execute(
            "INSERT INTO migraciones_aplicadas (nombre) VALUES ('matricula_desde_progreso')"
        )

    # ------------------------------------------------------------------
    # Procedimiento común y seguro para reconstruir una tabla (C-03)
    # ------------------------------------------------------------------
    def _reconstruir_tabla(self, nombre_tabla: str, ddl_tabla_nueva: str, columnas_a_preservar: list[str]) -> None:
        """Reconstruye 'nombre_tabla' con un esquema nuevo, preservando sus datos.

        Sigue el procedimiento de 12 pasos de la documentación de SQLite para cambios que
        ALTER TABLE no puede hacer (agregar ON DELETE CASCADE, quitar columnas, etc.):
        apagar las claves foráneas ANTES de abrir la transacción (ese pragma no tiene efecto
        dentro de una transacción ya iniciada), copiar la tabla con columnas explícitas (nunca
        SELECT *), reemplazarla sin pasar por un estado donde las tablas hijas queden
        apuntando a un nombre temporal, y verificar antes de confirmar.

        A diferencia de un DROP + CREATE simple, compara cantidad y contenido de
        'columnas_a_preservar' antes y después: la comprobación de integridad de SQLite
        (PRAGMA foreign_key_check / integrity_check) no detecta una pérdida de filas por una
        cascada mal configurada, porque al terminar la base queda perfectamente consistente
        con los datos que sobrevivieron, solo que son menos de los que debería haber.
        """
        conteo_antes, resumen_antes = self._contar_y_resumir(nombre_tabla, columnas_a_preservar)

        nivel_aislamiento_previo = self._conexion.isolation_level
        self._conexion.commit()
        self._conexion.isolation_level = None
        try:
            self._conexion.execute("PRAGMA foreign_keys = OFF")
            self._conexion.execute("BEGIN")
            try:
                nombre_temporal = f"{nombre_tabla}_nueva"
                self._conexion.execute(f"DROP TABLE IF EXISTS {nombre_temporal}")
                self._conexion.execute(ddl_tabla_nueva)

                lista_columnas = ", ".join(columnas_a_preservar)
                self._conexion.execute(
                    f"INSERT INTO {nombre_temporal} ({lista_columnas}) "
                    f"SELECT {lista_columnas} FROM {nombre_tabla}"
                )
                self._conexion.execute(f"DROP TABLE {nombre_tabla}")
                # No renombrar primero la tabla vieja: desde SQLite 3.26 el ALTER TABLE RENAME
                # reescribe las claves foráneas de las tablas hijas para que apunten al nombre
                # nuevo, así que la tabla final debe nacer con RENAME, no con el nombre directo.
                self._conexion.execute(f"ALTER TABLE {nombre_temporal} RENAME TO {nombre_tabla}")

                filas_rotas = self._conexion.execute("PRAGMA foreign_key_check").fetchall()
                if filas_rotas:
                    raise RuntimeError(
                        f"La reconstrucción de '{nombre_tabla}' dejó {len(filas_rotas)} clave(s) "
                        "foránea(s) rota(s)."
                    )

                conteo_despues, resumen_despues = self._contar_y_resumir(nombre_tabla, columnas_a_preservar)
                if conteo_antes != conteo_despues or resumen_antes != resumen_despues:
                    raise RuntimeError(
                        f"La reconstrucción de '{nombre_tabla}' no conservó los datos originales "
                        f"(antes: {conteo_antes} fila(s), después: {conteo_despues} fila(s))."
                    )

                self._conexion.execute("COMMIT")
            except Exception:
                self._conexion.execute("ROLLBACK")
                raise
        finally:
            self._conexion.execute("PRAGMA foreign_keys = ON")
            self._conexion.isolation_level = nivel_aislamiento_previo

    def _contar_y_resumir(self, nombre_tabla: str, columnas: list[str]) -> tuple[int, str]:
        """Cuenta las filas de 'nombre_tabla' y resume su contenido (columnas elegidas,
        en el orden de la fila, ordenadas por rowid) en un hash. Solo se piden las columnas
        que de verdad se preservan: si la tabla nueva agrega columnas con valor por defecto
        (como id_categoria), comparar con SELECT * daría un falso positivo de "cambió"."""
        lista_columnas = ", ".join(columnas)
        filas = self._conexion.execute(
            f"SELECT {lista_columnas} FROM {nombre_tabla} ORDER BY rowid"
        ).fetchall()
        resumen = hashlib.sha256(repr([tuple(fila) for fila in filas]).encode("utf-8")).hexdigest()
        return len(filas), resumen

    def _contar_todas_las_tablas(self) -> dict:
        return {
            tabla: self._conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            for tabla in _TABLAS_CON_DATOS
        }

    def _crear_respaldo_antes_de_migrar(self) -> str:
        marca_tiempo = datetime.now().strftime("%Y%m%d-%H%M%S")
        ruta_respaldo = f"{DATABASE_PATH}.pre-migracion-{marca_tiempo}.bak"
        self._conexion.commit()
        respaldo = sqlite3.connect(ruta_respaldo)
        try:
            self._conexion.backup(respaldo)
        finally:
            respaldo.close()
        return ruta_respaldo

    def _restaurar_respaldo(self, ruta_respaldo: str) -> None:
        """Vuelve a dejar DATABASE_PATH exactamente como estaba antes de intentar migrar.
        No se borra el respaldo: queda disponible para que un administrador lo revise."""
        self._conexion.close()
        shutil.copyfile(ruta_respaldo, DATABASE_PATH)
        self._conexion = sqlite3.connect(DATABASE_PATH)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")

    def _reconstruir_evaluaciones_si_falta_cascada(self):
        """La primera version de la migracion agrego id_contenido sin ON DELETE CASCADE.
        Si detecta ese caso, reconstruye la tabla preservando los datos existentes."""
        fila = self._conexion.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'evaluaciones'"
        ).fetchone()
        definicion_actual = fila["sql"] if fila else ""
        if definicion_actual.count("ON DELETE CASCADE") >= 2:
            return

        self._reconstruir_tabla(
            "evaluaciones",
            """
            CREATE TABLE evaluaciones_nueva (
                id_evaluacion       INTEGER PRIMARY KEY AUTOINCREMENT,
                id_curso            INTEGER NOT NULL,
                id_contenido        INTEGER,
                titulo              TEXT NOT NULL,
                tipo_evaluacion     TEXT NOT NULL DEFAULT 'CUESTIONARIO' CHECK (tipo_evaluacion IN ('CUESTIONARIO', 'SIMULACION')),
                nota_minima_aprobar REAL NOT NULL DEFAULT 3.0,
                intentos_permitidos INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (id_contenido) REFERENCES contenidos (id_contenido)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            """,
            ["id_evaluacion", "id_curso", "id_contenido", "titulo", "tipo_evaluacion",
             "nota_minima_aprobar", "intentos_permitidos"],
        )

    def _migrar_cursos_borrador_categoria_secuencial(self):
        """La primera version de 'cursos' solo aceptaba estado ACTIVO/INACTIVO y no tenia
        columnas de categoria ni aprendizaje secuencial. Si detecta ese caso, reconstruye la
        tabla preservando los datos existentes (los cursos ya creados siguen ACTIVO/INACTIVO
        como estaban; nada de esto los mueve a BORRADOR retroactivamente).

        Esta es la migración de mayor radio de impacto (contenidos, evaluaciones, progreso,
        inscripciones y talleres dependen de 'cursos'), así que además del procedimiento
        común se toma un respaldo del archivo completo antes de tocar nada, y se compara el
        conteo de TODAS las tablas con datos (no solo cursos) antes y después: si algo no
        coincide, se restaura el respaldo y se detiene el arranque con un mensaje claro en
        vez de seguir con una base parcialmente migrada."""
        columnas_cursos = {fila["name"] for fila in self._conexion.execute("PRAGMA table_info(cursos)")}
        if "aprendizaje_secuencial" in columnas_cursos:
            return

        ruta_respaldo = self._crear_respaldo_antes_de_migrar()
        conteos_antes = self._contar_todas_las_tablas()

        try:
            self._reconstruir_tabla(
                "cursos",
                """
                CREATE TABLE cursos_nueva (
                    id_curso                INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_curso            TEXT NOT NULL,
                    descripcion             TEXT,
                    id_instructor           INTEGER NOT NULL,
                    id_categoria            INTEGER,
                    estado                  TEXT NOT NULL DEFAULT 'BORRADOR' CHECK (estado IN ('BORRADOR', 'ACTIVO', 'INACTIVO')),
                    aprendizaje_secuencial  INTEGER NOT NULL DEFAULT 0 CHECK (aprendizaje_secuencial IN (0, 1)),
                    fecha_creacion          TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (id_instructor) REFERENCES usuarios (id_usuario)
                        ON UPDATE CASCADE ON DELETE RESTRICT,
                    FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
                        ON UPDATE CASCADE ON DELETE SET NULL
                )
                """,
                ["id_curso", "nombre_curso", "descripcion", "id_instructor", "estado", "fecha_creacion"],
            )

            conteos_despues = self._contar_todas_las_tablas()
            if conteos_antes != conteos_despues:
                raise RuntimeError(
                    "La actualización de la base de datos alteró tablas que no debía tocar "
                    f"(antes: {conteos_antes}, después: {conteos_despues})."
                )
        except Exception as error:
            self._restaurar_respaldo(ruta_respaldo)
            raise RuntimeError(
                "No se pudo actualizar la base de datos a la nueva versión de cursos. "
                f"Se conservó la información anterior; copia de seguridad en: {ruta_respaldo}"
            ) from error

    def _migrar_guia_aprendizaje_secciones_ampliadas(self):
        """La primera version de 'guias_aprendizaje' solo tenia objetivos, competencias,
        actividades (texto libre generico) y criterios_evaluacion. Se reconstruye la tabla para
        cubrir la metodologia completa (aprender/practicar/simular/evaluar/retroalimentar/
        reforzar/registrar) y se migra el contenido de la columna 'actividades' (ya no existe)
        hacia 'actividades_interactivas', la seccion mas cercana semanticamente."""
        columnas_guia = {fila["name"] for fila in self._conexion.execute("PRAGMA table_info(guias_aprendizaje)")}
        if "actividades_interactivas" in columnas_guia:
            return

        self._conexion.executescript(
            """
            DROP TABLE IF EXISTS guias_aprendizaje_nueva;
            CREATE TABLE guias_aprendizaje_nueva (
                id_guia                     INTEGER PRIMARY KEY AUTOINCREMENT,
                id_curso                    INTEGER NOT NULL UNIQUE,
                objetivo_general            TEXT,
                objetivos_especificos       TEXT,
                competencias                TEXT,
                introduccion                TEXT,
                conocimientos_previos       TEXT,
                procedimiento_paso_a_paso   TEXT,
                normas_seguridad            TEXT,
                ejemplos_practicos          TEXT,
                actividades_interactivas    TEXT,
                criterios_evaluacion        TEXT,
                retroalimentacion           TEXT,
                actividades_refuerzo        TEXT,
                evidencias_aprendizaje      TEXT,
                glosario                    TEXT,
                referencias                 TEXT,
                duracion_horas              INTEGER,
                fecha_actualizacion         TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
            INSERT INTO guias_aprendizaje_nueva
                (id_guia, id_curso, objetivo_general, objetivos_especificos, competencias,
                 actividades_interactivas, criterios_evaluacion, duracion_horas, fecha_actualizacion)
            SELECT id_guia, id_curso, objetivo_general, objetivos_especificos, competencias,
                   actividades, criterios_evaluacion, duracion_horas, fecha_actualizacion
            FROM guias_aprendizaje;
            DROP TABLE guias_aprendizaje;
            ALTER TABLE guias_aprendizaje_nueva RENAME TO guias_aprendizaje;
            """
        )

    def _migrar_guia_aprendizaje_quitar_retroalimentar_reforzar_registrar(self):
        """Se retiraron del alcance de la guía las secciones Retroalimentación, Actividades
        de refuerzo y Evidencias de aprendizaje (decisión del usuario tras revisar el primer
        diseño de 7 pestañas). Se reconstruye la tabla sin esas 3 columnas."""
        columnas_guia = {fila["name"] for fila in self._conexion.execute("PRAGMA table_info(guias_aprendizaje)")}
        if "retroalimentacion" not in columnas_guia:
            return

        self._conexion.executescript(
            """
            DROP TABLE IF EXISTS guias_aprendizaje_nueva;
            CREATE TABLE guias_aprendizaje_nueva (
                id_guia                     INTEGER PRIMARY KEY AUTOINCREMENT,
                id_curso                    INTEGER NOT NULL UNIQUE,
                objetivo_general            TEXT,
                objetivos_especificos       TEXT,
                competencias                TEXT,
                introduccion                TEXT,
                conocimientos_previos       TEXT,
                procedimiento_paso_a_paso   TEXT,
                normas_seguridad            TEXT,
                ejemplos_practicos          TEXT,
                actividades_interactivas    TEXT,
                criterios_evaluacion        TEXT,
                glosario                    TEXT,
                referencias                 TEXT,
                duracion_horas              INTEGER,
                fecha_actualizacion         TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
            INSERT INTO guias_aprendizaje_nueva
                (id_guia, id_curso, objetivo_general, objetivos_especificos, competencias,
                 introduccion, conocimientos_previos, procedimiento_paso_a_paso, normas_seguridad,
                 ejemplos_practicos, actividades_interactivas, criterios_evaluacion,
                 glosario, referencias, duracion_horas, fecha_actualizacion)
            SELECT id_guia, id_curso, objetivo_general, objetivos_especificos, competencias,
                   introduccion, conocimientos_previos, procedimiento_paso_a_paso, normas_seguridad,
                   ejemplos_practicos, actividades_interactivas, criterios_evaluacion,
                   glosario, referencias, duracion_horas, fecha_actualizacion
            FROM guias_aprendizaje;
            DROP TABLE guias_aprendizaje;
            ALTER TABLE guias_aprendizaje_nueva RENAME TO guias_aprendizaje;
            """
        )

    def obtener_cursor(self):
        return self._conexion.cursor()

    def confirmar(self):
        self._conexion.commit()

    def cerrar(self):
        self._conexion.close()
        ConexionBD._instancia = None
