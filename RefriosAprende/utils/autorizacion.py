"""Verificación de rol para las operaciones más sensibles del sistema. La vista ya oculta
estos botones a quien no es administrador, pero eso no evita que un error de la propia
vista, un script o una prueba llame al controlador directamente sin serlo. Esta app corre
en un solo proceso de escritorio (no hay un cliente separado del servidor), así que esto
es una red de seguridad adicional, no la única barrera."""
from model.entities.usuario import Usuario


class AccesoNoAutorizadoError(Exception):
    """Quien ejecuta la operación no tiene el rol requerido para hacerlo."""


def exigir_administrador(usuario_actor: Usuario | None) -> None:
    if usuario_actor is None or not usuario_actor.es_administrador():
        raise AccesoNoAutorizadoError("Esta operación requiere una cuenta de administrador.")
