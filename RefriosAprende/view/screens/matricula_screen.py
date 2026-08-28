"""Ventana modal: gestión de matrícula (qué aprendices están asignados a un curso)."""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
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
from controller.inscripcion_controller import InscripcionController
from model.entities.curso import Curso


class MatriculaWindow(ctk.CTkToplevel):
    """Dos columnas: aprendices matriculados en el curso y aprendices disponibles para agregar."""

    def __init__(self, master, curso: Curso):
        super().__init__(master)
        self._curso = curso
        self._controlador = InscripcionController()

        self.title(f"Estudiantes — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("760x560")
        self.minsize(680, 460)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_encabezado()
        self._construir_columnas()
        self._refrescar()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkLabel(
            self, text=f"Matrícula de «{self._curso.nombre_curso}»", font=(FONT_FAMILY, 18, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=24, pady=(22, 12))

    def _construir_columnas(self):
        panel_matriculados = ctk.CTkFrame(self, fg_color="transparent")
        panel_matriculados.grid(row=1, column=0, sticky="nsew", padx=(24, 12), pady=(0, 20))
        panel_matriculados.grid_columnconfigure(0, weight=1)
        panel_matriculados.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel_matriculados, text="Matriculados", font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_ACENTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self._lista_matriculados = ctk.CTkScrollableFrame(
            panel_matriculados, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        self._lista_matriculados.grid(row=1, column=0, sticky="nsew")
        self._lista_matriculados.grid_columnconfigure(0, weight=1)

        panel_disponibles = ctk.CTkFrame(self, fg_color="transparent")
        panel_disponibles.grid(row=1, column=1, sticky="nsew", padx=(12, 24), pady=(0, 20))
        panel_disponibles.grid_columnconfigure(0, weight=1)
        panel_disponibles.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel_disponibles, text="Disponibles", font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self._lista_disponibles = ctk.CTkScrollableFrame(
            panel_disponibles, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        self._lista_disponibles.grid(row=1, column=0, sticky="nsew")
        self._lista_disponibles.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _refrescar(self):
        for hijo in self._lista_matriculados.winfo_children():
            hijo.destroy()
        for hijo in self._lista_disponibles.winfo_children():
            hijo.destroy()

        matriculados = self._controlador.listar_aprendices_matriculados(self._curso.id_curso)
        if not matriculados:
            ctk.CTkLabel(
                self._lista_matriculados, text="Ningún aprendiz matriculado todavía.", font=(FONT_FAMILY, 12),
                text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=14, padx=14)
        for indice, aprendiz in enumerate(matriculados):
            self._construir_fila(self._lista_matriculados, indice, aprendiz, "Quitar", COLOR_ERROR, self._desmatricular)

        disponibles = self._controlador.listar_aprendices_disponibles(self._curso.id_curso)
        if not disponibles:
            ctk.CTkLabel(
                self._lista_disponibles, text="No hay más aprendices disponibles.", font=(FONT_FAMILY, 12),
                text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=14, padx=14)
        for indice, aprendiz in enumerate(disponibles):
            self._construir_fila(self._lista_disponibles, indice, aprendiz, "Agregar", COLOR_ACENTO_PRIMARIO, self._matricular)

    def _construir_fila(self, contenedor, fila: int, aprendiz, texto_boton: str, color_boton: str, accion):
        marco = ctk.CTkFrame(contenedor, fg_color="transparent")
        marco.grid(row=fila, column=0, sticky="ew", padx=10, pady=6)
        marco.grid_columnconfigure(0, weight=1)

        texto = ctk.CTkFrame(marco, fg_color="transparent")
        texto.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            texto, text=aprendiz.nombre_completo, font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            texto, text=aprendiz.usuario, font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w")

        ctk.CTkButton(
            marco, text=texto_boton, width=90, height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=GROSOR_BORDE_SUTIL, border_color=color_boton,
            text_color=color_boton, font=(FONT_FAMILY, 12, "bold"),
            command=lambda a=aprendiz: accion(a),
        ).grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    def _matricular(self, aprendiz):
        self._controlador.matricular(aprendiz.id_usuario, self._curso.id_curso)
        self._refrescar()

    def _desmatricular(self, aprendiz):
        self._controlador.desmatricular(aprendiz.id_usuario, self._curso.id_curso)
        self._refrescar()
