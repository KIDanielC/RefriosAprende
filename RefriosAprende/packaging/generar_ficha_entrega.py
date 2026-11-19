"""Genera los artefactos finales de una entrega: el paquete portable (ZIP de
dist/RefriosAprende), el historial de git en texto plano (no depende de tener el
repositorio), y una ficha de entrega en Markdown con versión, fecha, commit, huellas
SHA-256 del instalador y del paquete portable, versión de Python y dependencias, y el
resumen de la suite de pruebas.

Uso (desde la raíz de RefriosAprende, con dist/RefriosAprende y el instalador ya
compilados):
    py packaging/generar_ficha_entrega.py

Falla si el árbol de git tiene cambios sin confirmar en archivos ya versionados: una ficha
de entrega debe corresponder exactamente a un commit real, no a un estado a medio modificar.
"""
import hashlib
import os
import platform
import subprocess
import sys
import zipfile
from datetime import datetime

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_REPOSITORIO = os.path.dirname(_RAIZ_PROYECTO)

# 'packaging/' no es un paquete Python normal con __init__.py: al correr este archivo
# directamente ('py packaging/generar_ficha_entrega.py'), su propio directorio queda en
# sys.path pero la raíz del proyecto no, así que "from config.settings import ..." fallaría
# con ModuleNotFoundError. Se agrega explícitamente, antes de ese import.
if _RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, _RAIZ_PROYECTO)

from config.settings import APP_VERSION  # noqa: E402 (tiene que ir después del sys.path.insert)
_DIR_DIST = os.path.join(_RAIZ_PROYECTO, "dist", "RefriosAprende")
_DIR_SALIDA = os.path.join(_RAIZ_PROYECTO, "packaging", "salida")
_DIR_ENTREGA = os.path.join(_DIR_SALIDA, "entrega")
_RUTA_INSTALADOR = os.path.join(_DIR_SALIDA, f"RefriosAprende-Setup-{APP_VERSION}.exe")


class EntregaInvalidaError(Exception):
    """El estado del repositorio o de los artefactos no permite generar una ficha confiable."""


def _ejecutar(comando: list[str], cwd: str) -> str:
    resultado = subprocess.run(comando, cwd=cwd, capture_output=True, text=True, check=True)
    return resultado.stdout.strip()


def _verificar_arbol_limpio() -> None:
    # --untracked-files=no: a propósito no revisa archivos sueltos sin seguimiento (apuntes,
    # salidas de prueba locales); lo que de verdad no puede quedar suelto son cambios sobre
    # archivos YA versionados, porque esos sí alterarían el commit que la ficha describe.
    salida = _ejecutar(["git", "status", "--porcelain", "--untracked-files=no"], cwd=_RAIZ_REPOSITORIO)
    if salida:
        raise EntregaInvalidaError(
            "Hay cambios sin confirmar sobre archivos versionados. Confirma o descarta los "
            "cambios antes de generar la ficha de entrega:\n" + salida
        )


def _sha256_de(ruta_archivo: str) -> str:
    hasher = hashlib.sha256()
    with open(ruta_archivo, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            hasher.update(bloque)
    return hasher.hexdigest()


def _generar_paquete_portable() -> str:
    if not os.path.isdir(_DIR_DIST):
        raise EntregaInvalidaError(f"No existe {_DIR_DIST}. Compila primero con PyInstaller.")

    os.makedirs(_DIR_ENTREGA, exist_ok=True)
    ruta_zip = os.path.join(_DIR_ENTREGA, f"RefriosAprende-Portable-v{APP_VERSION}.zip")
    if os.path.isfile(ruta_zip):
        os.remove(ruta_zip)

    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zip_archivo:
        for carpeta_actual, _, archivos in os.walk(_DIR_DIST):
            for nombre_archivo in archivos:
                ruta_completa = os.path.join(carpeta_actual, nombre_archivo)
                ruta_relativa = os.path.join("RefriosAprende", os.path.relpath(ruta_completa, _DIR_DIST))
                zip_archivo.write(ruta_completa, ruta_relativa)

    return ruta_zip


def _generar_historial_git() -> str:
    os.makedirs(_DIR_ENTREGA, exist_ok=True)
    historial = _ejecutar(
        ["git", "log", "--date=iso", "--pretty=format:%h|%ad|%an|%s"], cwd=_RAIZ_REPOSITORIO
    )
    ruta_historial = os.path.join(_DIR_ENTREGA, "HISTORIAL_GIT.txt")
    with open(ruta_historial, "w", encoding="utf-8") as archivo:
        archivo.write(historial + "\n")
    return ruta_historial


def _generar_zip_codigo() -> str:
    os.makedirs(_DIR_ENTREGA, exist_ok=True)
    ruta_zip = os.path.join(_DIR_ENTREGA, f"RefriosAprende-Codigo-v{APP_VERSION}.zip")
    subprocess.run(
        ["git", "archive", "--format=zip", "-o", ruta_zip, "HEAD", "--", "RefriosAprende"],
        cwd=_RAIZ_REPOSITORIO, check=True,
    )
    return ruta_zip


def _resumen_de_pruebas() -> str:
    resultado = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=_RAIZ_PROYECTO, capture_output=True, text=True,
    )
    lineas = [linea for linea in resultado.stdout.splitlines() if linea.strip()]
    return lineas[-1] if lineas else "(no se pudo obtener el resumen de pytest)"


def _version_de_dependencias() -> str:
    resultado = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], cwd=_RAIZ_PROYECTO, capture_output=True, text=True,
    )
    return resultado.stdout.strip()


def generar_ficha_entrega() -> str:
    _verificar_arbol_limpio()
    if not os.path.isfile(_RUTA_INSTALADOR):
        raise EntregaInvalidaError(f"No existe el instalador en {_RUTA_INSTALADOR}. Compílalo primero.")

    ruta_portable = _generar_paquete_portable()
    _generar_historial_git()
    try:
        _generar_zip_codigo()
    except subprocess.CalledProcessError:
        pass  # el ZIP de código es un extra; no bloquea la ficha si git archive falla en este entorno

    commit = _ejecutar(["git", "rev-parse", "HEAD"], cwd=_RAIZ_REPOSITORIO)
    resumen_pruebas = _resumen_de_pruebas()
    dependencias = _version_de_dependencias()

    contenido = f"""# Ficha de entrega — Refrios Aprende v{APP_VERSION}

- **Versión:** {APP_VERSION}
- **Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Commit:** {commit}
- **Python:** {platform.python_version()} ({platform.architecture()[0]})

## Huellas SHA-256

| Archivo | SHA-256 |
|---|---|
| {os.path.basename(_RUTA_INSTALADOR)} | {_sha256_de(_RUTA_INSTALADOR)} |
| {os.path.basename(ruta_portable)} | {_sha256_de(ruta_portable)} |

## Resumen de la suite de pruebas

```
{resumen_pruebas}
```

## Dependencias (pip freeze)

```
{dependencias}
```
"""
    ruta_ficha = os.path.join(_DIR_ENTREGA, f"FICHA_ENTREGA_v{APP_VERSION}.md")
    with open(ruta_ficha, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print(f"Ficha de entrega generada en: {ruta_ficha}")
    return ruta_ficha


if __name__ == "__main__":
    try:
        generar_ficha_entrega()
    except EntregaInvalidaError as error:
        print(f"No se pudo generar la ficha de entrega:\n{error}")
        sys.exit(1)
