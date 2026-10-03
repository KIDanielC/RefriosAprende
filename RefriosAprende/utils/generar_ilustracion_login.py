"""Script de un solo uso: genera la ilustración de marca del panel de Login (un manómetro
doble de diagnóstico —baja presión en azul, alta presión en rojo/cobre—, dibujado por
código con la paleta "Manómetro" de la app). No es una foto de stock ni una imagen de IA:
evita cualquier duda de licencia y no depende de internet.

Ejecutar manualmente cada vez que se quiera regenerar la ilustración:
    py -m utils.generar_ilustracion_login
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

from config.settings import IMAGES_DIR

_ANCHO, _ALTO = 1800, 1100
_RUTA_DESTINO = os.path.join(IMAGES_DIR, "ilustracion_login.jpg")
_DIR_FUENTES = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def _cargar_fuente(nombre_archivo: str, tamano: int):
    try:
        return ImageFont.truetype(os.path.join(_DIR_FUENTES, nombre_archivo), tamano)
    except OSError:
        return ImageFont.load_default()


def _degradado_vertical(draw, ancho, alto, color_arriba, color_abajo):
    for y in range(alto):
        t = y / alto
        color = tuple(round(color_arriba[i] + (color_abajo[i] - color_arriba[i]) * t) for i in range(3))
        draw.line([(0, y), (ancho, y)], fill=color)


def _dibujar_gauge(draw, fuente_etiqueta, cx, cy, r, color_anillo, valor, etiqueta):
    """Dibuja un manómetro circular plano: anillo de color, cara color hueso, marcas,
    aguja y etiqueta. `valor` en [0, 1] controla el ángulo de la aguja."""
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color_anillo)

    r_cara = r - 26
    draw.ellipse(
        (cx - r_cara, cy - r_cara, cx + r_cara, cy + r_cara),
        fill=(243, 239, 228), outline=(36, 31, 24), width=3,
    )

    angulo_inicio, angulo_fin = 135, 405  # barrido de 270° en sentido horario
    for i in range(11):
        t = i / 10
        angulo = math.radians(angulo_inicio + t * (angulo_fin - angulo_inicio))
        es_mayor = i % 5 == 0
        r1 = r_cara - 14
        r2 = r_cara - (30 if es_mayor else 20)
        x1, y1 = cx + r1 * math.cos(angulo), cy + r1 * math.sin(angulo)
        x2, y2 = cx + r2 * math.cos(angulo), cy + r2 * math.sin(angulo)
        draw.line([(x1, y1), (x2, y2)], fill=(36, 31, 24), width=5 if es_mayor else 2)

    angulo_aguja = math.radians(angulo_inicio + valor * (angulo_fin - angulo_inicio))
    largo_aguja = r_cara - 46
    punta = (cx + largo_aguja * math.cos(angulo_aguja), cy + largo_aguja * math.sin(angulo_aguja))
    draw.line([(cx, cy), punta], fill=color_anillo, width=9)
    draw.ellipse((cx - 17, cy - 17, cx + 17, cy + 17), fill=(36, 31, 24))
    draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(243, 239, 228))

    caja_texto = draw.textbbox((0, 0), etiqueta, font=fuente_etiqueta)
    ancho_texto = caja_texto[2] - caja_texto[0]
    draw.text(
        (cx - ancho_texto / 2, cy + r_cara * 0.42), etiqueta, font=fuente_etiqueta, fill=(36, 31, 24),
    )


def generar_ilustracion_login() -> None:
    imagen = Image.new("RGB", (_ANCHO, _ALTO), "#1C2B3A")
    draw = ImageDraw.Draw(imagen)

    _degradado_vertical(draw, _ANCHO, _ALTO, (0x25, 0x39, 0x4B), (0x11, 0x1B, 0x25))

    color_rejilla = (0x2C, 0x40, 0x53)
    for x in range(0, _ANCHO, 90):
        draw.line([(x, 0), (x, _ALTO)], fill=color_rejilla, width=1)
    for y in range(0, _ALTO, 90):
        draw.line([(0, y), (_ANCHO, y)], fill=color_rejilla, width=1)

    # Manguera y bloque manifold central, conectando ambos manómetros.
    draw.line([(790, 560), (1010, 560)], fill=(150, 160, 170), width=14)
    draw.rounded_rectangle((760, 515, 1040, 640), radius=24, fill=(122, 132, 142), outline=(70, 80, 90), width=4)
    for vx in (840, 960):
        draw.ellipse((vx - 22, 553, vx + 22, 597), fill=(96, 106, 116), outline=(52, 60, 68), width=3)
        draw.ellipse((vx - 8, 567, vx + 8, 583), fill=(70, 78, 86))

    fuente_etiqueta = _cargar_fuente("GOTHICB.TTF", 32)
    _dibujar_gauge(draw, fuente_etiqueta, 560, 430, 250, (28, 95, 168), 0.32, "BAJA PRESIÓN")
    _dibujar_gauge(draw, fuente_etiqueta, 1240, 430, 250, (193, 68, 43), 0.68, "ALTA PRESIÓN")

    os.makedirs(IMAGES_DIR, exist_ok=True)
    imagen.save(_RUTA_DESTINO, quality=92)
    print(f"Ilustración generada: {_RUTA_DESTINO} ({imagen.size[0]}x{imagen.size[1]})")


if __name__ == "__main__":
    generar_ilustracion_login()
