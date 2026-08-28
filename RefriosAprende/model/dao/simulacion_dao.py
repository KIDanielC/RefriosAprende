"""Acceso a datos para la tabla simulaciones (casos clínicos de diagnóstico)."""
import sqlite3

from database.connection import ConexionBD
from model.entities.simulacion import Simulacion

_SELECT_BASE = """
    SELECT id_simulacion, id_evaluacion, titulo_caso, descripcion_escenario, diagnostico_correcto
    FROM simulaciones
"""


class SimulacionDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Simulacion:
        return Simulacion(
            id_simulacion=fila["id_simulacion"],
            id_evaluacion=fila["id_evaluacion"],
            titulo_caso=fila["titulo_caso"],
            descripcion_escenario=fila["descripcion_escenario"],
            diagnostico_correcto=fila["diagnostico_correcto"],
        )

    def obtener_por_evaluacion(self, id_evaluacion: int) -> Simulacion | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_evaluacion = ?", (id_evaluacion,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def crear(self, id_evaluacion: int, titulo_caso: str, descripcion_escenario: str, diagnostico_correcto: str) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO simulaciones (id_evaluacion, titulo_caso, descripcion_escenario, diagnostico_correcto)
            VALUES (?, ?, ?, ?)
            """,
            (id_evaluacion, titulo_caso, descripcion_escenario, diagnostico_correcto),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def actualizar(self, id_simulacion: int, titulo_caso: str, descripcion_escenario: str, diagnostico_correcto: str) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            UPDATE simulaciones
            SET titulo_caso = ?, descripcion_escenario = ?, diagnostico_correcto = ?
            WHERE id_simulacion = ?
            """,
            (titulo_caso, descripcion_escenario, diagnostico_correcto, id_simulacion),
        )
        self._conexion.confirmar()
