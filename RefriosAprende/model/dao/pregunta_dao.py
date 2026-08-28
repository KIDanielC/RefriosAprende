"""Acceso a datos para la tabla preguntas."""
import sqlite3

from database.connection import ConexionBD
from model.dao.opcion_dao import OpcionDAO
from model.entities.pregunta import Pregunta


class PreguntaDAO:
    def __init__(self):
        self._conexion = ConexionBD()
        self._opcion_dao = OpcionDAO()

    def _fila_a_entidad(self, fila: sqlite3.Row, incluir_opciones: bool = True) -> Pregunta:
        opciones = self._opcion_dao.listar_por_pregunta(fila["id_pregunta"]) if incluir_opciones else []
        return Pregunta(
            id_pregunta=fila["id_pregunta"],
            id_evaluacion=fila["id_evaluacion"],
            enunciado=fila["enunciado"],
            orden=fila["orden"],
            opciones=opciones,
        )

    def listar_por_evaluacion(self, id_evaluacion: int) -> list[Pregunta]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT id_pregunta, id_evaluacion, enunciado, orden FROM preguntas WHERE id_evaluacion = ? ORDER BY orden",
            (id_evaluacion,),
        )
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def obtener_por_id(self, id_pregunta: int) -> Pregunta | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT id_pregunta, id_evaluacion, enunciado, orden FROM preguntas WHERE id_pregunta = ?",
            (id_pregunta,),
        )
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def obtener_siguiente_orden(self, id_evaluacion: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT COALESCE(MAX(orden), 0) + 1 AS siguiente FROM preguntas WHERE id_evaluacion = ?", (id_evaluacion,)
        )
        return cursor.fetchone()["siguiente"]

    def crear(self, id_evaluacion: int, enunciado: str, orden: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT INTO preguntas (id_evaluacion, enunciado, orden) VALUES (?, ?, ?)",
            (id_evaluacion, enunciado, orden),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def actualizar_enunciado(self, id_pregunta: int, enunciado: str) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("UPDATE preguntas SET enunciado = ? WHERE id_pregunta = ?", (enunciado, id_pregunta))
        self._conexion.confirmar()

    def eliminar(self, id_pregunta: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM preguntas WHERE id_pregunta = ?", (id_pregunta,))
        self._conexion.confirmar()
