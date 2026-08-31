"""Controlador de gestión de cursos: valida y coordina Vista <-> Modelo."""
from model.dao.categoria_dao import CategoriaDAO
from model.dao.curso_dao import CursoDAO
from model.dao.prerrequisito_dao import PrerrequisitoDAO
from model.dao.usuario_dao import UsuarioDAO
from model.entities.categoria import Categoria
from model.entities.curso import Curso

_ESTADOS_VALIDOS = ("BORRADOR", "ACTIVO", "INACTIVO")


class DatosCursoInvalidosError(Exception):
    """Los datos del curso no cumplen las reglas de negocio."""


class CursoController:
    def __init__(self):
        self._curso_dao = CursoDAO()
        self._usuario_dao = UsuarioDAO()
        self._categoria_dao = CategoriaDAO()
        self._prerrequisito_dao = PrerrequisitoDAO()

    def listar_cursos(self) -> list[Curso]:
        return self._curso_dao.listar_todos()

    def listar_cursos_activos(self) -> list[Curso]:
        return [curso for curso in self._curso_dao.listar_todos() if curso.esta_activo()]

    def listar_instructores(self):
        return self._usuario_dao.listar_todos()

    def listar_categorias(self) -> list[Categoria]:
        return self._categoria_dao.listar_todas()

    def contar_cursos_activos(self) -> int:
        return self._curso_dao.contar_activos()

    def listar_prerrequisitos(self, id_curso: int) -> list[Curso]:
        return self._prerrequisito_dao.listar_prerrequisitos(id_curso)

    def listar_ids_prerrequisitos(self, id_curso: int) -> list[int]:
        return self._prerrequisito_dao.listar_ids_prerrequisitos(id_curso)

    def guardar_prerrequisitos(self, id_curso: int, ids_prerrequisitos: list[int]) -> None:
        self._prerrequisito_dao.guardar_prerrequisitos(id_curso, ids_prerrequisitos)

    def _validar_datos(self, nombre_curso: str, id_instructor: int):
        if not nombre_curso or len(nombre_curso.strip()) < 3:
            raise DatosCursoInvalidosError("El nombre del curso debe tener al menos 3 caracteres.")
        if self._usuario_dao.obtener_por_id(id_instructor) is None:
            raise DatosCursoInvalidosError("El instructor seleccionado no es válido.")

    def _resolver_categoria(self, nombre_categoria: str) -> int | None:
        nombre_categoria = (nombre_categoria or "").strip()
        if not nombre_categoria:
            return None
        return self._categoria_dao.obtener_o_crear(nombre_categoria).id_categoria

    def crear_curso(
        self, nombre_curso: str, descripcion: str, id_instructor: int,
        nombre_categoria: str = None, aprendizaje_secuencial: bool = False,
    ) -> Curso:
        """Los cursos nuevos siempre inician en estado BORRADOR: el instructor arma el
        contenido sin exponerlo todavía a los aprendices, y lo publica (ACTIVO) cuando
        esté listo, editando el curso."""
        self._validar_datos(nombre_curso, id_instructor)
        id_categoria = self._resolver_categoria(nombre_categoria)
        id_curso = self._curso_dao.crear(
            nombre_curso.strip(), (descripcion or "").strip(), id_instructor, id_categoria, aprendizaje_secuencial
        )
        return self._curso_dao.obtener_por_id(id_curso)

    def actualizar_curso(
        self, id_curso: int, nombre_curso: str, descripcion: str, id_instructor: int, estado: str,
        nombre_categoria: str = None, aprendizaje_secuencial: bool = False,
    ) -> Curso:
        self._validar_datos(nombre_curso, id_instructor)
        if estado not in _ESTADOS_VALIDOS:
            raise DatosCursoInvalidosError("El estado del curso no es válido.")
        id_categoria = self._resolver_categoria(nombre_categoria)
        self._curso_dao.actualizar(
            id_curso, nombre_curso.strip(), (descripcion or "").strip(), id_instructor, estado,
            id_categoria, aprendizaje_secuencial,
        )
        return self._curso_dao.obtener_por_id(id_curso)

    def eliminar_curso(self, id_curso: int) -> None:
        self._curso_dao.eliminar(id_curso)
