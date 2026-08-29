import pytest

from controller.usuario_controller import DatosInvalidosError, UsuarioController


def test_crear_usuario_valido(id_rol_aprendiz):
    uc = UsuarioController()
    usuario = uc.crear_usuario(
        "Juan Perez", "1122334455", "juan.perez@refrios.local", "juan.perez", "clave123", id_rol_aprendiz
    )
    assert usuario.id_usuario is not None
    assert usuario.nombre_completo == "Juan Perez"
    assert usuario.activo is True


@pytest.mark.parametrize("nombre,documento,correo,usuario_login", [
    ("ab", "123456", "a@b.com", "usr1"),          # nombre muy corto
    ("Nombre Valido", "abc123", "a@b.com", "usr2"),  # documento con letras
    ("Nombre Valido", "123456", "correo-invalido", "usr3"),  # correo sin formato válido
])
def test_crear_usuario_datos_invalidos(id_rol_aprendiz, nombre, documento, correo, usuario_login):
    uc = UsuarioController()
    with pytest.raises(DatosInvalidosError):
        uc.crear_usuario(nombre, documento, correo, usuario_login, "clave123", id_rol_aprendiz)


def test_crear_usuario_contrasena_corta(id_rol_aprendiz):
    uc = UsuarioController()
    with pytest.raises(DatosInvalidosError):
        uc.crear_usuario("Nombre Valido", "123456789", "ok@refrios.local", "ok.usuario", "123", id_rol_aprendiz)


def test_crear_usuario_duplicado(aprendiz, id_rol_aprendiz):
    uc = UsuarioController()
    with pytest.raises(DatosInvalidosError):
        uc.crear_usuario(
            "Otro Nombre", aprendiz.documento, "otro@refrios.local", "otro.usuario", "clave123", id_rol_aprendiz
        )


def test_actualizar_usuario(aprendiz):
    uc = UsuarioController()
    actualizado = uc.actualizar_usuario(
        aprendiz.id_usuario, "Nombre Actualizado", aprendiz.documento, aprendiz.correo, aprendiz.id_rol, activo=True
    )
    assert actualizado.nombre_completo == "Nombre Actualizado"


def test_cambiar_contrasena_corta_falla(aprendiz):
    uc = UsuarioController()
    with pytest.raises(DatosInvalidosError):
        uc.cambiar_contrasena(aprendiz.id_usuario, "123")


def test_eliminar_usuario(aprendiz):
    uc = UsuarioController()
    uc.eliminar_usuario(aprendiz.id_usuario)
    assert all(u.id_usuario != aprendiz.id_usuario for u in uc.listar_usuarios())
