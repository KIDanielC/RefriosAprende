import pytest

from controller.contenido_controller import ContenidoController
from controller.validacion_controller import DatosPreguntaInvalidosError, ValidacionController


@pytest.fixture
def contenido(curso):
    return ContenidoController().crear_contenido_texto(
        curso.id_curso, "Contenido con preguntas", "Texto con longitud suficiente para pasar."
    )


def test_contenido_sin_preguntas_al_crear(contenido):
    vc = ValidacionController()
    assert vc.listar_preguntas(contenido) == []


def test_crear_pregunta_de_validacion(contenido):
    vc = ValidacionController()
    pregunta = vc.crear_pregunta(contenido, "¿Cual es la presion correcta?", [("25 PSI", True), ("100 PSI", False)])
    assert pregunta.opcion_correcta().texto_opcion == "25 PSI"
    assert len(vc.listar_preguntas(contenido)) == 1


def test_crear_pregunta_sin_opcion_correcta_falla(contenido):
    vc = ValidacionController()
    with pytest.raises(DatosPreguntaInvalidosError):
        vc.crear_pregunta(contenido, "¿Pregunta valida?", [("Opcion A", False), ("Opcion B", False)])


def test_crear_pregunta_con_dos_correctas_falla(contenido):
    vc = ValidacionController()
    with pytest.raises(DatosPreguntaInvalidosError):
        vc.crear_pregunta(contenido, "¿Pregunta valida?", [("Opcion A", True), ("Opcion B", True)])


def test_crear_pregunta_una_sola_opcion_falla(contenido):
    vc = ValidacionController()
    with pytest.raises(DatosPreguntaInvalidosError):
        vc.crear_pregunta(contenido, "¿Pregunta valida?", [("Unica opcion", True)])
