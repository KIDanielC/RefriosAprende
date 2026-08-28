"""Controlador de autenticación: valida credenciales y gestiona la sesión activa."""
from model.dao.usuario_dao import UsuarioDAO
from model.entities.usuario import Usuario
from utils.seguridad import verificar_contrasena


class CredencialesInvalidasError(Exception):
    """Usuario o contraseña incorrectos."""


class UsuarioInactivoError(Exception):
    """El usuario existe pero está deshabilitado."""


class AutenticacionController:
    """Contiene las reglas de negocio del inicio de sesión."""

    def __init__(self):
        self._usuario_dao = UsuarioDAO()
        self._usuario_actual: Usuario | None = None

    def iniciar_sesion(self, usuario: str, contrasena: str) -> Usuario:
        usuario = (usuario or "").strip()
        contrasena = contrasena or ""

        if not usuario or not contrasena:
            raise CredencialesInvalidasError("Debe ingresar usuario y contraseña.")

        entidad_usuario = self._usuario_dao.obtener_por_usuario(usuario)
        if entidad_usuario is None:
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")

        if not verificar_contrasena(contrasena, entidad_usuario.contrasena_hash):
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")

        if not entidad_usuario.activo:
            raise UsuarioInactivoError("Este usuario se encuentra inactivo. Contacte al administrador.")

        self._usuario_actual = entidad_usuario
        return entidad_usuario

    def cerrar_sesion(self) -> None:
        self._usuario_actual = None

    def obtener_usuario_actual(self) -> Usuario | None:
        return self._usuario_actual
