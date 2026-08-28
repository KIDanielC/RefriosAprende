"""Ventana modal: Guía de Aprendizaje de un curso (edición para el administrador,
solo lectura para el aprendiz)."""
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
from controller.guia_aprendizaje_controller import DatosGuiaInvalidosError, GuiaAprendizajeController
from model.entities.curso import Curso

_CAMPOS = (
    ("objetivo_general", "Objetivo general"),
    ("objetivos_especificos", "Objetivos específicos"),
    ("competencias", "Competencias a desarrollar"),
    ("actividades", "Actividades de aprendizaje"),
    ("criterios_evaluacion", "Criterios de evaluación"),
)


class GuiaAprendizajeWindow(ctk.CTkToplevel):
    """Formulario editable (administrador) o vista de solo lectura (aprendiz)."""

    def __init__(self, master, curso: Curso, solo_lectura: bool = False):
        super().__init__(master)
        self._curso = curso
        self._solo_lectura = solo_lectura
        self._controlador = GuiaAprendizajeController()
        self._cajas_texto = {}

        self.title(f"Guía de aprendizaje — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("640x680")
        self.minsize(560, 520)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        guia = self._controlador.obtener_guia(self._curso.id_curso)

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 10))
        ctk.CTkLabel(
            encabezado, text=self._curso.nombre_curso, font=(FONT_FAMILY, 18, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            encabezado, text="Guía de aprendizaje", font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        if guia is None and self._solo_lectura:
            ctk.CTkLabel(
                self, text="Este curso todavía no tiene una guía de aprendizaje publicada.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=1, column=0, padx=24, pady=20)
            return

        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=1, column=0, sticky="nsew", padx=24)
        contenedor.grid_columnconfigure(0, weight=1)

        self._campo_duracion = self._construir_campo_duracion(contenedor, guia)

        for clave, etiqueta in _CAMPOS:
            valor = getattr(guia, clave, "") if guia else ""
            self._cajas_texto[clave] = self._construir_seccion(contenedor, etiqueta, valor or "")

        if not self._solo_lectura:
            pie = ctk.CTkFrame(self, fg_color="transparent")
            pie.grid(row=2, column=0, sticky="ew", padx=24, pady=18)
            pie.grid_columnconfigure(0, weight=1)

            self._etiqueta_estado = ctk.CTkLabel(pie, text="", font=(FONT_FAMILY, 12, "bold"))
            self._etiqueta_estado.grid(row=0, column=0, sticky="w")

            ctk.CTkButton(
                pie, text="Guardar guía", width=160, height=42, corner_radius=RADIO_BOTON,
                fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
                text_color="#FFFFFF", font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
            ).grid(row=0, column=1, sticky="e")

    def _construir_campo_duracion(self, contenedor, guia):
        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        fila.pack(fill="x", pady=(4, 12))
        ctk.CTkLabel(
            fila, text="Duración estimada (horas)", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(0, 6))
        campo = ctk.CTkEntry(
            fila, width=140, height=38, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_TARJETA,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13), state="disabled" if self._solo_lectura else "normal",
        )
        campo.pack(anchor="w")
        if guia and guia.duracion_horas:
            campo.configure(state="normal")
            campo.insert(0, str(guia.duracion_horas))
            if self._solo_lectura:
                campo.configure(state="disabled")
        return campo

    def _construir_seccion(self, contenedor, etiqueta: str, valor: str) -> ctk.CTkTextbox:
        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        fila.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(
            fila, text=etiqueta, font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        if self._solo_lectura:
            tarjeta = ctk.CTkFrame(
                fila, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
                border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.pack(fill="x")
            ctk.CTkLabel(
                tarjeta, text=valor or "Sin definir.", font=(FONT_FAMILY, 13),
                text_color=COLOR_TEXTO_PRIMARIO, anchor="w", justify="left", wraplength=540,
            ).pack(anchor="w", padx=16, pady=12)
            return None

        caja = ctk.CTkTextbox(
            fila, height=80, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_TARJETA,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13), wrap="word",
        )
        caja.pack(fill="x")
        if valor:
            caja.insert("1.0", valor)
        return caja

    # ------------------------------------------------------------------
    def _guardar(self):
        valores = {clave: caja.get("1.0", "end").strip() for clave, caja in self._cajas_texto.items()}
        duracion = self._campo_duracion.get()

        try:
            self._controlador.guardar_guia(
                self._curso.id_curso,
                valores["objetivo_general"],
                valores["objetivos_especificos"],
                valores["competencias"],
                valores["actividades"],
                valores["criterios_evaluacion"],
                duracion,
            )
        except DatosGuiaInvalidosError as error:
            self._etiqueta_estado.configure(text=str(error), text_color=COLOR_ERROR)
            return

        self._etiqueta_estado.configure(text="✓ Guía guardada correctamente", text_color=COLOR_EXITO)
