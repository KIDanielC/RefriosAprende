"""El comité reportó que una contraseña de 73 caracteres ASCII (o de 37 letras 'á', que en
UTF-8 pesan 2 bytes cada una) hace que bcrypt lance ValueError por superar los 72 bytes que
admite, y que ese error llegaba sin aviso comprensible hasta el inicio de sesión."""
import pytest

from controller.autenticacion_controller import AutenticacionController, CredencialesInvalidasError
from controller.usuario_controller import DatosInvalidosError, UsuarioController
from utils.seguridad import ContrasenaInvalidaError, validar_contrasena, verificar_contrasena

_72_ASCII = "a" * 72
_73_ASCII = "a" * 73
_36_TILDES = "á" * 36  # 36 * 2 bytes = 72 bytes exactos
_37_TILDES = "á" * 37  # 37 * 2 bytes = 74 bytes: ya se pasa


def test_validar_contrasena_acepta_72_bytes_ascii():
    validar_contrasena(_72_ASCII)  # no lanza


def test_validar_contrasena_rechaza_73_bytes_ascii():
    with pytest.raises(ContrasenaInvalidaError):
        validar_contrasena(_73_ASCII)


def test_validar_contrasena_acepta_36_tildes_72_bytes():
    validar_contrasena(_36_TILDES)  # no lanza


def test_validar_contrasena_rechaza_37_tildes_74_bytes():
    with pytest.raises(ContrasenaInvalidaError):
        validar_contrasena(_37_TILDES)


def test_crear_usuario_rechaza_contrasena_de_73_caracteres(id_rol_aprendiz):
    with pytest.raises(DatosInvalidosError):
        UsuarioController().crear_usuario(
            "Usuario de Prueba", "1000000099", "prueba.73@refrios.local", "prueba.73",
            _73_ASCII, id_rol_aprendiz,
        )


def test_cambiar_contrasena_rechaza_73_caracteres(aprendiz):
    with pytest.raises(DatosInvalidosError):
        UsuarioController().cambiar_contrasena(aprendiz.id_usuario, _73_ASCII)


def test_cambiar_contrasena_rechaza_37_tildes(aprendiz):
    with pytest.raises(DatosInvalidosError):
        UsuarioController().cambiar_contrasena(aprendiz.id_usuario, _37_TILDES)


def test_login_con_73_caracteres_devuelve_error_generico_sin_excepcion(aprendiz):
    """Antes de la corrección, esto llegaba a bcrypt.checkpw y lanzaba ValueError."""
    controlador = AutenticacionController()
    with pytest.raises(CredencialesInvalidasError):
        controlador.iniciar_sesion(aprendiz.usuario, _73_ASCII)


def test_la_contrasena_guardada_no_se_recorta(aprendiz):
    """crear_usuario (via la fixture 'aprendiz') guardó la clave real 'clave123': iniciar
    sesión con esa misma clave debe seguir funcionando tal cual, sin truncamientos."""
    controlador = AutenticacionController()
    usuario_autenticado = controlador.iniciar_sesion(aprendiz.usuario, "clave123")
    assert usuario_autenticado.id_usuario == aprendiz.id_usuario


def test_verificar_contrasena_con_entrada_larga_no_lanza_y_devuelve_falso():
    hash_valido = "$2b$12$" + "a" * 53  # con forma de hash bcrypt, no hace falta que sea real
    assert verificar_contrasena(_73_ASCII, hash_valido) is False
