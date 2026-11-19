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

# Base de datos semilla: SIEMPRE packaging/semilla/refrios.db (generada con
# 'py -m utils.crear_semilla'), nunca database/refrios.db. Esa última es la base real de
# desarrollo/demostración de quien compila, y empaquetarla metía usuarios, cursos y
# resultados de ejemplo dentro de un instalador que se iba a entregar como limpio. La
# semilla solo trae el esquema y los roles fijos (ADMINISTRADOR, APRENDIZ); el primer
# arranque abre la ventana de creación del primer administrador.
_ruta_bd_semilla = os.path.join(PROJECT_ROOT, "packaging", "semilla", "refrios.db")
if not os.path.isfile(_ruta_bd_semilla):
    raise FileNotFoundError(
        "Falta la base de datos semilla para empaquetar. Genera "
        f"{_ruta_bd_semilla} antes de compilar: 'py -m utils.crear_semilla' "
        "desde la raíz de RefriosAprende."
    )
datas.append((_ruta_bd_semilla, "database"))

# A propósito, NO se empaquetan resources/contenidos, fotos_perfil ni entregas: son
# archivos subidos por usuarios reales de una instalación concreta, nunca contenido de
# fábrica. Un paquete de demostración con datos de ejemplo, si se necesita, se arma aparte
# (ver documentation/EMPAQUETADO.md), nunca mezclado con el instalador que se entrega al taller.

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
