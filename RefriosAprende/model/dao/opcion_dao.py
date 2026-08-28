"""Acceso a datos para la tabla opciones."""
import sqlite3

from database.connection import ConexionBD
from model.entities.opcion import Opcion


class OpcionDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Opcion:
        return Opcion(
            id_opcion=fila["id_opcion"],
            id_pregunta=fila["id_pregunta"],
            texto_opcion=fila["texto_opcion"],
            es_correcta=fila["es_correcta"],
        )

    def listar_por_pregunta(self, id_pregunta: int) -> list[Opcion]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT id_opcion, id_pregunta, texto_opcion, es_correcta FROM opciones WHERE id_pregunta = ? ORDER BY id_opcion",
            (id_pregunta,),
        )
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def crear(self, id_pregunta: int, texto_opcion: str, es_correcta: bool) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES (?, ?, ?)",
            (id_pregunta, texto_opcion, int(es_correcta)),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def eliminar_por_pregunta(self, id_pregunta: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM opciones WHERE id_pregunta = ?", (id_pregunta,))
        self._conexion.confirmar()
