"""Carga la foto de perfil de un usuario como CTkImage cuadrada (recorte centrado + resize).
Devuelve None si el usuario no tiene foto o el archivo ya no existe, para que quien la use
pueda caer de vuelta a un avatar con iniciales."""
import os

import customtkinter as ctk
from PIL import Image, ImageDraw

from config.settings import BASE_DIR


def cargar_imagen_perfil(ruta_relativa: str, lado: int) -> ctk.CTkImage | None:
    """Recorta al centro, redimensiona a un cuadrado y recorta en círculo (alpha), para que
    se vea como un avatar redondo sobre el fondo circular donde siempre se muestra."""
    if not ruta_relativa:
        return None
    ruta_absoluta = os.path.join(BASE_DIR, ruta_relativa)
    if not os.path.isfile(ruta_absoluta):
        return None

    imagen = Image.open(ruta_absoluta).convert("RGB")
    lado_recorte = min(imagen.size)
    izquierda = (imagen.width - lado_recorte) // 2
    arriba = (imagen.height - lado_recorte) // 2
    imagen = imagen.crop((izquierda, arriba, izquierda + lado_recorte, arriba + lado_recorte))
    imagen = imagen.resize((lado, lado), Image.LANCZOS).convert("RGBA")

    mascara_circular = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara_circular).ellipse((0, 0, lado, lado), fill=255)
    imagen.putalpha(mascara_circular)

    return ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(lado, lado))
