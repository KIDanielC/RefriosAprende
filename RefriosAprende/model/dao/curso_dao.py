"""Acceso a datos para la tabla cursos."""
import sqlite3

from database.connection import ConexionBD
from model.entities.curso import Curso

_SELECT_BASE = """
    SELECT c.id_curso, c.nombre_curso, c.descripcion, c.id_instructor,
           c.estado, c.fecha_creacion, u.nombre_completo AS nombre_instructor
    FROM cursos c
    INNER JOIN usuarios u ON u.id_usuario = c.id_instructor
"""


class CursoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Curso:
        return Curso(
            id_curso=fila["id_curso"],
            nombre_curso=fila["nombre_curso"],
            descripcion=fila["descripcion"],
            id_instructor=fila["id_instructor"],
            estado=fila["estado"],
            fecha_creacion=fila["fecha_creacion"],
            nombre_instructor=fila["nombre_instructor"],
        )

    def obtener_por_id(self, id_curso: int) -> Curso | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE c.id_curso = ?", (id_curso,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_todos(self) -> list[Curso]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} ORDER BY c.fecha_creacion DESC")
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def contar_activos(self) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM cursos WHERE estado = 'ACTIVO'")
        return cursor.fetchone()["total"]

    def crear(self, nombre_curso: str, descripcion: str, id_instructor: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT INTO cursos (nombre_curso, descripcion, id_instructor) VALUES (?, ?, ?)",
            (nombre_curso, descripcion, id_instructor),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def actualizar(
        self, id_curso: int, nombre_curso: str, descripcion: str, id_instructor: int, estado: str
    ) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            UPDATE cursos
            SET nombre_curso = ?, descripcion = ?, id_instructor = ?, estado = ?
            WHERE id_curso = ?
            """,
            (nombre_curso, descripcion, id_instructor, estado, id_curso),
        )
        self._conexion.confirmar()

    def eliminar(self, id_curso: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM cursos WHERE id_curso = ?", (id_curso,))
        self._conexion.confirmar()
