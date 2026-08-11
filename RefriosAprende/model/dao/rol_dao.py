"""Acceso a datos para la tabla roles."""
from database.connection import ConexionBD
from model.entities.rol import Rol


class RolDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def obtener_por_id(self, id_rol: int) -> Rol | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE id_rol = ?", (id_rol,))
        fila = cursor.fetchone()
        return Rol(fila["id_rol"], fila["nombre_rol"]) if fila else None

    def obtener_por_nombre(self, nombre_rol: str) -> Rol | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE nombre_rol = ?", (nombre_rol,))
        fila = cursor.fetchone()
        return Rol(fila["id_rol"], fila["nombre_rol"]) if fila else None

    def listar_todos(self) -> list[Rol]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_rol, nombre_rol FROM roles ORDER BY nombre_rol")
        return [Rol(fila["id_rol"], fila["nombre_rol"]) for fila in cursor.fetchall()]
