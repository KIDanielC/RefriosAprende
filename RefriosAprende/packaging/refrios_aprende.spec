# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para "Refrios Aprende" (build --onedir).

Uso (desde la raíz de RefriosAprende, con el entorno virtual activado):

    py -m PyInstaller packaging/refrios_aprende.spec

El resultado queda en dist/RefriosAprende/ (un .exe más sus dependencias). Ese es el
insumo que después empaqueta packaging/instalador.iss con Inno Setup.

Ver documentation/EMPAQUETADO.md para el procedimiento completo.
"""
import os

PROJECT_ROOT = os.path.dirname(SPECPATH)  # packaging/ -> raíz del proyecto

datas = [
    (os.path.join(PROJECT_ROOT, "database", "schema.sql"), "database"),
    (os.path.join(PROJECT_ROOT, "resources", "icons"), "resources/icons"),
    (os.path.join(PROJECT_ROOT, "resources", "images"), "resources/images"),
]

# Base de datos precargada (opcional): si al compilar existe database/refrios.db, se
# incluye como semilla de fábrica. En el primer arranque, config/settings.py la copia a
# la carpeta de datos del usuario (%LOCALAPPDATA%\RefriosAprende). Si no existe, la app
# arranca con un esquema vacío (se crea solo a partir de schema.sql). Para publicar una
# versión "de demostración" con datos de ejemplo, colocar el refrios.db deseado en
# database/ antes de compilar; para una versión "en blanco", renombrarlo o borrarlo antes.
_ruta_bd_semilla = os.path.join(PROJECT_ROOT, "database", "refrios.db")
if os.path.isfile(_ruta_bd_semilla):
    datas.append((_ruta_bd_semilla, "database"))

# Contenidos ya subidos (PDF/imágenes de cursos): se incluyen como semilla solo si existen,
# para que una instalación de demostración muestre contenido real desde el primer arranque.
_dir_contenidos_semilla = os.path.join(PROJECT_ROOT, "resources", "contenidos")
if os.path.isdir(_dir_contenidos_semilla) and os.listdir(_dir_contenidos_semilla):
    datas.append((_dir_contenidos_semilla, "resources/contenidos"))

a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=["matplotlib.backends.backend_tkagg"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RefriosAprende",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=os.path.join(PROJECT_ROOT, "resources", "icons", "app.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="RefriosAprende",
)
