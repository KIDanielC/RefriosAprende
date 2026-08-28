"""Entidad Curso."""


class Curso:
    def __init__(
        self,
        id_curso: int,
        nombre_curso: str,
        descripcion: str,
        id_instructor: int,
        estado: str,
        fecha_creacion: str,
        nombre_instructor: str = None,
    ):
        self.id_curso = id_curso
        self.nombre_curso = nombre_curso
        self.descripcion = descripcion
        self.id_instructor = id_instructor
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.nombre_instructor = nombre_instructor

    def esta_activo(self) -> bool:
        return self.estado == "ACTIVO"

    def __repr__(self):
        return f"Curso(id_curso={self.id_curso}, nombre_curso='{self.nombre_curso}', estado='{self.estado}')"
