import os

import pytest

import controller.usuario_controller as usuario_controller_module
from controller.curso_controller import CursoController
from controller.usuario_controller import UsuarioController, DatosInvalidosError, UltimoAdministradorError


@pytest.fixture
def carpeta_fotos_perfil(tmp_path, monkeypatch):
    """Aísla dónde se guardan las fotos de perfil durante la prueba (nunca en resources/ real)."""
    monkeypatch.setattr(usuario_controller_module, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(usuario_controller_module, "FOTOS_PERFIL_DIR", str(tmp_path / "resources" / "fotos_perfil"))
    return tmp_path


def _crear_png_de_prueba(tmp_path, nombre="foto.png") -> str:
    ruta = tmp_path / nombre
    ruta.write_bytes(b"contenido png de prueba")
    return str(ruta)


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


def test_no_se_puede_desactivar_al_ultimo_administrador(admin):
    uc = UsuarioController()
    with pytest.raises(UltimoAdministradorError):
        uc.actualizar_usuario(
            admin.id_usuario, admin.nombre_completo, admin.documento, admin.correo, admin.id_rol, activo=False
        )


def test_no_se_puede_eliminar_al_ultimo_administrador(admin):
    uc = UsuarioController()
    with pytest.raises(UltimoAdministradorError):
        uc.eliminar_usuario(admin.id_usuario)


def test_se_puede_desactivar_administrador_si_hay_otro_activo(admin, id_rol_admin):
    uc = UsuarioController()
    otro_admin = uc.crear_usuario(
        "Otro Admin", "1000000099", "otro.admin@refrios.local", "otro.admin", "clave123", id_rol_admin
    )
    actualizado = uc.actualizar_usuario(
        admin.id_usuario, admin.nombre_completo, admin.documento, admin.correo, admin.id_rol, activo=False
    )
    assert actualizado.activo is False
    assert otro_admin.activo is True


def test_no_se_puede_eliminar_usuario_instructor_de_un_curso(admin, id_rol_admin):
    uc = UsuarioController()
    cc = CursoController()
    otro_admin = uc.crear_usuario(
        "Instructor de Prueba", "1000000098", "instructor.prueba@refrios.local", "instructor.prueba", "clave123", id_rol_admin
    )
    cc.crear_curso("Curso con instructor", "Descripción del curso de prueba", otro_admin.id_usuario)

    with pytest.raises(DatosInvalidosError):
        uc.eliminar_usuario(otro_admin.id_usuario)


def test_actualizar_foto_perfil_valida(aprendiz, carpeta_fotos_perfil):
    uc = UsuarioController()
    ruta_origen = _crear_png_de_prueba(carpeta_fotos_perfil)

    actualizado = uc.actualizar_foto_perfil(aprendiz.id_usuario, ruta_origen)

    assert actualizado.foto_perfil is not None
    assert actualizado.foto_perfil.endswith(".png")
    assert os.path.isfile(os.path.join(str(carpeta_fotos_perfil), actualizado.foto_perfil))


def test_actualizar_foto_perfil_rechaza_extension_no_png(aprendiz, carpeta_fotos_perfil):
    uc = UsuarioController()
    ruta_origen = _crear_png_de_prueba(carpeta_fotos_perfil, nombre="foto.jpg")

    with pytest.raises(DatosInvalidosError):
        uc.actualizar_foto_perfil(aprendiz.id_usuario, ruta_origen)


def test_actualizar_foto_perfil_rechaza_archivo_inexistente(aprendiz, carpeta_fotos_perfil):
    uc = UsuarioController()
    with pytest.raises(DatosInvalidosError):
        uc.actualizar_foto_perfil(aprendiz.id_usuario, str(carpeta_fotos_perfil / "no_existe.png"))


def test_actualizar_foto_perfil_reemplaza_y_borra_la_anterior(aprendiz, carpeta_fotos_perfil):
    uc = UsuarioController()
    primera = uc.actualizar_foto_perfil(aprendiz.id_usuario, _crear_png_de_prueba(carpeta_fotos_perfil, "primera.png"))
    ruta_primera_absoluta = os.path.join(str(carpeta_fotos_perfil), primera.foto_perfil)
    assert os.path.isfile(ruta_primera_absoluta)

    segunda = uc.actualizar_foto_perfil(aprendiz.id_usuario, _crear_png_de_prueba(carpeta_fotos_perfil, "segunda.png"))

    assert segunda.foto_perfil != primera.foto_perfil
    assert not os.path.isfile(ruta_primera_absoluta)
    assert os.path.isfile(os.path.join(str(carpeta_fotos_perfil), segunda.foto_perfil))
