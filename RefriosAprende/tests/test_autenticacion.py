import pytest

from controller.autenticacion_controller import (
    AutenticacionController,
    CredencialesInvalidasError,
    UsuarioInactivoError,
)
from controller.usuario_controller import UsuarioController


def test_inicio_sesion_exitoso(admin):
    resultado = AutenticacionController().iniciar_sesion("admin.prueba", "clave123")
    assert resultado.id_usuario == admin.id_usuario
    assert resultado.es_administrador()


def test_inicio_sesion_contrasena_incorrecta(admin):
    with pytest.raises(CredencialesInvalidasError):
        AutenticacionController().iniciar_sesion("admin.prueba", "clave_equivocada")


def test_inicio_sesion_usuario_inexistente():
    with pytest.raises(CredencialesInvalidasError):
        AutenticacionController().iniciar_sesion("no_existe", "cualquiera")


def test_inicio_sesion_campos_vacios():
    with pytest.raises(CredencialesInvalidasError):
        AutenticacionController().iniciar_sesion("", "")


def test_inicio_sesion_usuario_inactivo(admin, id_rol_aprendiz):
    uc = UsuarioController()
    inactivo = uc.crear_usuario(
        "Usuario Inactivo", "1000000099", "inactivo@refrios.local", "inactivo", "clave123", id_rol_aprendiz
    )
    uc.actualizar_usuario(
        inactivo.id_usuario, inactivo.nombre_completo, inactivo.documento, inactivo.correo,
        inactivo.id_rol, activo=False,
    )
    with pytest.raises(UsuarioInactivoError):
        AutenticacionController().iniciar_sesion("inactivo", "clave123")
