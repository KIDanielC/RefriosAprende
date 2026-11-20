"""Controlador de Certificado: arma el contenido del certificado de finalización de un
curso para un aprendiz, una vez que su progreso está COMPLETADO, y lo exporta a PDF."""
import hashlib
import os
from datetime import datetime

import qrcode
from PIL import Image, ImageDraw, ImageFont

from config.settings import APP_NAME
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.progreso_controller import ProgresoController
from controller.taller_controller import TallerController
from model.dao.resultado_dao import ResultadoDAO
from model.entities.progreso import COMPLETADO
from utils.texto_enriquecido import texto_plano_desde_markup

# Arial, no Century Gothic: Arial viene instalada de fábrica en todo Windows (Century
# Gothic depende de que Office u otro paquete la haya instalado). Un certificado necesita
# verse igual en cualquier equipo, no degradar a la fuente de mapa de bits de Pillow.
_DIR_FUENTES_WINDOWS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
_ANCHO_PX = 1754  # A4 horizontal a 150 dpi
_ALTO_PX = 1240
_COLOR_ACENTO = (28, 95, 168)
_COLOR_TEXTO = (36, 31, 24)
_COLOR_TEXTO_SECUNDARIO = (110, 101, 84)
_LARGO_CODIGO_VALIDACION = 16  # hex -> se muestra en 4 bloques de 4


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
        self._taller_controlador = TallerController()
        self._resultado_dao = ResultadoDAO()

    def curso_completado(self, id_usuario: int, id_curso: int) -> bool:
        progreso = self._progreso_controlador.obtener_progreso(id_usuario, id_curso)
        return progreso is not None and progreso.estado == COMPLETADO

    def obtener_datos_certificado(self, usuario, curso) -> dict:
        """Devuelve los datos ya resueltos para mostrar/imprimir el certificado.
        Lanza CursoNoCompletadoError si el progreso todavía no está en COMPLETADO."""
        progreso = self._progreso_controlador.obtener_progreso(usuario.id_usuario, curso.id_curso)
        if progreso is None or progreso.estado != COMPLETADO:
            raise CursoNoCompletadoError("Este curso todavía no está completado por el aprendiz.")

        guia = self._guia_controlador.obtener_guia(curso.id_curso)
        duracion_horas = guia.duracion_horas if guia and guia.duracion_horas else None
        competencias = texto_plano_desde_markup(guia.competencias) if guia and guia.competencias else None

        nota_obtenida = None
        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
        if evaluacion_final is not None:
            resultados = self._resultado_dao.listar_por_usuario_y_evaluacion(usuario.id_usuario, evaluacion_final.id_evaluacion)
            aprobados = [r for r in resultados if r.aprobado]
            if aprobados:
                nota_obtenida = max(r.nota_obtenida for r in aprobados)

        talleres = self._taller_controlador.listar_por_curso(curso.id_curso)

        fecha_finalizacion = self._formatear_fecha(progreso.fecha_actualizacion)
        codigo_validacion = self._generar_codigo_validacion(usuario, curso, fecha_finalizacion)

        return {
            "nombre_aprendiz": usuario.nombre_completo,
            "documento": usuario.documento,
            "nombre_curso": curso.nombre_curso,
            "nombre_instructor": curso.nombre_instructor,
            "nombre_emisor": APP_NAME,
            "duracion_horas": duracion_horas,
            "nota_obtenida": nota_obtenida,
            "tipo_participacion": self._describir_tipo_participacion(evaluacion_final, nota_obtenida, talleres),
            "competencias": competencias,
            "fecha_finalizacion": fecha_finalizacion,
            "fecha_emision": datetime.now().strftime("%d/%m/%Y"),
            "codigo_validacion": codigo_validacion,
        }

    def _formatear_fecha(self, fecha_sqlite: str) -> str:
        """fecha_actualizacion viene de SQLite como 'YYYY-MM-DD HH:MM:SS' (o solo la fecha);
        se muestra siempre en formato colombiano dd/mm/aaaa."""
        if not fecha_sqlite:
            return datetime.now().strftime("%d/%m/%Y")
        try:
            return datetime.strptime(fecha_sqlite[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return fecha_sqlite

    def _describir_tipo_participacion(self, evaluacion_final, nota_obtenida, talleres) -> str:
        """Deja explícito si la finalización exigió aprobar una evaluación y/o talleres
        calificados, o si el curso solo pedía ver todo el contenido (participación)."""
        requisitos = []
        if evaluacion_final is not None and nota_obtenida is not None:
            requisitos.append(f"evaluación final aprobada (nota {nota_obtenida:.1f} / 5.0)")
        if talleres:
            requisitos.append("talleres prácticos aprobados")

        if requisitos:
            return "Finalización mediante " + " y ".join(requisitos) + "."
        return "Participación completa de los contenidos del curso (sin evaluación obligatoria)."

    def _generar_codigo_validacion(self, usuario, curso, fecha_finalizacion: str) -> str:
        """Código determinístico (mismo participante + mismo curso + misma fecha de
        finalización siempre produce el mismo código): sirve para que quien recibe el
        certificado lo compare contra los registros de la institución. No es una firma
        criptográfica ni depende de un servidor en línea -- esta aplicación es de
        escritorio y no tiene un sistema de verificación web."""
        semilla = f"{APP_NAME}|{usuario.id_usuario}|{curso.id_curso}|{fecha_finalizacion}"
        huella = hashlib.sha256(semilla.encode("utf-8")).hexdigest()[:_LARGO_CODIGO_VALIDACION].upper()
        return "-".join(huella[i:i + 4] for i in range(0, len(huella), 4))

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

        fuente_emisor = _cargar_fuente("arialbd.ttf", 22)
        fuente_titulo = _cargar_fuente("arialbd.ttf", 50)
        fuente_nombre = _cargar_fuente("arialbd.ttf", 44)
        fuente_curso = _cargar_fuente("arialbd.ttf", 32)
        fuente_texto = _cargar_fuente("arial.ttf", 23)
        fuente_pequena = _cargar_fuente("arial.ttf", 17)
        fuente_pie = _cargar_fuente("arial.ttf", 17)

        def centrado(texto: str, fuente: ImageFont.FreeTypeFont, y: int, color=_COLOR_TEXTO) -> None:
            ancho_texto = dibujar.textlength(texto, font=fuente)
            dibujar.text(((_ANCHO_PX - ancho_texto) / 2, y), texto, font=fuente, fill=color)

        centrado(datos["nombre_emisor"].upper(), fuente_emisor, 108, _COLOR_ACENTO)
        centrado("CERTIFICADO DE FINALIZACIÓN", fuente_titulo, 150, _COLOR_ACENTO)
        centrado(datos["nombre_aprendiz"], fuente_nombre, 290)
        centrado(f"Documento de identidad: {datos['documento']}", fuente_texto, 360, _COLOR_TEXTO_SECUNDARIO)
        centrado("ha completado satisfactoriamente el curso", fuente_texto, 445, _COLOR_TEXTO_SECUNDARIO)
        centrado(f"«{datos['nombre_curso']}»", fuente_curso, 492, _COLOR_ACENTO)

        y_detalle = 590
        detalles = [f"Instructor responsable: {datos['nombre_instructor']}"]
        if datos["duracion_horas"]:
            detalles.append(f"Intensidad horaria: {datos['duracion_horas']} horas")
        detalles.append(datos["tipo_participacion"])
        detalles.append(f"Fecha de finalización: {datos['fecha_finalizacion']}")
        if datos["competencias"]:
            extracto = datos["competencias"][:70] + ("…" if len(datos["competencias"]) > 70 else "")
            detalles.append(f"Competencias desarrolladas: {extracto}")
        for detalle in detalles:
            centrado(detalle, fuente_texto, y_detalle, _COLOR_TEXTO_SECUNDARIO)
            y_detalle += 40

        self._dibujar_firma(imagen, dibujar, fuente_texto, fuente_pequena, datos)
        self._dibujar_validacion(imagen, dibujar, fuente_pequena, datos)

        centrado(
            f"Emitido el {datos['fecha_emision']}  ·  {datos['nombre_emisor']}", fuente_pie, _ALTO_PX - 92,
            _COLOR_TEXTO_SECUNDARIO,
        )

        return imagen

    def _dibujar_firma(self, imagen, dibujar, fuente_texto, fuente_pequena, datos: dict) -> None:
        """No hay captura de firma digitalizada en la aplicación: se dibuja la línea y el
        nombre del instructor con el formato tradicional de 'firma autorizada' en papel."""
        x_inicio, x_fin = 180, 620
        y_linea = 960
        dibujar.line((x_inicio, y_linea, x_fin, y_linea), fill=_COLOR_TEXTO, width=2)

        centro_x = (x_inicio + x_fin) / 2
        ancho_nombre = dibujar.textlength(datos["nombre_instructor"], font=fuente_texto)
        dibujar.text((centro_x - ancho_nombre / 2, y_linea + 10), datos["nombre_instructor"], font=fuente_texto, fill=_COLOR_TEXTO)

        texto_cargo = "Firma autorizada — Instructor del curso"
        ancho_cargo = dibujar.textlength(texto_cargo, font=fuente_pequena)
        dibujar.text((centro_x - ancho_cargo / 2, y_linea + 48), texto_cargo, font=fuente_pequena, fill=_COLOR_TEXTO_SECUNDARIO)

    def _dibujar_validacion(self, imagen, dibujar, fuente_pequena, datos: dict) -> None:
        """Código de validación + QR con los mismos datos, para que quien reciba el
        certificado pueda compararlo contra los registros de la institución. El QR no
        apunta a ningún servidor (la aplicación es de escritorio, sin backend en línea):
        guarda el texto de verificación para leerlo con cualquier lector de QR."""
        texto_verificacion = (
            f"{datos['nombre_emisor']} - CERTIFICADO\n"
            f"Código: {datos['codigo_validacion']}\n"
            f"Participante: {datos['nombre_aprendiz']} ({datos['documento']})\n"
            f"Curso: {datos['nombre_curso']}\n"
            f"Finalización: {datos['fecha_finalizacion']}"
        )
        qr_imagen = qrcode.make(texto_verificacion).convert("RGB").resize((165, 165))

        x_qr = _ANCHO_PX - 180 - 165
        y_qr = 870
        imagen.paste(qr_imagen, (x_qr, y_qr))

        etiqueta = "Código de validación"
        ancho_etiqueta = dibujar.textlength(etiqueta, font=fuente_pequena)
        dibujar.text((x_qr + 82 - ancho_etiqueta / 2, y_qr + 170), etiqueta, font=fuente_pequena, fill=_COLOR_TEXTO_SECUNDARIO)

        ancho_codigo = dibujar.textlength(datos["codigo_validacion"], font=fuente_pequena)
        dibujar.text((x_qr + 82 - ancho_codigo / 2, y_qr + 192), datos["codigo_validacion"], font=fuente_pequena, fill=_COLOR_TEXTO)
