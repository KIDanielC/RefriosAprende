"""Entidad Taller: ejercicio práctico/entrega que el instructor asigna a un curso."""


class Taller:
    def __init__(self, id_taller: int, id_curso: int, titulo: str, descripcion: str, fecha_creacion: str):
        self.id_taller = id_taller
        self.id_curso = id_curso
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion

    def __repr__(self):
        return f"Taller(id_taller={self.id_taller}, titulo='{self.titulo}')"
