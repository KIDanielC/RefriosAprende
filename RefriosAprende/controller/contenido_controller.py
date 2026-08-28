"""Controlador de gestión de contenidos de un curso (tipo TEXTO, PDF o IMAGEN)."""
import os
import shutil
import uuid

from config.settings import CONTENIDOS_DIR
from model.dao.contenido_dao import ContenidoDAO
from model.entities.contenido import Contenido

TIPO_TEXTO = "TEXTO"
TIPO_PDF = "PDF"
TIPO_IMAGEN = "IMAGEN"

_EXTENSIONES_IMAGEN = (".png", ".jpg", ".jpeg", ".gif", ".bmp")


class DatosContenidoInvalidosError(Exception):
    """Los datos del contenido no cumplen las reglas de negocio."""


class ContenidoController:
    def __init__(self):
        self._contenido_dao = ContenidoDAO()

    def listar_por_curso(self, id_curso: int) -> list[Contenido]:
        return self._contenido_dao.listar_por_curso(id_curso)

    def _validar_titulo(self, titulo: str):
        if not titulo or len(titulo.strip()) < 3:
            raise DatosContenidoInvalidosError("El título debe tener al menos 3 caracteres.")

    # -- Contenido de tipo TEXTO -----------------------------------------
    def crear_contenido_texto(self, id_curso: int, titulo: str, contenido_texto: str) -> Contenido:
        self._validar_titulo(titulo)
        if not contenido_texto or len(contenido_texto.strip()) < 10:
            raise DatosContenidoInvalidosError("El contenido debe tener al menos 10 caracteres.")

        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_TEXTO, None, contenido_texto.strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    # -- Contenido de tipo PDF --------------------------------------------
    def crear_contenido_pdf(self, id_curso: int, titulo: str, descripcion: str, ruta_pdf_origen: str) -> Contenido:
        self._validar_titulo(titulo)
        if not ruta_pdf_origen or not os.path.isfile(ruta_pdf_origen):
            raise DatosContenidoInvalidosError("Selecciona un archivo PDF válido.")
        if not ruta_pdf_origen.lower().endswith(".pdf"):
            raise DatosContenidoInvalidosError("El archivo seleccionado debe ser un PDF.")

        ruta_relativa = self._copiar_archivo_a_recursos(ruta_pdf_origen, ".pdf")
        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_PDF, ruta_relativa, (descripcion or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    # -- Contenido de tipo IMAGEN ------------------------------------------
    def crear_contenido_imagen(self, id_curso: int, titulo: str, descripcion: str, ruta_imagen_origen: str) -> Contenido:
        self._validar_titulo(titulo)
        if not ruta_imagen_origen or not os.path.isfile(ruta_imagen_origen):
            raise DatosContenidoInvalidosError("Selecciona un archivo de imagen válido.")
        extension = os.path.splitext(ruta_imagen_origen)[1].lower()
        if extension not in _EXTENSIONES_IMAGEN:
            raise DatosContenidoInvalidosError("La imagen debe ser PNG, JPG, JPEG, GIF o BMP.")

        ruta_relativa = self._copiar_archivo_a_recursos(ruta_imagen_origen, extension)
        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_IMAGEN, ruta_relativa, (descripcion or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    def _copiar_archivo_a_recursos(self, ruta_origen: str, extension: str) -> str:
        os.makedirs(CONTENIDOS_DIR, exist_ok=True)
        nombre_unico = f"{uuid.uuid4().hex}{extension}"
        destino = os.path.join(CONTENIDOS_DIR, nombre_unico)
        shutil.copyfile(ruta_origen, destino)
        return os.path.join("resources", "contenidos", nombre_unico)

    # -- Comunes ------------------------------------------------------------
    def actualizar_contenido(self, id_contenido: int, titulo: str, contenido_texto: str, orden: int) -> Contenido:
        self._validar_titulo(titulo)

        contenido_existente = self._contenido_dao.obtener_por_id(id_contenido)
        if contenido_existente is None:
            raise DatosContenidoInvalidosError("El contenido ya no existe.")

        if contenido_existente.tipo_contenido == TIPO_TEXTO and (not contenido_texto or len(contenido_texto.strip()) < 10):
            raise DatosContenidoInvalidosError("El contenido debe tener al menos 10 caracteres.")

        self._contenido_dao.actualizar(
            id_contenido, titulo.strip(), contenido_existente.ruta_archivo, (contenido_texto or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    def eliminar_contenido(self, id_contenido: int) -> None:
        contenido = self._contenido_dao.obtener_por_id(id_contenido)
        self._contenido_dao.eliminar(id_contenido)
        if contenido and contenido.ruta_archivo:
            self._eliminar_archivo_fisico(contenido.ruta_archivo)

    def _eliminar_archivo_fisico(self, ruta_relativa: str) -> None:
        from config.settings import BASE_DIR
        ruta_absoluta = os.path.join(BASE_DIR, ruta_relativa)
        if os.path.isfile(ruta_absoluta):
            try:
                os.remove(ruta_absoluta)
            except OSError:
                pass
