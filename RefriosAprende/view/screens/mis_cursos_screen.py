"""Pantalla del Aprendiz: navegar cursos activos y estudiar su contenido."""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
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
from controller.curso_controller import CursoController
from controller.progreso_controller import ProgresoController
from model.entities.curso import Curso
from view.screens.contenido_lector_screen import ContenidoLectorScreen
from view.screens.guia_aprendizaje_screen import GuiaAprendizajeWindow


class MisCursosScreen(ctk.CTkFrame):
    """Lista de cursos activos disponibles para el aprendiz."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._controlador = CursoController()
        self._progreso_controlador = ProgresoController()
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
            self._frame_interno, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=8)
        tarjeta.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 4))
        encabezado.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            encabezado, text=curso.nombre_curso, font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        progreso = self._progreso_controlador.obtener_progreso(self._usuario_sesion.id_usuario, curso.id_curso)
        porcentaje = progreso.porcentaje_avance if progreso else 0.0
        color_insignia = COLOR_EXITO if porcentaje >= 100 else COLOR_ACENTO_PRIMARIO
        insignia = ctk.CTkFrame(encabezado, fg_color=COLOR_FONDO_TARJETA_HOVER, corner_radius=99)
        insignia.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            insignia, text=f"{porcentaje:.0f}% completado", font=(FONT_FAMILY, 11, "bold"), text_color=color_insignia,
        ).pack(padx=12, pady=4)

        ctk.CTkLabel(
            tarjeta, text=f"Instructor: {curso.nombre_instructor}", font=(FONT_FAMILY, 12),
            text_color=COLOR_ACENTO_ALTERNO, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20)

        descripcion = curso.descripcion or "Sin descripción."
        ctk.CTkLabel(
            tarjeta, text=descripcion, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=700,
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(6, 10))

        barra = ctk.CTkProgressBar(
            tarjeta, height=8, corner_radius=99, fg_color=COLOR_BORDE_SUTIL, progress_color=color_insignia,
        )
        barra.set(porcentaje / 100)
        barra.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 14))

        fila_botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_botones.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 16))

        ctk.CTkButton(
            fila_botones, text="Ver contenido del curso", height=36, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 13, "bold"),
            command=lambda c=curso: self._mostrar_contenido(c),
        ).pack(side="left")

        ctk.CTkButton(
            fila_botones, text="Guía de aprendizaje", height=36, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_ALTERNO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 13, "bold"),
            command=lambda c=curso: GuiaAprendizajeWindow(self, curso=c, solo_lectura=True),
        ).pack(side="left", padx=(10, 0))

    # ------------------------------------------------------------------
    def _mostrar_contenido(self, curso: Curso):
        if self._frame_interno is not None:
            self._frame_interno.destroy()

        self._frame_interno = ContenidoLectorScreen(
            self, curso=curso, usuario_sesion=self._usuario_sesion, al_volver=self._mostrar_lista_cursos
        )
        self._frame_interno.grid(row=0, column=0, sticky="nsew")
