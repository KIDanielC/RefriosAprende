"""Ventana modal donde el aprendiz responde el cuestionario de validación de un contenido.
No guarda resultados formales (eso corresponde al módulo de Evaluaciones del Sprint 3):
es solo retroalimentación inmediata para reforzar el aprendizaje."""
import tkinter as tk

import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
)
from controller.validacion_controller import ValidacionController
from model.entities.contenido import Contenido


class ResponderQuizWindow(ctk.CTkToplevel):
    """Cuestionario de opción múltiple con corrección inmediata en pantalla."""

    def __init__(self, master, contenido: Contenido):
        super().__init__(master)
        self._contenido = contenido
        self._controlador = ValidacionController()
        self._preguntas = self._controlador.listar_preguntas(contenido)
        self._variables_por_pregunta = {}
        self._etiquetas_resultado_por_pregunta = {}

        self.title(f"Validación — {contenido.titulo}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("700x600")
        self.minsize(600, 450)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_encabezado()
        self._construir_preguntas()
        self._construir_pie()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkLabel(
            self, text=f"Validación de conocimiento: «{self._contenido.titulo}»",
            font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

    def _construir_preguntas(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=1, column=0, sticky="nsew", padx=24)
        contenedor.grid_columnconfigure(0, weight=1)

        for indice, pregunta in enumerate(self._preguntas):
            tarjeta = ctk.CTkFrame(
                contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=4,
                border_width=1, border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.grid(row=indice, column=0, sticky="ew", pady=6)
            tarjeta.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                tarjeta, text=f"{indice + 1}. {pregunta.enunciado}", font=(FONT_FAMILY, 14, "bold"),
                text_color=COLOR_TEXTO_PRIMARIO, anchor="w", justify="left", wraplength=600,
            ).grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

            variable = tk.IntVar(value=-1)
            self._variables_por_pregunta[pregunta.id_pregunta] = variable

            for indice_opcion, opcion in enumerate(pregunta.opciones):
                ctk.CTkRadioButton(
                    tarjeta, text=opcion.texto_opcion, variable=variable, value=indice_opcion,
                    fg_color=COLOR_ACENTO_PRIMARIO, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_SECUNDARIO,
                    font=(FONT_FAMILY, 13),
                ).grid(row=1 + indice_opcion, column=0, sticky="w", padx=24, pady=2)

            etiqueta_resultado = ctk.CTkLabel(tarjeta, text="", font=(FONT_FAMILY, 12, "bold"))
            etiqueta_resultado.grid(row=1 + len(pregunta.opciones), column=0, sticky="w", padx=16, pady=(4, 12))
            self._etiquetas_resultado_por_pregunta[pregunta.id_pregunta] = etiqueta_resultado

    def _construir_pie(self):
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=2, column=0, sticky="ew", padx=24, pady=20)
        pie.grid_columnconfigure(0, weight=1)

        self._etiqueta_puntaje = ctk.CTkLabel(pie, text="", font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXTO_PRIMARIO)
        self._etiqueta_puntaje.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pie, text="Corregir", width=160, height=42, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=self._corregir,
        ).grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    def _corregir(self):
        if not self._preguntas:
            return

        total_correctas = 0
        for pregunta in self._preguntas:
            indice_seleccionado = self._variables_por_pregunta[pregunta.id_pregunta].get()
            etiqueta_resultado = self._etiquetas_resultado_por_pregunta[pregunta.id_pregunta]

            indice_correcto = next(
                (i for i, opcion in enumerate(pregunta.opciones) if opcion.es_correcta), None
            )

            if indice_seleccionado == -1:
                etiqueta_resultado.configure(text="No respondiste esta pregunta.", text_color=COLOR_TEXTO_SECUNDARIO)
                continue

            if indice_seleccionado == indice_correcto:
                total_correctas += 1
                etiqueta_resultado.configure(text="✓ Correcto", text_color=COLOR_EXITO)
            else:
                correcta = pregunta.opciones[indice_correcto].texto_opcion
                etiqueta_resultado.configure(text=f"✗ Incorrecto — la respuesta correcta es: {correcta}", text_color=COLOR_ERROR)

        self._etiqueta_puntaje.configure(
            text=f"Resultado: {total_correctas} de {len(self._preguntas)} correctas"
        )
