"""Entidad Opción (alternativa de respuesta de una pregunta)."""


class Opcion:
    def __init__(self, id_opcion: int, id_pregunta: int, texto_opcion: str, es_correcta: bool):
        self.id_opcion = id_opcion
        self.id_pregunta = id_pregunta
        self.texto_opcion = texto_opcion
        self.es_correcta = bool(es_correcta)

    def __repr__(self):
        marca = "✓" if self.es_correcta else " "
        return f"Opcion([{marca}] '{self.texto_opcion}')"
