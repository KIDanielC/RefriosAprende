"""Gestión de la conexión a la base de datos SQLite (patrón Singleton)."""
import os
import sqlite3

from config.settings import DATABASE_PATH, SCHEMA_PATH


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

        self._conexion.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_evaluaciones_contenido_unico
            ON evaluaciones (id_contenido) WHERE id_contenido IS NOT NULL
            """
        )

    def _reconstruir_evaluaciones_si_falta_cascada(self):
        """La primera version de la migracion agrego id_contenido sin ON DELETE CASCADE.
        Si detecta ese caso, reconstruye la tabla preservando los datos existentes."""
        fila = self._conexion.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'evaluaciones'"
        ).fetchone()
        definicion_actual = fila["sql"] if fila else ""
        if definicion_actual.count("ON DELETE CASCADE") >= 2:
            return

        self._conexion.executescript(
            """
            DROP TABLE IF EXISTS evaluaciones_nueva;
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
            );
            INSERT INTO evaluaciones_nueva
                (id_evaluacion, id_curso, id_contenido, titulo, tipo_evaluacion, nota_minima_aprobar, intentos_permitidos)
            SELECT id_evaluacion, id_curso, id_contenido, titulo, tipo_evaluacion, nota_minima_aprobar, intentos_permitidos
            FROM evaluaciones;
            DROP TABLE evaluaciones;
            ALTER TABLE evaluaciones_nueva RENAME TO evaluaciones;
            """
        )

    def obtener_cursor(self):
        return self._conexion.cursor()

    def confirmar(self):
        self._conexion.commit()

    def cerrar(self):
        self._conexion.close()
        ConexionBD._instancia = None
