"""Controlador de autenticación: valida credenciales y gestiona la sesión activa."""
from datetime import datetime, timedelta

from model.dao.usuario_dao import UsuarioDAO
from model.entities.usuario import Usuario
from utils.seguridad import verificar_contrasena

_MAX_INTENTOS_FALLIDOS = 5
_MINUTOS_BLOQUEO = 5
_FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


class CredencialesInvalidasError(Exception):
    """Usuario o contraseña incorrectos (o la cuenta está bloqueada temporalmente)."""


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

        self._verificar_que_no_este_bloqueado(entidad_usuario)

        if not verificar_contrasena(contrasena, entidad_usuario.contrasena_hash):
            self._registrar_intento_fallido(entidad_usuario)
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")

        # La contraseña era correcta: ya no se le puede seguir contando como fuerza bruta,
        # sin importar si la cuenta resulta estar inactiva.
        self._usuario_dao.resetear_intentos_fallidos(entidad_usuario.id_usuario)

        if not entidad_usuario.activo:
            raise UsuarioInactivoError("Este usuario se encuentra inactivo. Contacte al administrador.")

        self._usuario_actual = entidad_usuario
        return entidad_usuario

    def _verificar_que_no_este_bloqueado(self, entidad_usuario: Usuario) -> None:
        if not entidad_usuario.bloqueado_hasta:
            return
        bloqueado_hasta = datetime.strptime(entidad_usuario.bloqueado_hasta, _FORMATO_FECHA)
        if datetime.now() >= bloqueado_hasta:
            return
        minutos_restantes = max(1, int((bloqueado_hasta - datetime.now()).total_seconds() // 60) + 1)
        raise CredencialesInvalidasError(
            f"Demasiados intentos fallidos. Intenta de nuevo en {minutos_restantes} minuto(s)."
        )

    def _registrar_intento_fallido(self, entidad_usuario: Usuario) -> None:
        """Tras _MAX_INTENTOS_FALLIDOS seguidos, bloquea la cuenta por _MINUTOS_BLOQUEO y
        reinicia el contador: el intento siguiente al vencimiento del bloqueo empieza de cero."""
        intentos = entidad_usuario.intentos_fallidos + 1
        bloqueado_hasta = None
        if intentos >= _MAX_INTENTOS_FALLIDOS:
            bloqueado_hasta = (datetime.now() + timedelta(minutes=_MINUTOS_BLOQUEO)).strftime(_FORMATO_FECHA)
            intentos = 0
        self._usuario_dao.registrar_intento_fallido(entidad_usuario.id_usuario, intentos, bloqueado_hasta)

    def cerrar_sesion(self) -> None:
        self._usuario_actual = None

    def obtener_usuario_actual(self) -> Usuario | None:
        return self._usuario_actual
