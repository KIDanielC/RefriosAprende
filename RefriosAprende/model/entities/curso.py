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
        id_categoria: int = None,
        nombre_categoria: str = None,
        aprendizaje_secuencial: bool = False,
    ):
        self.id_curso = id_curso
        self.nombre_curso = nombre_curso
        self.descripcion = descripcion
        self.id_instructor = id_instructor
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.nombre_instructor = nombre_instructor
        self.id_categoria = id_categoria
        self.nombre_categoria = nombre_categoria
        self.aprendizaje_secuencial = bool(aprendizaje_secuencial)

    def esta_activo(self) -> bool:
        return self.estado == "ACTIVO"

    def es_borrador(self) -> bool:
        return self.estado == "BORRADOR"

    def __repr__(self):
        return f"Curso(id_curso={self.id_curso}, nombre_curso='{self.nombre_curso}', estado='{self.estado}')"
