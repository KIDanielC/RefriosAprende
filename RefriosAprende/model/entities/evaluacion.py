"""Entidad Evaluación. En Sprint 2 solo se usa como contenedor interno del
cuestionario corto de validación de un contenido (id_contenido NOT NULL)."""


class Evaluacion:
    def __init__(
        self,
        id_evaluacion: int,
        id_curso: int,
        id_contenido: int,
        titulo: str,
        tipo_evaluacion: str,
        nota_minima_aprobar: float,
        intentos_permitidos: int,
    ):
        self.id_evaluacion = id_evaluacion
        self.id_curso = id_curso
        self.id_contenido = id_contenido
        self.titulo = titulo
        self.tipo_evaluacion = tipo_evaluacion
        self.nota_minima_aprobar = nota_minima_aprobar
        self.intentos_permitidos = intentos_permitidos

    def es_validacion_de_contenido(self) -> bool:
        return self.id_contenido is not None

    def __repr__(self):
        return f"Evaluacion(id_evaluacion={self.id_evaluacion}, titulo='{self.titulo}')"
