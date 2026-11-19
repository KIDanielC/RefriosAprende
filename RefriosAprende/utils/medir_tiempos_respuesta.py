"""Mide el tiempo de construir cada pantalla principal (con los controladores reales, no
simulados) sobre la base de datos que se le indique — normalmente una generada con
utils/poblar_carga.py. Reporta mediana, percentil 95 y máximo de N repeticiones por
pantalla, junto con los datos del equipo donde se corrió.

Uso (desde la raíz de RefriosAprende):
    py -m utils.medir_tiempos_respuesta <ruta_bd> <usuario_admin> <salida.md> [repeticiones]
"""
import os
import platform
import statistics
import sys
import time


def _construir_pantallas(master, admin):
    from view.screens.configuracion_screen import ConfiguracionScreen
    from view.screens.cursos_screen import CursosScreen
    from view.screens.reportes_screen import ReportesScreen
    from view.screens.usuarios_screen import UsuariosScreen

    return {
        "Usuarios": lambda: UsuariosScreen(master, usuario_sesion=admin),
        "Cursos": lambda: CursosScreen(master, usuario_sesion=admin),
        "Reportes": lambda: ReportesScreen(master, usuario_sesion=admin),
        "Configuración": lambda: ConfiguracionScreen(master, usuario_sesion=admin),
    }


def _info_equipo() -> str:
    memoria_gb = "?"
    try:
        import ctypes

        class _MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [
                (nombre, ctypes.c_ulonglong) for nombre in (
                    "ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile",
                    "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual",
                )
            ]

        estado = _MEMORYSTATUSEX()
        estado.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado))
        memoria_gb = round(estado.ullTotalPhys / (1024 ** 3), 1)
    except Exception:
        pass

    return (
        f"{platform.processor() or platform.machine()} · {memoria_gb} GB RAM · "
        f"{platform.system()} {platform.release()} · Python {platform.python_version()}"
    )


def medir(ruta_bd: str, usuario_admin: str, ruta_salida_md: str, repeticiones: int = 20) -> str:
    import config.settings as settings_module
    settings_module.DATABASE_PATH = ruta_bd
    import database.connection as connection_module
    connection_module.DATABASE_PATH = ruta_bd
    connection_module.ConexionBD._instancia = None

    import customtkinter as ctk
    from model.dao.usuario_dao import UsuarioDAO

    admin = UsuarioDAO().obtener_por_usuario(usuario_admin)
    if admin is None:
        raise ValueError(f"No existe el usuario '{usuario_admin}' en {ruta_bd}.")

    raiz = ctk.CTk()
    raiz.withdraw()

    filas_resultado = []
    try:
        for nombre_pantalla, constructor in _construir_pantallas(raiz, admin).items():
            tiempos_ms = []
            for _ in range(repeticiones):
                inicio = time.perf_counter()
                pantalla = constructor()
                pantalla.update_idletasks()
                tiempos_ms.append((time.perf_counter() - inicio) * 1000)
                pantalla.destroy()

            tiempos_ms.sort()
            indice_p95 = max(0, int(len(tiempos_ms) * 0.95) - 1)
            filas_resultado.append({
                "pantalla": nombre_pantalla,
                "mediana_ms": round(statistics.median(tiempos_ms), 1),
                "p95_ms": round(tiempos_ms[indice_p95], 1),
                "maximo_ms": round(max(tiempos_ms), 1),
            })
    finally:
        raiz.destroy()

    lineas = [
        "# Tiempos de respuesta por pantalla",
        "",
        f"Equipo: {_info_equipo()}",
        f"Base de datos: {ruta_bd}",
        f"Repeticiones por pantalla: {repeticiones}",
        "",
        "| Pantalla | Mediana (ms) | P95 (ms) | Máximo (ms) |",
        "|---|---|---|---|",
    ]
    for fila in filas_resultado:
        lineas.append(f"| {fila['pantalla']} | {fila['mediana_ms']} | {fila['p95_ms']} | {fila['maximo_ms']} |")

    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida_md)) or ".", exist_ok=True)
    with open(ruta_salida_md, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas) + "\n")

    print(f"Resultados escritos en: {ruta_salida_md}")
    return ruta_salida_md


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print("Uso: py -m utils.medir_tiempos_respuesta <ruta_bd> <usuario_admin> <salida.md> [repeticiones]")
        sys.exit(2)
    repeticiones = int(sys.argv[4]) if len(sys.argv) == 5 else 20
    medir(sys.argv[1], sys.argv[2], sys.argv[3], repeticiones)
