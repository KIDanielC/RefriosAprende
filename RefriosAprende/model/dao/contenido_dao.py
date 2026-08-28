"""Acceso a datos para la tabla contenidos."""
import sqlite3

from database.connection import ConexionBD
from model.entities.contenido import Contenido

_SELECT_BASE = """
    SELECT id_contenido, id_curso, titulo, tipo_contenido, ruta_archivo, contenido_texto, orden
    FROM contenidos
"""


class ContenidoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Contenido:
        return Contenido(
            id_contenido=fila["id_contenido"],
            id_curso=fila["id_curso"],
            titulo=fila["titulo"],
            tipo_contenido=fila["tipo_contenido"],
            ruta_archivo=fila["ruta_archivo"],
            contenido_texto=fila["contenido_texto"],
            orden=fila["orden"],
        )

    def listar_por_curso(self, id_curso: int) -> list[Contenido]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_curso = ? ORDER BY orden ASC", (id_curso,))
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def obtener_por_id(self, id_contenido: int) -> Contenido | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_contenido = ?", (id_contenido,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def obtener_siguiente_orden(self, id_curso: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT COALESCE(MAX(orden), 0) + 1 AS siguiente FROM contenidos WHERE id_curso = ?", (id_curso,))
        return cursor.fetchone()["siguiente"]

    def crear(self, id_curso: int, titulo: str, contenido_texto: str, orden: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO contenidos (id_curso, titulo, tipo_contenido, ruta_archivo, contenido_texto, orden)
            VALUES (?, ?, 'TEXTO', NULL, ?, ?)
            """,
            (id_curso, titulo, contenido_texto, orden),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def actualizar(self, id_contenido: int, titulo: str, contenido_texto: str, orden: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "UPDATE contenidos SET titulo = ?, contenido_texto = ?, orden = ? WHERE id_contenido = ?",
            (titulo, contenido_texto, orden, id_contenido),
        )
        self._conexion.confirmar()

    def eliminar(self, id_contenido: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM contenidos WHERE id_contenido = ?", (id_contenido,))
        self._conexion.confirmar()
