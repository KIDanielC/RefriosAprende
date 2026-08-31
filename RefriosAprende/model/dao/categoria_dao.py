"""Acceso a datos para la tabla categorias."""
import sqlite3

from database.connection import ConexionBD
from model.entities.categoria import Categoria


class CategoriaDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Categoria:
        return Categoria(id_categoria=fila["id_categoria"], nombre_categoria=fila["nombre_categoria"])

    def obtener_por_id(self, id_categoria: int) -> Categoria | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias WHERE id_categoria = ?", (id_categoria,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def obtener_por_nombre(self, nombre_categoria: str) -> Categoria | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias WHERE nombre_categoria = ?", (nombre_categoria,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_todas(self) -> list[Categoria]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria")
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def obtener_o_crear(self, nombre_categoria: str) -> Categoria:
        """Devuelve la categoría existente con ese nombre, o la crea si no existe todavía."""
        existente = self.obtener_por_nombre(nombre_categoria)
        if existente is not None:
            return existente
        cursor = self._conexion.obtener_cursor()
        cursor.execute("INSERT INTO categorias (nombre_categoria) VALUES (?)", (nombre_categoria,))
        self._conexion.confirmar()
        return self.obtener_por_id(cursor.lastrowid)
