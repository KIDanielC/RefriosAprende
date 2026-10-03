"""Recuperación de emergencia: restablece la contraseña de un administrador directamente en
la base de datos, para cuando TODOS los administradores olvidaron la suya y nadie puede
entrar a la aplicación para usar "Restablecer contraseña" desde Gestión de Usuarios.

Esto NO es un botón dentro de la app ni una clave maestra oculta en el código: a propósito,
el único camino de recuperación exige el mismo nivel de acceso que ya protege la base de
datos en disco (acceso físico/de archivos al computador donde está instalada la aplicación,
y tener Python disponible ahí, o copiar database/refrios.db a un equipo que sí lo tenga).

Uso (desde la raíz de RefriosAprende, con el entorno virtual activado):
    py -m utils.restablecer_admin
"""
import getpass
import sys

from controller.usuario_controller import DatosInvalidosError, UsuarioController
from model.dao.usuario_dao import UsuarioDAO


def _listar_administradores():
    return [usuario for usuario in UsuarioDAO().listar_todos() if usuario.es_administrador()]


def restablecer_admin() -> None:
    administradores = _listar_administradores()
    if not administradores:
        print("No hay ningún usuario con rol Administrador en esta base de datos.")
        return

    print("Administradores registrados:")
    for indice, admin in enumerate(administradores, start=1):
        estado = "activo" if admin.activo else "INACTIVO"
        print(f"  {indice}. {admin.nombre_completo} (usuario: {admin.usuario}) — {estado}")

    if len(administradores) == 1:
        elegido = administradores[0]
    else:
        seleccion = input(f"\nElige un número (1-{len(administradores)}): ").strip()
        if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(administradores)):
            print("Selección inválida. Cancelado.")
            return
        elegido = administradores[int(seleccion) - 1]

    print(f"\nVas a restablecer la contraseña de: {elegido.nombre_completo} ({elegido.usuario})")
    confirmacion = input("¿Confirmas? Escribe 'si' para continuar: ").strip().lower()
    if confirmacion not in ("si", "sí"):
        print("Cancelado.")
        return

    nueva_contrasena = getpass.getpass("Nueva contraseña (mínimo 6 caracteres): ")
    repetir = getpass.getpass("Repite la nueva contraseña: ")
    if nueva_contrasena != repetir:
        print("Las contraseñas no coinciden. Cancelado.")
        return

    try:
        UsuarioController().cambiar_contrasena(elegido.id_usuario, nueva_contrasena)
    except DatosInvalidosError as error:
        print(f"No se pudo cambiar la contraseña: {error}")
        return

    print(f"\nListo. La contraseña de '{elegido.usuario}' fue restablecida correctamente.")


if __name__ == "__main__":
    try:
        restablecer_admin()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelado.")
        sys.exit(1)
