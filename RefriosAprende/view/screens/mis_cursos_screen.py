"""Pantalla del Aprendiz: navegar cursos activos y estudiar su contenido."""
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
from controller.curso_controller import CursoController
from model.entities.curso import Curso
from view.screens.contenido_lector_screen import ContenidoLectorScreen


class MisCursosScreen(ctk.CTkFrame):
    """Lista de cursos activos disponibles para el aprendiz."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._controlador = CursoController()
        self._frame_interno = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._mostrar_lista_cursos()

    # ------------------------------------------------------------------
    def _mostrar_lista_cursos(self):
        if self._frame_interno is not None:
            self._frame_interno.destroy()

        self._frame_interno = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._frame_interno.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self._frame_interno.grid_columnconfigure(0, weight=1)

        cursos = self._controlador.listar_cursos_activos()
        if not cursos:
            ctk.CTkLabel(
                self._frame_interno, text="Todavía no hay cursos disponibles.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, curso in enumerate(cursos):
            self._construir_tarjeta_curso(indice, curso)

    def _construir_tarjeta_curso(self, fila: int, curso: Curso):
        tarjeta = ctk.CTkFrame(
            self._frame_interno, fg_color=COLOR_FONDO_TARJETA, corner_radius=4,
            border_width=2, border_color=COLOR_ACENTO_PRIMARIO,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=8)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=curso.nombre_curso, font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            tarjeta, text=f"Instructor: {curso.nombre_instructor}", font=(FONT_FAMILY, 12),
            text_color=COLOR_ACENTO_ALTERNO, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20)

        descripcion = curso.descripcion or "Sin descripción."
        ctk.CTkLabel(
            tarjeta, text=descripcion, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=700,
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(6, 14))

        ctk.CTkButton(
            tarjeta, text="Ver contenido del curso", height=36, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 13, "bold"),
            command=lambda c=curso: self._mostrar_contenido(c),
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 16))

    # ------------------------------------------------------------------
    def _mostrar_contenido(self, curso: Curso):
        if self._frame_interno is not None:
            self._frame_interno.destroy()

        self._frame_interno = ContenidoLectorScreen(self, curso=curso, al_volver=self._mostrar_lista_cursos)
        self._frame_interno.grid(row=0, column=0, sticky="nsew")
