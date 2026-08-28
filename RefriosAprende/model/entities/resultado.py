"""Entidad Resultado: intento de un aprendiz sobre una evaluación (final o simulación)."""


class Resultado:
    def __init__(
        self,
        id_resultado: int,
        id_usuario: int,
        id_evaluacion: int,
        nota_obtenida: float,
        aprobado: bool,
        fecha_intento: str,
    ):
        self.id_resultado = id_resultado
        self.id_usuario = id_usuario
        self.id_evaluacion = id_evaluacion
        self.nota_obtenida = nota_obtenida
        self.aprobado = bool(aprobado)
        self.fecha_intento = fecha_intento

    def __repr__(self):
        return f"Resultado(id_evaluacion={self.id_evaluacion}, nota={self.nota_obtenida}, aprobado={self.aprobado})"
