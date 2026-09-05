import pytest

from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import CAMPOS_TEXTO_GUIA, DatosGuiaInvalidosError, GuiaAprendizajeController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.reporte_controller import ReporteController
from controller.contenido_controller import ContenidoController
from controller.simulacion_controller import SimulacionController


def test_curso_sin_guia_devuelve_none(curso):
    gc = GuiaAprendizajeController()
    assert gc.obtener_guia(curso.id_curso) is None


def test_guardar_guia_valida(curso):
    gc = GuiaAprendizajeController()
    campos = {"objetivo_general": "Diagnosticar fallas comunes de A/C automotriz", "criterios_evaluacion": "Nota mínima 3.5"}
    guia = gc.guardar_guia(curso.id_curso, campos, "12")
    assert guia.objetivo_general == "Diagnosticar fallas comunes de A/C automotriz"
    assert guia.criterios_evaluacion == "Nota mínima 3.5"
    assert guia.duracion_horas == 12


def test_guardar_guia_objetivo_corto_falla(curso):
    gc = GuiaAprendizajeController()
    with pytest.raises(DatosGuiaInvalidosError):
        gc.guardar_guia(curso.id_curso, {"objetivo_general": "corto"}, "")


def test_guardar_guia_duracion_no_numerica_falla(curso):
    gc = GuiaAprendizajeController()
    campos = {"objetivo_general": "Objetivo general con longitud suficiente"}
    with pytest.raises(DatosGuiaInvalidosError):
        gc.guardar_guia(curso.id_curso, campos, "no-es-numero")


def test_guardar_guia_es_upsert(curso):
    gc = GuiaAprendizajeController()
    gc.guardar_guia(curso.id_curso, {"objetivo_general": "Objetivo original con longitud suficiente"}, "")
    actualizada = gc.guardar_guia(curso.id_curso, {"objetivo_general": "Objetivo actualizado con longitud suficiente"}, "")
    assert gc.obtener_guia(curso.id_curso).objetivo_general == actualizada.objetivo_general == "Objetivo actualizado con longitud suficiente"


def test_guardar_guia_con_todas_las_secciones_nuevas(curso):
    gc = GuiaAprendizajeController()
    campos = {clave: f"Texto de prueba para {clave}" for clave in CAMPOS_TEXTO_GUIA}
    guia = gc.guardar_guia(curso.id_curso, campos, "8")
    for clave in CAMPOS_TEXTO_GUIA:
        assert getattr(guia, clave) == f"Texto de prueba para {clave}"


def test_guardar_guia_campos_faltantes_en_dict_no_falla(curso):
    """El instructor debe poder guardar solo el objetivo general y completar el resto después."""
    gc = GuiaAprendizajeController()
    guia = gc.guardar_guia(curso.id_curso, {"objetivo_general": "Objetivo general con longitud suficiente"}, "")
    assert guia.objetivo_general == "Objetivo general con longitud suficiente"
    for clave in CAMPOS_TEXTO_GUIA:
        if clave != "objetivo_general":
            assert getattr(guia, clave) == ""


def test_secciones_computadas_reflejan_datos_reales(curso, aprendiz):
    """Lo que la ventana de guía muestra en sus tarjetas computadas (Contenido teórico,
    Simulación, Evaluación) debe venir de los controladores reales, no de texto libre."""
    contenido_controlador = ContenidoController()
    simulacion_controlador = SimulacionController()
    evaluacion_controlador = EvaluacionController()

    contenido = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Propiedades del refrigerante", "Texto con longitud suficiente para pasar la validación."
    )
    _evaluacion_caso, simulacion = simulacion_controlador.crear_caso(
        curso.id_curso, "Fuga en válvula", "Escenario clínico detallado de al menos 15 caracteres.", "Fuga de refrigerante"
    )
    evaluacion_final = evaluacion_controlador.crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.5, 2)

    assert contenido.id_contenido in [c.id_contenido for c in contenido_controlador.listar_por_curso(curso.id_curso)]
    assert any(s.titulo_caso == "Fuga en válvula" for _e, s in simulacion_controlador.listar_casos_por_curso(curso.id_curso))
    assert evaluacion_controlador.obtener_evaluacion_final(curso.id_curso).titulo == "Evaluación final"


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
