"""Reproduce, sobre bases de datos con esquemas antiguos reales, los escenarios que el
comité evaluador reportó en la Evaluación 1: actualizar una base ya en uso no debe borrar
datos ni dejar el arranque roto. Cada prueba construye el archivo SQLite directamente (sin
pasar por ConexionBD) con el DDL de una versión anterior y filas de ejemplo, y luego deja que
ConexionBD lo abra para disparar las migraciones."""
import sqlite3

import database.connection as connection_module
from database.connection import ConexionBD


def _conectar_sin_migrar(ruta: str) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = OFF")
    return conexion


def _construir_bd_evaluaciones_sin_cascada(ruta: str) -> None:
    """Esquema con evaluaciones.id_contenido ya agregado, pero con una versión anterior de
    la migración que no le puso ON DELETE CASCADE (el estado que de verdad dejó el comité:
    8 evaluaciones, 20 preguntas, 62 opciones y 8 resultados)."""
    conexion = _conectar_sin_migrar(ruta)
    conexion.executescript(
        """
        CREATE TABLE roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT NOT NULL UNIQUE
        );
        CREATE TABLE usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            documento TEXT NOT NULL UNIQUE,
            correo TEXT NOT NULL UNIQUE,
            usuario TEXT NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL,
            id_rol INTEGER NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE cursos (
            id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_curso TEXT NOT NULL,
            descripcion TEXT,
            id_instructor INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'ACTIVO',
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE contenidos (
            id_contenido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_curso INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            tipo_contenido TEXT NOT NULL,
            ruta_archivo TEXT,
            contenido_texto TEXT,
            orden INTEGER NOT NULL DEFAULT 1
        );
        -- id_contenido ya existe, pero sin ON DELETE CASCADE: así quedó la migración vieja.
        CREATE TABLE evaluaciones (
            id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_curso INTEGER NOT NULL,
            id_contenido INTEGER REFERENCES contenidos (id_contenido),
            titulo TEXT NOT NULL,
            tipo_evaluacion TEXT NOT NULL DEFAULT 'CUESTIONARIO',
            nota_minima_aprobar REAL NOT NULL DEFAULT 3.0,
            intentos_permitidos INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE preguntas (
            id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_evaluacion INTEGER NOT NULL,
            enunciado TEXT NOT NULL,
            caso_clinico TEXT,
            orden INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion) ON DELETE CASCADE
        );
        CREATE TABLE opciones (
            id_opcion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pregunta INTEGER NOT NULL,
            texto_opcion TEXT NOT NULL,
            es_correcta INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (id_pregunta) REFERENCES preguntas (id_pregunta) ON DELETE CASCADE
        );
        CREATE TABLE resultados (
            id_resultado INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            id_evaluacion INTEGER NOT NULL,
            nota_obtenida REAL NOT NULL,
            aprobado INTEGER NOT NULL,
            fecha_intento TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion) ON DELETE CASCADE
        );

        INSERT INTO roles (nombre_rol) VALUES ('ADMINISTRADOR'), ('APRENDIZ');
        INSERT INTO usuarios (nombre_completo, documento, correo, usuario, contrasena_hash, id_rol)
            VALUES ('Admin Legado', '9000000001', 'admin.legado@refrios.local', 'admin.legado', 'x', 1);
        """
    )
    for n in range(1, 9):
        conexion.execute(
            "INSERT INTO cursos (id_curso, nombre_curso, id_instructor) VALUES (?, ?, 1)",
            (n, f"Curso legado {n}"),
        )
        conexion.execute(
            "INSERT INTO evaluaciones (id_evaluacion, id_curso, titulo) VALUES (?, ?, ?)",
            (n, n, f"Evaluación final curso {n}"),
        )
        for p in range(1, 3):  # 2 preguntas x 8 evaluaciones = 16... se completa abajo
            pass
    # 20 preguntas y 62 opciones repartidas entre las 8 evaluaciones (no es necesario que
    # queden parejas: lo que importa es reproducir exactamente los conteos del comité).
    id_pregunta = 0
    id_opcion = 0
    preguntas_por_evaluacion = [3, 3, 2, 3, 2, 3, 2, 2]  # suma 20
    for id_evaluacion, total_preguntas in enumerate(preguntas_por_evaluacion, start=1):
        for _ in range(total_preguntas):
            id_pregunta += 1
            conexion.execute(
                "INSERT INTO preguntas (id_pregunta, id_evaluacion, enunciado) VALUES (?, ?, ?)",
                (id_pregunta, id_evaluacion, f"Pregunta {id_pregunta}"),
            )
            opciones_de_la_pregunta = 3 if id_pregunta <= 2 else 3
            for _ in range(3):
                id_opcion += 1
                if id_opcion > 62:
                    break
                conexion.execute(
                    "INSERT INTO opciones (id_opcion, id_pregunta, texto_opcion, es_correcta) VALUES (?, ?, ?, 0)",
                    (id_opcion, id_pregunta, f"Opción {id_opcion}"),
                )
    # Ajuste fino para dejar exactamente 62 opciones (20 preguntas * 3 = 60; faltan 2).
    for extra in range(2):
        id_opcion += 1
        conexion.execute(
            "INSERT INTO opciones (id_opcion, id_pregunta, texto_opcion, es_correcta) VALUES (?, ?, ?, 0)",
            (id_opcion, 1, f"Opción extra {id_opcion}"),
        )
    for n in range(1, 9):
        conexion.execute(
            "INSERT INTO resultados (id_usuario, id_evaluacion, nota_obtenida, aprobado) VALUES (1, ?, 4.0, 1)",
            (n,),
        )
    conexion.commit()
    conexion.close()


def _construir_bd_sin_id_contenido(ruta: str) -> None:
    """Esquema anterior a Sprint 2: evaluaciones todavía no tiene la columna id_contenido."""
    conexion = _conectar_sin_migrar(ruta)
    conexion.executescript(
        """
        CREATE TABLE roles (id_rol INTEGER PRIMARY KEY AUTOINCREMENT, nombre_rol TEXT NOT NULL UNIQUE);
        CREATE TABLE usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nombre_completo TEXT NOT NULL,
            documento TEXT NOT NULL UNIQUE, correo TEXT NOT NULL UNIQUE, usuario TEXT NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL, id_rol INTEGER NOT NULL, activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE cursos (
            id_curso INTEGER PRIMARY KEY AUTOINCREMENT, nombre_curso TEXT NOT NULL, descripcion TEXT,
            id_instructor INTEGER NOT NULL, estado TEXT NOT NULL DEFAULT 'ACTIVO',
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE contenidos (
            id_contenido INTEGER PRIMARY KEY AUTOINCREMENT, id_curso INTEGER NOT NULL, titulo TEXT NOT NULL,
            tipo_contenido TEXT NOT NULL, ruta_archivo TEXT, contenido_texto TEXT, orden INTEGER NOT NULL DEFAULT 1
        );
        -- Sin id_contenido todavía: la evaluación final era la única forma de evaluación.
        CREATE TABLE evaluaciones (
            id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT, id_curso INTEGER NOT NULL, titulo TEXT NOT NULL,
            tipo_evaluacion TEXT NOT NULL DEFAULT 'CUESTIONARIO', nota_minima_aprobar REAL NOT NULL DEFAULT 3.0,
            intentos_permitidos INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE preguntas (
            id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT, id_evaluacion INTEGER NOT NULL, enunciado TEXT NOT NULL,
            caso_clinico TEXT, orden INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion) ON DELETE CASCADE
        );
        CREATE TABLE opciones (
            id_opcion INTEGER PRIMARY KEY AUTOINCREMENT, id_pregunta INTEGER NOT NULL, texto_opcion TEXT NOT NULL,
            es_correcta INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (id_pregunta) REFERENCES preguntas (id_pregunta) ON DELETE CASCADE
        );
        CREATE TABLE resultados (
            id_resultado INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER NOT NULL, id_evaluacion INTEGER NOT NULL,
            nota_obtenida REAL NOT NULL, aprobado INTEGER NOT NULL, fecha_intento TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion) ON DELETE CASCADE
        );
        INSERT INTO roles (nombre_rol) VALUES ('ADMINISTRADOR'), ('APRENDIZ');
        INSERT INTO usuarios (nombre_completo, documento, correo, usuario, contrasena_hash, id_rol)
            VALUES ('Admin Legado', '9000000002', 'admin.legado2@refrios.local', 'admin.legado2', 'x', 1);
        INSERT INTO cursos (id_curso, nombre_curso, id_instructor) VALUES (1, 'Curso legado 1', 1);
        INSERT INTO evaluaciones (id_evaluacion, id_curso, titulo) VALUES (1, 1, 'Evaluación final');
        INSERT INTO preguntas (id_pregunta, id_evaluacion, enunciado) VALUES (1, 1, '¿Cuál es la presión normal?');
        INSERT INTO opciones (id_opcion, id_pregunta, texto_opcion, es_correcta) VALUES (1, 1, 'Opción A', 1);
        INSERT INTO resultados (id_usuario, id_evaluacion, nota_obtenida, aprobado) VALUES (1, 1, 5.0, 1);
        """
    )
    conexion.commit()
    conexion.close()


def _construir_bd_cursos_sin_categoria(ruta: str) -> None:
    """8 cursos sin id_categoria/aprendizaje_secuencial, con 23 contenidos, 8 evaluaciones,
    10 registros de progreso, 12 matrículas y talleres con entregas: los conteos exactos que
    reportó el comité para la migración de cursos."""
    conexion = _conectar_sin_migrar(ruta)
    conexion.executescript(
        """
        CREATE TABLE roles (id_rol INTEGER PRIMARY KEY AUTOINCREMENT, nombre_rol TEXT NOT NULL UNIQUE);
        CREATE TABLE usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nombre_completo TEXT NOT NULL,
            documento TEXT NOT NULL UNIQUE, correo TEXT NOT NULL UNIQUE, usuario TEXT NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL, id_rol INTEGER NOT NULL, activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
        );
        -- Cursos sin id_categoria ni aprendizaje_secuencial: el esquema anterior a esa migración.
        CREATE TABLE cursos (
            id_curso INTEGER PRIMARY KEY AUTOINCREMENT, nombre_curso TEXT NOT NULL, descripcion TEXT,
            id_instructor INTEGER NOT NULL, estado TEXT NOT NULL DEFAULT 'ACTIVO',
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (id_instructor) REFERENCES usuarios (id_usuario)
        );
        CREATE TABLE contenidos (
            id_contenido INTEGER PRIMARY KEY AUTOINCREMENT, id_curso INTEGER NOT NULL, titulo TEXT NOT NULL,
            tipo_contenido TEXT NOT NULL, ruta_archivo TEXT, contenido_texto TEXT, orden INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE evaluaciones (
            id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT, id_curso INTEGER NOT NULL,
            id_contenido INTEGER REFERENCES contenidos (id_contenido) ON DELETE CASCADE,
            titulo TEXT NOT NULL, tipo_evaluacion TEXT NOT NULL DEFAULT 'CUESTIONARIO',
            nota_minima_aprobar REAL NOT NULL DEFAULT 3.0, intentos_permitidos INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE inscripciones (
            id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER NOT NULL, id_curso INTEGER NOT NULL,
            fecha_inscripcion TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE (id_usuario, id_curso),
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE progreso (
            id_progreso INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER NOT NULL, id_curso INTEGER NOT NULL,
            porcentaje_avance REAL NOT NULL DEFAULT 0, estado TEXT NOT NULL DEFAULT 'NO_INICIADO',
            fecha_actualizacion TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE (id_usuario, id_curso),
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE talleres (
            id_taller INTEGER PRIMARY KEY AUTOINCREMENT, id_curso INTEGER NOT NULL, titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL, fecha_creacion TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) ON DELETE CASCADE
        );
        CREATE TABLE entregas_taller (
            id_entrega INTEGER PRIMARY KEY AUTOINCREMENT, id_taller INTEGER NOT NULL, id_usuario INTEGER NOT NULL,
            ruta_archivo TEXT NOT NULL, nombre_archivo_original TEXT, estado TEXT NOT NULL DEFAULT 'PENDIENTE',
            comentario_instructor TEXT, fecha_entrega TEXT NOT NULL DEFAULT (datetime('now')), fecha_calificacion TEXT,
            UNIQUE (id_taller, id_usuario),
            FOREIGN KEY (id_taller) REFERENCES talleres (id_taller) ON DELETE CASCADE
        );
        INSERT INTO roles (nombre_rol) VALUES ('ADMINISTRADOR'), ('APRENDIZ');
        INSERT INTO usuarios (nombre_completo, documento, correo, usuario, contrasena_hash, id_rol)
            VALUES ('Admin Legado', '9000000003', 'admin.legado3@refrios.local', 'admin.legado3', 'x', 1);
        """
    )
    for n in range(1, 11):  # 10 aprendices, para tener con quién matricular/progresar
        conexion.execute(
            "INSERT INTO usuarios (id_usuario, nombre_completo, documento, correo, usuario, contrasena_hash, id_rol) "
            "VALUES (?, ?, ?, ?, ?, 'x', 2)",
            (n + 1, f"Aprendiz legado {n}", f"910000{n:04d}", f"aprendiz{n}@refrios.local", f"aprendiz.legado{n}"),
        )
    for n in range(1, 9):  # 8 cursos
        conexion.execute(
            "INSERT INTO cursos (id_curso, nombre_curso, id_instructor) VALUES (?, ?, 1)",
            (n, f"Curso legado {n}"),
        )
    contenidos_por_curso = [3, 3, 3, 3, 3, 3, 3, 2]  # suma 23
    id_contenido = 0
    for id_curso, total in enumerate(contenidos_por_curso, start=1):
        for _ in range(total):
            id_contenido += 1
            conexion.execute(
                "INSERT INTO contenidos (id_contenido, id_curso, titulo, tipo_contenido) VALUES (?, ?, ?, 'TEXTO')",
                (id_contenido, id_curso, f"Contenido {id_contenido}"),
            )
    for n in range(1, 9):  # 8 evaluaciones (una final por curso)
        conexion.execute(
            "INSERT INTO evaluaciones (id_evaluacion, id_curso, titulo) VALUES (?, ?, ?)",
            (n, n, f"Evaluación final curso {n}"),
        )
    # Pares (id_usuario, id_curso) explícitos: los de progreso son un subconjunto de los de
    # inscripciones, igual que en una base real (nadie progresa en un curso sin matricularse
    # primero). Así la migración automática "matrícula desde progreso" (ya existente, no es
    # parte de esta corrección) no agrega matrículas nuevas y el conteo de 12 queda exacto.
    pares_inscripcion = [
        (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (2, 2), (3, 2),
    ]
    for id_usuario, id_curso in pares_inscripcion:
        conexion.execute("INSERT INTO inscripciones (id_usuario, id_curso) VALUES (?, ?)", (id_usuario, id_curso))

    for id_usuario, id_curso in pares_inscripcion[:10]:  # 10 progresos
        conexion.execute(
            "INSERT INTO progreso (id_usuario, id_curso, porcentaje_avance, estado) VALUES (?, ?, 50.0, 'EN_PROGRESO')",
            (id_usuario, id_curso),
        )
    conexion.execute(
        "INSERT INTO talleres (id_taller, id_curso, titulo, descripcion) VALUES (1, 1, 'Taller práctico', 'Descripción')"
    )
    conexion.execute(
        "INSERT INTO entregas_taller (id_taller, id_usuario, ruta_archivo, estado) "
        "VALUES (1, 2, 'resources/entregas/legado.pdf', 'PENDIENTE')"
    )
    conexion.commit()
    conexion.close()


def test_actualizar_bd_evaluaciones_sin_cascada_conserva_todo():
    ruta = str(connection_module.DATABASE_PATH)
    _construir_bd_evaluaciones_sin_cascada(ruta)

    conexion_bd = ConexionBD()
    cx = conexion_bd._conexion

    assert cx.execute("SELECT COUNT(*) FROM evaluaciones").fetchone()[0] == 8
    assert cx.execute("SELECT COUNT(*) FROM preguntas").fetchone()[0] == 20
    assert cx.execute("SELECT COUNT(*) FROM opciones").fetchone()[0] == 62
    assert cx.execute("SELECT COUNT(*) FROM resultados").fetchone()[0] == 8
    assert cx.execute("PRAGMA foreign_key_check").fetchall() == []

    definicion = cx.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'evaluaciones'"
    ).fetchone()["sql"]
    assert definicion.count("ON DELETE CASCADE") >= 2


def test_actualizar_bd_evaluaciones_sin_cascada_es_idempotente():
    ruta = str(connection_module.DATABASE_PATH)
    _construir_bd_evaluaciones_sin_cascada(ruta)

    ConexionBD()
    connection_module.ConexionBD._instancia = None
    conexion_bd = ConexionBD()  # segundo arranque sobre la base ya migrada
    cx = conexion_bd._conexion

    assert cx.execute("SELECT COUNT(*) FROM evaluaciones").fetchone()[0] == 8
    assert cx.execute("SELECT COUNT(*) FROM preguntas").fetchone()[0] == 20
    assert cx.execute("SELECT COUNT(*) FROM opciones").fetchone()[0] == 62
    assert cx.execute("SELECT COUNT(*) FROM resultados").fetchone()[0] == 8


def test_arranque_con_bd_sin_id_contenido_conserva_la_informacion():
    ruta = str(connection_module.DATABASE_PATH)
    _construir_bd_sin_id_contenido(ruta)

    conexion_bd = ConexionBD()  # antes de la corrección, esto lanzaba "no such column: id_contenido"
    cx = conexion_bd._conexion

    columnas = {fila["name"] for fila in cx.execute("PRAGMA table_info(evaluaciones)")}
    assert "id_contenido" in columnas
    assert cx.execute("SELECT COUNT(*) FROM evaluaciones").fetchone()[0] == 1
    assert cx.execute("SELECT COUNT(*) FROM preguntas").fetchone()[0] == 1
    assert cx.execute("SELECT COUNT(*) FROM opciones").fetchone()[0] == 1
    assert cx.execute("SELECT COUNT(*) FROM resultados").fetchone()[0] == 1

    indices = {
        fila["name"] for fila in cx.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'evaluaciones'"
        )
    }
    assert "idx_evaluaciones_contenido_unico" in indices
    assert "idx_evaluaciones_final_unica_por_curso" in indices

    connection_module.ConexionBD._instancia = None
    ConexionBD()  # repetir el arranque debe ser inofensivo (idempotencia)


def test_actualizar_bd_cursos_sin_categoria_ni_secuencial_conserva_todo():
    ruta = str(connection_module.DATABASE_PATH)
    _construir_bd_cursos_sin_categoria(ruta)

    conexion_bd = ConexionBD()
    cx = conexion_bd._conexion

    assert cx.execute("SELECT COUNT(*) FROM cursos").fetchone()[0] == 8
    assert cx.execute("SELECT COUNT(*) FROM contenidos").fetchone()[0] == 23
    assert cx.execute("SELECT COUNT(*) FROM evaluaciones").fetchone()[0] == 8
    assert cx.execute("SELECT COUNT(*) FROM progreso").fetchone()[0] == 10
    assert cx.execute("SELECT COUNT(*) FROM inscripciones").fetchone()[0] == 12
    assert cx.execute("SELECT COUNT(*) FROM talleres").fetchone()[0] == 1
    assert cx.execute("SELECT COUNT(*) FROM entregas_taller").fetchone()[0] == 1
    assert cx.execute("PRAGMA foreign_key_check").fetchall() == []

    columnas_cursos = {fila["name"] for fila in cx.execute("PRAGMA table_info(cursos)")}
    assert "id_categoria" in columnas_cursos
    assert "aprendizaje_secuencial" in columnas_cursos

    # Los cursos ya existentes no se movieron a BORRADOR retroactivamente.
    estados = {fila["estado"] for fila in cx.execute("SELECT estado FROM cursos")}
    assert estados == {"ACTIVO"}


def test_actualizacion_con_falla_revierte_y_conserva_la_base_original(monkeypatch):
    ruta = str(connection_module.DATABASE_PATH)
    _construir_bd_cursos_sin_categoria(ruta)

    contador_de_llamadas = {"n": 0}

    def _conteos_que_simulan_una_perdida_de_datos(self):
        contador_de_llamadas["n"] += 1
        # La primera llamada es "antes" de migrar; la segunda, "después". Se simula que la
        # segunda encontró menos filas, como si la migración hubiera perdido datos.
        return {"cursos": 8} if contador_de_llamadas["n"] == 1 else {"cursos": -1}

    monkeypatch.setattr(
        connection_module.ConexionBD, "_contar_todas_las_tablas", _conteos_que_simulan_una_perdida_de_datos
    )

    try:
        ConexionBD()
        assert False, "se esperaba que la migración fallara y detuviera el arranque"
    except RuntimeError as error:
        assert "No se pudo actualizar la base de datos" in str(error)

    # Se restauró el respaldo: la base vuelve a tener exactamente el esquema y los datos
    # de ANTES de intentar migrar (no se quedó con la tabla cursos a medio reconstruir).
    connection_module.ConexionBD._instancia = None
    monkeypatch.undo()
    conexion_directa = sqlite3.connect(ruta)
    columnas_cursos = {fila[1] for fila in conexion_directa.execute("PRAGMA table_info(cursos)")}
    assert "aprendizaje_secuencial" not in columnas_cursos
    assert conexion_directa.execute("SELECT COUNT(*) FROM cursos").fetchone()[0] == 8
    conexion_directa.close()

    import glob
    respaldos = glob.glob(f"{ruta}.pre-migracion-*.bak")
    assert len(respaldos) == 1


def test_foreign_keys_quedan_activas_despues_de_migrar():
    ruta = str(connection_module.DATABASE_PATH)
    _construir_bd_cursos_sin_categoria(ruta)

    conexion_bd = ConexionBD()
    valor = conexion_bd._conexion.execute("PRAGMA foreign_keys").fetchone()[0]
    assert valor == 1
