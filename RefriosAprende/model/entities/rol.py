"""Entidad Rol."""


class Rol:
    def __init__(self, id_rol: int, nombre_rol: str):
        self.id_rol = id_rol
        self.nombre_rol = nombre_rol

    def __repr__(self):
        return f"Rol(id_rol={self.id_rol}, nombre_rol='{self.nombre_rol}')"
