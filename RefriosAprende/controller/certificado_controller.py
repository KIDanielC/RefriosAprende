"""Controlador de Certificado: arma el contenido del certificado de finalización de un
curso para un aprendiz, una vez que su progreso está COMPLETADO."""
from datetime import datetime

from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.progreso_controller import ProgresoController
from model.dao.resultado_dao import ResultadoDAO
from model.entities.progreso import COMPLETADO


class CursoNoCompletadoError(Exception):
    """El aprendiz todavía no ha completado este curso; no se puede emitir certificado."""


class CertificadoController:
    def __init__(self):
        self._progreso_controlador = ProgresoController()
        self._evaluacion_controlador = EvaluacionController()
        self._guia_controlador = GuiaAprendizajeController()
        self._resultado_dao = ResultadoDAO()

    def curso_completado(self, id_usuario: int, id_curso: int) -> bool:
        progreso = self._progreso_controlador.obtener_progreso(id_usuario, id_curso)
        return progreso is not None and progreso.estado == COMPLETADO

    def obtener_datos_certificado(self, usuario, curso) -> dict:
        """Devuelve los datos ya resueltos para mostrar/imprimir el certificado.
        Lanza CursoNoCompletadoError si el progreso todavía no está en COMPLETADO."""
        if not self.curso_completado(usuario.id_usuario, curso.id_curso):
            raise CursoNoCompletadoError("Este curso todavía no está completado por el aprendiz.")

        guia = self._guia_controlador.obtener_guia(curso.id_curso)
        duracion_horas = guia.duracion_horas if guia and guia.duracion_horas else None

        nota_obtenida = None
        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
        if evaluacion_final is not None:
            resultados = self._resultado_dao.listar_por_usuario_y_evaluacion(usuario.id_usuario, evaluacion_final.id_evaluacion)
            aprobados = [r for r in resultados if r.aprobado]
            if aprobados:
                nota_obtenida = max(r.nota_obtenida for r in aprobados)

        return {
            "nombre_aprendiz": usuario.nombre_completo,
            "documento": usuario.documento,
            "nombre_curso": curso.nombre_curso,
            "nombre_instructor": curso.nombre_instructor,
            "duracion_horas": duracion_horas,
            "nota_obtenida": nota_obtenida,
            "fecha_emision": datetime.now().strftime("%d/%m/%Y"),
        }
