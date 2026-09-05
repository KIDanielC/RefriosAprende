"""Controlador de la Guía de Aprendizaje de un curso: valida y coordina Vista <-> Modelo."""
from model.dao.guia_aprendizaje_dao import COLUMNAS_TEXTO_LIBRE, GuiaAprendizajeDAO
from model.entities.guia_aprendizaje import GuiaAprendizaje

# Única fuente de verdad de qué campos de texto libre existen en la guía; la vista construye
# su formulario a partir de esta misma lista, para no duplicar el listado de claves válidas.
CAMPOS_TEXTO_GUIA = COLUMNAS_TEXTO_LIBRE


class DatosGuiaInvalidosError(Exception):
    """Los datos de la guía de aprendizaje no cumplen las reglas de negocio."""


class GuiaAprendizajeController:
    def __init__(self):
        self._guia_dao = GuiaAprendizajeDAO()

    def obtener_guia(self, id_curso: int) -> GuiaAprendizaje | None:
        return self._guia_dao.obtener_por_curso(id_curso)

    def guardar_guia(self, id_curso: int, campos: dict[str, str], duracion_horas: str) -> GuiaAprendizaje:
        """`campos` trae (algunas o todas) las claves de CAMPOS_TEXTO_GUIA. Solo el objetivo
        general es obligatorio: el resto puede quedar vacío y completarse más adelante, para
        que generar la guía sea rápido y no se sienta como un formulario de 15 campos obligatorios."""
        campos_limpios = {clave: (campos.get(clave) or "").strip() for clave in CAMPOS_TEXTO_GUIA}

        if len(campos_limpios["objetivo_general"]) < 10:
            raise DatosGuiaInvalidosError("El objetivo general debe tener al menos 10 caracteres.")

        duracion_valor = None
        duracion_texto = (duracion_horas or "").strip()
        if duracion_texto:
            try:
                duracion_valor = int(duracion_texto)
            except ValueError:
                raise DatosGuiaInvalidosError("La duración en horas debe ser un número entero.")
            if duracion_valor <= 0:
                raise DatosGuiaInvalidosError("La duración en horas debe ser mayor a cero.")

        self._guia_dao.guardar(id_curso, campos_limpios, duracion_valor)
        return self._guia_dao.obtener_por_curso(id_curso)
