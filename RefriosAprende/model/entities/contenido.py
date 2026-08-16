"""Entidad Contenido (unidad de aprendizaje dentro de un curso)."""


class Contenido:
    def __init__(
        self,
        id_contenido: int,
        id_curso: int,
        titulo: str,
        tipo_contenido: str,
        ruta_archivo: str,
        contenido_texto: str,
        orden: int,
    ):
        self.id_contenido = id_contenido
        self.id_curso = id_curso
        self.titulo = titulo
        self.tipo_contenido = tipo_contenido
        self.ruta_archivo = ruta_archivo
        self.contenido_texto = contenido_texto
        self.orden = orden

    def __repr__(self):
        return f"Contenido(id_contenido={self.id_contenido}, titulo='{self.titulo}', orden={self.orden})"
