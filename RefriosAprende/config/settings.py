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
FOTOS_PERFIL_DIR = os.path.join(BASE_DIR, "resources", "fotos_perfil")
ENTREGAS_DIR = os.path.join(BASE_DIR, "resources", "entregas")

APP_NAME = "Refrios Aprende"
APP_VERSION = "1.0.0"

# Paleta "HUD": oscura y minimalista, tipo panel técnico de diagnóstico, en vez de tarjetas
# cálidas y redondeadas. Fondo casi negro, acentos eléctricos (cian + violeta) y esquinas
# casi rectas (RADIO_TARJETA/RADIO_BOTON bajos) en toda la app.
COLOR_FONDO_APP = "#0B0F14"
COLOR_FONDO_PANEL = "#10151C"
COLOR_FONDO_TARJETA = "#151B23"
COLOR_FONDO_TARJETA_HOVER = "#1C232D"
COLOR_BORDE_SUTIL = "#232B36"

COLOR_ACENTO_PRIMARIO = "#2FD9FF"     # cian eléctrico: acciones, bordes activos
COLOR_ACENTO_SECUNDARIO = "#5EE6FF"   # cian claro: hover, énfasis suave
COLOR_ACENTO_GLOW = "#8FEEFF"
COLOR_ACENTO_ALTERNO = "#7C5CFF"      # violeta: alertas, insignias, hallazgos importantes
COLOR_ACENTO_ALTERNO_GLOW = "#A88CFF"

COLOR_BLANCO = "#FFFFFF"
COLOR_TEXTO_PRIMARIO = "#E7EDF3"      # casi blanco, no blanco puro
COLOR_TEXTO_SECUNDARIO = "#8B96A5"    # gris azulado

COLOR_ERROR = "#FF4D6D"
COLOR_EXITO = "#00E5A0"

# Radios de esquina: casi rectos, look de panel técnico en vez de tarjetas redondeadas.
RADIO_TARJETA = 4
RADIO_BOTON = 2
GROSOR_BORDE_SUTIL = 1

# Navegación (sidebar del Dashboard, panel de marca del Login): mismo tono que el fondo
# general, ya que toda la app es oscura (no hay un contenido claro que contrastar).
COLOR_NAV_FONDO = "#0B0F14"
COLOR_NAV_FONDO_HOVER = "#151B23"
COLOR_NAV_BORDE = "#232B36"
COLOR_NAV_TEXTO = "#E7EDF3"
COLOR_NAV_TEXTO_SECUNDARIO = "#5B6675"

# Texto sobre la foto del panel de marca del Login (imagen sin editar, fondo claro fijo).
COLOR_NEGRO = "#0A0A0A"
COLOR_AZUL_OSCURO = "#0B2C4A"

FONT_FAMILY = "Century Gothic"
FONT_FAMILY_MONO = "Consolas"

VENTANA_ANCHO = 1200
VENTANA_ALTO = 720
