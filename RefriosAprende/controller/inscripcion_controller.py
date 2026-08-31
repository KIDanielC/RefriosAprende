"""Controlador de Matrícula: asigna y consulta qué aprendices están inscritos en cada curso."""
from model.dao.inscripcion_dao import InscripcionDAO
from model.dao.prerrequisito_dao import PrerrequisitoDAO
from model.dao.progreso_dao import ProgresoDAO
from model.dao.usuario_dao import UsuarioDAO
from model.entities.curso import Curso
from model.entities.progreso import COMPLETADO
from model.entities.usuario import Usuario


class PrerrequisitosIncompletosError(Exception):
    """El aprendiz todavía no ha completado uno o más cursos que son prerrequisito."""


class InscripcionController:
    def __init__(self):
        self._inscripcion_dao = InscripcionDAO()
        self._usuario_dao = UsuarioDAO()
        self._prerrequisito_dao = PrerrequisitoDAO()
        self._progreso_dao = ProgresoDAO()

    def listar_aprendices_matriculados(self, id_curso: int) -> list[Usuario]:
        return self._inscripcion_dao.listar_usuarios_matriculados(id_curso)

    def listar_aprendices_disponibles(self, id_curso: int) -> list[Usuario]:
        """Aprendices activos que todavía no están matriculados en este curso."""
        matriculados = {u.id_usuario for u in self._inscripcion_dao.listar_usuarios_matriculados(id_curso)}
        return [
            u for u in self._usuario_dao.listar_todos()
            if not u.es_administrador() and u.activo and u.id_usuario not in matriculados
        ]

    def listar_cursos_matriculados(self, id_usuario: int) -> list[Curso]:
        return [c for c in self._inscripcion_dao.listar_cursos_matriculados(id_usuario) if c.esta_activo()]

    def contar_matriculados(self, id_curso: int) -> int:
        return self._inscripcion_dao.contar_matriculados(id_curso)

    def prerrequisitos_pendientes(self, id_usuario: int, id_curso: int) -> list[Curso]:
        """Prerrequisitos de id_curso que el usuario todavía no ha completado."""
        pendientes = []
        for prerrequisito in self._prerrequisito_dao.listar_prerrequisitos(id_curso):
            progreso = self._progreso_dao.obtener_por_usuario_y_curso(id_usuario, prerrequisito.id_curso)
            if progreso is None or progreso.estado != COMPLETADO:
                pendientes.append(prerrequisito)
        return pendientes

    def matricular(self, id_usuario: int, id_curso: int) -> None:
        pendientes = self.prerrequisitos_pendientes(id_usuario, id_curso)
        if pendientes:
            nombres = ", ".join(curso.nombre_curso for curso in pendientes)
            raise PrerrequisitosIncompletosError(
                f"Este aprendiz todavía no ha completado el/los curso(s) prerrequisito: {nombres}."
            )
        self._inscripcion_dao.matricular(id_usuario, id_curso)

    def desmatricular(self, id_usuario: int, id_curso: int) -> None:
        self._inscripcion_dao.desmatricular(id_usuario, id_curso)
