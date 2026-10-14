"""Configuración global de la aplicación: rutas y paleta institucional."""
import os
import shutil
import sys


def _en_modo_congelado() -> bool:
    """True cuando el código corre empaquetado con PyInstaller (no en desarrollo)."""
    return bool(getattr(sys, "frozen", False))


if _en_modo_congelado():
    # Carpeta de solo lectura: donde PyInstaller deja los recursos que se empaquetaron
    # junto al ejecutable (schema.sql, imágenes, base de datos precargada de fábrica).
    _DIR_RECURSOS_EMPAQUETADOS = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    # Carpeta persistente y escribible para la BD real y los archivos que suban los
    # instructores. El instalador suele dejar el .exe en "Program Files", donde un
    # usuario sin permisos de administrador no puede escribir.
    BASE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "RefriosAprende")
else:
    _DIR_RECURSOS_EMPAQUETADOS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = _DIR_RECURSOS_EMPAQUETADOS


def _preparar_datos_usuario() -> None:
    """Sincroniza BASE_DIR (escribible, fuera de Program Files) con lo que trae esta versión
    empaquetada. Dos tipos de contenido, con reglas distintas:

    - Recursos propios de la aplicación (iconos, imágenes de marca, schema.sql): se
      reemplazan en CADA arranque. Nunca los edita el usuario, así que una reinstalación
      con una versión nueva (ej. un rediseño de paleta o del login) se ve reflejada de
      inmediato, sin que quede una copia vieja atascada en %LOCALAPPDATA%.
    - Datos reales del usuario (la base de datos, los contenidos subidos, las fotos de
      perfil, las entregas de talleres): solo se copian la primera vez. Una vez existen,
      nunca se pisan, para no perder información real de la empresa."""
    if not _en_modo_congelado():
        return

    os.makedirs(BASE_DIR, exist_ok=True)

    for ruta_relativa in (os.path.join("resources", "icons"), os.path.join("resources", "images")):
        origen = os.path.join(_DIR_RECURSOS_EMPAQUETADOS, ruta_relativa)
        destino = os.path.join(BASE_DIR, ruta_relativa)
        if os.path.isdir(origen):
            shutil.rmtree(destino, ignore_errors=True)
            shutil.copytree(origen, destino)

    origen_schema = os.path.join(_DIR_RECURSOS_EMPAQUETADOS, "database", "schema.sql")
    destino_schema = os.path.join(BASE_DIR, "database", "schema.sql")
    if os.path.isfile(origen_schema):
        os.makedirs(os.path.dirname(destino_schema), exist_ok=True)
        shutil.copyfile(origen_schema, destino_schema)

    origen_bd = os.path.join(_DIR_RECURSOS_EMPAQUETADOS, "database", "refrios.db")
    destino_bd = os.path.join(BASE_DIR, "database", "refrios.db")
    if os.path.isfile(origen_bd) and not os.path.isfile(destino_bd):
        shutil.copyfile(origen_bd, destino_bd)

    for carpeta in ("contenidos", "fotos_perfil", "entregas"):
        origen = os.path.join(_DIR_RECURSOS_EMPAQUETADOS, "resources", carpeta)
        destino = os.path.join(BASE_DIR, "resources", carpeta)
        if os.path.isdir(origen) and not os.path.isdir(destino):
            shutil.copytree(origen, destino)


_preparar_datos_usuario()

DATABASE_PATH = os.path.join(BASE_DIR, "database", "refrios.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
IMAGES_DIR = os.path.join(BASE_DIR, "resources", "images")
CONTENIDOS_DIR = os.path.join(BASE_DIR, "resources", "contenidos")
FOTOS_PERFIL_DIR = os.path.join(BASE_DIR, "resources", "fotos_perfil")
ENTREGAS_DIR = os.path.join(BASE_DIR, "resources", "entregas")

APP_NAME = "Refrios Aprende"
APP_VERSION = "1.0.0"

# Paleta "Manómetro": inspirada en los manómetros de diagnóstico de A/C (azul de baja
# presión + rojo/cobre de alta presión) sobre un fondo cálido tipo papel técnico, en vez
# del panel oscuro "HUD" anterior. Pensada para un software educativo: cálida, legible,
# con esquinas redondeadas y acentos que remiten directamente al oficio (refrigeración
# automotriz), no a un dashboard de videojuego.
COLOR_FONDO_APP = "#F3EFE4"           # papel técnico cálido, nunca blanco puro
COLOR_FONDO_PANEL = "#EAE2CD"         # franjas/paneles (encabezados, fondos de tabla)
COLOR_FONDO_TARJETA = "#FFFFFF"       # tarjetas: blanco limpio, contraste con el fondo cálido
COLOR_FONDO_TARJETA_HOVER = "#F6F0E2"
COLOR_BORDE_SUTIL = "#DCD0AE"         # línea de cuaderno técnico

COLOR_ACENTO_PRIMARIO = "#1C5FA8"     # azul de manómetro (lado de baja presión): acción principal
COLOR_ACENTO_SECUNDARIO = "#3D7FC4"   # azul claro: hover, énfasis suave
COLOR_ACENTO_GLOW = "#7FB3E8"
COLOR_ACENTO_ALTERNO = "#C1442B"      # rojo/cobre de manómetro (lado de alta presión): insignias, simulación
COLOR_ACENTO_ALTERNO_GLOW = "#DE6A4E"

COLOR_BLANCO = "#FFFFFF"
COLOR_TEXTO_PRIMARIO = "#241F18"      # tinta grafito cálida, no negro puro
COLOR_TEXTO_SECUNDARIO = "#6E6554"    # taupe cálido

COLOR_ERROR = "#A3271E"
COLOR_EXITO = "#2E7D4F"

# Radios de esquina: tarjetas y botones redondeados, cercanos y educativos.
RADIO_TARJETA = 14
RADIO_BOTON = 10
GROSOR_BORDE_SUTIL = 1

# Navegación (sidebar del Dashboard): azul pizarra oscuro -tipo cubierta de manual técnico-,
# deliberadamente distinto del contenido cálido y claro: layout híbrido, no monocromático.
COLOR_NAV_FONDO = "#1C2B3A"
COLOR_NAV_FONDO_HOVER = "#263B4E"
COLOR_NAV_BORDE = "#34495E"
COLOR_NAV_TEXTO = "#F3EFE4"
COLOR_NAV_TEXTO_SECUNDARIO = "#9FB3C8"

FONT_FAMILY = "Century Gothic"
FONT_FAMILY_MONO = "Consolas"

VENTANA_ANCHO = 1200
VENTANA_ALTO = 720
