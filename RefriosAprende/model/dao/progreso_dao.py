"""Acceso a datos para la tabla progreso."""
import sqlite3

from database.connection import ConexionBD
from model.entities.progreso import Progreso

_SELECT_BASE = """
    SELECT id_progreso, id_usuario, id_curso, porcentaje_avance, estado, fecha_actualizacion
    FROM progreso
"""


class ProgresoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Progreso:
        return Progreso(
            id_progreso=fila["id_progreso"],
            id_usuario=fila["id_usuario"],
            id_curso=fila["id_curso"],
            porcentaje_avance=fila["porcentaje_avance"],
            estado=fila["estado"],
            fecha_actualizacion=fila["fecha_actualizacion"],
        )

    def obtener_por_usuario_y_curso(self, id_usuario: int, id_curso: int) -> Progreso | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_usuario = ? AND id_curso = ?", (id_usuario, id_curso))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_por_usuario(self, id_usuario: int) -> list[Progreso]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_usuario = ?", (id_usuario,))
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def listar_por_curso(self, id_curso: int) -> list[Progreso]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_curso = ?", (id_curso,))
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def guardar(self, id_usuario: int, id_curso: int, porcentaje_avance: float, estado: str) -> Progreso:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO progreso (id_usuario, id_curso, porcentaje_avance, estado, fecha_actualizacion)
            VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
            ON CONFLICT (id_usuario, id_curso) DO UPDATE SET
                porcentaje_avance = excluded.porcentaje_avance,
                estado = excluded.estado,
                fecha_actualizacion = excluded.fecha_actualizacion
            """,
            (id_usuario, id_curso, porcentaje_avance, estado),
        )
        self._conexion.confirmar()
        return self.obtener_por_usuario_y_curso(id_usuario, id_curso)
