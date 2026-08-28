"""Ventana modal: administración de la evaluación final de un curso (Administrador)."""
import customtkinter as ctk

from config.settings import (
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
from controller.evaluacion_controller import DatosEvaluacionInvalidosError, EvaluacionController
from model.entities.curso import Curso
from model.entities.evaluacion import Evaluacion
from model.entities.pregunta import Pregunta
from view.screens.formulario_pregunta import FormularioPregunta


class EvaluacionFinalWindow(ctk.CTkToplevel):
    """Muestra el formulario de configuración si no existe evaluación final,
    o la gestión de preguntas si ya fue creada."""

    def __init__(self, master, curso: Curso):
        super().__init__(master)
        self._curso = curso
        self._controlador = EvaluacionController()

        self.title(f"Evaluación final — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("700x620")
        self.minsize(650, 500)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._refrescar()

    # ------------------------------------------------------------------
    def _refrescar(self):
        for hijo in self.winfo_children():
            hijo.destroy()

        evaluacion = self._controlador.obtener_evaluacion_final(self._curso.id_curso)
        if evaluacion is None:
            self._construir_formulario_configuracion()
        else:
            self._construir_gestion_preguntas(evaluacion)

    # -- Sin evaluación aún: crearla ---------------------------------------
    def _construir_formulario_configuracion(self):
        contenedor = ctk.CTkFrame(self, fg_color=COLOR_FONDO_APP, corner_radius=0)
        contenedor.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            contenedor, text=f"«{self._curso.nombre_curso}» todavía no tiene evaluación final",
            font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(28, 4), anchor="w")
        ctk.CTkLabel(
            contenedor, text="Configúrala para poder agregarle preguntas.",
            font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(padx=28, pady=(0, 20), anchor="w")

        campo_titulo = self._crear_campo(contenedor, "Título de la evaluación")
        campo_titulo.insert(0, f"Evaluación final: {self._curso.nombre_curso}")

        campo_nota_minima = self._crear_campo(contenedor, "Nota mínima para aprobar (escala 0 a 5)")
        campo_nota_minima.insert(0, "3.0")

        campo_intentos = self._crear_campo(contenedor, "Intentos permitidos")
        campo_intentos.insert(0, "2")

        etiqueta_error = ctk.CTkLabel(contenedor, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR)
        etiqueta_error.pack(padx=28, pady=(6, 0), anchor="w")

        def _crear():
            try:
                nota_minima = float(campo_nota_minima.get().replace(",", "."))
                intentos = int(campo_intentos.get())
            except ValueError:
                etiqueta_error.configure(text="La nota mínima y los intentos deben ser numéricos.")
                return

            try:
                self._controlador.crear_evaluacion_final(self._curso.id_curso, campo_titulo.get(), nota_minima, intentos)
            except DatosEvaluacionInvalidosError as error:
                etiqueta_error.configure(text=str(error))
                return

            self._refrescar()

        ctk.CTkButton(
            contenedor, text="Crear evaluación final", width=380, height=44, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=_crear,
        ).pack(padx=28, pady=(16, 24))

    def _crear_campo(self, contenedor, etiqueta: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            contenedor, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            contenedor, width=380, height=40, corner_radius=4, fg_color=COLOR_FONDO_TARJETA,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        campo.pack(padx=28, pady=(0, 2))
        return campo

    # -- Evaluación existente: gestión de preguntas -------------------------
    def _construir_gestion_preguntas(self, evaluacion: Evaluacion):
        self.grid_rowconfigure(2, weight=1)

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            encabezado, text=evaluacion.titulo, font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(anchor="w")
        ctk.CTkLabel(
            encabezado,
            text=f"Nota mínima para aprobar: {evaluacion.nota_minima_aprobar:.1f} / 5.0  ·  Intentos permitidos: {evaluacion.intentos_permitidos}",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", pady=(4, 0))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=24, pady=(8, 8))
        ctk.CTkButton(
            barra, text="+  Nueva pregunta", height=36, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"),
            command=lambda: FormularioPregunta(
                self,
                guardar_pregunta=lambda enunciado, opciones: self._controlador.crear_pregunta(
                    evaluacion.id_evaluacion, enunciado, opciones
                ),
                al_guardar=self._refrescar,
            ),
        ).pack(side="left")
        ctk.CTkButton(
            barra, text="Eliminar evaluación", height=36, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color="#FBE1E4", border_width=1, border_color=COLOR_ERROR,
            text_color=COLOR_ERROR, font=(FONT_FAMILY, 13, "bold"),
            command=lambda: self._eliminar_evaluacion(evaluacion),
        ).pack(side="left", padx=8)

        lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        lista.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        lista.grid_columnconfigure(0, weight=1)

        preguntas = self._controlador.listar_preguntas(evaluacion.id_evaluacion)
        if not preguntas:
            ctk.CTkLabel(
                lista, text="Todavía no hay preguntas. Los aprendices no podrán presentar la evaluación hasta que agregues al menos una.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO, wraplength=600, justify="left",
            ).grid(row=0, column=0, pady=20)
            return

        for indice, pregunta in enumerate(preguntas):
            self._construir_tarjeta_pregunta(lista, indice, pregunta, evaluacion)

    def _construir_tarjeta_pregunta(self, contenedor, fila: int, pregunta: Pregunta, evaluacion: Evaluacion):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_BORDE_SUTIL
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=f"{pregunta.orden}. {pregunta.enunciado}", font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w", justify="left", wraplength=580,
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

        for indice_opcion, opcion in enumerate(pregunta.opciones):
            color = COLOR_EXITO if opcion.es_correcta else COLOR_TEXTO_SECUNDARIO
            marca = "✓" if opcion.es_correcta else "○"
            ctk.CTkLabel(
                tarjeta, text=f"   {marca}  {opcion.texto_opcion}", font=(FONT_FAMILY, 12), text_color=color, anchor="w",
            ).grid(row=1 + indice_opcion, column=0, sticky="ew", padx=16)

        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=1 + len(pregunta.opciones), column=0, sticky="w", padx=16, pady=(8, 12))

        ctk.CTkButton(
            barra_acciones, text="Editar", width=90, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda: FormularioPregunta(
                self,
                guardar_pregunta=lambda enunciado, opciones: self._controlador.actualizar_pregunta(
                    pregunta.id_pregunta, enunciado, opciones
                ),
                al_guardar=self._refrescar, pregunta_existente=pregunta,
            ),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Eliminar", width=90, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12, "bold"),
            command=lambda: self._eliminar_pregunta(pregunta),
        ).pack(side="left")

    def _eliminar_pregunta(self, pregunta: Pregunta):
        self._controlador.eliminar_pregunta(pregunta.id_pregunta)
        self._refrescar()

    def _eliminar_evaluacion(self, evaluacion: Evaluacion):
        self._controlador.eliminar_evaluacion_final(evaluacion.id_evaluacion)
        self._refrescar()
