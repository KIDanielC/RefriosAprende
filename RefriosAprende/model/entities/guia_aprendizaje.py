"""Entidad Guía de Aprendizaje: objetivos, competencias y actividades de un curso."""


class GuiaAprendizaje:
    def __init__(
        self,
        id_guia: int,
        id_curso: int,
        objetivo_general: str,
        objetivos_especificos: str,
        competencias: str,
        actividades: str,
        criterios_evaluacion: str,
        duracion_horas: int,
        fecha_actualizacion: str,
    ):
        self.id_guia = id_guia
        self.id_curso = id_curso
        self.objetivo_general = objetivo_general
        self.objetivos_especificos = objetivos_especificos
        self.competencias = competencias
        self.actividades = actividades
        self.criterios_evaluacion = criterios_evaluacion
        self.duracion_horas = duracion_horas
        self.fecha_actualizacion = fecha_actualizacion

    def esta_completa(self) -> bool:
        return bool((self.objetivo_general or "").strip())

    def __repr__(self):
        return f"GuiaAprendizaje(id_guia={self.id_guia}, id_curso={self.id_curso})"
