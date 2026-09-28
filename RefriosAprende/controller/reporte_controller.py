"""Controlador de Reportes: agrega datos de cursos, matrícula, progreso y resultados para el administrador."""
from datetime import datetime

from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from model.dao.inscripcion_dao import InscripcionDAO
from model.dao.progreso_dao import ProgresoDAO
from model.dao.resultado_dao import ResultadoDAO
from model.dao.tiempo_uso_curso_dao import TiempoUsoCursoDAO
from model.dao.usuario_dao import UsuarioDAO
from model.entities.progreso import COMPLETADO

# Un aprendiz se marca "en riesgo" si lleva matriculado más de este número de días con un
# avance menor a este porcentaje (y todavía no completó el curso).
UMBRAL_DIAS_RIESGO = 15
UMBRAL_AVANCE_RIESGO = 30.0

SEMAFORO_VERDE = "VERDE"
SEMAFORO_AMARILLO = "AMARILLO"
SEMAFORO_ROJO = "ROJO"


class ReporteController:
    def __init__(self):
        self._curso_controlador = CursoController()
        self._evaluacion_controlador = EvaluacionController()
        self._guia_controlador = GuiaAprendizajeController()
        self._inscripcion_dao = InscripcionDAO()
        self._progreso_dao = ProgresoDAO()
        self._resultado_dao = ResultadoDAO()
        self._tiempo_uso_dao = TiempoUsoCursoDAO()
        self._usuario_dao = UsuarioDAO()

    def resumen_general(self) -> dict:
        cursos_activos = self._curso_controlador.listar_cursos_activos()
        aprendices = [u for u in self._usuario_dao.listar_todos() if not u.es_administrador()]

        total_intentos = 0
        total_aprobados = 0
        porcentajes_avance = []
        for curso in cursos_activos:
            evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
            if evaluacion_final is not None:
                resultados = self._resultado_dao.listar_por_evaluacion(evaluacion_final.id_evaluacion)
                total_intentos += len(resultados)
                total_aprobados += sum(1 for r in resultados if r.aprobado)
            for progreso in self._progreso_dao.listar_por_curso(curso.id_curso):
                porcentajes_avance.append(progreso.porcentaje_avance)

        return {
            "total_cursos_activos": len(cursos_activos),
            "total_aprendices": len(aprendices),
            "total_evaluaciones_presentadas": total_intentos,
            "porcentaje_aprobacion": (total_aprobados / total_intentos * 100) if total_intentos else 0.0,
            "progreso_promedio_general": (
                sum(porcentajes_avance) / len(porcentajes_avance) if porcentajes_avance else 0.0
            ),
        }

    def detalle_por_curso(self) -> list[dict]:
        filas = []
        for curso in self._curso_controlador.listar_cursos_activos():
            aprendices_inscritos = self._inscripcion_dao.contar_matriculados(curso.id_curso)
            progresos = self._progreso_dao.listar_por_curso(curso.id_curso)
            # Promedio sobre los matriculados: quien aún no ha visto nada cuenta como 0%.
            progreso_promedio = (
                sum(p.porcentaje_avance for p in progresos) / aprendices_inscritos if aprendices_inscritos else 0.0
            )

            evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
            if evaluacion_final is not None:
                resultados = self._resultado_dao.listar_por_evaluacion(evaluacion_final.id_evaluacion)
                intentos = len(resultados)
                aprobados = sum(1 for r in resultados if r.aprobado)
                porcentaje_aprobacion = (aprobados / intentos * 100) if intentos else 0.0
            else:
                intentos = 0
                porcentaje_aprobacion = None

            filas.append({
                "nombre_curso": curso.nombre_curso,
                "aprendices_inscritos": aprendices_inscritos,
                "progreso_promedio": progreso_promedio,
                "evaluaciones_presentadas": intentos,
                "porcentaje_aprobacion": porcentaje_aprobacion,
            })
        return filas

    # -- Seguimiento por estudiante (instructor): riesgo, avance y horas de uso real ---------
    @staticmethod
    def _dias_desde(fecha_texto: str) -> int:
        fecha = datetime.fromisoformat(fecha_texto)
        return max(0, (datetime.now() - fecha).days)

    def avance_por_estudiante(self, id_instructor: int) -> list[dict]:
        """Por cada curso de este instructor y cada aprendiz matriculado: días matriculado,
        % de avance, horas reales acumuladas en el curso vs. la duración estimada de la Guía
        de Aprendizaje, y un semáforo de seguimiento (VERDE/AMARILLO/ROJO)."""
        filas = []
        for curso in self._curso_controlador.listar_cursos_por_instructor(id_instructor):
            if not curso.esta_activo():
                continue
            guia = self._guia_controlador.obtener_guia(curso.id_curso)
            horas_esperadas = guia.duracion_horas if guia and guia.duracion_horas else None

            for aprendiz, fecha_inscripcion in self._inscripcion_dao.listar_matriculas_detalle_por_curso(curso.id_curso):
                progreso = self._progreso_dao.obtener_por_usuario_y_curso(aprendiz.id_usuario, curso.id_curso)
                porcentaje_avance = progreso.porcentaje_avance if progreso else 0.0
                estado_progreso = progreso.estado if progreso else "NO_INICIADO"
                dias_matriculado = self._dias_desde(fecha_inscripcion)
                horas_acumuladas = self._tiempo_uso_dao.horas_por_usuario_y_curso(aprendiz.id_usuario, curso.id_curso)

                en_riesgo = (
                    estado_progreso != COMPLETADO
                    and dias_matriculado > UMBRAL_DIAS_RIESGO
                    and porcentaje_avance < UMBRAL_AVANCE_RIESGO
                )
                if estado_progreso == COMPLETADO:
                    semaforo = SEMAFORO_VERDE
                elif en_riesgo:
                    semaforo = SEMAFORO_ROJO
                elif horas_esperadas and horas_acumuladas < horas_esperadas:
                    semaforo = SEMAFORO_AMARILLO
                else:
                    semaforo = SEMAFORO_VERDE

                filas.append({
                    "nombre_curso": curso.nombre_curso,
                    "nombre_estudiante": aprendiz.nombre_completo,
                    "dias_matriculado": dias_matriculado,
                    "porcentaje_avance": porcentaje_avance,
                    "horas_acumuladas": horas_acumuladas,
                    "horas_esperadas": horas_esperadas,
                    "en_riesgo": en_riesgo,
                    "semaforo": semaforo,
                })
        return filas

    def estudiantes_en_riesgo(self, id_instructor: int) -> list[dict]:
        return [fila for fila in self.avance_por_estudiante(id_instructor) if fila["en_riesgo"]]
