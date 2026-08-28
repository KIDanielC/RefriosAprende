"""Ventana modal: el aprendiz presenta la evaluación final de un curso.
A diferencia del cuestionario de validación por contenido, aquí sí se registra
un Resultado formal (nota, aprobado) y se respeta el límite de intentos."""
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
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
)
from controller.evaluacion_controller import DatosEvaluacionInvalidosError, EvaluacionController, IntentosAgotadosError
from model.entities.evaluacion import Evaluacion
from model.entities.usuario import Usuario


class PresentarEvaluacionWindow(ctk.CTkToplevel):
    def __init__(self, master, evaluacion: Evaluacion, usuario_sesion: Usuario):
        super().__init__(master)
        self._evaluacion = evaluacion
        self._usuario_sesion = usuario_sesion
        self._controlador = EvaluacionController()
        self._variables_por_pregunta = {}

        self.title(evaluacion.titulo)
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("700x620")
        self.minsize(600, 480)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._refrescar()

    # ------------------------------------------------------------------
    def _refrescar(self):
        for hijo in self.winfo_children():
            hijo.destroy()
        self._variables_por_pregunta = {}

        intentos_usados = self._controlador.intentos_usados(self._usuario_sesion.id_usuario, self._evaluacion.id_evaluacion)
        preguntas = self._controlador.listar_preguntas(self._evaluacion.id_evaluacion)

        ctk.CTkLabel(
            self, text=self._evaluacion.titulo, font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            self,
            text=(
                f"Nota mínima para aprobar: {self._evaluacion.nota_minima_aprobar:.1f} / 5.0  ·  "
                f"Intentos: {intentos_usados} de {self._evaluacion.intentos_permitidos} usados"
            ),
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(48, 0))

        if not preguntas:
            ctk.CTkLabel(
                self, text="Esta evaluación todavía no tiene preguntas publicadas.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=1, column=0, padx=24, pady=20)
            return

        if intentos_usados >= self._evaluacion.intentos_permitidos:
            ctk.CTkLabel(
                self, text="Ya usaste todos los intentos permitidos para esta evaluación.",
                font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_ERROR,
            ).grid(row=1, column=0, padx=24, pady=20)
            return

        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=1, column=0, sticky="nsew", padx=24)
        contenedor.grid_columnconfigure(0, weight=1)

        for indice, pregunta in enumerate(preguntas):
            tarjeta = ctk.CTkFrame(
                contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
                border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.grid(row=indice, column=0, sticky="ew", pady=6)
            tarjeta.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                tarjeta, text=f"{indice + 1}. {pregunta.enunciado}", font=(FONT_FAMILY, 14, "bold"),
                text_color=COLOR_TEXTO_PRIMARIO, anchor="w", justify="left", wraplength=600,
            ).grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

            variable = tk.IntVar(value=-1)
            self._variables_por_pregunta[pregunta.id_pregunta] = (variable, pregunta)

            for indice_opcion, opcion in enumerate(pregunta.opciones):
                ctk.CTkRadioButton(
                    tarjeta, text=opcion.texto_opcion, variable=variable, value=opcion.id_opcion,
                    fg_color=COLOR_ACENTO_PRIMARIO, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_SECUNDARIO,
                    font=(FONT_FAMILY, 13),
                ).grid(row=1 + indice_opcion, column=0, sticky="w", padx=24, pady=(2, 10 if indice_opcion == len(pregunta.opciones) - 1 else 2))

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=2, column=0, sticky="ew", padx=24, pady=20)
        pie.grid_columnconfigure(0, weight=1)

        self._etiqueta_resultado = ctk.CTkLabel(pie, text="", font=(FONT_FAMILY, 14, "bold"))
        self._etiqueta_resultado.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pie, text="Enviar evaluación", width=180, height=44, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 14, "bold"), command=self._enviar,
        ).grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    def _enviar(self):
        respuestas = {
            id_pregunta: variable.get()
            for id_pregunta, (variable, _pregunta) in self._variables_por_pregunta.items()
            if variable.get() != -1
        }

        try:
            resultado = self._controlador.presentar_evaluacion(self._usuario_sesion.id_usuario, self._evaluacion, respuestas)
        except (IntentosAgotadosError, DatosEvaluacionInvalidosError) as error:
            self._etiqueta_resultado.configure(text=str(error), text_color=COLOR_ERROR)
            return

        if resultado.aprobado:
            texto = f"✓ Aprobado — Nota: {resultado.nota_obtenida:.1f} / 5.0"
            color = COLOR_EXITO
        else:
            texto = f"✗ No aprobado — Nota: {resultado.nota_obtenida:.1f} / 5.0 (mínimo {self._evaluacion.nota_minima_aprobar:.1f})"
            color = COLOR_ERROR

        self._etiqueta_resultado.configure(text=texto, text_color=color)
        self.after(1800, self._refrescar)
