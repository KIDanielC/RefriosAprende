import pytest

from controller.evaluacion_controller import (
    DatosEvaluacionInvalidosError,
    EvaluacionController,
    IntentosAgotadosError,
)


def test_crear_evaluacion_final(curso):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.5, 2)
    assert evaluacion.nota_minima_aprobar == 3.5
    assert evaluacion.intentos_permitidos == 2


def test_no_permite_dos_evaluaciones_finales_por_curso(curso):
    ec = EvaluacionController()
    ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.5, 2)
    with pytest.raises(DatosEvaluacionInvalidosError):
        ec.crear_evaluacion_final(curso.id_curso, "Otra evaluacion", 3.0, 1)


@pytest.mark.parametrize("nota_minima,intentos", [(-1, 2), (6, 2), (3.0, 0)])
def test_crear_evaluacion_datos_invalidos(curso, nota_minima, intentos):
    ec = EvaluacionController()
    with pytest.raises(DatosEvaluacionInvalidosError):
        ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", nota_minima, intentos)


def _crear_pregunta_con_respuesta_correcta(ec, id_evaluacion):
    pregunta = ec.crear_pregunta(
        id_evaluacion, "¿Cual es la respuesta correcta?",
        [("Correcta", True), ("Incorrecta", False)],
    )
    return pregunta


def test_presentar_evaluacion_aprobado(curso, aprendiz):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2)
    pregunta = _crear_pregunta_con_respuesta_correcta(ec, evaluacion.id_evaluacion)
    id_opcion_correcta = pregunta.opcion_correcta().id_opcion

    resultado = ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})
    assert resultado.aprobado is True
    assert resultado.nota_obtenida == 5.0


def test_presentar_evaluacion_reprobado(curso, aprendiz):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2)
    pregunta = _crear_pregunta_con_respuesta_correcta(ec, evaluacion.id_evaluacion)
    opcion_incorrecta = next(o for o in pregunta.opciones if not o.es_correcta)

    resultado = ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: opcion_incorrecta.id_opcion})
    assert resultado.aprobado is False
    assert resultado.nota_obtenida == 0.0


def test_intentos_agotados(curso, aprendiz):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 1)
    pregunta = _crear_pregunta_con_respuesta_correcta(ec, evaluacion.id_evaluacion)
    id_opcion_correcta = pregunta.opcion_correcta().id_opcion

    ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})
    with pytest.raises(IntentosAgotadosError):
        ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})


def test_presentar_evaluacion_sin_preguntas_falla(curso, aprendiz):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2)
    with pytest.raises(DatosEvaluacionInvalidosError):
        ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {})
