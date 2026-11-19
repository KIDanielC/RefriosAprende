"""Utilidades de seguridad: hash y verificación de contraseñas con bcrypt."""
import bcrypt

LONGITUD_MINIMA_CONTRASENA = 6
# bcrypt ignora en silencio (o directamente rechaza, según la versión) todo lo que pase de
# 72 bytes: hay que frenar la contraseña ANTES de llegar ahí, nunca dejar que se recorte sola.
LONGITUD_MAXIMA_CONTRASENA_BYTES = 72


class ContrasenaInvalidaError(Exception):
    """La contraseña no cumple los límites de longitud admitidos."""


def validar_contrasena(contrasena: str) -> None:
    """Único lugar donde se decide qué es una contraseña válida: se usa al crear un
    usuario, al cambiar o restablecer una contraseña, y en el primer administrador."""
    if not contrasena or len(contrasena) < LONGITUD_MINIMA_CONTRASENA:
        raise ContrasenaInvalidaError(
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_CONTRASENA} caracteres."
        )
    if len(contrasena.encode("utf-8")) > LONGITUD_MAXIMA_CONTRASENA_BYTES:
        raise ContrasenaInvalidaError(
            "La contraseña no puede superar los 72 bytes (unos 72 caracteres; menos si usa tildes o ñ)."
        )


def generar_hash(contrasena_plana: str) -> str:
    return bcrypt.hashpw(contrasena_plana.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    # Una entrada que ya supera el límite de bcrypt nunca puede ser la contraseña real
    # (que sí pasó por validar_contrasena al crearse), así que se descarta sin tocar bcrypt:
    # ni hace falta la llamada, ni se arriesga el ValueError que antes tumbaba el login.
    if len(contrasena_plana.encode("utf-8")) > LONGITUD_MAXIMA_CONTRASENA_BYTES:
        return False
    return bcrypt.checkpw(contrasena_plana.encode("utf-8"), contrasena_hash.encode("utf-8"))
