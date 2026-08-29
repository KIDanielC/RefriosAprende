import pytest

from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import DatosGuiaInvalidosError, GuiaAprendizajeController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.reporte_controller import ReporteController
from controller.contenido_controller import ContenidoController


def test_curso_sin_guia_devuelve_none(curso):
    gc = GuiaAprendizajeController()
    assert gc.obtener_guia(curso.id_curso) is None


def test_guardar_guia_valida(curso):
    gc = GuiaAprendizajeController()
    guia = gc.guardar_guia(
        curso.id_curso, "Diagnosticar fallas comunes de A/C automotriz", "1. Identificar fugas.", "Manejo seguro",
        "Practica en taller", "Nota minima 3.5", "12",
    )
    assert guia.objetivo_general == "Diagnosticar fallas comunes de A/C automotriz"
    assert guia.duracion_horas == 12


def test_guardar_guia_objetivo_corto_falla(curso):
    gc = GuiaAprendizajeController()
    with pytest.raises(DatosGuiaInvalidosError):
        gc.guardar_guia(curso.id_curso, "corto", "", "", "", "", "")


def test_guardar_guia_duracion_no_numerica_falla(curso):
    gc = GuiaAprendizajeController()
    with pytest.raises(DatosGuiaInvalidosError):
        gc.guardar_guia(curso.id_curso, "Objetivo general con longitud suficiente", "", "", "", "", "no-es-numero")


def test_guardar_guia_es_upsert(curso):
    gc = GuiaAprendizajeController()
    gc.guardar_guia(curso.id_curso, "Objetivo original con longitud suficiente", "", "", "", "", "")
    actualizada = gc.guardar_guia(curso.id_curso, "Objetivo actualizado con longitud suficiente", "", "", "", "", "")
    assert gc.obtener_guia(curso.id_curso).objetivo_general == actualizada.objetivo_general == "Objetivo actualizado con longitud suficiente"


def test_reporte_resumen_general_curso_vacio(curso):
    rc = ReporteController()
    resumen = rc.resumen_general()
    assert resumen["total_cursos_activos"] >= 1
    assert resumen["progreso_promedio_general"] == 0.0
    assert resumen["porcentaje_aprobacion"] == 0.0


def test_reporte_detalle_refleja_matricula_real(curso, aprendiz):
    ic = InscripcionController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)

    rc = ReporteController()
    fila = next(f for f in rc.detalle_por_curso() if f["nombre_curso"] == curso.nombre_curso)
    assert fila["aprendices_inscritos"] == 1
    assert fila["progreso_promedio"] == 0.0


def test_reporte_detalle_con_avance_y_aprobacion(curso, aprendiz):
    ic = InscripcionController()
    ctrl = ContenidoController()
    pc = ProgresoController()
    ec = EvaluacionController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    contenido = ctrl.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)

    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2)
    pregunta = ec.crear_pregunta(evaluacion.id_evaluacion, "¿Pregunta?", [("Correcta", True), ("Incorrecta", False)])
    ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: pregunta.opcion_correcta().id_opcion})

    rc = ReporteController()
    fila = next(f for f in rc.detalle_por_curso() if f["nombre_curso"] == curso.nombre_curso)
    assert fila["aprendices_inscritos"] == 1
    assert fila["progreso_promedio"] == 100.0
    assert fila["evaluaciones_presentadas"] == 1
    assert fila["porcentaje_aprobacion"] == 100.0
