"""Controlador de gestión de cursos: valida y coordina Vista <-> Modelo."""
from model.dao.curso_dao import CursoDAO
from model.dao.usuario_dao import UsuarioDAO
from model.entities.curso import Curso

_ESTADOS_VALIDOS = ("ACTIVO", "INACTIVO")


class DatosCursoInvalidosError(Exception):
    """Los datos del curso no cumplen las reglas de negocio."""


class CursoController:
    def __init__(self):
        self._curso_dao = CursoDAO()
        self._usuario_dao = UsuarioDAO()

    def listar_cursos(self) -> list[Curso]:
        return self._curso_dao.listar_todos()

    def listar_cursos_activos(self) -> list[Curso]:
        return [curso for curso in self._curso_dao.listar_todos() if curso.esta_activo()]

    def listar_instructores(self):
        return self._usuario_dao.listar_todos()

    def contar_cursos_activos(self) -> int:
        return self._curso_dao.contar_activos()

    def _validar_datos(self, nombre_curso: str, id_instructor: int):
        if not nombre_curso or len(nombre_curso.strip()) < 3:
            raise DatosCursoInvalidosError("El nombre del curso debe tener al menos 3 caracteres.")
        if self._usuario_dao.obtener_por_id(id_instructor) is None:
            raise DatosCursoInvalidosError("El instructor seleccionado no es válido.")

    def crear_curso(self, nombre_curso: str, descripcion: str, id_instructor: int) -> Curso:
        self._validar_datos(nombre_curso, id_instructor)
        id_curso = self._curso_dao.crear(nombre_curso.strip(), (descripcion or "").strip(), id_instructor)
        return self._curso_dao.obtener_por_id(id_curso)

    def actualizar_curso(
        self, id_curso: int, nombre_curso: str, descripcion: str, id_instructor: int, estado: str
    ) -> Curso:
        self._validar_datos(nombre_curso, id_instructor)
        if estado not in _ESTADOS_VALIDOS:
            raise DatosCursoInvalidosError("El estado del curso no es válido.")
        self._curso_dao.actualizar(id_curso, nombre_curso.strip(), (descripcion or "").strip(), id_instructor, estado)
        return self._curso_dao.obtener_por_id(id_curso)

    def eliminar_curso(self, id_curso: int) -> None:
        self._curso_dao.eliminar(id_curso)
