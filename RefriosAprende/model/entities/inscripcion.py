"""Entidad Inscripción: matrícula de un aprendiz en un curso."""


class Inscripcion:
    def __init__(self, id_inscripcion: int, id_usuario: int, id_curso: int, fecha_inscripcion: str):
        self.id_inscripcion = id_inscripcion
        self.id_usuario = id_usuario
        self.id_curso = id_curso
        self.fecha_inscripcion = fecha_inscripcion

    def __repr__(self):
        return f"Inscripcion(id_usuario={self.id_usuario}, id_curso={self.id_curso})"
