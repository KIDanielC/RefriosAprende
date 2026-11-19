"""Controlador de Certificado: arma el contenido del certificado de finalización de un
curso para un aprendiz, una vez que su progreso está COMPLETADO, y lo exporta a PDF."""
import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from config.settings import APP_NAME
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.progreso_controller import ProgresoController
from model.dao.resultado_dao import ResultadoDAO
from model.entities.progreso import COMPLETADO

# Arial, no Century Gothic: Arial viene instalada de fábrica en todo Windows (Century
# Gothic depende de que Office u otro paquete la haya instalado). Un certificado necesita
# verse igual en cualquier equipo, no degradar a la fuente de mapa de bits de Pillow.
_DIR_FUENTES_WINDOWS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
_ANCHO_PX = 1754  # A4 horizontal a 150 dpi
_ALTO_PX = 1240
_COLOR_ACENTO = (28, 95, 168)
_COLOR_TEXTO = (36, 31, 24)
_COLOR_TEXTO_SECUNDARIO = (110, 101, 84)


def _cargar_fuente(nombre_archivo: str, tamano: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(os.path.join(_DIR_FUENTES_WINDOWS, nombre_archivo), tamano)
    except OSError:
        return ImageFont.load_default()


class CursoNoCompletadoError(Exception):
    """El aprendiz todavía no ha completado este curso; no se puede emitir certificado."""


class CertificadoController:
    def __init__(self):
        self._progreso_controlador = ProgresoController()
        self._evaluacion_controlador = EvaluacionController()
        self._guia_controlador = GuiaAprendizajeController()
        self._resultado_dao = ResultadoDAO()

    def curso_completado(self, id_usuario: int, id_curso: int) -> bool:
        progreso = self._progreso_controlador.obtener_progreso(id_usuario, id_curso)
        return progreso is not None and progreso.estado == COMPLETADO

    def obtener_datos_certificado(self, usuario, curso) -> dict:
        """Devuelve los datos ya resueltos para mostrar/imprimir el certificado.
        Lanza CursoNoCompletadoError si el progreso todavía no está en COMPLETADO."""
        if not self.curso_completado(usuario.id_usuario, curso.id_curso):
            raise CursoNoCompletadoError("Este curso todavía no está completado por el aprendiz.")

        guia = self._guia_controlador.obtener_guia(curso.id_curso)
        duracion_horas = guia.duracion_horas if guia and guia.duracion_horas else None

        nota_obtenida = None
        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
        if evaluacion_final is not None:
            resultados = self._resultado_dao.listar_por_usuario_y_evaluacion(usuario.id_usuario, evaluacion_final.id_evaluacion)
            aprobados = [r for r in resultados if r.aprobado]
            if aprobados:
                nota_obtenida = max(r.nota_obtenida for r in aprobados)

        return {
            "nombre_aprendiz": usuario.nombre_completo,
            "documento": usuario.documento,
            "nombre_curso": curso.nombre_curso,
            "nombre_instructor": curso.nombre_instructor,
            "duracion_horas": duracion_horas,
            "nota_obtenida": nota_obtenida,
            "fecha_emision": datetime.now().strftime("%d/%m/%Y"),
        }

    def exportar_certificado(self, usuario, curso, ruta_destino: str) -> str:
        """Genera el certificado como PDF en ruta_destino. Lanza CursoNoCompletadoError si
        el curso todavía no está completado (mismo chequeo que obtener_datos_certificado)."""
        datos = self.obtener_datos_certificado(usuario, curso)
        imagen = self._dibujar_certificado(datos)
        imagen.save(ruta_destino, "PDF", resolution=150.0)
        return ruta_destino

    def _dibujar_certificado(self, datos: dict) -> Image.Image:
        imagen = Image.new("RGB", (_ANCHO_PX, _ALTO_PX), "#FFFFFF")
        dibujar = ImageDraw.Draw(imagen)

        dibujar.rectangle((40, 40, _ANCHO_PX - 40, _ALTO_PX - 40), outline=_COLOR_ACENTO, width=6)
        dibujar.rectangle((62, 62, _ANCHO_PX - 62, _ALTO_PX - 62), outline=_COLOR_ACENTO, width=2)

        fuente_titulo = _cargar_fuente("arialbd.ttf", 54)
        fuente_nombre = _cargar_fuente("arialbd.ttf", 46)
        fuente_curso = _cargar_fuente("arialbd.ttf", 34)
        fuente_texto = _cargar_fuente("arial.ttf", 24)
        fuente_pie = _cargar_fuente("arial.ttf", 18)

        def centrado(texto: str, fuente: ImageFont.FreeTypeFont, y: int, color=_COLOR_TEXTO) -> None:
            ancho_texto = dibujar.textlength(texto, font=fuente)
            dibujar.text(((_ANCHO_PX - ancho_texto) / 2, y), texto, font=fuente, fill=color)

        centrado("CERTIFICADO DE FINALIZACIÓN", fuente_titulo, 150, _COLOR_ACENTO)
        centrado(datos["nombre_aprendiz"], fuente_nombre, 300)
        centrado(f"Documento: {datos['documento']}", fuente_texto, 370, _COLOR_TEXTO_SECUNDARIO)
        centrado("ha completado satisfactoriamente el curso", fuente_texto, 460, _COLOR_TEXTO_SECUNDARIO)
        centrado(f"«{datos['nombre_curso']}»", fuente_curso, 510, _COLOR_ACENTO)

        y_detalle = 630
        detalles = [f"Instructor: {datos['nombre_instructor']}"]
        if datos["duracion_horas"]:
            detalles.append(f"Duración: {datos['duracion_horas']} horas")
        if datos["nota_obtenida"] is not None:
            detalles.append(f"Nota evaluación final: {datos['nota_obtenida']:.1f} / 5.0")
        for detalle in detalles:
            centrado(detalle, fuente_texto, y_detalle, _COLOR_TEXTO_SECUNDARIO)
            y_detalle += 42

        centrado(
            f"Emitido el {datos['fecha_emision']}  ·  {APP_NAME}", fuente_pie, _ALTO_PX - 120,
            _COLOR_TEXTO_SECUNDARIO,
        )

        return imagen
