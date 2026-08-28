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
        self._conexion.commit()

    def obtener_cursor(self):
        return self._conexion.cursor()

    def confirmar(self):
        self._conexion.commit()

    def cerrar(self):
        self._conexion.close()
        ConexionBD._instancia = None
