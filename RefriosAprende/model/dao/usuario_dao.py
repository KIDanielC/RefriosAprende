"""Acceso a datos para la tabla usuarios."""
import sqlite3

from database.connection import ConexionBD
from model.entities.usuario import Usuario

_SELECT_BASE = """
    SELECT u.id_usuario, u.nombre_completo, u.documento, u.correo, u.usuario,
           u.contrasena_hash, u.id_rol, u.activo, u.fecha_creacion, r.nombre_rol
    FROM usuarios u
    INNER JOIN roles r ON r.id_rol = u.id_rol
"""


class UsuarioYaExisteError(Exception):
    """Se lanza cuando el documento, correo o usuario ya están registrados."""


class UsuarioDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Usuario:
        return Usuario(
            id_usuario=fila["id_usuario"],
            nombre_completo=fila["nombre_completo"],
            documento=fila["documento"],
            correo=fila["correo"],
            usuario=fila["usuario"],
            contrasena_hash=fila["contrasena_hash"],
            id_rol=fila["id_rol"],
            activo=fila["activo"],
            fecha_creacion=fila["fecha_creacion"],
            nombre_rol=fila["nombre_rol"],
        )

    def obtener_por_usuario(self, usuario: str) -> Usuario | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE u.usuario = ?", (usuario,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE u.id_usuario = ?", (id_usuario,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_todos(self) -> list[Usuario]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} ORDER BY u.nombre_completo")
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def crear(
        self,
        nombre_completo: str,
        documento: str,
        correo: str,
        usuario: str,
        contrasena_hash: str,
        id_rol: int,
    ) -> int:
        cursor = self._conexion.obtener_cursor()
        try:
            cursor.execute(
                """
                INSERT INTO usuarios
                    (nombre_completo, documento, correo, usuario, contrasena_hash, id_rol)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nombre_completo, documento, correo, usuario, contrasena_hash, id_rol),
            )
            self._conexion.confirmar()
            return cursor.lastrowid
        except sqlite3.IntegrityError as error:
            raise UsuarioYaExisteError(
                "El documento, correo o nombre de usuario ya está registrado."
            ) from error

    def actualizar(
        self,
        id_usuario: int,
        nombre_completo: str,
        documento: str,
        correo: str,
        id_rol: int,
        activo: bool,
    ) -> None:
        cursor = self._conexion.obtener_cursor()
        try:
            cursor.execute(
                """
                UPDATE usuarios
                SET nombre_completo = ?, documento = ?, correo = ?, id_rol = ?, activo = ?
                WHERE id_usuario = ?
                """,
                (nombre_completo, documento, correo, id_rol, int(activo), id_usuario),
            )
            self._conexion.confirmar()
        except sqlite3.IntegrityError as error:
            raise UsuarioYaExisteError(
                "El documento o correo ya está registrado en otro usuario."
            ) from error

    def actualizar_contrasena(self, id_usuario: int, contrasena_hash: str) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "UPDATE usuarios SET contrasena_hash = ? WHERE id_usuario = ?",
            (contrasena_hash, id_usuario),
        )
        self._conexion.confirmar()

    def eliminar(self, id_usuario: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        self._conexion.confirmar()
