import pytest

from controller.simulacion_controller import DatosSimulacionInvalidosError, SimulacionController


def test_crear_caso_simulacion(curso):
    sc = SimulacionController()
    evaluacion, simulacion = sc.crear_caso(
        curso.id_curso, "Fuga en valvula", "Escenario clinico detallado de al menos 15 caracteres.", "Fuga de refrigerante"
    )
    assert evaluacion.tipo_evaluacion == "SIMULACION"
    assert simulacion.titulo_caso == "Fuga en valvula"


def test_un_curso_puede_tener_varios_casos(curso):
    sc = SimulacionController()
    sc.crear_caso(curso.id_curso, "Caso uno", "Escenario clinico detallado de al menos 15 caracteres.", "Diagnostico uno")
    sc.crear_caso(curso.id_curso, "Caso dos", "Escenario clinico detallado de al menos 15 caracteres.", "Diagnostico dos")
    assert len(sc.listar_casos_por_curso(curso.id_curso)) == 2


def test_crear_caso_escenario_muy_corto_falla(curso):
    sc = SimulacionController()
    with pytest.raises(DatosSimulacionInvalidosError):
        sc.crear_caso(curso.id_curso, "Caso", "corto", "Diagnostico")


def test_presentar_caso_simulacion(curso, aprendiz):
    sc = SimulacionController()
    evaluacion, _simulacion = sc.crear_caso(
        curso.id_curso, "Caso", "Escenario clinico detallado de al menos 15 caracteres.", "Diagnostico correcto"
    )
    pregunta = sc.crear_pregunta(
        evaluacion.id_evaluacion, "¿Cual es el diagnostico?", [("Correcto", True), ("Incorrecto", False)]
    )
    id_opcion_correcta = pregunta.opcion_correcta().id_opcion

    resultado = sc.presentar_caso(aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta})
    assert resultado.aprobado is True


def test_presentar_caso_sin_preguntas_falla(curso, aprendiz):
    sc = SimulacionController()
    evaluacion, _simulacion = sc.crear_caso(
        curso.id_curso, "Caso", "Escenario clinico detallado de al menos 15 caracteres.", "Diagnostico correcto"
    )
    with pytest.raises(DatosSimulacionInvalidosError):
        sc.presentar_caso(aprendiz.id_usuario, evaluacion, {})
