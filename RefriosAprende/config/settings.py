"""Configuración global de la aplicación: rutas y paleta institucional."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "refrios.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
IMAGES_DIR = os.path.join(BASE_DIR, "resources", "images")

APP_NAME = "Refrios Aprende"
APP_VERSION = "0.1.0"

# Paleta "HUD de diagnóstico" en clave OSCURA — toda la aplicación (contenido, tarjetas,
# tablas, sidebar) comparte el mismo fondo oscuro, igual que el mockup de referencia.
COLOR_FONDO_APP = "#0B0E15"          # fondo general del contenido
COLOR_FONDO_PANEL = "#10141C"        # paneles / barra superior
COLOR_FONDO_TARJETA = "#141924"      # tarjetas / cards
COLOR_FONDO_TARJETA_HOVER = "#1B2130"
COLOR_BORDE_SUTIL = "#262E40"

COLOR_ACENTO_PRIMARIO = "#00ACC6"    # cian: acciones, bordes activos
COLOR_ACENTO_SECUNDARIO = "#4FD6E8"  # cian claro: hover, énfasis suave
COLOR_ACENTO_GLOW = "#4FD6E8"
COLOR_ACENTO_ALTERNO = "#E5187E"     # magenta: alertas, insignias, hallazgos importantes
COLOR_ACENTO_ALTERNO_GLOW = "#FF63AC"

COLOR_BLANCO = "#FFFFFF"
COLOR_TEXTO_PRIMARIO = "#EDF1F8"     # texto principal sobre fondo oscuro
COLOR_TEXTO_SECUNDARIO = "#9AA5BC"   # texto secundario / labels

COLOR_ERROR = "#F0576B"
COLOR_EXITO = "#2FBE8C"

# Radios de esquina del rediseño "moderno": tarjetas y botones más redondeados,
# bordes finos en vez de gruesos, para un look menos "recuadrado".
RADIO_TARJETA = 14
RADIO_BOTON = 10
GROSOR_BORDE_SUTIL = 1

# Navegación (sidebar del Dashboard, panel de marca del Login): un tono ligeramente
# más oscuro que el fondo general, para diferenciarse sin romper la unidad visual.
COLOR_NAV_FONDO = "#080A10"
COLOR_NAV_FONDO_HOVER = "#171E2C"
COLOR_NAV_BORDE = "#1E2536"
COLOR_NAV_TEXTO = "#EDF1F8"
COLOR_NAV_TEXTO_SECUNDARIO = "#8E99B0"

# Texto sobre la foto del panel de marca del Login (fondo claro, imagen sin editar).
COLOR_NEGRO = "#0A0A0A"
COLOR_AZUL_OSCURO = "#0B2C4A"

FONT_FAMILY = "Century Gothic"
FONT_FAMILY_MONO = "Consolas"

VENTANA_ANCHO = 1200
VENTANA_ALTO = 720
