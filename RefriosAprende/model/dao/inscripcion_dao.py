"""Acceso a datos para la tabla inscripciones (matrícula de aprendices en cursos)."""
import sqlite3

from database.connection import ConexionBD
from model.entities.curso import Curso
from model.entities.usuario import Usuario

_SELECT_USUARIOS_MATRICULADOS = """
    SELECT u.id_usuario, u.nombre_completo, u.documento, u.correo, u.usuario,
           u.contrasena_hash, u.id_rol, u.activo, u.fecha_creacion, r.nombre_rol
    FROM inscripciones i
    INNER JOIN usuarios u ON u.id_usuario = i.id_usuario
    INNER JOIN roles r ON r.id_rol = u.id_rol
    WHERE i.id_curso = ?
    ORDER BY u.nombre_completo
"""

_SELECT_CURSOS_MATRICULADOS = """
    SELECT c.id_curso, c.nombre_curso, c.descripcion, c.id_instructor,
           c.estado, c.fecha_creacion, ui.nombre_completo AS nombre_instructor
    FROM inscripciones i
    INNER JOIN cursos c ON c.id_curso = i.id_curso
    INNER JOIN usuarios ui ON ui.id_usuario = c.id_instructor
    WHERE i.id_usuario = ?
    ORDER BY c.nombre_curso
"""


class InscripcionDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_usuario(self, fila: sqlite3.Row) -> Usuario:
        return Usuario(
            id_usuario=fila["id_usuario"], nombre_completo=fila["nombre_completo"], documento=fila["documento"],
            correo=fila["correo"], usuario=fila["usuario"], contrasena_hash=fila["contrasena_hash"],
            id_rol=fila["id_rol"], activo=fila["activo"], fecha_creacion=fila["fecha_creacion"],
            nombre_rol=fila["nombre_rol"],
        )

    def _fila_a_curso(self, fila: sqlite3.Row) -> Curso:
        return Curso(
            id_curso=fila["id_curso"], nombre_curso=fila["nombre_curso"], descripcion=fila["descripcion"],
            id_instructor=fila["id_instructor"], estado=fila["estado"], fecha_creacion=fila["fecha_creacion"],
            nombre_instructor=fila["nombre_instructor"],
        )

    def existe(self, id_usuario: int, id_curso: int) -> bool:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT 1 FROM inscripciones WHERE id_usuario = ? AND id_curso = ? LIMIT 1", (id_usuario, id_curso)
        )
        return cursor.fetchone() is not None

    def matricular(self, id_usuario: int, id_curso: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO inscripciones (id_usuario, id_curso) VALUES (?, ?)", (id_usuario, id_curso)
        )
        self._conexion.confirmar()

    def desmatricular(self, id_usuario: int, id_curso: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM inscripciones WHERE id_usuario = ? AND id_curso = ?", (id_usuario, id_curso))
        self._conexion.confirmar()

    def listar_usuarios_matriculados(self, id_curso: int) -> list[Usuario]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(_SELECT_USUARIOS_MATRICULADOS, (id_curso,))
        return [self._fila_a_usuario(fila) for fila in cursor.fetchall()]

    def listar_cursos_matriculados(self, id_usuario: int) -> list[Curso]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(_SELECT_CURSOS_MATRICULADOS, (id_usuario,))
        return [self._fila_a_curso(fila) for fila in cursor.fetchall()]

    def contar_matriculados(self, id_curso: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM inscripciones WHERE id_curso = ?", (id_curso,))
        return cursor.fetchone()["total"]
