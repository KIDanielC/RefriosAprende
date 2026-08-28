"""Script de un solo uso: redimensiona el logo original (pesado, 18 MB) a un tamaño
liviano para el panel de Login. No se modifica color, brillo, contraste ni opacidad —
la imagen se muestra tal cual es, solo más pequeña para que la app cargue rápido.

Ejecutar manualmente cada vez que se reemplace resources/images/Logo_Interfaz.png:
    py -m utils.generar_fondo_login
"""
import os

from PIL import Image

from config.settings import IMAGES_DIR

_ARCHIVO_ORIGEN = os.path.join(IMAGES_DIR, "Logo_Interfaz.png")
_ARCHIVO_DESTINO = os.path.join(IMAGES_DIR, "fondo_login.png")
_LADO_MAXIMO = 900


def generar_fondo_login():
    imagen = Image.open(_ARCHIVO_ORIGEN).convert("RGB")

    proporcion = min(_LADO_MAXIMO / imagen.width, _LADO_MAXIMO / imagen.height)
    nuevo_tamano = (round(imagen.width * proporcion), round(imagen.height * proporcion))
    imagen = imagen.resize(nuevo_tamano, Image.LANCZOS)

    imagen.save(_ARCHIVO_DESTINO, optimize=True)
    print(f"Fondo generado (imagen original sin editar): {_ARCHIVO_DESTINO} ({imagen.size[0]}x{imagen.size[1]})")


if __name__ == "__main__":
    generar_fondo_login()
