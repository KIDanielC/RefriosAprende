"""Acceso a datos para la tabla entregas_taller."""
import sqlite3

from database.connection import ConexionBD
from model.entities.entrega_taller import EntregaTaller

_SELECT_BASE = """
    SELECT e.id_entrega, e.id_taller, e.id_usuario, e.ruta_archivo, e.nombre_archivo_original,
           e.estado, e.comentario_instructor, e.fecha_entrega, e.fecha_calificacion,
           u.nombre_completo AS nombre_usuario
    FROM entregas_taller e
    INNER JOIN usuarios u ON u.id_usuario = e.id_usuario
"""


class EntregaTallerDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> EntregaTaller:
        return EntregaTaller(
            id_entrega=fila["id_entrega"],
            id_taller=fila["id_taller"],
            id_usuario=fila["id_usuario"],
            ruta_archivo=fila["ruta_archivo"],
            nombre_archivo_original=fila["nombre_archivo_original"],
            estado=fila["estado"],
            comentario_instructor=fila["comentario_instructor"],
            fecha_entrega=fila["fecha_entrega"],
            fecha_calificacion=fila["fecha_calificacion"],
            nombre_usuario=fila["nombre_usuario"],
        )

    def obtener_por_id(self, id_entrega: int) -> EntregaTaller | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE e.id_entrega = ?", (id_entrega,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def obtener_por_taller_y_usuario(self, id_taller: int, id_usuario: int) -> EntregaTaller | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE e.id_taller = ? AND e.id_usuario = ?", (id_taller, id_usuario))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_por_taller(self, id_taller: int) -> list[EntregaTaller]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE e.id_taller = ? ORDER BY e.fecha_entrega", (id_taller,))
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def crear_o_reemplazar(self, id_taller: int, id_usuario: int, ruta_archivo: str, nombre_original: str) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO entregas_taller (id_taller, id_usuario, ruta_archivo, nombre_archivo_original)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (id_taller, id_usuario) DO UPDATE SET
                ruta_archivo = excluded.ruta_archivo,
                nombre_archivo_original = excluded.nombre_archivo_original,
                estado = 'PENDIENTE',
                comentario_instructor = NULL,
                fecha_entrega = datetime('now', 'localtime'),
                fecha_calificacion = NULL
            """,
            (id_taller, id_usuario, ruta_archivo, nombre_original),
        )
        self._conexion.confirmar()

    def calificar(self, id_entrega: int, estado: str, comentario: str) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            UPDATE entregas_taller
            SET estado = ?, comentario_instructor = ?, fecha_calificacion = datetime('now', 'localtime')
            WHERE id_entrega = ?
            """,
            (estado, comentario, id_entrega),
        )
        self._conexion.confirmar()
