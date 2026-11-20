import pytest

from controller.evaluacion_controller import (
    EvaluacionController,
    DatosEvaluacionInvalidosError,
    IntentosAgotadosError,
)


def test_crear_evaluacion_final(curso, admin):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.5, 2, usuario_actor=admin)
    assert evaluacion.nota_minima_aprobar == 3.5
    assert evaluacion.intentos_permitidos == 2


def test_no_permite_dos_evaluaciones_finales_por_curso(curso, admin):
    ec = EvaluacionController()
    ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.5, 2, usuario_actor=admin)
    with pytest.raises(DatosEvaluacionInvalidosError):
        ec.crear_evaluacion_final(curso.id_curso, "Otra evaluacion", 3.0, 1, usuario_actor=admin)


@pytest.mark.parametrize("nota_minima,intentos", [(-1, 2), (6, 2), (3.0, 0)])
def test_crear_evaluacion_datos_invalidos(curso, admin, nota_minima, intentos):
    ec = EvaluacionController()
    with pytest.raises(DatosEvaluacionInvalidosError):
        ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", nota_minima, intentos, usuario_actor=admin)


def _crear_pregunta_con_respuesta_correcta(ec, id_evaluacion, admin):
    pregunta = ec.crear_pregunta(
        id_evaluacion, "¿Cual es la respuesta correcta?",
        [("Correcta", True), ("Incorrecta", False)], usuario_actor=admin,
    )
    return pregunta


def test_presentar_evaluacion_aprobado(curso, aprendiz, admin):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2, usuario_actor=admin)
    pregunta = _crear_pregunta_con_respuesta_correcta(ec, evaluacion.id_evaluacion, admin)
    id_opcion_correcta = pregunta.opcion_correcta().id_opcion

    resultado = ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})
    assert resultado.aprobado is True
    assert resultado.nota_obtenida == 5.0


def test_presentar_evaluacion_reprobado(curso, aprendiz, admin):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2, usuario_actor=admin)
    pregunta = _crear_pregunta_con_respuesta_correcta(ec, evaluacion.id_evaluacion, admin)
    opcion_incorrecta = next(o for o in pregunta.opciones if not o.es_correcta)

    resultado = ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: opcion_incorrecta.id_opcion})
    assert resultado.aprobado is False
    assert resultado.nota_obtenida == 0.0


def test_intentos_agotados(curso, aprendiz, admin):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 1, usuario_actor=admin)
    pregunta = _crear_pregunta_con_respuesta_correcta(ec, evaluacion.id_evaluacion, admin)
    id_opcion_correcta = pregunta.opcion_correcta().id_opcion

    ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})
    with pytest.raises(IntentosAgotadosError):
        ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})


def test_presentar_evaluacion_sin_preguntas_falla(curso, aprendiz, admin):
    ec = EvaluacionController()
    evaluacion = ec.crear_evaluacion_final(curso.id_curso, "Evaluacion final", 3.0, 2, usuario_actor=admin)
    with pytest.raises(DatosEvaluacionInvalidosError):
        ec.presentar_evaluacion(aprendiz.id_usuario, evaluacion, {})
