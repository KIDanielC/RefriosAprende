"""Controlador de Reportes: agrega datos de cursos, matrícula, progreso y resultados para el administrador."""
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from model.dao.inscripcion_dao import InscripcionDAO
from model.dao.progreso_dao import ProgresoDAO
from model.dao.resultado_dao import ResultadoDAO
from model.dao.usuario_dao import UsuarioDAO


class ReporteController:
    def __init__(self):
        self._curso_controlador = CursoController()
        self._evaluacion_controlador = EvaluacionController()
        self._inscripcion_dao = InscripcionDAO()
        self._progreso_dao = ProgresoDAO()
        self._resultado_dao = ResultadoDAO()
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
