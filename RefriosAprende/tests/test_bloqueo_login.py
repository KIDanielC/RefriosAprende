"""El comité señaló que el inicio de sesión no tenía límite de intentos. Se agrega un
bloqueo temporal tras varios intentos fallidos seguidos."""
from datetime import datetime, timedelta

import pytest

from controller.autenticacion_controller import AutenticacionController, CredencialesInvalidasError
from model.dao.usuario_dao import UsuarioDAO


def test_cuatro_intentos_fallidos_no_bloquean(aprendiz):
    controlador = AutenticacionController()
    for _ in range(4):
        with pytest.raises(CredencialesInvalidasError) as error:
            controlador.iniciar_sesion(aprendiz.usuario, "clave_incorrecta")
        assert "Demasiados intentos" not in str(error.value)

    # El quinto intento, con la clave correcta, debe funcionar: todavía no se bloqueó.
    autenticado = controlador.iniciar_sesion(aprendiz.usuario, "clave123")
    assert autenticado.id_usuario == aprendiz.id_usuario


def test_quinto_intento_fallido_bloquea_la_cuenta(aprendiz):
    controlador = AutenticacionController()
    for _ in range(5):
        with pytest.raises(CredencialesInvalidasError):
            controlador.iniciar_sesion(aprendiz.usuario, "clave_incorrecta")

    # Ni siquiera con la contraseña correcta deja entrar mientras está bloqueada.
    with pytest.raises(CredencialesInvalidasError) as error:
        controlador.iniciar_sesion(aprendiz.usuario, "clave123")
    assert "Demasiados intentos" in str(error.value)


def test_login_correcto_reinicia_el_contador(aprendiz):
    controlador = AutenticacionController()
    for _ in range(3):
        with pytest.raises(CredencialesInvalidasError):
            controlador.iniciar_sesion(aprendiz.usuario, "clave_incorrecta")

    controlador.iniciar_sesion(aprendiz.usuario, "clave123")  # resetea el contador

    # Hacen falta 5 fallos NUEVOS para bloquear, no solo 2 más (3 + 2 = 5 del intento anterior).
    for _ in range(4):
        with pytest.raises(CredencialesInvalidasError) as error:
            controlador.iniciar_sesion(aprendiz.usuario, "clave_incorrecta")
        assert "Demasiados intentos" not in str(error.value)

    autenticado = controlador.iniciar_sesion(aprendiz.usuario, "clave123")
    assert autenticado.id_usuario == aprendiz.id_usuario


def test_el_bloqueo_se_libera_despues_del_tiempo(aprendiz):
    controlador = AutenticacionController()
    for _ in range(5):
        with pytest.raises(CredencialesInvalidasError):
            controlador.iniciar_sesion(aprendiz.usuario, "clave_incorrecta")

    # Simula que ya pasó el tiempo de bloqueo (sin esperar de verdad los 5 minutos).
    bloqueado_hasta_en_el_pasado = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    UsuarioDAO().registrar_intento_fallido(aprendiz.id_usuario, 0, bloqueado_hasta_en_el_pasado)

    autenticado = controlador.iniciar_sesion(aprendiz.usuario, "clave123")
    assert autenticado.id_usuario == aprendiz.id_usuario
