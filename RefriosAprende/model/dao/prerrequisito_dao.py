"""Acceso a datos para la tabla cursos_prerrequisitos (prerrequisitos entre cursos)."""
import sqlite3

from database.connection import ConexionBD
from model.entities.curso import Curso

_SELECT_PRERREQUISITOS = """
    SELECT c.id_curso, c.nombre_curso, c.descripcion, c.id_instructor, c.id_categoria,
           c.estado, c.aprendizaje_secuencial, c.fecha_creacion, u.nombre_completo AS nombre_instructor
    FROM cursos_prerrequisitos cp
    INNER JOIN cursos c ON c.id_curso = cp.id_curso_prerrequisito
    INNER JOIN usuarios u ON u.id_usuario = c.id_instructor
    WHERE cp.id_curso = ?
    ORDER BY c.nombre_curso
"""


class PrerrequisitoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_curso(self, fila: sqlite3.Row) -> Curso:
        return Curso(
            id_curso=fila["id_curso"], nombre_curso=fila["nombre_curso"], descripcion=fila["descripcion"],
            id_instructor=fila["id_instructor"], id_categoria=fila["id_categoria"], estado=fila["estado"],
            aprendizaje_secuencial=fila["aprendizaje_secuencial"], fecha_creacion=fila["fecha_creacion"],
            nombre_instructor=fila["nombre_instructor"],
        )

    def listar_prerrequisitos(self, id_curso: int) -> list[Curso]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(_SELECT_PRERREQUISITOS, (id_curso,))
        return [self._fila_a_curso(fila) for fila in cursor.fetchall()]

    def listar_ids_prerrequisitos(self, id_curso: int) -> list[int]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_curso_prerrequisito FROM cursos_prerrequisitos WHERE id_curso = ?", (id_curso,))
        return [fila["id_curso_prerrequisito"] for fila in cursor.fetchall()]

    def guardar_prerrequisitos(self, id_curso: int, ids_prerrequisitos: list[int]) -> None:
        """Reemplaza por completo el conjunto de prerrequisitos de un curso."""
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM cursos_prerrequisitos WHERE id_curso = ?", (id_curso,))
        for id_prerrequisito in ids_prerrequisitos:
            if id_prerrequisito == id_curso:
                continue
            cursor.execute(
                "INSERT OR IGNORE INTO cursos_prerrequisitos (id_curso, id_curso_prerrequisito) VALUES (?, ?)",
                (id_curso, id_prerrequisito),
            )
        self._conexion.confirmar()
