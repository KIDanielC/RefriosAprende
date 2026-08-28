"""Entidad Usuario."""


class Usuario:
    def __init__(
        self,
        id_usuario: int,
        nombre_completo: str,
        documento: str,
        correo: str,
        usuario: str,
        contrasena_hash: str,
        id_rol: int,
        activo: bool,
        fecha_creacion: str,
        nombre_rol: str = None,
    ):
        self.id_usuario = id_usuario
        self.nombre_completo = nombre_completo
        self.documento = documento
        self.correo = correo
        self.usuario = usuario
        self.contrasena_hash = contrasena_hash
        self.id_rol = id_rol
        self.activo = bool(activo)
        self.fecha_creacion = fecha_creacion
        self.nombre_rol = nombre_rol

    def es_administrador(self) -> bool:
        return self.nombre_rol == "ADMINISTRADOR"

    def __repr__(self):
        return f"Usuario(id_usuario={self.id_usuario}, usuario='{self.usuario}', rol='{self.nombre_rol}')"
