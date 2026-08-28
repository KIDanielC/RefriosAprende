"""Controlador de Matrícula: asigna y consulta qué aprendices están inscritos en cada curso."""
from model.dao.inscripcion_dao import InscripcionDAO
from model.dao.usuario_dao import UsuarioDAO
from model.entities.curso import Curso
from model.entities.usuario import Usuario


class InscripcionController:
    def __init__(self):
        self._inscripcion_dao = InscripcionDAO()
        self._usuario_dao = UsuarioDAO()

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

    def matricular(self, id_usuario: int, id_curso: int) -> None:
        self._inscripcion_dao.matricular(id_usuario, id_curso)

    def desmatricular(self, id_usuario: int, id_curso: int) -> None:
        self._inscripcion_dao.desmatricular(id_usuario, id_curso)
