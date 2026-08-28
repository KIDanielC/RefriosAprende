"""Configuración global de la aplicación: rutas y paleta institucional."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "refrios.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
IMAGES_DIR = os.path.join(BASE_DIR, "resources", "images")

APP_NAME = "Refrios Aprende"
APP_VERSION = "0.1.0"

# Paleta institucional (Azul / Amarillo / Blanco) reinterpretada en clave oscura/futurista.
# Se conservan azul y amarillo como colores de marca exigidos por el proyecto de grado,
# pero aplicados sobre fondos oscuros con acentos tipo "glow" en vez de superficies blancas planas.
COLOR_FONDO_APP = "#0A0E17"          # fondo general (casi negro, tinte azulado)
COLOR_FONDO_PANEL = "#0F1521"        # paneles grandes (sidebar, panel de marca)
COLOR_FONDO_TARJETA = "#161D2E"      # tarjetas / cards
COLOR_FONDO_TARJETA_HOVER = "#1D2740"
COLOR_BORDE_SUTIL = "#242E45"

COLOR_AZUL_PRIMARIO = "#1E5FE0"      # azul institucional, versión eléctrica
COLOR_AZUL_SECUNDARIO = "#3B82F6"
COLOR_AZUL_GLOW = "#4F8FFF"
COLOR_AMARILLO = "#FFC93C"           # amarillo institucional, versión neón suave
COLOR_AMARILLO_GLOW = "#FFD966"

COLOR_BLANCO = "#FFFFFF"
COLOR_TEXTO_PRIMARIO = "#E8ECF4"     # texto principal sobre fondo oscuro
COLOR_TEXTO_SECUNDARIO = "#8B94A8"   # texto secundario / labels
COLOR_GRIS_CLARO = COLOR_FONDO_APP   # alias retrocompatible
COLOR_GRIS_TEXTO = COLOR_TEXTO_SECUNDARIO

COLOR_ERROR = "#FF5C5C"
COLOR_EXITO = "#3DDC97"

FONT_FAMILY = "Segoe UI Variable Display"
FONT_FAMILY_MONO = "Consolas"

VENTANA_ANCHO = 1200
VENTANA_ALTO = 720
