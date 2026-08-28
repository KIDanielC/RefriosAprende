"""Acceso a datos para la tabla guias_aprendizaje."""
import sqlite3

from database.connection import ConexionBD
from model.entities.guia_aprendizaje import GuiaAprendizaje

_SELECT_BASE = """
    SELECT id_guia, id_curso, objetivo_general, objetivos_especificos, competencias,
           actividades, criterios_evaluacion, duracion_horas, fecha_actualizacion
    FROM guias_aprendizaje
"""


class GuiaAprendizajeDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> GuiaAprendizaje:
        return GuiaAprendizaje(
            id_guia=fila["id_guia"],
            id_curso=fila["id_curso"],
            objetivo_general=fila["objetivo_general"],
            objetivos_especificos=fila["objetivos_especificos"],
            competencias=fila["competencias"],
            actividades=fila["actividades"],
            criterios_evaluacion=fila["criterios_evaluacion"],
            duracion_horas=fila["duracion_horas"],
            fecha_actualizacion=fila["fecha_actualizacion"],
        )

    def obtener_por_curso(self, id_curso: int) -> GuiaAprendizaje | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_curso = ?", (id_curso,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def guardar(
        self,
        id_curso: int,
        objetivo_general: str,
        objetivos_especificos: str,
        competencias: str,
        actividades: str,
        criterios_evaluacion: str,
        duracion_horas: int | None,
    ) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            INSERT INTO guias_aprendizaje
                (id_curso, objetivo_general, objetivos_especificos, competencias,
                 actividades, criterios_evaluacion, duracion_horas, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            ON CONFLICT (id_curso) DO UPDATE SET
                objetivo_general = excluded.objetivo_general,
                objetivos_especificos = excluded.objetivos_especificos,
                competencias = excluded.competencias,
                actividades = excluded.actividades,
                criterios_evaluacion = excluded.criterios_evaluacion,
                duracion_horas = excluded.duracion_horas,
                fecha_actualizacion = excluded.fecha_actualizacion
            """,
            (
                id_curso, objetivo_general, objetivos_especificos, competencias,
                actividades, criterios_evaluacion, duracion_horas,
            ),
        )
        self._conexion.confirmar()
