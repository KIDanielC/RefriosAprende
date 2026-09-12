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
    """Primer arranque de la versión empaquetada: copia el esquema, la base de datos
    precargada (si el instalador la incluyó) y los recursos originales desde la carpeta
    de solo lectura del instalador hacia BASE_DIR (escribible). No hace nada si BASE_DIR
    ya existe, para nunca pisar datos reales que el usuario ya haya generado."""
    if not _en_modo_congelado() or os.path.isdir(BASE_DIR):
        return
    os.makedirs(BASE_DIR, exist_ok=True)
    for carpeta in ("database", "resources"):
        origen = os.path.join(_DIR_RECURSOS_EMPAQUETADOS, carpeta)
        destino = os.path.join(BASE_DIR, carpeta)
        if os.path.isdir(origen):
            shutil.copytree(origen, destino, dirs_exist_ok=True)


_preparar_datos_usuario()

DATABASE_PATH = os.path.join(BASE_DIR, "database", "refrios.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
IMAGES_DIR = os.path.join(BASE_DIR, "resources", "images")
CONTENIDOS_DIR = os.path.join(BASE_DIR, "resources", "contenidos")

APP_NAME = "Refrios Aprende"
APP_VERSION = "0.1.0"

# Paleta "Cobre" — cálida e industrial (cobre/latón + pátina verde-azulada), inspirada en
# tubería de cobre y manómetros de diagnóstico de A/C, en vez de los tonos institucionales
# genéricos (azul/amarillo) o el HUD cian/negro de versiones anteriores. Contenido en tono
# crema cálido, sidebar en grafito oscuro cálido: un híbrido claro/oscuro deliberado, no el
# "todo oscuro con un acento" que se repite en la mayoría de dashboards.
COLOR_FONDO_APP = "#F5F1E7"          # fondo general del contenido (crema cálido, no blanco puro)
COLOR_FONDO_PANEL = "#EEE7D8"        # paneles / barra superior
COLOR_FONDO_TARJETA = "#FFFFFF"      # tarjetas / cards
COLOR_FONDO_TARJETA_HOVER = "#F1E9D8"
COLOR_BORDE_SUTIL = "#E1D5BF"

COLOR_ACENTO_PRIMARIO = "#B5541A"    # cobre quemado: acciones, bordes activos
COLOR_ACENTO_SECUNDARIO = "#D97B3B"  # cobre claro: hover, énfasis suave
COLOR_ACENTO_GLOW = "#E89A5C"
COLOR_ACENTO_ALTERNO = "#0F6E63"     # pátina/teal profundo: alertas, insignias, hallazgos importantes
COLOR_ACENTO_ALTERNO_GLOW = "#37A093"

COLOR_BLANCO = "#FFFFFF"
COLOR_TEXTO_PRIMARIO = "#241C14"     # grafito cálido, no negro puro
COLOR_TEXTO_SECUNDARIO = "#6B5F4E"   # taupe / marrón cálido

COLOR_ERROR = "#C23B3B"
COLOR_EXITO = "#1E8F5E"

# Radios de esquina: tarjetas y botones redondeados, look moderno sin ser "recuadrado".
RADIO_TARJETA = 16
RADIO_BOTON = 12
GROSOR_BORDE_SUTIL = 1

# Navegación (sidebar del Dashboard, panel de marca del Login): grafito oscuro cálido,
# a propósito muy distinto del contenido claro — un layout híbrido, no monocromático.
COLOR_NAV_FONDO = "#241C14"
COLOR_NAV_FONDO_HOVER = "#342A1E"
COLOR_NAV_BORDE = "#3D3225"
COLOR_NAV_TEXTO = "#F5F1E7"
COLOR_NAV_TEXTO_SECUNDARIO = "#B8A88E"

# Texto sobre la foto del panel de marca del Login (fondo claro, imagen sin editar).
COLOR_NEGRO = "#0A0A0A"
COLOR_AZUL_OSCURO = "#0B2C4A"

FONT_FAMILY = "Century Gothic"
FONT_FAMILY_MONO = "Consolas"

VENTANA_ANCHO = 1200
VENTANA_ALTO = 720
