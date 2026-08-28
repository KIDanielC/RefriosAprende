"""Configuración global de la aplicación: rutas y paleta institucional."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "refrios.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
IMAGES_DIR = os.path.join(BASE_DIR, "resources", "images")

APP_NAME = "Refrios Aprende"
APP_VERSION = "0.1.0"

# Paleta "HUD de diagnóstico" en clave clara: sin colores corporativos. El contenido
# (formularios, tablas, dashboard) va en blanco/gris muy claro con texto oscuro.
# La navegación (sidebar del Dashboard y panel de marca del Login) usa su PROPIA
# paleta oscura — así queda visualmente diferenciada y el logo/los íconos no se lavan
# contra un fondo blanco.
COLOR_FONDO_APP = "#F3F5F9"          # fondo general del contenido (blanco con tinte azulado)
COLOR_FONDO_PANEL = "#FFFFFF"        # paneles de contenido
COLOR_FONDO_TARJETA = "#FFFFFF"      # tarjetas / cards
COLOR_FONDO_TARJETA_HOVER = "#E9EDF4"
COLOR_BORDE_SUTIL = "#D8DEE8"

COLOR_ACENTO_PRIMARIO = "#0089A3"    # cian: acciones, bordes activos
COLOR_ACENTO_SECUNDARIO = "#00ACC6"  # cian claro: hover, énfasis suave
COLOR_ACENTO_GLOW = "#4FD6E8"
COLOR_ACENTO_ALTERNO = "#E5187E"     # magenta: alertas, insignias, hallazgos importantes
COLOR_ACENTO_ALTERNO_GLOW = "#FF4FA0"

COLOR_BLANCO = "#FFFFFF"
COLOR_TEXTO_PRIMARIO = "#12161F"     # texto principal sobre fondo claro
COLOR_TEXTO_SECUNDARIO = "#5A6577"   # texto secundario / labels

COLOR_ERROR = "#D6293E"
COLOR_EXITO = "#1D9A6C"

# Navegación (sidebar del Dashboard): paleta oscura propia, independiente del contenido.
COLOR_NAV_FONDO = "#10141C"
COLOR_NAV_FONDO_HOVER = "#1D2432"
COLOR_NAV_BORDE = "#262E3D"
COLOR_NAV_TEXTO = "#F3F5F9"
COLOR_NAV_TEXTO_SECUNDARIO = "#98A2B5"

# Texto sobre la foto del panel de marca del Login (fondo claro, imagen sin editar).
COLOR_NEGRO = "#0A0A0A"
COLOR_AZUL_OSCURO = "#0B2C4A"

FONT_FAMILY = "Century Gothic"
FONT_FAMILY_MONO = "Consolas"

VENTANA_ANCHO = 1200
VENTANA_ALTO = 720
