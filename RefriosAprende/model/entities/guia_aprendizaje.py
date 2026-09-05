"""Entidad Guía de Aprendizaje: documento pedagógico completo de un curso, organizado según
la metodología aprender -> practicar -> simular -> evaluar. Una guía por curso, compartida por
todos los aprendices matriculados."""


class GuiaAprendizaje:
    def __init__(
        self,
        id_guia: int,
        id_curso: int,
        objetivo_general: str,
        objetivos_especificos: str,
        competencias: str,
        introduccion: str,
        conocimientos_previos: str,
        procedimiento_paso_a_paso: str,
        normas_seguridad: str,
        ejemplos_practicos: str,
        actividades_interactivas: str,
        criterios_evaluacion: str,
        glosario: str,
        referencias: str,
        duracion_horas: int,
        fecha_actualizacion: str,
    ):
        self.id_guia = id_guia
        self.id_curso = id_curso
        self.objetivo_general = objetivo_general
        self.objetivos_especificos = objetivos_especificos
        self.competencias = competencias
        self.introduccion = introduccion
        self.conocimientos_previos = conocimientos_previos
        self.procedimiento_paso_a_paso = procedimiento_paso_a_paso
        self.normas_seguridad = normas_seguridad
        self.ejemplos_practicos = ejemplos_practicos
        self.actividades_interactivas = actividades_interactivas
        self.criterios_evaluacion = criterios_evaluacion
        self.glosario = glosario
        self.referencias = referencias
        self.duracion_horas = duracion_horas
        self.fecha_actualizacion = fecha_actualizacion

    def esta_completa(self) -> bool:
        return bool((self.objetivo_general or "").strip())

    def __repr__(self):
        return f"GuiaAprendizaje(id_guia={self.id_guia}, id_curso={self.id_curso})"
