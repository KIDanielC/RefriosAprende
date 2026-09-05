"""Acceso a datos para la tabla guias_aprendizaje."""
import sqlite3

from database.connection import ConexionBD
from model.entities.guia_aprendizaje import GuiaAprendizaje

_SELECT_BASE = """
    SELECT id_guia, id_curso, objetivo_general, objetivos_especificos, competencias,
           introduccion, conocimientos_previos, procedimiento_paso_a_paso, normas_seguridad,
           ejemplos_practicos, actividades_interactivas, criterios_evaluacion,
           glosario, referencias, duracion_horas, fecha_actualizacion
    FROM guias_aprendizaje
"""

# Columnas de texto libre que se guardan/leen genéricamente vía dict (12 en total). id_curso y
# duracion_horas quedan fuera: tienen tipo y validación propios, no son texto libre simétrico.
COLUMNAS_TEXTO_LIBRE = (
    "objetivo_general", "objetivos_especificos", "competencias",
    "introduccion", "conocimientos_previos",
    "procedimiento_paso_a_paso", "normas_seguridad", "ejemplos_practicos", "actividades_interactivas",
    "criterios_evaluacion",
    "glosario", "referencias",
)


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
            introduccion=fila["introduccion"],
            conocimientos_previos=fila["conocimientos_previos"],
            procedimiento_paso_a_paso=fila["procedimiento_paso_a_paso"],
            normas_seguridad=fila["normas_seguridad"],
            ejemplos_practicos=fila["ejemplos_practicos"],
            actividades_interactivas=fila["actividades_interactivas"],
            criterios_evaluacion=fila["criterios_evaluacion"],
            glosario=fila["glosario"],
            referencias=fila["referencias"],
            duracion_horas=fila["duracion_horas"],
            fecha_actualizacion=fila["fecha_actualizacion"],
        )

    def obtener_por_curso(self, id_curso: int) -> GuiaAprendizaje | None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_curso = ?", (id_curso,))
        fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def guardar(self, id_curso: int, campos: dict[str, str], duracion_horas: int | None) -> None:
        """Upsert de la guía completa. `campos` trae (algunas o todas) las claves de
        COLUMNAS_TEXTO_LIBRE; las que falten se guardan como cadena vacía."""
        columnas = ", ".join(COLUMNAS_TEXTO_LIBRE)
        placeholders = ", ".join(["?"] * len(COLUMNAS_TEXTO_LIBRE))
        actualizaciones = ", ".join(f"{columna} = excluded.{columna}" for columna in COLUMNAS_TEXTO_LIBRE)
        valores = tuple(campos.get(columna, "") for columna in COLUMNAS_TEXTO_LIBRE)

        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            f"""
            INSERT INTO guias_aprendizaje (id_curso, {columnas}, duracion_horas, fecha_actualizacion)
            VALUES (?, {placeholders}, ?, datetime('now', 'localtime'))
            ON CONFLICT (id_curso) DO UPDATE SET
                {actualizaciones},
                duracion_horas = excluded.duracion_horas,
                fecha_actualizacion = excluded.fecha_actualizacion
            """,
            (id_curso, *valores, duracion_horas),
        )
        self._conexion.confirmar()
