"""Controlador de Simulaciones: casos clínicos de diagnóstico con preguntas
de opción múltiple. Es un tipo de evaluación (tipo_evaluacion='SIMULACION'),
sin límite de una sola por curso: un curso puede tener varios casos."""
from controller._pregunta_opcion_utils import (
    DatosPreguntaInvalidosError,
    actualizar_pregunta_con_opciones,
    crear_pregunta_con_opciones,
)
from model.dao.evaluacion_dao import EvaluacionDAO
from model.dao.opcion_dao import OpcionDAO
from model.dao.pregunta_dao import PreguntaDAO
from model.dao.resultado_dao import ResultadoDAO
from model.dao.simulacion_dao import SimulacionDAO
from model.entities.evaluacion import Evaluacion
from model.entities.pregunta import Pregunta
from model.entities.resultado import Resultado
from model.entities.simulacion import Simulacion

_NOTA_MAXIMA = 5.0
_NOTA_MINIMA_APROBAR_DEFECTO = 3.0
_INTENTOS_PERMITIDOS_DEFECTO = 3


class DatosSimulacionInvalidosError(Exception):
    """Los datos del caso de simulación no cumplen las reglas de negocio."""


class SimulacionController:
    def __init__(self):
        self._evaluacion_dao = EvaluacionDAO()
        self._simulacion_dao = SimulacionDAO()
        self._pregunta_dao = PreguntaDAO()
        self._opcion_dao = OpcionDAO()
        self._resultado_dao = ResultadoDAO()

    # -- Administración -------------------------------------------------
    def listar_casos_por_curso(self, id_curso: int) -> list[tuple[Evaluacion, Simulacion]]:
        evaluaciones = self._evaluacion_dao.listar_simulaciones_por_curso(id_curso)
        return [(evaluacion, self._simulacion_dao.obtener_por_evaluacion(evaluacion.id_evaluacion)) for evaluacion in evaluaciones]

    def crear_caso(
        self, id_curso: int, titulo_caso: str, descripcion_escenario: str, diagnostico_correcto: str
    ) -> tuple[Evaluacion, Simulacion]:
        self._validar_datos(titulo_caso, descripcion_escenario, diagnostico_correcto)

        id_evaluacion = self._evaluacion_dao.crear_evaluacion_curso(
            id_curso, titulo_caso.strip(), "SIMULACION", _NOTA_MINIMA_APROBAR_DEFECTO, _INTENTOS_PERMITIDOS_DEFECTO
        )
        self._simulacion_dao.crear(id_evaluacion, titulo_caso.strip(), descripcion_escenario.strip(), diagnostico_correcto.strip())

        evaluacion = self._evaluacion_dao.obtener_por_id(id_evaluacion)
        simulacion = self._simulacion_dao.obtener_por_evaluacion(id_evaluacion)
        return evaluacion, simulacion

    def actualizar_caso(
        self, simulacion: Simulacion, titulo_caso: str, descripcion_escenario: str, diagnostico_correcto: str
    ) -> Simulacion:
        self._validar_datos(titulo_caso, descripcion_escenario, diagnostico_correcto)
        self._simulacion_dao.actualizar(simulacion.id_simulacion, titulo_caso.strip(), descripcion_escenario.strip(), diagnostico_correcto.strip())
        self._evaluacion_dao.actualizar_evaluacion_curso(
            simulacion.id_evaluacion, titulo_caso.strip(), _NOTA_MINIMA_APROBAR_DEFECTO, _INTENTOS_PERMITIDOS_DEFECTO
        )
        return self._simulacion_dao.obtener_por_evaluacion(simulacion.id_evaluacion)

    def eliminar_caso(self, id_evaluacion: int) -> None:
        self._evaluacion_dao.eliminar(id_evaluacion)

    def _validar_datos(self, titulo_caso: str, descripcion_escenario: str, diagnostico_correcto: str):
        if not titulo_caso or len(titulo_caso.strip()) < 3:
            raise DatosSimulacionInvalidosError("El título del caso debe tener al menos 3 caracteres.")
        if not descripcion_escenario or len(descripcion_escenario.strip()) < 15:
            raise DatosSimulacionInvalidosError("Describe el escenario clínico con al menos 15 caracteres.")
        if not diagnostico_correcto or len(diagnostico_correcto.strip()) < 3:
            raise DatosSimulacionInvalidosError("Indica el diagnóstico correcto del caso.")

    # -- Preguntas (opción múltiple sobre el caso) ------------------------
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

    def presentar_caso(self, id_usuario: int, evaluacion: Evaluacion, respuestas: dict[int, int]) -> Resultado:
        preguntas = self._pregunta_dao.listar_por_evaluacion(evaluacion.id_evaluacion)
        if not preguntas:
            raise DatosSimulacionInvalidosError("Este caso todavía no tiene preguntas de diagnóstico.")

        correctas = 0
        for pregunta in preguntas:
            id_opcion_seleccionada = respuestas.get(pregunta.id_pregunta)
            opcion_correcta = pregunta.opcion_correcta()
            if id_opcion_seleccionada is not None and opcion_correcta is not None and id_opcion_seleccionada == opcion_correcta.id_opcion:
                correctas += 1

        nota_obtenida = round((correctas / len(preguntas)) * _NOTA_MAXIMA, 2)
        aprobado = nota_obtenida >= evaluacion.nota_minima_aprobar

        self._resultado_dao.crear(id_usuario, evaluacion.id_evaluacion, nota_obtenida, aprobado)

        return Resultado(
            id_resultado=0,
            id_usuario=id_usuario,
            id_evaluacion=evaluacion.id_evaluacion,
            nota_obtenida=nota_obtenida,
            aprobado=aprobado,
            fecha_intento="",
        )
