"""Controlador de seguimiento: calcula el avance de un aprendiz en un curso.

Regla de negocio: el curso se marca COMPLETADO cuando el aprendiz vio todos sus
contenidos Y (si el curso tiene evaluación final) la aprobó. Si no hay evaluación
final configurada, ver todos los contenidos ya lo completa.
"""
from model.dao.contenido_dao import ContenidoDAO
from model.dao.contenido_visto_dao import ContenidoVistoDAO
from model.dao.evaluacion_dao import EvaluacionDAO
from model.dao.inscripcion_dao import InscripcionDAO
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
        self._inscripcion_dao = InscripcionDAO()

    def registrar_contenido_visto(self, id_usuario: int, contenido) -> Progreso:
        self._contenido_visto_dao.marcar_visto(id_usuario, contenido.id_contenido)
        return self.recalcular_progreso(id_usuario, contenido.id_curso)

    def desregistrar_contenido_visto(self, id_usuario: int, contenido) -> Progreso:
        self._contenido_visto_dao.quitar_visto(id_usuario, contenido.id_contenido)
        return self.recalcular_progreso(id_usuario, contenido.id_curso)

    def ya_visto(self, id_usuario: int, contenido) -> bool:
        return self._contenido_visto_dao.fue_visto(id_usuario, contenido.id_contenido)

    def contenido_bloqueado(self, id_usuario: int, contenido, curso) -> bool:
        """Si el curso tiene aprendizaje secuencial activado, un contenido está bloqueado
        hasta que el aprendiz haya visto todos los contenidos de orden anterior."""
        if not curso.aprendizaje_secuencial:
            return False
        anteriores = [
            c for c in self._contenido_dao.listar_por_curso(curso.id_curso) if c.orden < contenido.orden
        ]
        return any(not self._contenido_visto_dao.fue_visto(id_usuario, c.id_contenido) for c in anteriores)

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

    # ------------------------------------------------------------------
    def historial_progreso_aprendiz(self, id_usuario: int) -> list[tuple[str, float]]:
        """Serie (fecha, % acumulado) de avance de un aprendiz, a partir de sus contenidos vistos
        reales en el tiempo. El techo (100%) es la suma de contenidos de sus cursos matriculados."""
        cursos = self._inscripcion_dao.listar_cursos_matriculados(id_usuario)
        total_posible = sum(len(self._contenido_dao.listar_por_curso(c.id_curso)) for c in cursos)
        fechas = self._contenido_visto_dao.listar_fechas_por_usuario(id_usuario)
        return self._acumular_por_fecha(fechas, total_posible)

    def historial_progreso_general(self) -> list[tuple[str, float]]:
        """Serie (fecha, % acumulado) de avance agregado de toda la plataforma, a partir de todos
        los contenidos vistos reales en el tiempo. El techo (100%) es la suma, por cada matrícula
        (usuario, curso), de los contenidos de ese curso."""
        cursor_contenidos = {}

        def contenidos_del_curso(id_curso):
            if id_curso not in cursor_contenidos:
                cursor_contenidos[id_curso] = len(self._contenido_dao.listar_por_curso(id_curso))
            return cursor_contenidos[id_curso]

        total_posible = 0
        for curso in self._obtener_todos_los_cursos_con_matricula():
            total_posible += contenidos_del_curso(curso.id_curso) * self._inscripcion_dao.contar_matriculados(curso.id_curso)

        fechas = self._contenido_visto_dao.listar_fechas_todas()
        return self._acumular_por_fecha(fechas, total_posible)

    def _obtener_todos_los_cursos_con_matricula(self):
        # Mismo criterio de "cursos" que ReporteController: solo cursos activos,
        # para que el histórico de progreso y los reportes del administrador cuadren.
        from controller.curso_controller import CursoController
        return CursoController().listar_cursos_activos()

    def _acumular_por_fecha(self, fechas: list[str], total_posible: int) -> list[tuple[str, float]]:
        if not fechas or total_posible == 0:
            return []

        conteo_por_fecha = {}
        for fecha in fechas:
            conteo_por_fecha[fecha] = conteo_por_fecha.get(fecha, 0) + 1

        serie = []
        acumulado = 0
        for fecha in sorted(conteo_por_fecha.keys()):
            acumulado += conteo_por_fecha[fecha]
            porcentaje = min(100.0, (acumulado / total_posible) * 100)
            serie.append((fecha, porcentaje))
        return serie
