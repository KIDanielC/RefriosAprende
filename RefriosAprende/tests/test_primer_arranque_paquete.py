"""El comité pidió cerrar el primer arranque con una prueba que muestre que existe un
administrador activo, que puede ingresar y que puede cambiar su contraseña inicial. Con la
opción adoptada (ventana de primer administrador, sin semilla de fábrica), no hay una
contraseña inicial que entregar: el administrador define la suya propia al crearla."""
from controller.autenticacion_controller import AutenticacionController
from controller.usuario_controller import DatosInvalidosError, UsuarioController
from model.dao.rol_dao import RolDAO
from model.dao.usuario_dao import UsuarioDAO


def test_sin_usuarios_no_existe_administrador_activo():
    """Es el estado de una base recién creada a partir de schema.sql: ningún usuario
    todavía. main.py debe mostrar la ventana de primer administrador, no el login."""
    assert UsuarioController().existe_administrador_activo() is False


def test_con_administrador_creado_existe_administrador_activo(admin):
    assert UsuarioController().existe_administrador_activo() is True


def test_administrador_unico_inactivo_no_cuenta_como_activo(admin):
    """Caso límite: si el único administrador quedó inactivo (manipulación directa de la
    base, fuera de la app: el propio controlador no deja desactivar al último admin activo),
    la app debe seguir pidiendo crear uno nuevo, no un login que nadie podría usar."""
    rol_admin = RolDAO().obtener_por_nombre("ADMINISTRADOR")
    UsuarioDAO().actualizar(
        admin.id_usuario, admin.nombre_completo, admin.documento, admin.correo, rol_admin.id_rol, False
    )
    assert UsuarioController().existe_administrador_activo() is False


def test_primer_administrador_se_crea_ingresa_y_cambia_su_contrasena():
    """Reproduce el procedimiento completo que pidió el comité: crear la primera cuenta,
    iniciar sesión con ella, cambiar la contraseña inicial y volver a entrar con la nueva."""
    controlador_usuarios = UsuarioController()
    assert controlador_usuarios.existe_administrador_activo() is False

    rol_admin = RolDAO().obtener_por_nombre("ADMINISTRADOR")
    administrador = controlador_usuarios.crear_usuario(
        "Instructor Jefe", "1000000500", "jefe@refrios.local", "jefe.refrios", "ClaveInicial1", rol_admin.id_rol,
    )
    assert controlador_usuarios.existe_administrador_activo() is True

    controlador_sesion = AutenticacionController()
    autenticado = controlador_sesion.iniciar_sesion("jefe.refrios", "ClaveInicial1")
    assert autenticado.id_usuario == administrador.id_usuario

    controlador_usuarios.cambiar_contrasena(administrador.id_usuario, "ClaveNueva2", usuario_actor=administrador)

    controlador_sesion_nueva = AutenticacionController()
    autenticado_de_nuevo = controlador_sesion_nueva.iniciar_sesion("jefe.refrios", "ClaveNueva2")
    assert autenticado_de_nuevo.id_usuario == administrador.id_usuario


def test_primer_administrador_rechaza_contrasena_demasiado_corta():
    rol_admin = RolDAO().obtener_por_nombre("ADMINISTRADOR")
    try:
        UsuarioController().crear_usuario(
            "Instructor Jefe", "1000000501", "jefe2@refrios.local", "jefe.refrios2", "abc", rol_admin.id_rol,
        )
        assert False, "se esperaba DatosInvalidosError"
    except DatosInvalidosError:
        pass
