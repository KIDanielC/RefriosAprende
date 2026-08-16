"""Entidad Pregunta, con sus opciones de respuesta asociadas."""
from model.entities.opcion import Opcion


class Pregunta:
    def __init__(self, id_pregunta: int, id_evaluacion: int, enunciado: str, orden: int, opciones: list[Opcion] = None):
        self.id_pregunta = id_pregunta
        self.id_evaluacion = id_evaluacion
        self.enunciado = enunciado
        self.orden = orden
        self.opciones = opciones or []

    def opcion_correcta(self) -> Opcion | None:
        return next((opcion for opcion in self.opciones if opcion.es_correcta), None)

    def __repr__(self):
        return f"Pregunta(id_pregunta={self.id_pregunta}, enunciado='{self.enunciado}', opciones={len(self.opciones)})"
