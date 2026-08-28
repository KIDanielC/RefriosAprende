"""Acceso a datos para la tabla evaluaciones."""
import sqlite3

from database.connection import ConexionBD
from model.entities.evaluacion import Evaluacion

_SELECT_BASE = """
    SELECT id_evaluacion, id_curso, id_contenido, titulo, tipo_evaluacion,
           nota_minima_aprobar, intentos_permitidos
    FROM evaluaciones
"""


class EvaluacionDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Evaluacion:
        return Evaluacion(
            id_evaluacion=fila["id_evaluacion"],
            id_curso=fila["id_curso"],
            id_contenido=fila["id_contenido"],
            titulo=fila["titulo"],
            tipo_evaluacion=fila["tipo_evaluacion"],
            nota_minima_aprobar=fila["nota_minima_aprobar"],
            intentos_permitidos=fila["intentos_permitidos"],
        )

    def obtener_por_contenido(self, id_contenido: int) -> Evaluacion | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_contenido = ?", (id_contenido,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def crear_para_contenido(self, id_curso: int, id_contenido: int, titulo: str) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO evaluaciones (id_curso, id_contenido, titulo, tipo_evaluacion)
            VALUES (?, ?, ?, 'CUESTIONARIO')
            """,
            (id_curso, id_contenido, titulo),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def obtener_o_crear_para_contenido(self, id_curso: int, id_contenido: int, titulo: str) -> Evaluacion:
        evaluacion = self.obtener_por_contenido(id_contenido)
        if evaluacion is not None:
            return evaluacion
        self.crear_para_contenido(id_curso, id_contenido, titulo)
        return self.obtener_por_contenido(id_contenido)

    # -- Evaluaciones a nivel de curso (evaluación final y simulaciones) ------
    def obtener_por_id(self, id_evaluacion: int) -> Evaluacion | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_evaluacion = ?", (id_evaluacion,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def obtener_evaluacion_final_por_curso(self, id_curso: int) -> Evaluacion | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            f"{_SELECT_BASE} WHERE id_curso = ? AND id_contenido IS NULL AND tipo_evaluacion = 'CUESTIONARIO'",
            (id_curso,),
        )
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def listar_simulaciones_por_curso(self, id_curso: int) -> list[Evaluacion]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            f"{_SELECT_BASE} WHERE id_curso = ? AND id_contenido IS NULL AND tipo_evaluacion = 'SIMULACION' "
            "ORDER BY id_evaluacion",
            (id_curso,),
        )
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def crear_evaluacion_curso(
        self, id_curso: int, titulo: str, tipo_evaluacion: str, nota_minima_aprobar: float, intentos_permitidos: int
    ) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO evaluaciones (id_curso, id_contenido, titulo, tipo_evaluacion, nota_minima_aprobar, intentos_permitidos)
            VALUES (?, NULL, ?, ?, ?, ?)
            """,
            (id_curso, titulo, tipo_evaluacion, nota_minima_aprobar, intentos_permitidos),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def actualizar_evaluacion_curso(
        self, id_evaluacion: int, titulo: str, nota_minima_aprobar: float, intentos_permitidos: int
    ) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "UPDATE evaluaciones SET titulo = ?, nota_minima_aprobar = ?, intentos_permitidos = ? WHERE id_evaluacion = ?",
            (titulo, nota_minima_aprobar, intentos_permitidos, id_evaluacion),
        )
        self._conexion.confirmar()

    def eliminar(self, id_evaluacion: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute("DELETE FROM evaluaciones WHERE id_evaluacion = ?", (id_evaluacion,))
        self._conexion.confirmar()
