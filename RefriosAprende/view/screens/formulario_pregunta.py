"""Formulario modal reutilizable para crear/editar una pregunta de opción múltiple.
La función `guardar_pregunta` ya debe tener resuelto a qué evaluación/pregunta aplica
(ver evaluacion_final_screen.py y simulaciones_screen.py para ejemplos de uso)."""
import tkinter as tk

import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
)
from controller._pregunta_opcion_utils import DatosPreguntaInvalidosError, MAXIMO_OPCIONES
from model.entities.pregunta import Pregunta


class FormularioPregunta(ctk.CTkToplevel):
    def __init__(self, master, guardar_pregunta, al_guardar, pregunta_existente: Pregunta = None):
        super().__init__(master)
        self._guardar_pregunta = guardar_pregunta
        self._al_guardar = al_guardar
        self._pregunta_existente = pregunta_existente
        self._var_correcta = tk.IntVar(value=0)
        self._campos_opcion = []

        self.title("Editar pregunta" if pregunta_existente else "Nueva pregunta")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("520x640")
        self.minsize(520, 640)
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        if pregunta_existente:
            self._precargar_datos(pregunta_existente)

    def _construir_formulario(self):
        ctk.CTkLabel(
            self, text="Editar pregunta" if self._pregunta_existente else "Nueva pregunta",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(24, 16), anchor="w")

        ctk.CTkLabel(
            self, text="Enunciado", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(0, 2), anchor="w")
        self._campo_enunciado = ctk.CTkTextbox(
            self, width=460, height=70, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        self._campo_enunciado.pack(padx=28, pady=(0, 14))

        ctk.CTkLabel(
            self, text="Opciones de respuesta (marca la correcta con el círculo)",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(padx=28, pady=(0, 6), anchor="w")

        for indice in range(MAXIMO_OPCIONES):
            fila = ctk.CTkFrame(self, fg_color="transparent")
            fila.pack(padx=28, pady=4, fill="x")

            ctk.CTkRadioButton(
                fila, text="", variable=self._var_correcta, value=indice,
                fg_color=COLOR_ACENTO_PRIMARIO, border_color=COLOR_BORDE_SUTIL,
            ).pack(side="left", padx=(0, 8))

            campo = ctk.CTkEntry(
                fila, width=380, height=38, corner_radius=4, fg_color=COLOR_FONDO_APP,
                border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
                placeholder_text=f"Opción {indice + 1}" + (" (opcional)" if indice >= 2 else ""),
            )
            campo.pack(side="left")
            self._campos_opcion.append(campo)

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=460
        )
        self._etiqueta_error.pack(padx=28, pady=(10, 0))

        ctk.CTkButton(
            self, text="Guardar", width=460, height=44, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(18, 24))

    def _precargar_datos(self, pregunta: Pregunta):
        self._campo_enunciado.insert("1.0", pregunta.enunciado)
        for indice, opcion in enumerate(pregunta.opciones[:MAXIMO_OPCIONES]):
            self._campos_opcion[indice].insert(0, opcion.texto_opcion)
            if opcion.es_correcta:
                self._var_correcta.set(indice)

    def _guardar(self):
        enunciado = self._campo_enunciado.get("1.0", "end").strip()
        indice_correcta = self._var_correcta.get()
        opciones = [
            (campo.get(), indice == indice_correcta) for indice, campo in enumerate(self._campos_opcion)
        ]

        try:
            self._guardar_pregunta(enunciado, opciones)
        except DatosPreguntaInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()
