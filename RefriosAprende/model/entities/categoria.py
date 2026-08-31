"""Entidad Categoría (agrupación temática de cursos)."""


class Categoria:
    def __init__(self, id_categoria: int, nombre_categoria: str):
        self.id_categoria = id_categoria
        self.nombre_categoria = nombre_categoria

    def __repr__(self):
        return f"Categoria(id_categoria={self.id_categoria}, nombre_categoria='{self.nombre_categoria}')"
