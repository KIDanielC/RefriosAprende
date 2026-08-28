"""Controlador de gestión de contenidos de un curso (Sprint 2: solo tipo TEXTO)."""
from model.dao.contenido_dao import ContenidoDAO
from model.entities.contenido import Contenido


class DatosContenidoInvalidosError(Exception):
    """Los datos del contenido no cumplen las reglas de negocio."""


class ContenidoController:
    def __init__(self):
        self._contenido_dao = ContenidoDAO()

    def listar_por_curso(self, id_curso: int) -> list[Contenido]:
        return self._contenido_dao.listar_por_curso(id_curso)

    def _validar_datos(self, titulo: str, contenido_texto: str):
        if not titulo or len(titulo.strip()) < 3:
            raise DatosContenidoInvalidosError("El título debe tener al menos 3 caracteres.")
        if not contenido_texto or len(contenido_texto.strip()) < 10:
            raise DatosContenidoInvalidosError("El contenido debe tener al menos 10 caracteres.")

    def crear_contenido(self, id_curso: int, titulo: str, contenido_texto: str) -> Contenido:
        self._validar_datos(titulo, contenido_texto)
        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(id_curso, titulo.strip(), contenido_texto.strip(), orden)
        return self._contenido_dao.obtener_por_id(id_contenido)

    def actualizar_contenido(self, id_contenido: int, titulo: str, contenido_texto: str, orden: int) -> Contenido:
        self._validar_datos(titulo, contenido_texto)
        self._contenido_dao.actualizar(id_contenido, titulo.strip(), contenido_texto.strip(), orden)
        return self._contenido_dao.obtener_por_id(id_contenido)

    def eliminar_contenido(self, id_contenido: int) -> None:
        self._contenido_dao.eliminar(id_contenido)
