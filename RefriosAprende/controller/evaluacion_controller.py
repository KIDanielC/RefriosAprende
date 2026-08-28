"""Controlador de la evaluación final de un curso: preguntas de opción múltiple,
nota mínima e intentos permitidos, y presentación por parte del aprendiz."""
from controller._pregunta_opcion_utils import (
    DatosPreguntaInvalidosError,
    actualizar_pregunta_con_opciones,
    crear_pregunta_con_opciones,
)
from controller.progreso_controller import ProgresoController
from model.dao.evaluacion_dao import EvaluacionDAO
from model.dao.opcion_dao import OpcionDAO
from model.dao.pregunta_dao import PreguntaDAO
from model.dao.resultado_dao import ResultadoDAO
from model.entities.evaluacion import Evaluacion
from model.entities.pregunta import Pregunta
from model.entities.resultado import Resultado

_NOTA_MAXIMA = 5.0


class DatosEvaluacionInvalidosError(Exception):
    """Los datos de la evaluación no cumplen las reglas de negocio."""


class IntentosAgotadosError(Exception):
    """El aprendiz ya usó todos los intentos permitidos para esta evaluación."""


class EvaluacionController:
    def __init__(self):
        self._evaluacion_dao = EvaluacionDAO()
        self._pregunta_dao = PreguntaDAO()
        self._opcion_dao = OpcionDAO()
        self._resultado_dao = ResultadoDAO()
        self._progreso_controlador = ProgresoController()

    # -- Administración -------------------------------------------------
    def obtener_evaluacion_final(self, id_curso: int) -> Evaluacion | None:
        return self._evaluacion_dao.obtener_evaluacion_final_por_curso(id_curso)

    def crear_evaluacion_final(
        self, id_curso: int, titulo: str, nota_minima_aprobar: float, intentos_permitidos: int
    ) -> Evaluacion:
        self._validar_datos(titulo, nota_minima_aprobar, intentos_permitidos)
        if self._evaluacion_dao.obtener_evaluacion_final_por_curso(id_curso) is not None:
            raise DatosEvaluacionInvalidosError("Este curso ya tiene una evaluación final. Edítala en vez de crear otra.")

        id_evaluacion = self._evaluacion_dao.crear_evaluacion_curso(
            id_curso, titulo.strip(), "CUESTIONARIO", nota_minima_aprobar, intentos_permitidos
        )
        return self._evaluacion_dao.obtener_por_id(id_evaluacion)

    def actualizar_evaluacion_final(
        self, id_evaluacion: int, titulo: str, nota_minima_aprobar: float, intentos_permitidos: int
    ) -> Evaluacion:
        self._validar_datos(titulo, nota_minima_aprobar, intentos_permitidos)
        self._evaluacion_dao.actualizar_evaluacion_curso(id_evaluacion, titulo.strip(), nota_minima_aprobar, intentos_permitidos)
        return self._evaluacion_dao.obtener_por_id(id_evaluacion)

    def eliminar_evaluacion_final(self, id_evaluacion: int) -> None:
        self._evaluacion_dao.eliminar(id_evaluacion)

    def _validar_datos(self, titulo: str, nota_minima_aprobar: float, intentos_permitidos: int):
        if not titulo or len(titulo.strip()) < 3:
            raise DatosEvaluacionInvalidosError("El título debe tener al menos 3 caracteres.")
        if not (0 < nota_minima_aprobar <= _NOTA_MAXIMA):
            raise DatosEvaluacionInvalidosError(f"La nota mínima debe estar entre 0 y {_NOTA_MAXIMA:.0f}.")
        if intentos_permitidos < 1:
            raise DatosEvaluacionInvalidosError("Los intentos permitidos deben ser al menos 1.")

    # -- Preguntas --------------------------------------------------------
    def listar_preguntas(self, id_evaluacion: int) -> list[Pregunta]:
        return self._pregunta_dao.listar_por_evaluacion(id_evaluacion)

    def crear_pregunta(self, id_evaluacion: int, enunciado: str, opciones: list[tuple[str, bool]]) -> Pregunta:
        return crear_pregunta_con_opciones(self._pregunta_dao, self._opcion_dao, id_evaluacion, enunciado, opciones)

    def actualizar_pregunta(self, id_pregunta: int, enunciado: str, opciones: list[tuple[str, bool]]) -> Pregunta:
        return actualizar_pregunta_con_opciones(self._pregunta_dao, self._opcion_dao, id_pregunta, enunciado, opciones)

    def eliminar_pregunta(self, id_pregunta: int) -> None:
        self._pregunta_dao.eliminar(id_pregunta)

    # -- Presentación (Aprendiz) -------------------------------------------
    def intentos_usados(self, id_usuario: int, id_evaluacion: int) -> int:
        return len(self._resultado_dao.listar_por_usuario_y_evaluacion(id_usuario, id_evaluacion))

    def presentar_evaluacion(
        self, id_usuario: int, evaluacion: Evaluacion, respuestas: dict[int, int]
    ) -> Resultado:
        """respuestas: {id_pregunta: id_opcion_seleccionada}"""
        if self.intentos_usados(id_usuario, evaluacion.id_evaluacion) >= evaluacion.intentos_permitidos:
            raise IntentosAgotadosError("Ya usaste todos los intentos permitidos para esta evaluación.")

        preguntas = self._pregunta_dao.listar_por_evaluacion(evaluacion.id_evaluacion)
        if not preguntas:
            raise DatosEvaluacionInvalidosError("Esta evaluación todavía no tiene preguntas.")

        correctas = 0
        for pregunta in preguntas:
            id_opcion_seleccionada = respuestas.get(pregunta.id_pregunta)
            opcion_correcta = pregunta.opcion_correcta()
            if id_opcion_seleccionada is not None and opcion_correcta is not None and id_opcion_seleccionada == opcion_correcta.id_opcion:
                correctas += 1

        nota_obtenida = round((correctas / len(preguntas)) * _NOTA_MAXIMA, 2)
        aprobado = nota_obtenida >= evaluacion.nota_minima_aprobar

        self._resultado_dao.crear(id_usuario, evaluacion.id_evaluacion, nota_obtenida, aprobado)
        self._progreso_controlador.recalcular_progreso(id_usuario, evaluacion.id_curso)

        return Resultado(
            id_resultado=0,
            id_usuario=id_usuario,
            id_evaluacion=evaluacion.id_evaluacion,
            nota_obtenida=nota_obtenida,
            aprobado=aprobado,
            fecha_intento="",
        )
