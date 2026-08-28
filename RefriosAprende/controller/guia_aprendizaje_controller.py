"""Controlador de la Guía de Aprendizaje de un curso: valida y coordina Vista <-> Modelo."""
from model.dao.guia_aprendizaje_dao import GuiaAprendizajeDAO
from model.entities.guia_aprendizaje import GuiaAprendizaje


class DatosGuiaInvalidosError(Exception):
    """Los datos de la guía de aprendizaje no cumplen las reglas de negocio."""


class GuiaAprendizajeController:
    def __init__(self):
        self._guia_dao = GuiaAprendizajeDAO()

    def obtener_guia(self, id_curso: int) -> GuiaAprendizaje | None:
        return self._guia_dao.obtener_por_curso(id_curso)

    def guardar_guia(
        self,
        id_curso: int,
        objetivo_general: str,
        objetivos_especificos: str,
        competencias: str,
        actividades: str,
        criterios_evaluacion: str,
        duracion_horas: str,
    ) -> GuiaAprendizaje:
        objetivo_general = (objetivo_general or "").strip()
        if len(objetivo_general) < 10:
            raise DatosGuiaInvalidosError("El objetivo general debe tener al menos 10 caracteres.")

        duracion_valor = None
        duracion_texto = (duracion_horas or "").strip()
        if duracion_texto:
            try:
                duracion_valor = int(duracion_texto)
            except ValueError:
                raise DatosGuiaInvalidosError("La duración en horas debe ser un número entero.")
            if duracion_valor <= 0:
                raise DatosGuiaInvalidosError("La duración en horas debe ser mayor a cero.")

        self._guia_dao.guardar(
            id_curso,
            objetivo_general,
            (objetivos_especificos or "").strip(),
            (competencias or "").strip(),
            (actividades or "").strip(),
            (criterios_evaluacion or "").strip(),
            duracion_valor,
        )
        return self._guia_dao.obtener_por_curso(id_curso)
