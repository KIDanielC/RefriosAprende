"""Acceso a datos para la tabla talleres."""
import sqlite3

from database.connection import ConexionBD
from model.entities.taller import Taller


class TallerDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Taller:
        return Taller(
            id_taller=fila["id_taller"],
            id_curso=fila["id_curso"],
            titulo=fila["titulo"],
            descripcion=fila["descripcion"],
            fecha_creacion=fila["fecha_creacion"],
        )

    def crear(self, id_curso: int, titulo: str, descripcion: str) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT INTO talleres (id_curso, titulo, descripcion) VALUES (?, ?, ?)",
            (id_curso, titulo, descripcion),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def obtener_por_id(self, id_taller: int) -> Taller | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT * FROM talleres WHERE id_taller = ?", (id_taller,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_por_curso(self, id_curso: int) -> list[Taller]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT * FROM talleres WHERE id_curso = ? ORDER BY fecha_creacion", (id_curso,))
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def actualizar(self, id_taller: int, titulo: str, descripcion: str) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "UPDATE talleres SET titulo = ?, descripcion = ? WHERE id_taller = ?",
            (titulo, descripcion, id_taller),
        )
        self._conexion.confirmar()

    def eliminar(self, id_taller: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM talleres WHERE id_taller = ?", (id_taller,))
        self._conexion.confirmar()
