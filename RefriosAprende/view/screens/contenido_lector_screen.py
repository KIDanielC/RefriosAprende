"""Pantalla del Aprendiz: lectura de contenidos de un curso y acceso al cuestionario de validación."""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
)
from controller.contenido_controller import ContenidoController
from controller.validacion_controller import ValidacionController
from model.entities.contenido import Contenido
from model.entities.curso import Curso
from view.screens.responder_quiz_screen import ResponderQuizWindow


class ContenidoLectorScreen(ctk.CTkFrame):
    """Lista los contenidos de un curso en modo lectura, con acceso al cuestionario de validación."""

    def __init__(self, master, curso: Curso, al_volver):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._curso = curso
        self._al_volver = al_volver
        self._controlador = ContenidoController()
        self._validacion_controlador = ValidacionController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado()
        self._construir_lista()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkButton(
            self, text="←  Volver a mis cursos", fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            text_color=COLOR_ACENTO_SECUNDARIO, font=(FONT_FAMILY, 13, "bold"), width=170, height=32,
            command=self._al_volver,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 4))

        ctk.CTkLabel(
            self, text=self._curso.nombre_curso, font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(4, 12))

    def _construir_lista(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        contenedor.grid_columnconfigure(0, weight=1)

        contenidos = self._controlador.listar_por_curso(self._curso.id_curso)
        if not contenidos:
            ctk.CTkLabel(
                contenedor, text="Este curso aún no tiene contenidos publicados.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, contenido in enumerate(contenidos):
            self._construir_tarjeta_contenido(contenedor, indice, contenido)

    def _construir_tarjeta_contenido(self, contenedor, fila: int, contenido: Contenido):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=4,
            border_width=1, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=f"{contenido.orden}. {contenido.titulo}", font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            tarjeta, text=contenido.contenido_texto, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=760,
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))

        total_preguntas = len(self._validacion_controlador.listar_preguntas(contenido))
        if total_preguntas > 0:
            ctk.CTkButton(
                tarjeta, text=f"Responder preguntas de validación ({total_preguntas})", height=34, corner_radius=4,
                fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_ALTERNO,
                text_color=COLOR_ACENTO_ALTERNO, font=(FONT_FAMILY, 12, "bold"),
                command=lambda c=contenido: self._abrir_quiz(c),
            ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 14))

    # ------------------------------------------------------------------
    def _abrir_quiz(self, contenido: Contenido):
        ResponderQuizWindow(self, contenido=contenido)
