"""Controlador de gestión de contenidos de un curso (tipo TEXTO, PDF, IMAGEN o VIDEO_LOCAL)."""
import logging
import os
import shutil
import uuid

from config.settings import CONTENIDOS_DIR
from model.dao.contenido_dao import ContenidoDAO
from model.entities.contenido import Contenido
from utils.autorizacion import exigir_administrador
from utils.texto_enriquecido import texto_plano_desde_markup

_logger = logging.getLogger(__name__)

TIPO_TEXTO = "TEXTO"
TIPO_PDF = "PDF"
TIPO_IMAGEN = "IMAGEN"
TIPO_VIDEO = "VIDEO_LOCAL"

_EXTENSIONES_IMAGEN = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
_EXTENSIONES_VIDEO = (".mp4", ".avi", ".mkv")
_TAMANO_MAXIMO_BYTES = 20 * 1024 * 1024  # 20 MB
_TAMANO_MAXIMO_VIDEO_BYTES = 200 * 1024 * 1024  # 200 MB


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
    def crear_contenido_texto(self, id_curso: int, titulo: str, contenido_texto: str, usuario_actor=None) -> Contenido:
        exigir_administrador(usuario_actor)
        self._validar_titulo(titulo)
        if not contenido_texto or len(texto_plano_desde_markup(contenido_texto).strip()) < 10:
            raise DatosContenidoInvalidosError("El contenido debe tener al menos 10 caracteres.")

        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_TEXTO, None, contenido_texto.strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    # -- Contenido de tipo PDF --------------------------------------------
    def crear_contenido_pdf(self, id_curso: int, titulo: str, descripcion: str, ruta_pdf_origen: str, usuario_actor=None) -> Contenido:
        exigir_administrador(usuario_actor)
        self._validar_titulo(titulo)
        if not ruta_pdf_origen or not os.path.isfile(ruta_pdf_origen):
            raise DatosContenidoInvalidosError("Selecciona un archivo PDF válido.")
        if not ruta_pdf_origen.lower().endswith(".pdf"):
            raise DatosContenidoInvalidosError("El archivo seleccionado debe ser un PDF.")
        if os.path.getsize(ruta_pdf_origen) > _TAMANO_MAXIMO_BYTES:
            raise DatosContenidoInvalidosError("El PDF no puede superar los 20 MB.")

        ruta_relativa = self._copiar_archivo_a_recursos(ruta_pdf_origen, ".pdf")
        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_PDF, ruta_relativa, (descripcion or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    # -- Contenido de tipo IMAGEN ------------------------------------------
    def crear_contenido_imagen(self, id_curso: int, titulo: str, descripcion: str, ruta_imagen_origen: str, usuario_actor=None) -> Contenido:
        exigir_administrador(usuario_actor)
        self._validar_titulo(titulo)
        if not ruta_imagen_origen or not os.path.isfile(ruta_imagen_origen):
            raise DatosContenidoInvalidosError("Selecciona un archivo de imagen válido.")
        extension = os.path.splitext(ruta_imagen_origen)[1].lower()
        if extension not in _EXTENSIONES_IMAGEN:
            raise DatosContenidoInvalidosError("La imagen debe ser PNG, JPG, JPEG, GIF o BMP.")
        if os.path.getsize(ruta_imagen_origen) > _TAMANO_MAXIMO_BYTES:
            raise DatosContenidoInvalidosError("La imagen no puede superar los 20 MB.")

        ruta_relativa = self._copiar_archivo_a_recursos(ruta_imagen_origen, extension)
        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_IMAGEN, ruta_relativa, (descripcion or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    # -- Contenido de tipo VIDEO_LOCAL --------------------------------------
    def crear_contenido_video(self, id_curso: int, titulo: str, descripcion: str, ruta_video_origen: str, usuario_actor=None) -> Contenido:
        exigir_administrador(usuario_actor)
        self._validar_titulo(titulo)
        if not ruta_video_origen or not os.path.isfile(ruta_video_origen):
            raise DatosContenidoInvalidosError("Selecciona un archivo de video válido.")
        extension = os.path.splitext(ruta_video_origen)[1].lower()
        if extension not in _EXTENSIONES_VIDEO:
            raise DatosContenidoInvalidosError("El video debe ser MP4, AVI o MKV.")
        if os.path.getsize(ruta_video_origen) > _TAMANO_MAXIMO_VIDEO_BYTES:
            raise DatosContenidoInvalidosError("El video no puede superar los 200 MB.")

        ruta_relativa = self._copiar_archivo_a_recursos(ruta_video_origen, extension)
        orden = self._contenido_dao.obtener_siguiente_orden(id_curso)
        id_contenido = self._contenido_dao.crear(
            id_curso, titulo.strip(), TIPO_VIDEO, ruta_relativa, (descripcion or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    def _copiar_archivo_a_recursos(self, ruta_origen: str, extension: str) -> str:
        os.makedirs(CONTENIDOS_DIR, exist_ok=True)
        nombre_unico = f"{uuid.uuid4().hex}{extension}"
        destino = os.path.join(CONTENIDOS_DIR, nombre_unico)
        shutil.copyfile(ruta_origen, destino)
        return os.path.join("resources", "contenidos", nombre_unico)

    # -- Comunes ------------------------------------------------------------
    def actualizar_contenido(self, id_contenido: int, titulo: str, contenido_texto: str, orden: int, usuario_actor=None) -> Contenido:
        exigir_administrador(usuario_actor)
        self._validar_titulo(titulo)

        contenido_existente = self._contenido_dao.obtener_por_id(id_contenido)
        if contenido_existente is None:
            raise DatosContenidoInvalidosError("El contenido ya no existe.")

        if contenido_existente.tipo_contenido == TIPO_TEXTO and (
            not contenido_texto or len(texto_plano_desde_markup(contenido_texto).strip()) < 10
        ):
            raise DatosContenidoInvalidosError("El contenido debe tener al menos 10 caracteres.")

        self._contenido_dao.actualizar(
            id_contenido, titulo.strip(), contenido_existente.ruta_archivo, (contenido_texto or "").strip(), orden
        )
        return self._contenido_dao.obtener_por_id(id_contenido)

    def eliminar_contenido(self, id_contenido: int, usuario_actor=None) -> None:
        exigir_administrador(usuario_actor)
        contenido = self._contenido_dao.obtener_por_id(id_contenido)
        self._contenido_dao.eliminar(id_contenido)
        if contenido and contenido.ruta_archivo:
            self._eliminar_archivo_fisico(contenido.ruta_archivo)

    def mover_contenido(self, id_contenido: int, direccion: str, usuario_actor=None) -> None:
        """direccion: 'subir' o 'bajar'. No hace nada si ya está en el extremo correspondiente
        (primero no sube, último no baja)."""
        exigir_administrador(usuario_actor)
        if direccion not in ("subir", "bajar"):
            raise DatosContenidoInvalidosError("La dirección debe ser 'subir' o 'bajar'.")

        contenido = self._contenido_dao.obtener_por_id(id_contenido)
        if contenido is None:
            raise DatosContenidoInvalidosError("El contenido ya no existe.")

        contenidos_del_curso = self._contenido_dao.listar_por_curso(contenido.id_curso)
        indice = next(i for i, c in enumerate(contenidos_del_curso) if c.id_contenido == id_contenido)

        if direccion == "subir":
            if indice == 0:
                return
            vecino = contenidos_del_curso[indice - 1]
        else:
            if indice == len(contenidos_del_curso) - 1:
                return
            vecino = contenidos_del_curso[indice + 1]

        self._contenido_dao.intercambiar_orden(id_contenido, vecino.id_contenido)

    def _eliminar_archivo_fisico(self, ruta_relativa: str) -> None:
        from config.settings import BASE_DIR
        ruta_absoluta = os.path.join(BASE_DIR, ruta_relativa)
        if os.path.isfile(ruta_absoluta):
            try:
                os.remove(ruta_absoluta)
            except OSError:
                _logger.warning("No se pudo eliminar el archivo físico del contenido: %s", ruta_absoluta, exc_info=True)
