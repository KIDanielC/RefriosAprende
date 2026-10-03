"""Ventana modal: administración de los talleres (ejercicios prácticos) de un curso y
calificación de las entregas de los aprendices (Administrador/Instructor)."""
import os
import subprocess
import sys

import customtkinter as ctk

from config.settings import (
    BASE_DIR,
    COLOR_FONDO_APP,
    FONT_FAMILY,
    COLOR_TEXTO_PRIMARIO,
    RADIO_BOTON,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_FONDO_TARJETA,
    RADIO_TARJETA,
    GROSOR_BORDE_SUTIL,
    COLOR_BORDE_SUTIL,
    COLOR_EXITO,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_ACENTO_ALTERNO,
    COLOR_ERROR,
)
from controller.taller_controller import DatosTallerInvalidosError, TallerController
from model.entities.curso import Curso
from model.entities.entrega_taller import EntregaTaller
from model.entities.taller import Taller
from view.components.editor_texto_enriquecido import EditorTextoEnriquecido

_COLOR_ESTADO = {
    "PENDIENTE": COLOR_ACENTO_ALTERNO,
    "APROBADO": COLOR_EXITO,
    "RECHAZADO": COLOR_ERROR,
}
_TEXTO_ESTADO = {
    "PENDIENTE": "Pendiente de calificar",
    "APROBADO": "✓ Aprobado",
    "RECHAZADO": "✗ Rechazado",
}


def abrir_archivo(ruta_relativa: str) -> None:
    """Abre un archivo con la aplicación predeterminada del sistema operativo."""
    ruta_absoluta = os.path.join(BASE_DIR, ruta_relativa)
    if not os.path.isfile(ruta_absoluta):
        return
    if sys.platform.startswith("win"):
        os.startfile(ruta_absoluta)
    elif sys.platform == "darwin":
        subprocess.run(["open", ruta_absoluta], check=False)
    else:
        subprocess.run(["xdg-open", ruta_absoluta], check=False)


class TalleresWindow(ctk.CTkToplevel):
    """Lista los talleres de un curso; permite crear, editar, eliminar y abrir la
    cola de calificación de entregas de cada uno."""

    def __init__(self, master, curso: Curso):
        super().__init__(master)
        self._curso = curso
        self._controlador = TallerController()

        self.title(f"Talleres — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("760x640")
        self.minsize(700, 520)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado()
        self._construir_barra_herramientas()
        self._construir_lista()
        self._cargar_talleres()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkLabel(
            self, text=f"Talleres prácticos de «{self._curso.nombre_curso}»",
            font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

    def _construir_barra_herramientas(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 8))
        ctk.CTkButton(
            barra, text="+  Nuevo taller", height=36, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 13, "bold"), command=self._abrir_formulario_creacion,
        ).pack(side="left")

    def _construir_lista(self):
        self._lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self._lista.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _cargar_talleres(self):
        for hijo in self._lista.winfo_children():
            hijo.destroy()

        talleres = self._controlador.listar_por_curso(self._curso.id_curso)
        if not talleres:
            ctk.CTkLabel(
                self._lista, text="Este curso aún no tiene talleres prácticos.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, taller in enumerate(talleres):
            self._construir_tarjeta_taller(indice, taller)

    def _construir_tarjeta_taller(self, fila: int, taller: Taller):
        tarjeta = ctk.CTkFrame(
            self._lista, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=taller.titulo, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))
        ctk.CTkLabel(
            tarjeta, text=taller.descripcion, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=680,
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        total_entregas = len(self._controlador.listar_entregas_por_taller(taller.id_taller))
        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 14))

        ctk.CTkButton(
            barra_acciones, text=f"Entregas ({total_entregas})", width=110, height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_ALTERNO,
            text_color=COLOR_ACENTO_ALTERNO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda t=taller: self._abrir_entregas(t),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Editar", width=90, height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda t=taller: self._abrir_formulario_edicion(t),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Eliminar", width=90, height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12, "bold"), command=lambda t=taller: self._eliminar_taller(t),
        ).pack(side="left")

    # ------------------------------------------------------------------
    def _eliminar_taller(self, taller: Taller):
        self._controlador.eliminar_taller(taller.id_taller)
        self._cargar_talleres()

    def _abrir_entregas(self, taller: Taller):
        EntregasTallerWindow(self, taller=taller, al_calificar=self._cargar_talleres)

    def _abrir_formulario_creacion(self):
        FormularioTaller(self, controlador=self._controlador, id_curso=self._curso.id_curso, al_guardar=self._cargar_talleres)

    def _abrir_formulario_edicion(self, taller: Taller):
        FormularioTaller(
            self, controlador=self._controlador, id_curso=self._curso.id_curso,
            al_guardar=self._cargar_talleres, taller_existente=taller,
        )


class EntregasTallerWindow(ctk.CTkToplevel):
    """Cola de calificación: lista las entregas de los aprendices para un taller, con
    acción de Aprobar/Rechazar + comentario para cada una."""

    def __init__(self, master, taller: Taller, al_calificar):
        super().__init__(master)
        self._taller = taller
        self._al_calificar = al_calificar
        self._controlador = TallerController()

        self.title(f"Entregas — {taller.titulo}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("680x600")
        self.minsize(600, 460)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_encabezado()
        self._construir_lista()
        self._cargar_entregas()

    def _construir_encabezado(self):
        ctk.CTkLabel(
            self, text=self._taller.titulo, font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

    def _construir_lista(self):
        self._lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self._lista.grid_columnconfigure(0, weight=1)

    def _cargar_entregas(self):
        for hijo in self._lista.winfo_children():
            hijo.destroy()

        entregas = self._controlador.listar_entregas_por_taller(self._taller.id_taller)
        if not entregas:
            ctk.CTkLabel(
                self._lista, text="Ningún aprendiz ha entregado este taller todavía.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, entrega in enumerate(entregas):
            self._construir_tarjeta_entrega(indice, entrega)

    def _construir_tarjeta_entrega(self, fila: int, entrega: EntregaTaller):
        tarjeta = ctk.CTkFrame(
            self._lista, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 2))
        encabezado.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            encabezado, text=entrega.nombre_usuario, font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            encabezado, text=entrega.fecha_entrega, font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="e",
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            tarjeta, text=_TEXTO_ESTADO.get(entrega.estado, entrega.estado), font=(FONT_FAMILY, 12, "bold"),
            text_color=_COLOR_ESTADO.get(entrega.estado, COLOR_TEXTO_SECUNDARIO), anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkButton(
            tarjeta, text=f"📎  Abrir {entrega.nombre_archivo_original or 'archivo'}", height=30, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_PRIMARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 11, "bold"),
            command=lambda e=entrega: abrir_archivo(e.ruta_archivo),
        ).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

        campo_comentario = ctk.CTkEntry(
            tarjeta, placeholder_text="Comentario para el aprendiz (opcional)", height=34, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        if entrega.comentario_instructor:
            campo_comentario.insert(0, entrega.comentario_instructor)
        campo_comentario.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 10))

        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=4, column=0, sticky="w", padx=16, pady=(0, 14))
        ctk.CTkButton(
            barra_acciones, text="✓  Aprobar", width=100, height=32, corner_radius=RADIO_BOTON,
            fg_color=COLOR_EXITO, hover_color=COLOR_EXITO, text_color="#FFFFFF", font=(FONT_FAMILY, 12, "bold"),
            command=lambda e=entrega, c=campo_comentario: self._calificar(e, True, c),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="✗  Rechazar", width=100, height=32, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR,
            text_color=COLOR_ERROR, font=(FONT_FAMILY, 12, "bold"),
            command=lambda e=entrega, c=campo_comentario: self._calificar(e, False, c),
        ).pack(side="left")

    def _calificar(self, entrega: EntregaTaller, aprobado: bool, campo_comentario: ctk.CTkEntry):
        self._controlador.calificar_entrega(entrega.id_entrega, aprobado, campo_comentario.get())
        self._cargar_entregas()
        self._al_calificar()


class FormularioTaller(ctk.CTkToplevel):
    """Formulario modal para crear o editar un taller (ejercicio práctico)."""

    def __init__(self, master, controlador: TallerController, id_curso: int, al_guardar, taller_existente: Taller = None):
        super().__init__(master)
        self._controlador = controlador
        self._id_curso = id_curso
        self._al_guardar = al_guardar
        self._taller_existente = taller_existente

        self.title("Editar taller" if taller_existente else "Nuevo taller")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("520x520")
        self.minsize(520, 520)
        self.resizable(True, True)
        self.grab_set()

        self._construir_formulario()
        if taller_existente:
            self._precargar_datos(taller_existente)

    def _construir_formulario(self):
        ctk.CTkLabel(
            self, text="Editar taller" if self._taller_existente else "Nuevo taller",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(24, 16), anchor="w")

        ctk.CTkLabel(
            self, text="Título", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(0, 2), anchor="w")
        self._campo_titulo = ctk.CTkEntry(
            self, width=460, height=40, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        self._campo_titulo.pack(padx=28, pady=(0, 10))

        ctk.CTkLabel(
            self, text="Instrucciones de la actividad", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(0, 2), anchor="w")
        self._campo_descripcion = EditorTextoEnriquecido(self, altura_minima_lineas=6)
        self._campo_descripcion.pack(padx=28, pady=(0, 10), fill="x")

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=460
        )
        self._etiqueta_error.pack(padx=28, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=460, height=44, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(18, 24))

    def _precargar_datos(self, taller: Taller):
        self._campo_titulo.insert(0, taller.titulo)
        self._campo_descripcion.cargar_markup(taller.descripcion)

    def _guardar(self):
        titulo = self._campo_titulo.get()
        descripcion = self._campo_descripcion.obtener_markup()

        try:
            if self._taller_existente:
                self._controlador.actualizar_taller(self._taller_existente.id_taller, titulo, descripcion)
            else:
                self._controlador.crear_taller(self._id_curso, titulo, descripcion)
        except DatosTallerInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()
