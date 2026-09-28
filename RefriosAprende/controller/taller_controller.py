"""Controlador de Talleres: ejercicios prácticos que el instructor asigna a un curso y que
el aprendiz debe entregar (imagen, PDF o Word) para que sean calificados. Aprobar todos los
talleres de un curso es requisito para completarlo, igual que la evaluación final
(ver ProgresoController.recalcular_progreso)."""
import logging
import os
import shutil
import uuid

from config.settings import BASE_DIR, ENTREGAS_DIR
from controller.progreso_controller import ProgresoController
from model.dao.entrega_taller_dao import EntregaTallerDAO
from model.dao.taller_dao import TallerDAO
from model.entities.entrega_taller import APROBADO, EntregaTaller, RECHAZADO
from model.entities.taller import Taller

_logger = logging.getLogger(__name__)
_EXTENSIONES_PERMITIDAS = (".png", ".jpg", ".jpeg", ".pdf", ".doc", ".docx")


class DatosTallerInvalidosError(Exception):
    """Los datos del taller o de la entrega no cumplen las reglas de negocio."""


class TallerController:
    def __init__(self):
        self._taller_dao = TallerDAO()
        self._entrega_dao = EntregaTallerDAO()

    # -- Administración (instructor) ----------------------------------------
    def listar_por_curso(self, id_curso: int) -> list[Taller]:
        return self._taller_dao.listar_por_curso(id_curso)

    def crear_taller(self, id_curso: int, titulo: str, descripcion: str) -> Taller:
        self._validar_datos(titulo, descripcion)
        id_taller = self._taller_dao.crear(id_curso, titulo.strip(), descripcion.strip())
        return self._taller_dao.obtener_por_id(id_taller)

    def actualizar_taller(self, id_taller: int, titulo: str, descripcion: str) -> Taller:
        self._validar_datos(titulo, descripcion)
        self._taller_dao.actualizar(id_taller, titulo.strip(), descripcion.strip())
        return self._taller_dao.obtener_por_id(id_taller)

    def eliminar_taller(self, id_taller: int) -> None:
        for entrega in self._entrega_dao.listar_por_taller(id_taller):
            self._eliminar_archivo_fisico(entrega.ruta_archivo)
        self._taller_dao.eliminar(id_taller)

    def _validar_datos(self, titulo: str, descripcion: str):
        if not titulo or len(titulo.strip()) < 3:
            raise DatosTallerInvalidosError("El título debe tener al menos 3 caracteres.")
        if not descripcion or len(descripcion.strip()) < 10:
            raise DatosTallerInvalidosError("Describe la actividad con al menos 10 caracteres.")

    # -- Entrega (aprendiz) ---------------------------------------------------
    def obtener_entrega(self, id_taller: int, id_usuario: int) -> EntregaTaller | None:
        return self._entrega_dao.obtener_por_taller_y_usuario(id_taller, id_usuario)

    def subir_entrega(self, id_taller: int, id_usuario: int, ruta_origen: str) -> EntregaTaller:
        if not ruta_origen or not os.path.isfile(ruta_origen):
            raise DatosTallerInvalidosError("Selecciona un archivo válido.")
        extension = os.path.splitext(ruta_origen)[1].lower()
        if extension not in _EXTENSIONES_PERMITIDAS:
            raise DatosTallerInvalidosError("El archivo debe ser una imagen (PNG/JPG), un PDF o un Word (DOC/DOCX).")

        entrega_existente = self._entrega_dao.obtener_por_taller_y_usuario(id_taller, id_usuario)

        os.makedirs(ENTREGAS_DIR, exist_ok=True)
        nombre_unico = f"{uuid.uuid4().hex}{extension}"
        shutil.copyfile(ruta_origen, os.path.join(ENTREGAS_DIR, nombre_unico))
        ruta_relativa = os.path.join("resources", "entregas", nombre_unico)
        nombre_original = os.path.basename(ruta_origen)

        self._entrega_dao.crear_o_reemplazar(id_taller, id_usuario, ruta_relativa, nombre_original)

        if entrega_existente is not None:
            self._eliminar_archivo_fisico(entrega_existente.ruta_archivo)

        return self._entrega_dao.obtener_por_taller_y_usuario(id_taller, id_usuario)

    def _eliminar_archivo_fisico(self, ruta_relativa: str) -> None:
        ruta_absoluta = os.path.join(BASE_DIR, ruta_relativa)
        if os.path.isfile(ruta_absoluta):
            try:
                os.remove(ruta_absoluta)
            except OSError:
                _logger.warning("No se pudo eliminar el archivo de una entrega de taller: %s", ruta_absoluta, exc_info=True)

    # -- Calificación (instructor) --------------------------------------------
    def listar_entregas_por_taller(self, id_taller: int) -> list[EntregaTaller]:
        return self._entrega_dao.listar_por_taller(id_taller)

    def calificar_entrega(self, id_entrega: int, aprobado: bool, comentario: str) -> EntregaTaller:
        entrega = self._entrega_dao.obtener_por_id(id_entrega)
        if entrega is None:
            raise DatosTallerInvalidosError("La entrega ya no existe.")

        estado = APROBADO if aprobado else RECHAZADO
        self._entrega_dao.calificar(id_entrega, estado, (comentario or "").strip())

        taller = self._taller_dao.obtener_por_id(entrega.id_taller)
        if taller is not None:
            ProgresoController().recalcular_progreso(entrega.id_usuario, taller.id_curso)

        return self._entrega_dao.obtener_por_id(id_entrega)
