"""Controlador de gestión de usuarios: valida y coordina Vista <-> Modelo."""
import re

from model.dao.rol_dao import RolDAO
from model.dao.usuario_dao import UsuarioDAO, UsuarioReferenciadoError, UsuarioYaExisteError
from model.entities.usuario import Usuario
from utils.seguridad import generar_hash

_PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NOMBRE_ROL_ADMINISTRADOR = "ADMINISTRADOR"


class DatosInvalidosError(Exception):
    """Los datos ingresados no cumplen las reglas de negocio."""


class UltimoAdministradorError(Exception):
    """No se puede desactivar/eliminar al único administrador activo del sistema."""


class UsuarioController:
    def __init__(self):
        self._usuario_dao = UsuarioDAO()
        self._rol_dao = RolDAO()

    def listar_usuarios(self) -> list[Usuario]:
        return self._usuario_dao.listar_todos()

    def listar_roles(self):
        return self._rol_dao.listar_todos()

    def _validar_datos_basicos(self, nombre_completo, documento, correo):
        if not nombre_completo or len(nombre_completo.strip()) < 3:
            raise DatosInvalidosError("El nombre completo debe tener al menos 3 caracteres.")
        if not documento or not documento.strip().isdigit():
            raise DatosInvalidosError("El documento debe contener solo números.")
        if not correo or not _PATRON_CORREO.match(correo.strip()):
            raise DatosInvalidosError("El correo electrónico no tiene un formato válido.")

    def crear_usuario(
        self,
        nombre_completo: str,
        documento: str,
        correo: str,
        usuario: str,
        contrasena: str,
        id_rol: int,
    ) -> Usuario:
        self._validar_datos_basicos(nombre_completo, documento, correo)

        if not usuario or len(usuario.strip()) < 4:
            raise DatosInvalidosError("El usuario debe tener al menos 4 caracteres.")
        if not contrasena or len(contrasena) < 6:
            raise DatosInvalidosError("La contraseña debe tener al menos 6 caracteres.")
        if self._rol_dao.obtener_por_id(id_rol) is None:
            raise DatosInvalidosError("El rol seleccionado no es válido.")

        try:
            id_usuario = self._usuario_dao.crear(
                nombre_completo.strip(),
                documento.strip(),
                correo.strip().lower(),
                usuario.strip(),
                generar_hash(contrasena),
                id_rol,
            )
        except UsuarioYaExisteError as error:
            raise DatosInvalidosError(str(error)) from error

        return self._usuario_dao.obtener_por_id(id_usuario)

    def actualizar_usuario(
        self,
        id_usuario: int,
        nombre_completo: str,
        documento: str,
        correo: str,
        id_rol: int,
        activo: bool,
    ) -> Usuario:
        self._validar_datos_basicos(nombre_completo, documento, correo)
        if self._rol_dao.obtener_por_id(id_rol) is None:
            raise DatosInvalidosError("El rol seleccionado no es válido.")

        usuario_actual = self._usuario_dao.obtener_por_id(id_usuario)
        deja_de_ser_admin_activo = usuario_actual is not None and usuario_actual.es_administrador() and usuario_actual.activo and (
            not activo or id_rol != usuario_actual.id_rol
        )
        if deja_de_ser_admin_activo and self._es_ultimo_administrador_activo(id_usuario):
            raise UltimoAdministradorError(
                "No se puede desactivar ni cambiar de rol al único administrador activo del sistema."
            )

        try:
            self._usuario_dao.actualizar(
                id_usuario, nombre_completo.strip(), documento.strip(), correo.strip().lower(), id_rol, activo
            )
        except UsuarioYaExisteError as error:
            raise DatosInvalidosError(str(error)) from error

        return self._usuario_dao.obtener_por_id(id_usuario)

    def cambiar_contrasena(self, id_usuario: int, contrasena_nueva: str) -> None:
        if not contrasena_nueva or len(contrasena_nueva) < 6:
            raise DatosInvalidosError("La contraseña debe tener al menos 6 caracteres.")
        self._usuario_dao.actualizar_contrasena(id_usuario, generar_hash(contrasena_nueva))

    def eliminar_usuario(self, id_usuario: int) -> None:
        usuario = self._usuario_dao.obtener_por_id(id_usuario)
        if usuario is not None and usuario.es_administrador() and usuario.activo and self._es_ultimo_administrador_activo(id_usuario):
            raise UltimoAdministradorError(
                "No se puede eliminar al único administrador activo del sistema."
            )
        try:
            self._usuario_dao.eliminar(id_usuario)
        except UsuarioReferenciadoError as error:
            raise DatosInvalidosError(str(error)) from error

    def _es_ultimo_administrador_activo(self, id_usuario_excluido: int) -> bool:
        """True si, al excluir a id_usuario_excluido, no queda ningún administrador activo."""
        rol_admin = self._rol_dao.obtener_por_nombre(_NOMBRE_ROL_ADMINISTRADOR)
        if rol_admin is None:
            return False
        total_admins_activos = self._usuario_dao.contar_activos_por_rol(rol_admin.id_rol)
        return total_admins_activos <= 1
