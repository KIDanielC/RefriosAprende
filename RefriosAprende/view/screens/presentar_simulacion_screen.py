"""Ventanas modales: el aprendiz practica los casos de simulación de un curso."""
import tkinter as tk

import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_ALTERNO_GLOW,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
)
from controller.simulacion_controller import DatosSimulacionInvalidosError, SimulacionController
from model.entities.curso import Curso
from model.entities.evaluacion import Evaluacion
from model.entities.simulacion import Simulacion
from model.entities.usuario import Usuario


class ListaSimulacionesWindow(ctk.CTkToplevel):
    """Lista los casos de simulación disponibles en un curso para que el aprendiz elija cuál practicar."""

    def __init__(self, master, curso: Curso, usuario_sesion: Usuario):
        super().__init__(master)
        self._curso = curso
        self._usuario_sesion = usuario_sesion
        self._controlador = SimulacionController()

        self.title(f"Simulaciones — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("680x560")
        self.minsize(600, 460)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text=f"Casos de diagnóstico de «{curso.nombre_curso}»", font=(FONT_FAMILY, 17, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        contenedor.grid_columnconfigure(0, weight=1)

        casos = self._controlador.listar_casos_por_curso(curso.id_curso)
        for indice, (evaluacion, simulacion) in enumerate(casos):
            self._construir_tarjeta_caso(contenedor, indice, evaluacion, simulacion)

    def _construir_tarjeta_caso(self, contenedor, fila: int, evaluacion: Evaluacion, simulacion: Simulacion):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=8)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=simulacion.titulo_caso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))
        ctk.CTkLabel(
            tarjeta, text=simulacion.descripcion_escenario, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=580,
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        ctk.CTkButton(
            tarjeta, text="Practicar este caso", height=34, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_ALTERNO, hover_color=COLOR_ACENTO_ALTERNO_GLOW,
            text_color="#FFFFFF",
            font=(FONT_FAMILY, 12, "bold"),
            command=lambda e=evaluacion, s=simulacion: PresentarCasoWindow(
                self, evaluacion=e, simulacion=s, usuario_sesion=self._usuario_sesion
            ),
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 14))


class PresentarCasoWindow(ctk.CTkToplevel):
    """Resuelve un caso clínico: muestra el escenario y sus preguntas de diagnóstico."""

    def __init__(self, master, evaluacion: Evaluacion, simulacion: Simulacion, usuario_sesion: Usuario):
        super().__init__(master)
        self._evaluacion = evaluacion
        self._simulacion = simulacion
        self._usuario_sesion = usuario_sesion
        self._controlador = SimulacionController()
        self._variables_por_pregunta = {}

        self.title(simulacion.titulo_caso)
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("700x640")
        self.minsize(600, 480)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir()

    def _construir(self):
        encabezado = ctk.CTkFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_ALTERNO,
        )
        encabezado.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        ctk.CTkLabel(
            encabezado, text=self._simulacion.titulo_caso, font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
            anchor="w",
        ).pack(padx=16, pady=(14, 4), anchor="w")
        ctk.CTkLabel(
            encabezado, text=self._simulacion.descripcion_escenario, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=600,
        ).pack(padx=16, pady=(0, 14), anchor="w")

        preguntas = self._controlador.listar_preguntas(self._evaluacion.id_evaluacion)

        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=1, column=0, sticky="nsew", padx=24)
        contenedor.grid_columnconfigure(0, weight=1)

        if not preguntas:
            ctk.CTkLabel(
                contenedor, text="Este caso todavía no tiene preguntas de diagnóstico.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
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
            self._variables_por_pregunta[pregunta.id_pregunta] = variable

            for indice_opcion, opcion in enumerate(pregunta.opciones):
                ctk.CTkRadioButton(
                    tarjeta, text=opcion.texto_opcion, variable=variable, value=opcion.id_opcion,
                    fg_color=COLOR_ACENTO_PRIMARIO, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_SECUNDARIO,
                    font=(FONT_FAMILY, 13),
                ).grid(row=1 + indice_opcion, column=0, sticky="w", padx=24, pady=2)

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=2, column=0, sticky="ew", padx=24, pady=20)
        pie.grid_columnconfigure(0, weight=1)

        self._etiqueta_resultado = ctk.CTkLabel(pie, text="", font=(FONT_FAMILY, 14, "bold"))
        self._etiqueta_resultado.grid(row=0, column=0, sticky="w")

        if preguntas:
            ctk.CTkButton(
                pie, text="Diagnosticar", width=160, height=42, corner_radius=RADIO_BOTON,
                fg_color=COLOR_ACENTO_ALTERNO, hover_color=COLOR_ACENTO_ALTERNO_GLOW,
                text_color="#FFFFFF",
                font=(FONT_FAMILY, 14, "bold"), command=self._enviar,
            ).grid(row=0, column=1, sticky="e")

    def _enviar(self):
        respuestas = {
            id_pregunta: variable.get() for id_pregunta, variable in self._variables_por_pregunta.items() if variable.get() != -1
        }

        try:
            resultado = self._controlador.presentar_caso(self._usuario_sesion.id_usuario, self._evaluacion, respuestas)
        except DatosSimulacionInvalidosError as error:
            self._etiqueta_resultado.configure(text=str(error), text_color=COLOR_ERROR)
            return

        if resultado.aprobado:
            texto = f"✓ Diagnóstico acertado — Nota: {resultado.nota_obtenida:.1f} / 5.0"
            color = COLOR_EXITO
        else:
            texto = f"✗ Diagnóstico incorrecto — Nota: {resultado.nota_obtenida:.1f} / 5.0. El diagnóstico correcto era: {self._simulacion.diagnostico_correcto}"
            color = COLOR_ERROR

        self._etiqueta_resultado.configure(text=texto, text_color=color)
