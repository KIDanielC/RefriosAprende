"""Mide el tiempo de respuesta de cada operación de negocio por separado (crear curso,
crear usuario, matricular, presentar evaluación, calificar entrega, exportar certificado,
generar reportes, etc.), usando los controladores reales -- nunca llamadas simuladas --
sobre bases de datos con tres volúmenes de fondo (pequeño/mediano/grande, los mismos de
utils/poblar_carga.py), para poder ver si el tiempo de cada operación se
degrada a medida que crece el volumen de datos ("prueba de saturación").

Por cada operación y volumen se repite la llamada muchas veces y se reporta: mínimo,
media, mediana, P90, P95, P99, máximo y desviación estándar, en milisegundos.

Uso (desde la raíz de RefriosAprende):
    py -m utils.medir_tiempos_operaciones <carpeta_salida> [repeticiones]

Genera, dentro de <carpeta_salida>:
    - bd_pequeno.db, bd_mediano.db, bd_grande.db (quedan para poder inspeccionarlas)
    - INFORME_TIEMPOS_OPERACIONES.md
"""
import os
import platform
import shutil
import statistics
import sys
import tempfile
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPETICIONES_POR_DEFECTO = 30


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


def _percentil(valores_ordenados: list[float], fraccion: float) -> float:
    indice = max(0, min(len(valores_ordenados) - 1, int(len(valores_ordenados) * fraccion) - 1))
    return valores_ordenados[indice]


def _resumen(tiempos_ms: list[float]) -> dict:
    ordenados = sorted(tiempos_ms)
    return {
        "n": len(ordenados),
        "min_ms": round(min(ordenados), 2),
        "media_ms": round(statistics.mean(ordenados), 2),
        "mediana_ms": round(statistics.median(ordenados), 2),
        "p90_ms": round(_percentil(ordenados, 0.90), 2),
        "p95_ms": round(_percentil(ordenados, 0.95), 2),
        "p99_ms": round(_percentil(ordenados, 0.99), 2),
        "max_ms": round(max(ordenados), 2),
        "desvest_ms": round(statistics.pstdev(ordenados), 2) if len(ordenados) > 1 else 0.0,
    }


def _cronometrar(repeticiones: int, operacion) -> list[float]:
    """operacion(indice_de_repeticion) ejecuta UNA llamada real y no debe incluir
    preparación de datos: toda la preparación va antes, fuera del cronómetro."""
    tiempos_ms = []
    for i in range(repeticiones):
        inicio = time.perf_counter()
        operacion(i)
        tiempos_ms.append((time.perf_counter() - inicio) * 1000)
    return tiempos_ms


def _apuntar_bd(ruta_bd: str) -> None:
    import config.settings as settings_module
    settings_module.DATABASE_PATH = ruta_bd
    import database.connection as connection_module
    connection_module.DATABASE_PATH = ruta_bd
    connection_module.ConexionBD._instancia = None


def _archivo_temporal(sufijo: str, contenido: bytes) -> str:
    descriptor, ruta = tempfile.mkstemp(suffix=sufijo)
    with os.fdopen(descriptor, "wb") as archivo:
        archivo.write(contenido)
    return ruta


def medir_operaciones(ruta_bd: str, repeticiones: int = REPETICIONES_POR_DEFECTO) -> dict:
    """Sobre una base de datos YA poblada con el volumen de fondo que se quiera medir,
    ejecuta y cronometra cada operación de negocio por separado. Devuelve
    {nombre_operacion: resumen_estadistico}."""
    _apuntar_bd(ruta_bd)

    from PIL import Image

    from controller.autenticacion_controller import AutenticacionController
    from controller.certificado_controller import CertificadoController
    from controller.contenido_controller import ContenidoController
    from controller.curso_controller import CursoController
    from controller.evaluacion_controller import EvaluacionController
    from controller.inscripcion_controller import InscripcionController
    from controller.progreso_controller import ProgresoController
    from controller.reporte_controller import ReporteController
    from controller.taller_controller import TallerController
    from controller.usuario_controller import UsuarioController
    from model.dao.rol_dao import RolDAO
    from model.dao.usuario_dao import UsuarioDAO

    rol_aprendiz = RolDAO().obtener_por_nombre("APRENDIZ")
    admin = UsuarioDAO().obtener_por_usuario("admin.carga")
    if admin is None:
        raise ValueError(f"La base {ruta_bd} no tiene el usuario 'admin.carga' (¿se generó con poblar_carga?).")

    uc = UsuarioController()
    cc = CursoController()
    contenido_ctrl = ContenidoController()
    inscripcion_ctrl = InscripcionController()
    evaluacion_ctrl = EvaluacionController()
    taller_ctrl = TallerController()
    progreso_ctrl = ProgresoController()
    reporte_ctrl = ReporteController()
    auth_ctrl = AutenticacionController()
    certificado_ctrl = CertificadoController()

    prefijo = uuid.uuid4().hex[:8]  # evita choques de 'usuario' entre corridas
    prefijo_numerico = str(uuid.uuid4().int)[:6]  # 'documento' solo admite dígitos
    contador = {"valor": 0}

    def _siguiente_aprendiz():
        contador["valor"] += 1
        n = contador["valor"]
        return uc.crear_usuario(
            f"Aprendiz Medicion {prefijo}-{n}", f"7{prefijo_numerico}{n:06d}",
            f"med.{prefijo}.{n}@refrios.local", f"med_{prefijo}_{n}", "ClaveMedicion1",
            rol_aprendiz.id_rol, usuario_actor=admin,
        )

    resultados = {}

    # -- Autenticación --------------------------------------------------------
    aprendiz_login = _siguiente_aprendiz()
    resultados["Autenticación - iniciar_sesion (credenciales correctas)"] = _resumen(_cronometrar(
        repeticiones, lambda i: auth_ctrl.iniciar_sesion(aprendiz_login.usuario, "ClaveMedicion1")
    ))

    # -- Usuarios ---------------------------------------------------------------
    resultados["Usuarios - crear_usuario (aprendiz nuevo)"] = _resumen(_cronometrar(
        repeticiones, lambda i: _siguiente_aprendiz()
    ))
    resultados["Usuarios - listar_usuarios (lectura completa)"] = _resumen(_cronometrar(
        repeticiones, lambda i: uc.listar_usuarios()
    ))

    # -- Cursos -------------------------------------------------------------
    resultados["Cursos - crear_curso (borrador)"] = _resumen(_cronometrar(
        repeticiones, lambda i: cc.crear_curso(
            f"Curso Medicion {prefijo}-{i}", "Curso para medir tiempos.", admin.id_usuario, usuario_actor=admin,
        )
    ))

    cursos_para_publicar = [
        cc.crear_curso(f"Curso Publicar {prefijo}-{i}", "Curso para medir publicación.", admin.id_usuario, usuario_actor=admin)
        for i in range(repeticiones)
    ]
    resultados["Cursos - actualizar_curso (publicar a ACTIVO)"] = _resumen(_cronometrar(
        repeticiones, lambda i: cc.actualizar_curso(
            cursos_para_publicar[i].id_curso, cursos_para_publicar[i].nombre_curso,
            cursos_para_publicar[i].descripcion, admin.id_usuario, "ACTIVO", usuario_actor=admin,
        )
    ))
    resultados["Cursos - listar_cursos_activos (lectura)"] = _resumen(_cronometrar(
        repeticiones, lambda i: cc.listar_cursos_activos()
    ))

    # -- Contenidos ------------------------------------------------------------
    curso_contenidos = cc.crear_curso(f"Curso Contenidos {prefijo}", "Curso para medir contenidos.", admin.id_usuario, usuario_actor=admin)
    resultados["Contenidos - crear_contenido_texto"] = _resumen(_cronometrar(
        repeticiones, lambda i: contenido_ctrl.crear_contenido_texto(
            curso_contenidos.id_curso, f"Texto {i}", "Texto con longitud suficiente para pasar la validación. " * 3,
            usuario_actor=admin,
        )
    ))

    ruta_pdf = _archivo_temporal(".pdf", b"%PDF-1.4\n%%EOF")
    resultados["Contenidos - crear_contenido_pdf"] = _resumen(_cronometrar(
        repeticiones, lambda i: contenido_ctrl.crear_contenido_pdf(
            curso_contenidos.id_curso, f"PDF {i}", "Manual técnico.", ruta_pdf, usuario_actor=admin,
        )
    ))

    ruta_imagen = _archivo_temporal(".png", b"")
    Image.new("RGB", (400, 200), color=(10, 20, 30)).save(ruta_imagen)
    resultados["Contenidos - crear_contenido_imagen"] = _resumen(_cronometrar(
        repeticiones, lambda i: contenido_ctrl.crear_contenido_imagen(
            curso_contenidos.id_curso, f"Imagen {i}", "Diagrama.", ruta_imagen, usuario_actor=admin,
        )
    ))

    ruta_video = _archivo_temporal(".mp4", b"contenido de prueba de video" * 100)
    resultados["Contenidos - crear_contenido_video"] = _resumen(_cronometrar(
        repeticiones, lambda i: contenido_ctrl.crear_contenido_video(
            curso_contenidos.id_curso, f"Video {i}", "Procedimiento en video.", ruta_video, usuario_actor=admin,
        )
    ))

    contenidos_para_reordenar = contenido_ctrl.listar_por_curso(curso_contenidos.id_curso)
    id_primero = contenidos_para_reordenar[0].id_contenido

    def _bajar_y_medir(i):
        inicio = time.perf_counter()
        contenido_ctrl.mover_contenido(id_primero, "bajar", usuario_actor=admin)
        duracion_ms = (time.perf_counter() - inicio) * 1000
        contenido_ctrl.mover_contenido(id_primero, "subir", usuario_actor=admin)  # deja el orden como estaba, fuera del cronómetro
        return duracion_ms

    tiempos_mover = [_bajar_y_medir(i) for i in range(repeticiones)]
    resultados["Contenidos - mover_contenido (reordenar, 'bajar')"] = _resumen(tiempos_mover)

    # -- Matrícula ------------------------------------------------------------
    curso_matricula = cc.crear_curso(f"Curso Matricula {prefijo}", "Curso para medir matrícula.", admin.id_usuario, usuario_actor=admin)
    aprendices_para_matricular = [_siguiente_aprendiz() for _ in range(repeticiones)]
    resultados["Matrícula - matricular"] = _resumen(_cronometrar(
        repeticiones, lambda i: inscripcion_ctrl.matricular(
            aprendices_para_matricular[i].id_usuario, curso_matricula.id_curso, usuario_actor=admin,
        )
    ))

    # -- Evaluaciones -----------------------------------------------------------
    cursos_para_evaluacion = [
        cc.crear_curso(f"Curso Evaluacion {prefijo}-{i}", "Curso para medir evaluaciones.", admin.id_usuario, usuario_actor=admin)
        for i in range(repeticiones)
    ]
    resultados["Evaluaciones - crear_evaluacion_final"] = _resumen(_cronometrar(
        repeticiones, lambda i: evaluacion_ctrl.crear_evaluacion_final(
            cursos_para_evaluacion[i].id_curso, "Evaluación final", 3.0, 999, usuario_actor=admin,
        )
    ))
    evaluaciones_creadas = [evaluacion_ctrl.obtener_evaluacion_final(c.id_curso) for c in cursos_para_evaluacion]
    resultados["Evaluaciones - crear_pregunta"] = _resumen(_cronometrar(
        repeticiones, lambda i: evaluacion_ctrl.crear_pregunta(
            evaluaciones_creadas[i].id_evaluacion, "¿Cuál opción es correcta?",
            [("Correcta", True), ("Incorrecta", False)], usuario_actor=admin,
        )
    ))

    curso_presentar = cc.crear_curso(
        f"Curso Presentar {prefijo}", "Curso para medir presentación de evaluación.", admin.id_usuario, usuario_actor=admin,
    )
    evaluacion_presentar = evaluacion_ctrl.crear_evaluacion_final(
        curso_presentar.id_curso, "Evaluación final", 3.0, repeticiones + 10, usuario_actor=admin,
    )
    evaluacion_ctrl.crear_pregunta(
        evaluacion_presentar.id_evaluacion, "¿Cuál opción es correcta?", [("Correcta", True), ("Incorrecta", False)],
        usuario_actor=admin,
    )
    pregunta_presentar = evaluacion_ctrl.listar_preguntas(evaluacion_presentar.id_evaluacion)[0]
    aprendiz_presentar = _siguiente_aprendiz()
    resultados["Evaluaciones - presentar_evaluacion"] = _resumen(_cronometrar(
        repeticiones, lambda i: evaluacion_ctrl.presentar_evaluacion(
            aprendiz_presentar.id_usuario, evaluacion_presentar,
            {pregunta_presentar.id_pregunta: pregunta_presentar.opcion_correcta().id_opcion},
        )
    ))

    # -- Talleres ----------------------------------------------------------
    curso_talleres = cc.crear_curso(f"Curso Talleres {prefijo}", "Curso para medir talleres.", admin.id_usuario, usuario_actor=admin)
    resultados["Talleres - crear_taller"] = _resumen(_cronometrar(
        repeticiones, lambda i: taller_ctrl.crear_taller(
            curso_talleres.id_curso, f"Taller {i}", "Actividad práctica de ejemplo.", usuario_actor=admin,
        )
    ))

    taller_para_entregas = taller_ctrl.crear_taller(
        curso_talleres.id_curso, "Taller de entregas", "Actividad práctica de ejemplo.", usuario_actor=admin,
    )
    ruta_entrega = _archivo_temporal(".png", b"")
    Image.new("RGB", (200, 200), color=(50, 50, 50)).save(ruta_entrega)
    aprendices_para_entregas = [_siguiente_aprendiz() for _ in range(repeticiones)]
    resultados["Talleres - subir_entrega"] = _resumen(_cronometrar(
        repeticiones, lambda i: taller_ctrl.subir_entrega(
            taller_para_entregas.id_taller, aprendices_para_entregas[i].id_usuario, ruta_entrega,
        )
    ))

    entregas_para_calificar = taller_ctrl.listar_entregas_por_taller(taller_para_entregas.id_taller)
    resultados["Talleres - calificar_entrega"] = _resumen(_cronometrar(
        repeticiones, lambda i: taller_ctrl.calificar_entrega(
            entregas_para_calificar[i].id_entrega, True, "Buen trabajo.", usuario_actor=admin,
        )
    ))

    # -- Certificado ------------------------------------------------------------
    curso_certificado = cc.crear_curso(
        f"Curso Certificado {prefijo}", "Curso para medir certificado.", admin.id_usuario, usuario_actor=admin,
    )
    contenido_certificado = contenido_ctrl.crear_contenido_texto(
        curso_certificado.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación.",
        usuario_actor=admin,
    )
    aprendiz_certificado = _siguiente_aprendiz()
    progreso_ctrl.registrar_contenido_visto(aprendiz_certificado.id_usuario, contenido_certificado)
    carpeta_certificados = tempfile.mkdtemp(prefix="certificados_medicion_")
    resultados["Certificado - exportar_certificado (PDF)"] = _resumen(_cronometrar(
        repeticiones, lambda i: certificado_ctrl.exportar_certificado(
            aprendiz_certificado, curso_certificado, os.path.join(carpeta_certificados, f"certificado_{i}.pdf"),
        )
    ))
    shutil.rmtree(carpeta_certificados, ignore_errors=True)

    # -- Reportes (los que más escalan con el volumen de datos) -----------------
    resultados["Reportes - resumen_general"] = _resumen(_cronometrar(
        repeticiones, lambda i: reporte_ctrl.resumen_general()
    ))
    resultados["Reportes - detalle_por_curso"] = _resumen(_cronometrar(
        repeticiones, lambda i: reporte_ctrl.detalle_por_curso()
    ))
    resultados["Reportes - avance_por_estudiante"] = _resumen(_cronometrar(
        repeticiones, lambda i: reporte_ctrl.avance_por_estudiante(admin.id_usuario)
    ))
    resultados["Reportes - estudiantes_en_riesgo"] = _resumen(_cronometrar(
        repeticiones, lambda i: reporte_ctrl.estudiantes_en_riesgo(admin.id_usuario)
    ))

    for ruta in (ruta_pdf, ruta_imagen, ruta_video, ruta_entrega):
        try:
            os.remove(ruta)
        except OSError:
            pass

    return resultados


def ejecutar_para_todos_los_volumenes(carpeta_salida: str, repeticiones: int = REPETICIONES_POR_DEFECTO) -> str:
    from utils.poblar_carga import VOLUMENES, poblar

    os.makedirs(carpeta_salida, exist_ok=True)
    resultados_por_volumen = {}
    resumenes_poblado = {}

    for nombre_volumen in VOLUMENES:
        ruta_bd = os.path.join(carpeta_salida, f"bd_{nombre_volumen}.db")
        if os.path.isfile(ruta_bd):
            os.remove(ruta_bd)
        print(f"--- Poblando volumen '{nombre_volumen}' en {ruta_bd} ---")
        resumenes_poblado[nombre_volumen] = poblar(nombre_volumen, ruta_bd)
        print(f"--- Midiendo operaciones sobre volumen '{nombre_volumen}' ({repeticiones} repeticiones por operación) ---")
        resultados_por_volumen[nombre_volumen] = medir_operaciones(ruta_bd, repeticiones)

    ruta_informe = _escribir_informe(carpeta_salida, resultados_por_volumen, resumenes_poblado, repeticiones)
    print(f"Informe escrito en: {ruta_informe}")
    return ruta_informe


def _escribir_informe(carpeta_salida: str, resultados_por_volumen: dict, resumenes_poblado: dict, repeticiones: int) -> str:
    from utils.poblar_carga import VOLUMENES

    orden_volumenes = list(VOLUMENES)
    nombres_operacion = list(next(iter(resultados_por_volumen.values())).keys())

    lineas = [
        "# Tiempos de respuesta por operación — prueba de saturación",
        "",
        "Mide cada operación de negocio por separado (no toda la pantalla), usando los "
        "controladores reales, sobre tres volúmenes de datos de fondo. El objetivo es poder "
        "ver si una operación se vuelve más lenta a medida que la base de datos "
        "crece (\"saturación\"), y no solo un promedio global.",
        "",
        f"Equipo: {_info_equipo()}",
        f"Repeticiones por operación y por volumen: {repeticiones}",
        "",
        "## Volúmenes de fondo usados",
        "",
        "| Volumen | Usuarios | Cursos | Resultados de evaluación | Tiempo en generarlo (s) |",
        "|---|---|---|---|---|",
    ]
    for nombre_volumen in orden_volumenes:
        resumen = resumenes_poblado[nombre_volumen]
        lineas.append(
            f"| {nombre_volumen} | {resumen['usuarios']} | {resumen['cursos']} | "
            f"{resumen['resultados']} | {resumen['segundos']} |"
        )

    lineas += [
        "",
        "## Tiempos por operación (milisegundos)",
        "",
        "Cada celda es `mediana / P95 / máximo` en ms, sobre las repeticiones indicadas arriba. "
        "La mediana muestra el caso típico; el P95 y el máximo muestran el peor caso real que "
        "puede encontrar un usuario.",
        "",
    ]

    encabezado = "| Operación | " + " | ".join(f"{v} (mediana / P95 / máx)" for v in orden_volumenes) + " |"
    separador = "|---|" + "---|" * len(orden_volumenes)
    lineas += [encabezado, separador]
    for nombre_operacion in nombres_operacion:
        celdas = []
        for nombre_volumen in orden_volumenes:
            r = resultados_por_volumen[nombre_volumen][nombre_operacion]
            celdas.append(f"{r['mediana_ms']} / {r['p95_ms']} / {r['max_ms']}")
        lineas.append(f"| {nombre_operacion} | " + " | ".join(celdas) + " |")

    lineas += [
        "",
        "## Detalle estadístico completo por operación y volumen",
        "",
    ]
    for nombre_operacion in nombres_operacion:
        lineas.append(f"### {nombre_operacion}")
        lineas.append("")
        lineas.append("| Volumen | n | Mín | Media | Mediana | P90 | P95 | P99 | Máx | Desv. estándar |")
        lineas.append("|---|---|---|---|---|---|---|---|---|---|")
        for nombre_volumen in orden_volumenes:
            r = resultados_por_volumen[nombre_volumen][nombre_operacion]
            lineas.append(
                f"| {nombre_volumen} | {r['n']} | {r['min_ms']} | {r['media_ms']} | {r['mediana_ms']} | "
                f"{r['p90_ms']} | {r['p95_ms']} | {r['p99_ms']} | {r['max_ms']} | {r['desvest_ms']} |"
            )
        lineas.append("")

    ruta_informe = os.path.join(carpeta_salida, "INFORME_TIEMPOS_OPERACIONES.md")
    with open(ruta_informe, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas) + "\n")
    return ruta_informe


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Uso: py -m utils.medir_tiempos_operaciones <carpeta_salida> [repeticiones]")
        sys.exit(2)
    reps = int(sys.argv[2]) if len(sys.argv) == 3 else REPETICIONES_POR_DEFECTO
    ejecutar_para_todos_los_volumenes(sys.argv[1], reps)
