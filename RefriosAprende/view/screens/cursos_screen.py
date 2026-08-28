"""Pantalla de Gestión de Cursos (CRUD) con acceso a la gestión de sus contenidos."""
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
)
from controller.curso_controller import CursoController, DatosCursoInvalidosError
from model.entities.curso import Curso
from view.screens.contenidos_screen import ContenidosScreen
from view.screens.evaluacion_final_screen import EvaluacionFinalWindow
from view.screens.guia_aprendizaje_screen import GuiaAprendizajeWindow
from view.screens.simulaciones_screen import SimulacionesWindow


class CursosScreen(ctk.CTkFrame):
    """Sección completa de gestión de cursos: tabla + acciones + acceso a contenidos."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._controlador = CursoController()
        self._curso_seleccionado: Curso | None = None
        self._texto_filtro = tk.StringVar()
        self._frame_interno = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._mostrar_lista_cursos()

    # ------------------------------------------------------------------
    def _mostrar_lista_cursos(self):
        if self._frame_interno is not None:
            self._frame_interno.destroy()

        self._frame_interno = ctk.CTkFrame(self, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._frame_interno.grid(row=0, column=0, sticky="nsew")
        self._frame_interno.grid_columnconfigure(0, weight=1)
        self._frame_interno.grid_rowconfigure(2, weight=1)

        self._construir_barra_herramientas(self._frame_interno)
        self._construir_barra_acciones(self._frame_interno)
        self._construir_tabla(self._frame_interno)
        self._cargar_cursos()

    def _mostrar_contenidos(self, curso: Curso):
        if self._frame_interno is not None:
            self._frame_interno.destroy()

        self._frame_interno = ContenidosScreen(self, curso=curso, al_volver=self._mostrar_lista_cursos)
        self._frame_interno.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    def _construir_barra_herramientas(self, contenedor):
        barra = ctk.CTkFrame(contenedor, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        barra.grid_columnconfigure(1, weight=1)

        campo_busqueda = ctk.CTkEntry(
            barra, textvariable=self._texto_filtro, placeholder_text="Buscar por nombre de curso…",
            width=340, height=40, corner_radius=4, fg_color=COLOR_FONDO_TARJETA,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        campo_busqueda.grid(row=0, column=0, sticky="w")
        self._texto_filtro.trace_add("write", lambda *args: self._cargar_cursos())

        ctk.CTkButton(
            barra, text="+  Nuevo curso", height=40, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self._abrir_formulario_creacion,
        ).grid(row=0, column=2, sticky="e")

    def _construir_barra_acciones(self, contenedor):
        barra = ctk.CTkFrame(contenedor, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))

        self._boton_guia = ctk.CTkButton(
            barra, text="Guía de aprendizaje", width=170, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_ALTERNO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._abrir_guia_aprendizaje,
        )
        self._boton_guia.pack(side="left", padx=(0, 8))

        self._boton_contenidos = ctk.CTkButton(
            barra, text="Gestionar contenidos", width=170, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_ALTERNO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._ir_a_contenidos,
        )
        self._boton_contenidos.pack(side="left", padx=8)

        self._boton_evaluacion = ctk.CTkButton(
            barra, text="Evaluación final", width=150, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_PRIMARIO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._abrir_evaluacion_final,
        )
        self._boton_evaluacion.pack(side="left", padx=8)

        self._boton_simulaciones = ctk.CTkButton(
            barra, text="Simulaciones", width=140, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_PRIMARIO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._abrir_simulaciones,
        )
        self._boton_simulaciones.pack(side="left", padx=8)

        self._boton_editar = ctk.CTkButton(
            barra, text="Editar", width=110, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_SECUNDARIO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._abrir_formulario_edicion,
        )
        self._boton_editar.pack(side="left", padx=8)

        self._boton_eliminar = ctk.CTkButton(
            barra, text="Eliminar", width=110, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color="#FBE1E4",
            border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR, font=(FONT_FAMILY, 12, "bold"),
            state="disabled", command=self._eliminar_curso,
        )
        self._boton_eliminar.pack(side="left", padx=8)

        self._etiqueta_mensaje = ctk.CTkLabel(barra, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR)
        self._etiqueta_mensaje.pack(side="left", padx=16)

    def _construir_tabla(self, contenedor):
        marco = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_BORDE_SUTIL
        )
        marco.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Cursos.Treeview", background=COLOR_FONDO_TARJETA, fieldbackground=COLOR_FONDO_TARJETA,
            foreground=COLOR_TEXTO_PRIMARIO, rowheight=34, borderwidth=0, font=(FONT_FAMILY, 12),
        )
        estilo.configure(
            "Cursos.Treeview.Heading", background=COLOR_FONDO_PANEL, foreground=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), borderwidth=0, relief="flat",
        )
        estilo.map(
            "Cursos.Treeview", background=[("selected", COLOR_ACENTO_PRIMARIO)], foreground=[("selected", COLOR_TEXTO_PRIMARIO)],
        )

        columnas = ("nombre", "instructor", "estado", "fecha")
        self._tabla = ttk.Treeview(marco, columns=columnas, show="headings", style="Cursos.Treeview", selectmode="browse")
        titulos = {"nombre": "Curso", "instructor": "Instructor", "estado": "Estado", "fecha": "Creado"}
        anchos = {"nombre": 320, "instructor": 220, "estado": 100, "fecha": 160}
        for columna in columnas:
            self._tabla.heading(columna, text=titulos[columna])
            self._tabla.column(columna, width=anchos[columna], anchor="w")

        self._tabla.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

        barra_scroll = ttk.Scrollbar(marco, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=barra_scroll.set)
        barra_scroll.grid(row=0, column=1, sticky="ns")

    # ------------------------------------------------------------------
    def _cargar_cursos(self):
        filtro = self._texto_filtro.get().strip().lower()
        self._tabla.delete(*self._tabla.get_children())
        self._cursos_por_fila = {}

        for curso in self._controlador.listar_cursos():
            if filtro and filtro not in curso.nombre_curso.lower():
                continue
            fila_id = self._tabla.insert(
                "", "end",
                values=(
                    curso.nombre_curso,
                    curso.nombre_instructor,
                    "Activo" if curso.esta_activo() else "Inactivo",
                    curso.fecha_creacion,
                ),
            )
            self._cursos_por_fila[fila_id] = curso

        self._curso_seleccionado = None
        self._actualizar_estado_botones()

    def _al_seleccionar_fila(self, evento=None):
        seleccion = self._tabla.selection()
        self._curso_seleccionado = self._cursos_por_fila.get(seleccion[0]) if seleccion else None
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self):
        estado = "normal" if self._curso_seleccionado else "disabled"
        self._boton_guia.configure(state=estado)
        self._boton_contenidos.configure(state=estado)
        self._boton_evaluacion.configure(state=estado)
        self._boton_simulaciones.configure(state=estado)
        self._boton_editar.configure(state=estado)
        self._boton_eliminar.configure(state=estado)
        self._etiqueta_mensaje.configure(text="")

    # ------------------------------------------------------------------
    def _ir_a_contenidos(self):
        if self._curso_seleccionado is not None:
            self._mostrar_contenidos(self._curso_seleccionado)

    def _abrir_guia_aprendizaje(self):
        if self._curso_seleccionado is not None:
            GuiaAprendizajeWindow(self, curso=self._curso_seleccionado, solo_lectura=False)

    def _abrir_evaluacion_final(self):
        if self._curso_seleccionado is not None:
            EvaluacionFinalWindow(self, curso=self._curso_seleccionado)

    def _abrir_simulaciones(self):
        if self._curso_seleccionado is not None:
            SimulacionesWindow(self, curso=self._curso_seleccionado)

    def _eliminar_curso(self):
        if self._curso_seleccionado is None:
            return
        self._controlador.eliminar_curso(self._curso_seleccionado.id_curso)
        self._cargar_cursos()

    def _abrir_formulario_creacion(self):
        FormularioCurso(self, controlador=self._controlador, al_guardar=self._cargar_cursos)

    def _abrir_formulario_edicion(self):
        if self._curso_seleccionado is not None:
            FormularioCurso(
                self, controlador=self._controlador, al_guardar=self._cargar_cursos,
                curso_existente=self._curso_seleccionado,
            )


class FormularioCurso(ctk.CTkToplevel):
    """Formulario modal para crear o editar un curso."""

    def __init__(self, master, controlador: CursoController, al_guardar, curso_existente: Curso = None):
        super().__init__(master)
        self._controlador = controlador
        self._al_guardar = al_guardar
        self._curso_existente = curso_existente
        self._instructores = controlador.listar_instructores()

        self.title("Editar curso" if curso_existente else "Nuevo curso")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("480x600")
        self.minsize(480, 600)
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        if curso_existente:
            self._precargar_datos(curso_existente)

    def _construir_formulario(self):
        ctk.CTkLabel(
            self, text="Editar curso" if self._curso_existente else "Nuevo curso",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(24, 16), anchor="w")

        self._campo_nombre = self._crear_campo("Nombre del curso")

        ctk.CTkLabel(
            self, text="Descripción", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        self._campo_descripcion = ctk.CTkTextbox(
            self, width=380, height=110, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        self._campo_descripcion.pack(padx=28, pady=(0, 4))

        ctk.CTkLabel(
            self, text="Instructor", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        nombres_instructores = [instructor.nombre_completo for instructor in self._instructores]
        self._combo_instructor = ctk.CTkComboBox(
            self, values=nombres_instructores, width=380, height=40, corner_radius=4,
            fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            button_color=COLOR_ACENTO_PRIMARIO, button_hover_color=COLOR_ACENTO_SECUNDARIO,
            dropdown_fg_color=COLOR_FONDO_TARJETA,
        )
        self._combo_instructor.set(nombres_instructores[0] if nombres_instructores else "")
        self._combo_instructor.pack(padx=28, pady=(0, 10))

        if self._curso_existente:
            ctk.CTkLabel(
                self, text="Estado", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
            ).pack(padx=28, pady=(6, 2), anchor="w")
            self._combo_estado = ctk.CTkComboBox(
                self, values=["ACTIVO", "INACTIVO"], width=380, height=40, corner_radius=4,
                fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
                button_color=COLOR_ACENTO_PRIMARIO, button_hover_color=COLOR_ACENTO_SECUNDARIO,
                dropdown_fg_color=COLOR_FONDO_TARJETA,
            )
            self._combo_estado.pack(padx=28, pady=(0, 10))

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=380
        )
        self._etiqueta_error.pack(padx=28, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=380, height=44, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(16, 24))

    def _crear_campo(self, etiqueta: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            self, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            self, width=380, height=40, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        campo.pack(padx=28, pady=(0, 2))
        return campo

    def _precargar_datos(self, curso: Curso):
        self._campo_nombre.insert(0, curso.nombre_curso)
        self._campo_descripcion.insert("1.0", curso.descripcion or "")
        self._combo_instructor.set(curso.nombre_instructor)
        self._combo_estado.set(curso.estado)

    def _guardar(self):
        instructor_seleccionado = next(
            (i for i in self._instructores if i.nombre_completo == self._combo_instructor.get()), None
        )
        if instructor_seleccionado is None:
            self._etiqueta_error.configure(text="Selecciona un instructor válido.")
            return

        descripcion = self._campo_descripcion.get("1.0", "end").strip()

        try:
            if self._curso_existente:
                self._controlador.actualizar_curso(
                    self._curso_existente.id_curso, self._campo_nombre.get(), descripcion,
                    instructor_seleccionado.id_usuario, self._combo_estado.get(),
                )
            else:
                self._controlador.crear_curso(
                    self._campo_nombre.get(), descripcion, instructor_seleccionado.id_usuario
                )
        except DatosCursoInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()
