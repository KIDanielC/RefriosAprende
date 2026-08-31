"""Ventana modal: certificado de finalización de un curso para el aprendiz."""
import customtkinter as ctk

from config.settings import (
    APP_NAME,
    COLOR_ACENTO_PRIMARIO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    RADIO_TARJETA,
)
from controller.certificado_controller import CertificadoController


class CertificadoWindow(ctk.CTkToplevel):
    """Muestra el certificado de finalización del curso ya completado por el aprendiz."""

    def __init__(self, master, usuario, curso):
        super().__init__(master)
        self._controlador = CertificadoController()

        self.title(f"Certificado — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("640x520")
        self.minsize(560, 460)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        datos = self._controlador.obtener_datos_certificado(usuario, curso)
        self._construir(datos)

    def _construir(self, datos: dict):
        marco = ctk.CTkFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=2, border_color=COLOR_ACENTO_PRIMARIO,
        )
        marco.grid(row=0, column=0, sticky="nsew", padx=32, pady=32)
        marco.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            marco, text="🏆", font=(FONT_FAMILY, 40), text_color=COLOR_ACENTO_PRIMARIO,
        ).grid(row=0, column=0, pady=(36, 4))

        ctk.CTkLabel(
            marco, text="CERTIFICADO DE FINALIZACIÓN", font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=1, column=0, pady=(0, 20))

        ctk.CTkLabel(
            marco, text=datos["nombre_aprendiz"], font=(FONT_FAMILY, 26, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=2, column=0, pady=(0, 4))
        ctk.CTkLabel(
            marco, text=f"Documento: {datos['documento']}", font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=3, column=0, pady=(0, 24))

        ctk.CTkLabel(
            marco, text="ha completado satisfactoriamente el curso", font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=4, column=0)
        ctk.CTkLabel(
            marco, text=f"«{datos['nombre_curso']}»", font=(FONT_FAMILY, 19, "bold"), text_color=COLOR_ACENTO_PRIMARIO,
            wraplength=520,
        ).grid(row=5, column=0, pady=(6, 24))

        detalle = ctk.CTkFrame(marco, fg_color="transparent")
        detalle.grid(row=6, column=0, pady=(0, 8))
        partes = [f"Instructor: {datos['nombre_instructor']}"]
        if datos["duracion_horas"]:
            partes.append(f"Duración: {datos['duracion_horas']} horas")
        if datos["nota_obtenida"] is not None:
            partes.append(f"Nota evaluación final: {datos['nota_obtenida']:.1f} / 5.0")
        for parte in partes:
            ctk.CTkLabel(
                detalle, text=parte, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=1)

        ctk.CTkLabel(
            marco, text=f"Emitido el {datos['fecha_emision']}  ·  {APP_NAME}", font=(FONT_FAMILY, 10.5),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=7, column=0, pady=(20, 32))
