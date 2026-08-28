"""Utilidades compartidas para crear/editar preguntas de opción múltiple.
Usadas por los controladores de Evaluaciones y Simulaciones."""
from model.dao.opcion_dao import OpcionDAO
from model.dao.pregunta_dao import PreguntaDAO

MINIMO_OPCIONES = 2
MAXIMO_OPCIONES = 4


class DatosPreguntaInvalidosError(Exception):
    """Los datos de la pregunta o sus opciones no cumplen las reglas de negocio."""


def validar_opciones(opciones: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    opciones_con_texto = [(texto.strip(), es_correcta) for texto, es_correcta in opciones if texto.strip()]

    if len(opciones_con_texto) < MINIMO_OPCIONES:
        raise DatosPreguntaInvalidosError(f"Debes ingresar al menos {MINIMO_OPCIONES} opciones de respuesta.")
    if len(opciones_con_texto) > MAXIMO_OPCIONES:
        raise DatosPreguntaInvalidosError(f"No puedes ingresar más de {MAXIMO_OPCIONES} opciones de respuesta.")

    total_correctas = sum(1 for _, es_correcta in opciones_con_texto if es_correcta)
    if total_correctas != 1:
        raise DatosPreguntaInvalidosError("Debes marcar exactamente una opción como correcta.")

    return opciones_con_texto


def crear_pregunta_con_opciones(
    pregunta_dao: PreguntaDAO, opcion_dao: OpcionDAO, id_evaluacion: int, enunciado: str, opciones: list[tuple[str, bool]]
):
    if not enunciado or len(enunciado.strip()) < 5:
        raise DatosPreguntaInvalidosError("El enunciado debe tener al menos 5 caracteres.")
    opciones_validas = validar_opciones(opciones)

    orden = pregunta_dao.obtener_siguiente_orden(id_evaluacion)
    id_pregunta = pregunta_dao.crear(id_evaluacion, enunciado.strip(), orden)
    for texto_opcion, es_correcta in opciones_validas:
        opcion_dao.crear(id_pregunta, texto_opcion, es_correcta)

    return pregunta_dao.obtener_por_id(id_pregunta)


def actualizar_pregunta_con_opciones(
    pregunta_dao: PreguntaDAO, opcion_dao: OpcionDAO, id_pregunta: int, enunciado: str, opciones: list[tuple[str, bool]]
):
    if not enunciado or len(enunciado.strip()) < 5:
        raise DatosPreguntaInvalidosError("El enunciado debe tener al menos 5 caracteres.")
    opciones_validas = validar_opciones(opciones)

    pregunta_dao.actualizar_enunciado(id_pregunta, enunciado.strip())
    opcion_dao.eliminar_por_pregunta(id_pregunta)
    for texto_opcion, es_correcta in opciones_validas:
        opcion_dao.crear(id_pregunta, texto_opcion, es_correcta)

    return pregunta_dao.obtener_por_id(id_pregunta)
