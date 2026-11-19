"""Respaldo y restauración de la carpeta de datos real de la aplicación (BASE_DIR cuando
corre empaquetada, o la raíz del proyecto en desarrollo): database/refrios.db más los
archivos subidos por instructores y aprendices (resources/contenidos, fotos_perfil,
entregas). Es toda la información que una reinstalación, un disco dañado o un error del
usuario podrían hacer perder.

No es todavía un botón dentro de la aplicación (ver Anexo S: línea de evolución futura);
por ahora es la herramienta de línea de comandos que demuestra que el respaldo y la
restauración funcionan de verdad sobre una carpeta de datos real.

Uso:
    py -m utils.respaldo respaldar <carpeta_datos> <archivo_zip_destino>
    py -m utils.respaldo restaurar <archivo_zip> <carpeta_datos_destino>
"""
import json
import os
import sys
import zipfile
from datetime import datetime

from config.settings import APP_VERSION

_SUBCARPETAS_A_RESPALDAR = (
    "database",
    os.path.join("resources", "contenidos"),
    os.path.join("resources", "fotos_perfil"),
    os.path.join("resources", "entregas"),
)
_NOMBRE_METADATA = "_respaldo_metadata.json"


def crear_respaldo(carpeta_datos: str, ruta_zip_destino: str) -> str:
    carpeta_del_zip = os.path.dirname(os.path.abspath(ruta_zip_destino))
    if carpeta_del_zip:
        os.makedirs(carpeta_del_zip, exist_ok=True)

    metadata = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version_app": APP_VERSION,
    }

    with zipfile.ZipFile(ruta_zip_destino, "w", zipfile.ZIP_DEFLATED) as zip_archivo:
        zip_archivo.writestr(_NOMBRE_METADATA, json.dumps(metadata, ensure_ascii=False, indent=2))
        for subcarpeta in _SUBCARPETAS_A_RESPALDAR:
            ruta_absoluta = os.path.join(carpeta_datos, subcarpeta)
            if not os.path.isdir(ruta_absoluta):
                continue
            for carpeta_actual, _, archivos in os.walk(ruta_absoluta):
                for nombre_archivo in archivos:
                    ruta_completa = os.path.join(carpeta_actual, nombre_archivo)
                    ruta_relativa = os.path.relpath(ruta_completa, carpeta_datos)
                    zip_archivo.write(ruta_completa, ruta_relativa)

    return ruta_zip_destino


def leer_metadata_respaldo(ruta_zip: str) -> dict:
    with zipfile.ZipFile(ruta_zip, "r") as zip_archivo:
        return json.loads(zip_archivo.read(_NOMBRE_METADATA).decode("utf-8"))


def restaurar_respaldo(ruta_zip: str, carpeta_datos_destino: str) -> None:
    os.makedirs(carpeta_datos_destino, exist_ok=True)
    with zipfile.ZipFile(ruta_zip, "r") as zip_archivo:
        for nombre in zip_archivo.namelist():
            if nombre == _NOMBRE_METADATA:
                continue
            zip_archivo.extract(nombre, carpeta_datos_destino)


def _uso_y_salir() -> None:
    print(
        "Uso:\n"
        "  py -m utils.respaldo respaldar <carpeta_datos> <archivo_zip_destino>\n"
        "  py -m utils.respaldo restaurar <archivo_zip> <carpeta_datos_destino>"
    )
    sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("respaldar", "restaurar"):
        _uso_y_salir()
    elif sys.argv[1] == "respaldar":
        print(f"Respaldo creado en: {crear_respaldo(sys.argv[2], sys.argv[3])}")
    else:
        restaurar_respaldo(sys.argv[2], sys.argv[3])
        print(f"Restaurado en: {sys.argv[3]}")
