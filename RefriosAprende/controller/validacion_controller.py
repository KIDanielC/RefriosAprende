"""Controlador de preguntas de opción múltiple para validar el conocimiento de un contenido puntual.

No es el módulo formal de Evaluaciones (Sprint 3): estas preguntas son cuestionarios cortos
de refuerzo por contenido, sin nota mínima ni intentos. Internamente reutilizan las tablas
evaluaciones/preguntas/opciones, pero ese detalle no se expone a la Vista.
"""
from model.dao.evaluacion_dao import EvaluacionDAO
from model.dao.opcion_dao import OpcionDAO
from model.dao.pregunta_dao import PreguntaDAO
from model.entities.contenido import Contenido
from model.entities.pregunta import Pregunta

_MINIMO_OPCIONES = 2
_MAXIMO_OPCIONES = 4


class DatosPreguntaInvalidosError(Exception):
    """Los datos de la pregunta o sus opciones no cumplen las reglas de negocio."""


class ValidacionController:
    def __init__(self):
        self._evaluacion_dao = EvaluacionDAO()
        self._pregunta_dao = PreguntaDAO()
        self._opcion_dao = OpcionDAO()

    def listar_preguntas(self, contenido: Contenido) -> list[Pregunta]:
        evaluacion = self._evaluacion_dao.obtener_por_contenido(contenido.id_contenido)
        if evaluacion is None:
            return []
        return self._pregunta_dao.listar_por_evaluacion(evaluacion.id_evaluacion)

    def _validar_opciones(self, opciones: list[tuple[str, bool]]):
        opciones_con_texto = [(texto.strip(), es_correcta) for texto, es_correcta in opciones if texto.strip()]

        if len(opciones_con_texto) < _MINIMO_OPCIONES:
            raise DatosPreguntaInvalidosError(f"Debes ingresar al menos {_MINIMO_OPCIONES} opciones de respuesta.")
        if len(opciones_con_texto) > _MAXIMO_OPCIONES:
            raise DatosPreguntaInvalidosError(f"No puedes ingresar más de {_MAXIMO_OPCIONES} opciones de respuesta.")

        total_correctas = sum(1 for _, es_correcta in opciones_con_texto if es_correcta)
        if total_correctas != 1:
            raise DatosPreguntaInvalidosError("Debes marcar exactamente una opción como correcta.")

        return opciones_con_texto

    def crear_pregunta(
        self, contenido: Contenido, enunciado: str, opciones: list[tuple[str, bool]]
    ) -> Pregunta:
        if not enunciado or len(enunciado.strip()) < 5:
            raise DatosPreguntaInvalidosError("El enunciado debe tener al menos 5 caracteres.")
        opciones_validas = self._validar_opciones(opciones)

        evaluacion = self._evaluacion_dao.obtener_o_crear_para_contenido(
            contenido.id_curso, contenido.id_contenido, f"Validación de: {contenido.titulo}"
        )
        orden = self._pregunta_dao.obtener_siguiente_orden(evaluacion.id_evaluacion)
        id_pregunta = self._pregunta_dao.crear(evaluacion.id_evaluacion, enunciado.strip(), orden)

        for texto_opcion, es_correcta in opciones_validas:
            self._opcion_dao.crear(id_pregunta, texto_opcion, es_correcta)

        return self._pregunta_dao.obtener_por_id(id_pregunta)

    def actualizar_pregunta(
        self, id_pregunta: int, enunciado: str, opciones: list[tuple[str, bool]]
    ) -> Pregunta:
        if not enunciado or len(enunciado.strip()) < 5:
            raise DatosPreguntaInvalidosError("El enunciado debe tener al menos 5 caracteres.")
        opciones_validas = self._validar_opciones(opciones)

        self._pregunta_dao.actualizar_enunciado(id_pregunta, enunciado.strip())
        self._opcion_dao.eliminar_por_pregunta(id_pregunta)
        for texto_opcion, es_correcta in opciones_validas:
            self._opcion_dao.crear(id_pregunta, texto_opcion, es_correcta)

        return self._pregunta_dao.obtener_por_id(id_pregunta)

    def eliminar_pregunta(self, id_pregunta: int) -> None:
        self._pregunta_dao.eliminar(id_pregunta)
