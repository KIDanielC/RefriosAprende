"""Ventana modal: certificado de finalización de un curso para el aprendiz."""
from tkinter import filedialog

import customtkinter as ctk

from config.settings import (
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    RADIO_TARJETA,
    RADIO_BOTON,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    FONT_FAMILY,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_TEXTO_PRIMARIO,
    COLOR_EXITO,
    COLOR_ERROR,
    APP_NAME,
)
from controller.certificado_controller import CertificadoController


class CertificadoWindow(ctk.CTkToplevel):
    """Muestra el certificado de finalización del curso ya completado por el aprendiz."""

    def __init__(self, master, usuario, curso):
        super().__init__(master)
        self._controlador = CertificadoController()
        self._usuario = usuario
        self._curso = curso

        self.title(f"Certificado — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("640x700")
        self.minsize(560, 640)
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
        partes.append(datos["tipo_participacion"])
        partes.append(f"Fecha de finalización: {datos['fecha_finalizacion']}")
        if datos["competencias"]:
            extracto = datos["competencias"][:70] + ("…" if len(datos["competencias"]) > 70 else "")
            partes.append(f"Competencias desarrolladas: {extracto}")
        for parte in partes:
            ctk.CTkLabel(
                detalle, text=parte, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
                wraplength=520, justify="center",
            ).pack(pady=1)

        ctk.CTkLabel(
            marco, text=f"Código de validación: {datos['codigo_validacion']}", font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=7, column=0, pady=(10, 0))
        ctk.CTkLabel(
            marco, text="(el PDF incluye además el código QR y la firma autorizada del instructor)",
            font=(FONT_FAMILY, 10), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=8, column=0, pady=(2, 0))

        ctk.CTkLabel(
            marco, text=f"Emitido el {datos['fecha_emision']}  ·  {APP_NAME}", font=(FONT_FAMILY, 10.5),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=9, column=0, pady=(14, 16))

        self._etiqueta_estado = ctk.CTkLabel(marco, text="", font=(FONT_FAMILY, 11), text_color=COLOR_EXITO)
        self._etiqueta_estado.grid(row=10, column=0, pady=(0, 4))

        ctk.CTkButton(
            marco, text="Guardar como PDF", width=220, height=38, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 12, "bold"), command=self._guardar_como_pdf,
        ).grid(row=11, column=0, pady=(0, 28))

    def _guardar_como_pdf(self):
        ruta_destino = filedialog.asksaveasfilename(
            parent=self, title="Guardar certificado", defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            initialfile=f"Certificado - {self._curso.nombre_curso}.pdf",
        )
        if not ruta_destino:
            return
        try:
            self._controlador.exportar_certificado(self._usuario, self._curso, ruta_destino)
        except Exception as error:
            self._etiqueta_estado.configure(text=f"No se pudo guardar: {error}", text_color=COLOR_ERROR)
            return
        self._etiqueta_estado.configure(text=f"Guardado en: {ruta_destino}", text_color=COLOR_EXITO)
