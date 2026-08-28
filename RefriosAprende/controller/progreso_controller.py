"""Controlador de seguimiento: calcula el avance de un aprendiz en un curso.

Regla de negocio: el curso se marca COMPLETADO cuando el aprendiz vio todos sus
contenidos Y (si el curso tiene evaluación final) la aprobó. Si no hay evaluación
final configurada, ver todos los contenidos ya lo completa.
"""
from model.dao.contenido_dao import ContenidoDAO
from model.dao.contenido_visto_dao import ContenidoVistoDAO
from model.dao.evaluacion_dao import EvaluacionDAO
from model.dao.progreso_dao import ProgresoDAO
from model.dao.resultado_dao import ResultadoDAO
from model.entities.progreso import COMPLETADO, EN_PROGRESO, NO_INICIADO, Progreso


class ProgresoController:
    def __init__(self):
        self._contenido_dao = ContenidoDAO()
        self._contenido_visto_dao = ContenidoVistoDAO()
        self._evaluacion_dao = EvaluacionDAO()
        self._resultado_dao = ResultadoDAO()
        self._progreso_dao = ProgresoDAO()

    def registrar_contenido_visto(self, id_usuario: int, contenido) -> Progreso:
        self._contenido_visto_dao.marcar_visto(id_usuario, contenido.id_contenido)
        return self.recalcular_progreso(id_usuario, contenido.id_curso)

    def recalcular_progreso(self, id_usuario: int, id_curso: int) -> Progreso:
        total_contenidos = len(self._contenido_dao.listar_por_curso(id_curso))
        vistos = self._contenido_visto_dao.contar_vistos_de_curso(id_usuario, id_curso)

        if total_contenidos == 0:
            porcentaje = 0.0
        else:
            porcentaje = min(100.0, (vistos / total_contenidos) * 100)

        if vistos == 0:
            estado = NO_INICIADO
        elif total_contenidos > 0 and vistos >= total_contenidos:
            evaluacion_final = self._evaluacion_dao.obtener_evaluacion_final_por_curso(id_curso)
            if evaluacion_final is None or self._resultado_dao.existe_aprobado(id_usuario, evaluacion_final.id_evaluacion):
                estado = COMPLETADO
            else:
                estado = EN_PROGRESO
        else:
            estado = EN_PROGRESO

        return self._progreso_dao.guardar(id_usuario, id_curso, porcentaje, estado)

    def obtener_progreso(self, id_usuario: int, id_curso: int) -> Progreso | None:
        return self._progreso_dao.obtener_por_usuario_y_curso(id_usuario, id_curso)

    def listar_progreso_usuario(self, id_usuario: int) -> list[Progreso]:
        return self._progreso_dao.listar_por_usuario(id_usuario)
