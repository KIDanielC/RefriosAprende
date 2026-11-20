from controller.usuario_controller import UsuarioController
from utils.restablecer_admin import _listar_administradores


def test_listar_administradores_solo_incluye_rol_administrador(admin, aprendiz):
    administradores = _listar_administradores()
    ids = [a.id_usuario for a in administradores]
    assert admin.id_usuario in ids
    assert aprendiz.id_usuario not in ids


def test_listar_administradores_vacio_sin_admins(id_rol_aprendiz):
    """Si por algún motivo la base de datos no tiene ningún administrador, la lista
    debe quedar vacía (no debe fallar ni incluir aprendices). Se crea el aprendiz
    directamente (sin la fixture `aprendiz`, que ya depende de que exista un admin)
    para dejar la base con un único usuario que no es administrador."""
    UsuarioController().crear_usuario(
        "Aprendiz Sin Admin", "1000000777", "sinadmin@refrios.local", "sinadmin", "clave123", id_rol_aprendiz,
    )
    administradores = _listar_administradores()
    assert administradores == []
