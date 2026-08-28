"""Utilidades de seguridad: hash y verificación de contraseñas con bcrypt."""
import bcrypt


def generar_hash(contrasena_plana: str) -> str:
    return bcrypt.hashpw(contrasena_plana.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    return bcrypt.checkpw(contrasena_plana.encode("utf-8"), contrasena_hash.encode("utf-8"))
