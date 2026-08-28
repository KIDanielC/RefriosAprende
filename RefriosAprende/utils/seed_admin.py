"""Script único de inicialización: crea el usuario administrador por defecto si no existe."""
from controller.usuario_controller import DatosInvalidosError, UsuarioController
from model.dao.rol_dao import RolDAO
from model.dao.usuario_dao import UsuarioDAO


def crear_admin_por_defecto():
    usuario_dao = UsuarioDAO()
    if usuario_dao.obtener_por_usuario("admin") is not None:
        print("El usuario 'admin' ya existe. No se realizaron cambios.")
        return

    rol_admin = RolDAO().obtener_por_nombre("ADMINISTRADOR")
    controlador = UsuarioController()
    try:
        controlador.crear_usuario(
            nombre_completo="Administrador Refrios",
            documento="0000000000",
            correo="admin@refrios.local",
            usuario="admin",
            contrasena="admin123",
            id_rol=rol_admin.id_rol,
        )
        print("Usuario administrador creado -> usuario: admin | contraseña: admin123")
    except DatosInvalidosError as error:
        print(f"No se pudo crear el administrador: {error}")


if __name__ == "__main__":
    crear_admin_por_defecto()
