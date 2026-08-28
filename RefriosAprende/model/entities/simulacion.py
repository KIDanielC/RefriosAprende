"""Entidad Simulacion: caso clínico de diagnóstico asociado a una evaluación tipo SIMULACION."""


class Simulacion:
    def __init__(
        self,
        id_simulacion: int,
        id_evaluacion: int,
        titulo_caso: str,
        descripcion_escenario: str,
        diagnostico_correcto: str,
    ):
        self.id_simulacion = id_simulacion
        self.id_evaluacion = id_evaluacion
        self.titulo_caso = titulo_caso
        self.descripcion_escenario = descripcion_escenario
        self.diagnostico_correcto = diagnostico_correcto

    def __repr__(self):
        return f"Simulacion(id_simulacion={self.id_simulacion}, titulo_caso='{self.titulo_caso}')"
