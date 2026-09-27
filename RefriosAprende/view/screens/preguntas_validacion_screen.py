"""Ventana modal para gestionar preguntas de opción múltiple de validación de un contenido."""
import customtkinter as ctk

from config.settings import (
    COLOR_FONDO_APP,
    FONT_FAMILY,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    RADIO_BOTON,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_FONDO_TARJETA,
    RADIO_TARJETA,
    GROSOR_BORDE_SUTIL,
    COLOR_BORDE_SUTIL,
    COLOR_EXITO,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_ERROR,
)
from controller.validacion_controller import ValidacionController
from model.entities.contenido import Contenido
from model.entities.pregunta import Pregunta
from view.screens.formulario_pregunta import FormularioPregunta


class PreguntasValidacionWindow(ctk.CTkToplevel):
    """Lista y administra las preguntas de validación de un contenido específico."""

    def __init__(self, master, contenido: Contenido):
        super().__init__(master)
        self._contenido = contenido
        self._controlador = ValidacionController()

        self.title(f"Preguntas de validación — {contenido.titulo}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("700x600")
        self.minsize(700, 500)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado()
        self._construir_barra_herramientas()
        self._construir_lista()
        self._cargar_preguntas()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkLabel(
            self, text=f"Validación de conocimiento: «{self._contenido.titulo}»",
            font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            self, text="Preguntas de opción múltiple para reforzar este tema (no es la evaluación final del curso).",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 12))

    def _construir_barra_herramientas(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="e", padx=24, pady=(0, 8))
        ctk.CTkButton(
            barra, text="+  Nueva pregunta", height=36, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self._abrir_formulario_creacion,
        ).pack(side="right")

    def _construir_lista(self):
        self._lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self._lista.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _cargar_preguntas(self):
        for hijo in self._lista.winfo_children():
            hijo.destroy()

        preguntas = self._controlador.listar_preguntas(self._contenido)
        if not preguntas:
            ctk.CTkLabel(
                self._lista, text="Este contenido aún no tiene preguntas de validación.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, pregunta in enumerate(preguntas):
            self._construir_tarjeta_pregunta(indice, pregunta)

    def _construir_tarjeta_pregunta(self, fila: int, pregunta: Pregunta):
        tarjeta = ctk.CTkFrame(
            self._lista, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=f"{pregunta.orden}. {pregunta.enunciado}", font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w", justify="left", wraplength=600,
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))

        for indice_opcion, opcion in enumerate(pregunta.opciones):
            color_texto = COLOR_EXITO if opcion.es_correcta else COLOR_TEXTO_SECUNDARIO
            marca = "✓" if opcion.es_correcta else "○"
            ctk.CTkLabel(
                tarjeta, text=f"   {marca}  {opcion.texto_opcion}", font=(FONT_FAMILY, 12),
                text_color=color_texto, anchor="w",
            ).grid(row=1 + indice_opcion, column=0, sticky="ew", padx=18)

        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=1 + len(pregunta.opciones), column=0, sticky="w", padx=18, pady=(10, 14))

        ctk.CTkButton(
            barra_acciones, text="Editar", width=90, height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda p=pregunta: self._abrir_formulario_edicion(p),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Eliminar", width=90, height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12, "bold"), command=lambda p=pregunta: self._eliminar_pregunta(p),
        ).pack(side="left")

    # ------------------------------------------------------------------
    def _eliminar_pregunta(self, pregunta: Pregunta):
        self._controlador.eliminar_pregunta(pregunta.id_pregunta)
        self._cargar_preguntas()

    def _abrir_formulario_creacion(self):
        FormularioPregunta(
            self,
            guardar_pregunta=lambda enunciado, opciones: self._controlador.crear_pregunta(
                self._contenido, enunciado, opciones
            ),
            al_guardar=self._cargar_preguntas,
        )

    def _abrir_formulario_edicion(self, pregunta: Pregunta):
        FormularioPregunta(
            self,
            guardar_pregunta=lambda enunciado, opciones: self._controlador.actualizar_pregunta(
                pregunta.id_pregunta, enunciado, opciones
            ),
            al_guardar=self._cargar_preguntas, pregunta_existente=pregunta,
        )
