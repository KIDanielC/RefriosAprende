"""Ventana modal: administración de los casos de simulación de un curso (Administrador)."""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
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
)
from controller.simulacion_controller import DatosSimulacionInvalidosError, SimulacionController
from model.entities.curso import Curso
from model.entities.evaluacion import Evaluacion
from model.entities.pregunta import Pregunta
from model.entities.simulacion import Simulacion
from view.screens.formulario_pregunta import FormularioPregunta


class SimulacionesWindow(ctk.CTkToplevel):
    """Lista los casos de simulación de un curso; permite crear, editar, eliminar
    y gestionar las preguntas de diagnóstico de cada caso."""

    def __init__(self, master, curso: Curso):
        super().__init__(master)
        self._curso = curso
        self._controlador = SimulacionController()

        self.title(f"Simulaciones — {curso.nombre_curso}")
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
        self._cargar_casos()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkLabel(
            self, text=f"Casos de diagnóstico de «{self._curso.nombre_curso}»",
            font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

    def _construir_barra_herramientas(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 8))
        ctk.CTkButton(
            barra, text="+  Nuevo caso", height=36, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self._abrir_formulario_creacion,
        ).pack(side="left")

    def _construir_lista(self):
        self._lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self._lista.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _cargar_casos(self):
        for hijo in self._lista.winfo_children():
            hijo.destroy()

        casos = self._controlador.listar_casos_por_curso(self._curso.id_curso)
        if not casos:
            ctk.CTkLabel(
                self._lista, text="Este curso aún no tiene casos de simulación.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, (evaluacion, simulacion) in enumerate(casos):
            self._construir_tarjeta_caso(indice, evaluacion, simulacion)

    def _construir_tarjeta_caso(self, fila: int, evaluacion: Evaluacion, simulacion: Simulacion):
        tarjeta = ctk.CTkFrame(
            self._lista, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_BORDE_SUTIL
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=simulacion.titulo_caso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))
        ctk.CTkLabel(
            tarjeta, text=simulacion.descripcion_escenario, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=680,
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 6))
        ctk.CTkLabel(
            tarjeta, text=f"Diagnóstico esperado: {simulacion.diagnostico_correcto}", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_EXITO, anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))

        total_preguntas = len(self._controlador.listar_preguntas(evaluacion.id_evaluacion))
        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 14))

        ctk.CTkButton(
            barra_acciones, text=f"Preguntas ({total_preguntas})", width=110, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_ALTERNO,
            text_color=COLOR_ACENTO_ALTERNO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda e=evaluacion: self._abrir_preguntas(e),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Editar", width=90, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda s=simulacion: self._abrir_formulario_edicion(s),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Eliminar", width=90, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12, "bold"), command=lambda e=evaluacion: self._eliminar_caso(e),
        ).pack(side="left")

    # ------------------------------------------------------------------
    def _eliminar_caso(self, evaluacion: Evaluacion):
        self._controlador.eliminar_caso(evaluacion.id_evaluacion)
        self._cargar_casos()

    def _abrir_preguntas(self, evaluacion: Evaluacion):
        PreguntasCasoWindow(self, controlador=self._controlador, evaluacion=evaluacion)

    def _abrir_formulario_creacion(self):
        FormularioCaso(self, controlador=self._controlador, id_curso=self._curso.id_curso, al_guardar=self._cargar_casos)

    def _abrir_formulario_edicion(self, simulacion: Simulacion):
        FormularioCaso(
            self, controlador=self._controlador, id_curso=self._curso.id_curso,
            al_guardar=self._cargar_casos, simulacion_existente=simulacion,
        )


class PreguntasCasoWindow(ctk.CTkToplevel):
    """Gestión de preguntas de diagnóstico (opción múltiple) de un caso de simulación."""

    def __init__(self, master, controlador: SimulacionController, evaluacion: Evaluacion):
        super().__init__(master)
        self._controlador = controlador
        self._evaluacion = evaluacion

        self.title(f"Preguntas — {evaluacion.titulo}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("620x560")
        self.minsize(560, 460)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._refrescar()

    def _refrescar(self):
        for hijo in self.winfo_children():
            hijo.destroy()

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 8))
        ctk.CTkButton(
            barra, text="+  Nueva pregunta", height=34, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 12, "bold"),
            command=lambda: FormularioPregunta(
                self,
                guardar_pregunta=lambda enunciado, opciones: self._controlador.crear_pregunta(
                    self._evaluacion.id_evaluacion, enunciado, opciones
                ),
                al_guardar=self._refrescar,
            ),
        ).pack(side="left")

        lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        lista.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        lista.grid_columnconfigure(0, weight=1)

        preguntas = self._controlador.listar_preguntas(self._evaluacion.id_evaluacion)
        if not preguntas:
            ctk.CTkLabel(
                lista, text="Este caso todavía no tiene preguntas de diagnóstico.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, pregunta in enumerate(preguntas):
            self._construir_tarjeta_pregunta(lista, indice, pregunta)

    def _construir_tarjeta_pregunta(self, contenedor, fila: int, pregunta: Pregunta):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_BORDE_SUTIL
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=f"{pregunta.orden}. {pregunta.enunciado}", font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w", justify="left", wraplength=500,
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))

        for indice_opcion, opcion in enumerate(pregunta.opciones):
            color = COLOR_EXITO if opcion.es_correcta else COLOR_TEXTO_SECUNDARIO
            marca = "✓" if opcion.es_correcta else "○"
            ctk.CTkLabel(
                tarjeta, text=f"   {marca}  {opcion.texto_opcion}", font=(FONT_FAMILY, 11), text_color=color, anchor="w",
            ).grid(row=1 + indice_opcion, column=0, sticky="ew", padx=14)

        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=1 + len(pregunta.opciones), column=0, sticky="w", padx=14, pady=(6, 10))
        ctk.CTkButton(
            barra_acciones, text="Editar", width=80, height=28, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 11, "bold"),
            command=lambda: FormularioPregunta(
                self,
                guardar_pregunta=lambda enunciado, opciones: self._controlador.actualizar_pregunta(
                    pregunta.id_pregunta, enunciado, opciones
                ),
                al_guardar=self._refrescar, pregunta_existente=pregunta,
            ),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            barra_acciones, text="Eliminar", width=80, height=28, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 11, "bold"),
            command=lambda: self._eliminar_pregunta(pregunta),
        ).pack(side="left")

    def _eliminar_pregunta(self, pregunta: Pregunta):
        self._controlador.eliminar_pregunta(pregunta.id_pregunta)
        self._refrescar()


class FormularioCaso(ctk.CTkToplevel):
    """Formulario modal para crear o editar un caso clínico de simulación."""

    def __init__(self, master, controlador: SimulacionController, id_curso: int, al_guardar, simulacion_existente: Simulacion = None):
        super().__init__(master)
        self._controlador = controlador
        self._id_curso = id_curso
        self._al_guardar = al_guardar
        self._simulacion_existente = simulacion_existente

        self.title("Editar caso" if simulacion_existente else "Nuevo caso de simulación")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("520x600")
        self.minsize(520, 600)
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        if simulacion_existente:
            self._precargar_datos(simulacion_existente)

    def _construir_formulario(self):
        ctk.CTkLabel(
            self, text="Editar caso" if self._simulacion_existente else "Nuevo caso de simulación",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(24, 16), anchor="w")

        self._campo_titulo = self._crear_campo("Título del caso")

        ctk.CTkLabel(
            self, text="Descripción del escenario clínico", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        self._campo_escenario = ctk.CTkTextbox(
            self, width=460, height=140, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 13),
        )
        self._campo_escenario.pack(padx=28, pady=(0, 10))

        self._campo_diagnostico = self._crear_campo("Diagnóstico correcto (referencia)")

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=460
        )
        self._etiqueta_error.pack(padx=28, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=460, height=44, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(18, 24))

    def _crear_campo(self, etiqueta: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            self, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            self, width=460, height=40, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        campo.pack(padx=28, pady=(0, 2))
        return campo

    def _precargar_datos(self, simulacion: Simulacion):
        self._campo_titulo.insert(0, simulacion.titulo_caso)
        self._campo_escenario.insert("1.0", simulacion.descripcion_escenario)
        self._campo_diagnostico.insert(0, simulacion.diagnostico_correcto)

    def _guardar(self):
        titulo = self._campo_titulo.get()
        escenario = self._campo_escenario.get("1.0", "end").strip()
        diagnostico = self._campo_diagnostico.get()

        try:
            if self._simulacion_existente:
                self._controlador.actualizar_caso(self._simulacion_existente, titulo, escenario, diagnostico)
            else:
                self._controlador.crear_caso(self._id_curso, titulo, escenario, diagnostico)
        except DatosSimulacionInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()
