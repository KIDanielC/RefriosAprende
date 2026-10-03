from utils.restablecer_admin import _listar_administradores


def test_listar_administradores_solo_incluye_rol_administrador(admin, aprendiz):
    administradores = _listar_administradores()
    ids = [a.id_usuario for a in administradores]
    assert admin.id_usuario in ids
    assert aprendiz.id_usuario not in ids


def test_listar_administradores_vacio_sin_admins(aprendiz):
    """Si por algún motivo la base de datos no tiene ningún administrador, la lista
    debe quedar vacía (no debe fallar ni incluir aprendices)."""
    administradores = _listar_administradores()
    assert administradores == []
