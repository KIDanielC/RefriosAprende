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
    RADIO_BOTON,
)
from controller.curso_controller import CursoController, DatosCursoInvalidosError
from model.entities.curso import Curso
from view.screens.gestionar_curso_screen import GestionarCursoWindow


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

        self._boton_gestionar = ctk.CTkButton(
            barra, text="Gestionar curso", width=150, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_ALTERNO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._abrir_gestionar_curso,
        )
        self._boton_gestionar.pack(side="left", padx=(0, 8))

        self._boton_editar = ctk.CTkButton(
            barra, text="Editar", width=110, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1, border_color=COLOR_ACENTO_SECUNDARIO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), state="disabled", command=self._abrir_formulario_edicion,
        )
        self._boton_editar.pack(side="left", padx=8)

        self._boton_eliminar = ctk.CTkButton(
            barra, text="Eliminar", width=110, height=34, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA, hover_color=COLOR_FONDO_TARJETA_HOVER,
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

        columnas = ("nombre", "categoria", "instructor", "estado", "fecha")
        self._tabla = ttk.Treeview(marco, columns=columnas, show="headings", style="Cursos.Treeview", selectmode="browse")
        titulos = {"nombre": "Curso", "categoria": "Categoría", "instructor": "Instructor", "estado": "Estado", "fecha": "Creado"}
        anchos = {"nombre": 280, "categoria": 140, "instructor": 200, "estado": 100, "fecha": 140}
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
                    curso.nombre_categoria or "—",
                    curso.nombre_instructor,
                    curso.estado.capitalize(),
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
        self._boton_gestionar.configure(state=estado)
        self._boton_editar.configure(state=estado)
        self._boton_eliminar.configure(state=estado)
        self._etiqueta_mensaje.configure(text="")

    # ------------------------------------------------------------------
    def _abrir_gestionar_curso(self):
        if self._curso_seleccionado is not None:
            GestionarCursoWindow(self, curso=self._curso_seleccionado)

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
        self._otros_cursos = [c for c in controlador.listar_cursos() if not curso_existente or c.id_curso != curso_existente.id_curso]
        self._casillas_prerrequisito = {}

        self.title("Editar curso" if curso_existente else "Nuevo curso")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("480x760")
        self.minsize(480, 600)
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        if curso_existente:
            self._precargar_datos(curso_existente)

    def _construir_formulario(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Editar curso" if self._curso_existente else "Nuevo curso",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, padx=28, pady=(24, 12), sticky="w")

        cuerpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, sticky="nsew", padx=4)
        cuerpo.grid_columnconfigure(0, weight=1)

        self._campo_nombre = self._crear_campo(cuerpo, "Nombre del curso")

        ctk.CTkLabel(
            cuerpo, text="Descripción", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=24, pady=(6, 2), anchor="w")
        self._campo_descripcion = ctk.CTkTextbox(
            cuerpo, width=380, height=90, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        self._campo_descripcion.pack(padx=24, pady=(0, 4))

        ctk.CTkLabel(
            cuerpo, text="Instructor", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=24, pady=(6, 2), anchor="w")
        nombres_instructores = [instructor.nombre_completo for instructor in self._instructores]
        self._combo_instructor = ctk.CTkComboBox(
            cuerpo, values=nombres_instructores, width=380, height=40, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            button_color=COLOR_ACENTO_PRIMARIO, button_hover_color=COLOR_ACENTO_SECUNDARIO,
            dropdown_fg_color=COLOR_FONDO_TARJETA,
        )
        self._combo_instructor.set(nombres_instructores[0] if nombres_instructores else "")
        self._combo_instructor.pack(padx=24, pady=(0, 10))

        ctk.CTkLabel(
            cuerpo, text="Categoría", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=24, pady=(6, 2), anchor="w")
        nombres_categorias = [c.nombre_categoria for c in self._controlador.listar_categorias()]
        self._combo_categoria = ctk.CTkComboBox(
            cuerpo, values=nombres_categorias, width=380, height=40, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            button_color=COLOR_ACENTO_PRIMARIO, button_hover_color=COLOR_ACENTO_SECUNDARIO,
            dropdown_fg_color=COLOR_FONDO_TARJETA,
        )
        self._combo_categoria.set("")
        self._combo_categoria.pack(padx=24, pady=(0, 10))
        ctk.CTkLabel(
            cuerpo, text="Elige una existente o escribe el nombre de una categoría nueva.",
            font=(FONT_FAMILY, 10.5), text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(padx=24, pady=(0, 10), anchor="w")

        self._casilla_secuencial = ctk.CTkCheckBox(
            cuerpo, text="Aprendizaje secuencial (bloquea cada contenido hasta ver el anterior)",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_PRIMARIO,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            border_color=COLOR_BORDE_SUTIL, checkmark_color="#FFFFFF",
        )
        self._casilla_secuencial.pack(padx=24, pady=(0, 12), anchor="w")

        if self._curso_existente:
            ctk.CTkLabel(
                cuerpo, text="Estado", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
            ).pack(padx=24, pady=(6, 2), anchor="w")
            self._combo_estado = ctk.CTkComboBox(
                cuerpo, values=["BORRADOR", "ACTIVO", "INACTIVO"], width=380, height=40, corner_radius=RADIO_BOTON,
                fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
                button_color=COLOR_ACENTO_PRIMARIO, button_hover_color=COLOR_ACENTO_SECUNDARIO,
                dropdown_fg_color=COLOR_FONDO_TARJETA,
            )
            self._combo_estado.pack(padx=24, pady=(0, 10))

            ctk.CTkLabel(
                cuerpo, text="Prerrequisitos (el aprendiz debe completar estos cursos antes)",
                font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(padx=24, pady=(6, 4), anchor="w")
            if self._otros_cursos:
                marco_prerrequisitos = ctk.CTkFrame(
                    cuerpo, fg_color=COLOR_FONDO_APP, corner_radius=RADIO_BOTON,
                    border_width=1, border_color=COLOR_BORDE_SUTIL,
                )
                marco_prerrequisitos.pack(padx=24, pady=(0, 10), fill="x")
                for curso_otro in self._otros_cursos:
                    casilla = ctk.CTkCheckBox(
                        marco_prerrequisitos, text=curso_otro.nombre_curso, font=(FONT_FAMILY, 12),
                        text_color=COLOR_TEXTO_PRIMARIO, fg_color=COLOR_ACENTO_PRIMARIO,
                        hover_color=COLOR_ACENTO_SECUNDARIO, border_color=COLOR_BORDE_SUTIL,
                        checkmark_color="#FFFFFF",
                    )
                    casilla.pack(padx=12, pady=6, anchor="w")
                    self._casillas_prerrequisito[curso_otro.id_curso] = casilla
            else:
                ctk.CTkLabel(
                    cuerpo, text="No hay otros cursos todavía.", font=(FONT_FAMILY, 11),
                    text_color=COLOR_TEXTO_SECUNDARIO,
                ).pack(padx=24, pady=(0, 10), anchor="w")
        else:
            ctk.CTkLabel(
                cuerpo, text="El curso se creará como Borrador. Los prerrequisitos se configuran al editarlo.",
                font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, wraplength=380, justify="left",
            ).pack(padx=24, pady=(0, 10), anchor="w")

        self._etiqueta_error = ctk.CTkLabel(
            cuerpo, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=380
        )
        self._etiqueta_error.pack(padx=24, pady=(6, 0))

        ctk.CTkButton(
            cuerpo, text="Guardar", width=380, height=44, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=24, pady=(16, 24))

    def _crear_campo(self, cuerpo, etiqueta: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            cuerpo, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=24, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            cuerpo, width=380, height=40, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        campo.pack(padx=24, pady=(0, 2))
        return campo

    def _precargar_datos(self, curso: Curso):
        self._campo_nombre.insert(0, curso.nombre_curso)
        self._campo_descripcion.insert("1.0", curso.descripcion or "")
        self._combo_instructor.set(curso.nombre_instructor)
        self._combo_categoria.set(curso.nombre_categoria or "")
        if curso.aprendizaje_secuencial:
            self._casilla_secuencial.select()
        self._combo_estado.set(curso.estado)
        ids_prerrequisitos = set(self._controlador.listar_ids_prerrequisitos(curso.id_curso))
        for id_curso, casilla in self._casillas_prerrequisito.items():
            if id_curso in ids_prerrequisitos:
                casilla.select()

    def _guardar(self):
        instructor_seleccionado = next(
            (i for i in self._instructores if i.nombre_completo == self._combo_instructor.get()), None
        )
        if instructor_seleccionado is None:
            self._etiqueta_error.configure(text="Selecciona un instructor válido.")
            return

        descripcion = self._campo_descripcion.get("1.0", "end").strip()
        nombre_categoria = self._combo_categoria.get()
        aprendizaje_secuencial = bool(self._casilla_secuencial.get())

        try:
            if self._curso_existente:
                curso_guardado = self._controlador.actualizar_curso(
                    self._curso_existente.id_curso, self._campo_nombre.get(), descripcion,
                    instructor_seleccionado.id_usuario, self._combo_estado.get(),
                    nombre_categoria, aprendizaje_secuencial,
                )
                ids_seleccionados = [
                    id_curso for id_curso, casilla in self._casillas_prerrequisito.items() if casilla.get()
                ]
                self._controlador.guardar_prerrequisitos(curso_guardado.id_curso, ids_seleccionados)
            else:
                self._controlador.crear_curso(
                    self._campo_nombre.get(), descripcion, instructor_seleccionado.id_usuario,
                    nombre_categoria, aprendizaje_secuencial,
                )
        except DatosCursoInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()
