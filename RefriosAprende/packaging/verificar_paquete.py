"""Verifica que un paquete compilado (dist/RefriosAprende/_internal, o la carpeta de una
instalación ya hecha) trae la base de datos semilla (solo esquema y roles, sin usuarios,
cursos ni ningún otro dato real) y no arrastra contenidos, fotos de perfil ni entregas de
ningún taller real.

Uso:
    py packaging/verificar_paquete.py <ruta a la carpeta que contiene database/ y resources/>

Ejemplos de ruta:
    dist\\RefriosAprende\\_internal
    %TEMP%\\ra_prueba\\_internal      (tras instalar en silencio en una carpeta temporal)
"""
import os
import sqlite3
import sys

# roles no está en esta lista a propósito: debe tener exactamente los 2 roles fijos del
# sistema (ADMINISTRADOR, APRENDIZ), no estar vacía.
_TABLAS_QUE_DEBEN_ESTAR_VACIAS = (
    "usuarios", "categorias", "cursos", "cursos_prerrequisitos", "guias_aprendizaje",
    "inscripciones", "contenidos", "evaluaciones", "preguntas", "opciones", "resultados",
    "progreso", "simulaciones", "talleres", "entregas_taller", "tiempo_uso_curso",
    "contenidos_vistos",
)
_CARPETAS_QUE_DEBEN_ESTAR_VACIAS = ("contenidos", "fotos_perfil", "entregas")


class PaqueteNoLimpioError(Exception):
    """El paquete trae datos que no deberían ir en una instalación limpia del taller."""


def verificar_paquete(ruta_base: str) -> None:
    ruta_bd = os.path.join(ruta_base, "database", "refrios.db")
    if not os.path.isfile(ruta_bd):
        raise PaqueteNoLimpioError(f"No se encontró la base de datos en: {ruta_bd}")

    hallazgos = []
    conexion = sqlite3.connect(ruta_bd)
    try:
        total_roles = conexion.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
        if total_roles != 2:
            hallazgos.append(f"  - La tabla 'roles' tiene {total_roles} fila(s); deberían ser exactamente 2.")

        for tabla in _TABLAS_QUE_DEBEN_ESTAR_VACIAS:
            cantidad = conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            if cantidad > 0:
                hallazgos.append(f"  - La tabla '{tabla}' tiene {cantidad} fila(s); debería estar vacía.")
    finally:
        conexion.close()

    for carpeta in _CARPETAS_QUE_DEBEN_ESTAR_VACIAS:
        ruta_carpeta = os.path.join(ruta_base, "resources", carpeta)
        if os.path.isdir(ruta_carpeta) and os.listdir(ruta_carpeta):
            hallazgos.append(
                f"  - resources/{carpeta} no está vacía ({len(os.listdir(ruta_carpeta))} archivo(s))."
            )

    if hallazgos:
        raise PaqueteNoLimpioError(
            "El paquete trae datos que no deberían ir en una instalación limpia:\n" + "\n".join(hallazgos)
        )

    print(f"OK: '{ruta_base}' está limpio (solo esquema y roles, sin datos de ejemplo).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py packaging/verificar_paquete.py <ruta>")
        sys.exit(2)
    try:
        verificar_paquete(sys.argv[1])
    except PaqueteNoLimpioError as error:
        print(f"FALLÓ:\n{error}")
        sys.exit(1)
