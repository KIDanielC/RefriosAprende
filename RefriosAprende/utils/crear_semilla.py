"""Genera la base de datos "semilla" que se empaqueta con el instalador: solo el esquema y
los roles fijos (ADMINISTRADOR, APRENDIZ), sin usuarios, cursos ni ningún otro dato de
ejemplo. Al no traer ninguna cuenta creada, el primer arranque abre la ventana de primer
administrador (ver view/screens/primer_administrador_view.py) en vez de depender de una
cuenta y una contraseña de fábrica escritas en el código.

Hay que volver a correr este script cada vez que cambie database/schema.sql, para que la
semilla empaquetada no quede desactualizada.

Uso (desde la raíz de RefriosAprende):
    py -m utils.crear_semilla
"""
import os
import sqlite3

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RUTA_SCHEMA = os.path.join(_RAIZ_PROYECTO, "database", "schema.sql")
_RUTA_SEMILLA = os.path.join(_RAIZ_PROYECTO, "packaging", "semilla", "refrios.db")


def crear_semilla() -> str:
    os.makedirs(os.path.dirname(_RUTA_SEMILLA), exist_ok=True)
    if os.path.isfile(_RUTA_SEMILLA):
        os.remove(_RUTA_SEMILLA)

    with open(_RUTA_SCHEMA, "r", encoding="utf-8") as archivo_esquema:
        script_sql = archivo_esquema.read()

    conexion = sqlite3.connect(_RUTA_SEMILLA)
    try:
        conexion.executescript(script_sql)
        conexion.commit()
    finally:
        conexion.close()

    print(f"Semilla creada en: {_RUTA_SEMILLA}")
    return _RUTA_SEMILLA


if __name__ == "__main__":
    crear_semilla()
