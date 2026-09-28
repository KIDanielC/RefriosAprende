"""Entidad TiempoUsoCurso: un registro de tiempo real que un aprendiz pasó con la pantalla
de un curso abierta (base para comparar horas acumuladas vs. duración estimada del curso)."""


class TiempoUsoCurso:
    def __init__(
        self, id_registro: int, id_usuario: int, id_curso: int,
        fecha_inicio: str, fecha_fin: str, duracion_segundos: int,
    ):
        self.id_registro = id_registro
        self.id_usuario = id_usuario
        self.id_curso = id_curso
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.duracion_segundos = duracion_segundos
