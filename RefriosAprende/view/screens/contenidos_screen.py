"""Pantalla de gestión de contenidos (tipo TEXTO o PDF) de un curso específico."""
from tkinter import filedialog

import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
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
)
from controller.contenido_controller import (
    TIPO_IMAGEN,
    TIPO_PDF,
    TIPO_TEXTO,
    ContenidoController,
    DatosContenidoInvalidosError,
)
from model.entities.contenido import Contenido
from model.entities.curso import Curso
from view.screens.preguntas_validacion_screen import PreguntasValidacionWindow


class ContenidosScreen(ctk.CTkFrame):
    """Lista y administra los contenidos (texto) de un curso. Se muestra dentro del área de sección."""

    def __init__(self, master, curso: Curso, al_volver):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._curso = curso
        self._al_volver = al_volver
        self._controlador = ContenidoController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado()
        self._construir_barra_herramientas()
        self._construir_lista()
        self._cargar_contenidos()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 4))

        ctk.CTkButton(
            barra, text="←  Volver a cursos", fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            text_color=COLOR_ACENTO_SECUNDARIO, font=(FONT_FAMILY, 13, "bold"), width=160, height=32,
            command=self._al_volver,
        ).pack(side="left")

        ctk.CTkLabel(
            self, text=f"Contenidos de «{self._curso.nombre_curso}»", font=(FONT_FAMILY, 20, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(4, 12))

    def _construir_barra_herramientas(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))

        ctk.CTkButton(
            barra, text="+  Nuevo contenido", height=38, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self._abrir_formulario_creacion,
        ).pack(side="left")

    def _construir_lista(self):
        self._lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        self._lista.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _cargar_contenidos(self):
        for hijo in self._lista.winfo_children():
            hijo.destroy()

        contenidos = self._controlador.listar_por_curso(self._curso.id_curso)

        if not contenidos:
            ctk.CTkLabel(
                self._lista, text="Este curso aún no tiene contenidos.", font=(FONT_FAMILY, 14),
                text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, contenido in enumerate(contenidos):
            self._construir_tarjeta_contenido(indice, contenido)

    def _construir_tarjeta_contenido(self, fila: int, contenido: Contenido):
        tarjeta = ctk.CTkFrame(
            self._lista, fg_color=COLOR_FONDO_TARJETA, corner_radius=4,
            border_width=1, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            encabezado, text=f"{contenido.orden}.", font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_ACENTO_ALTERNO,
        ).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkLabel(
            encabezado, text=contenido.titulo, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        if contenido.tipo_contenido == TIPO_PDF:
            ctk.CTkLabel(
                encabezado, text="📄 PDF", font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_ACENTO_PRIMARIO,
            ).grid(row=0, column=2, padx=(10, 0))
        elif contenido.tipo_contenido == TIPO_IMAGEN:
            ctk.CTkLabel(
                encabezado, text="🖼 Imagen", font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_ACENTO_ALTERNO,
            ).grid(row=0, column=2, padx=(10, 0))

        texto = contenido.contenido_texto or ""
        extracto = texto[:160] + ("…" if len(texto) > 160 else "") if texto else "Sin descripción."
        ctk.CTkLabel(
            tarjeta, text=extracto, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=800,
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        barra_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_acciones.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 14))

        ctk.CTkButton(
            barra_acciones, text="Editar", width=90, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda c=contenido: self._abrir_formulario_edicion(c),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            barra_acciones, text="Eliminar", width=90, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ERROR, text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12, "bold"), command=lambda c=contenido: self._eliminar_contenido(c),
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            barra_acciones, text="Preguntas de validación", width=180, height=30, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_ALTERNO, text_color=COLOR_ACENTO_ALTERNO,
            font=(FONT_FAMILY, 12, "bold"), command=lambda c=contenido: self._abrir_preguntas_validacion(c),
        ).pack(side="left", padx=(8, 0))

    # ------------------------------------------------------------------
    def _eliminar_contenido(self, contenido: Contenido):
        self._controlador.eliminar_contenido(contenido.id_contenido)
        self._cargar_contenidos()

    def _abrir_preguntas_validacion(self, contenido: Contenido):
        PreguntasValidacionWindow(self, contenido=contenido)

    def _abrir_formulario_creacion(self):
        FormularioContenido(
            self, controlador=self._controlador, id_curso=self._curso.id_curso, al_guardar=self._cargar_contenidos
        )

    def _abrir_formulario_edicion(self, contenido: Contenido):
        FormularioContenido(
            self, controlador=self._controlador, id_curso=self._curso.id_curso,
            al_guardar=self._cargar_contenidos, contenido_existente=contenido,
        )


class FormularioContenido(ctk.CTkToplevel):
    """Formulario modal para crear un contenido (Texto, PDF o Imagen) o editar uno existente.

    El tipo de contenido no se puede cambiar una vez creado (solo aplica al crear)."""

    def __init__(self, master, controlador: ContenidoController, id_curso: int, al_guardar, contenido_existente: Contenido = None):
        super().__init__(master)
        self._controlador = controlador
        self._id_curso = id_curso
        self._al_guardar = al_guardar
        self._contenido_existente = contenido_existente
        self._ruta_archivo_seleccionado = None
        self._tipo_seleccionado = contenido_existente.tipo_contenido if contenido_existente else TIPO_TEXTO

        self.title("Editar contenido" if contenido_existente else "Nuevo contenido")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("560x560")
        self.minsize(560, 480)
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        if contenido_existente:
            self._precargar_datos(contenido_existente)

    def _construir_formulario(self):
        ctk.CTkLabel(
            self, text="Editar contenido" if self._contenido_existente else "Nuevo contenido",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(24, 16), anchor="w")

        if not self._contenido_existente:
            ctk.CTkLabel(
                self, text="Tipo de contenido", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
            ).pack(padx=28, pady=(0, 2), anchor="w")
            self._selector_tipo = ctk.CTkSegmentedButton(
                self, values=["Texto", "PDF", "Imagen"], command=self._al_cambiar_tipo,
                fg_color=COLOR_FONDO_APP, selected_color=COLOR_ACENTO_PRIMARIO,
                selected_hover_color=COLOR_ACENTO_SECUNDARIO, unselected_color=COLOR_FONDO_APP,
                text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 13, "bold"),
            )
            self._selector_tipo.set("Texto")
            self._selector_tipo.pack(padx=28, pady=(0, 12), anchor="w")

        ctk.CTkLabel(
            self, text="Título", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(0, 2), anchor="w")
        self._campo_titulo = ctk.CTkEntry(
            self, width=500, height=40, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
        )
        self._campo_titulo.pack(padx=28, pady=(0, 10))

        self._area_dinamica = ctk.CTkFrame(self, fg_color="transparent")
        self._area_dinamica.pack(padx=28, pady=(0, 4), fill="x")
        self._construir_area_texto()

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=500
        )
        self._etiqueta_error.pack(padx=28, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=500, height=44, corner_radius=4,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(16, 24))

    def _al_cambiar_tipo(self, valor: str):
        self._tipo_seleccionado = {"PDF": TIPO_PDF, "Imagen": TIPO_IMAGEN}.get(valor, TIPO_TEXTO)
        for hijo in self._area_dinamica.winfo_children():
            hijo.destroy()
        if self._tipo_seleccionado == TIPO_PDF:
            self._construir_area_archivo("Archivo PDF", "Elegir PDF…", [("Archivos PDF", "*.pdf")])
        elif self._tipo_seleccionado == TIPO_IMAGEN:
            self._construir_area_archivo(
                "Archivo de imagen", "Elegir imagen…",
                [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")],
            )
        else:
            self._construir_area_texto()

    def _construir_area_texto(self):
        ctk.CTkLabel(
            self._area_dinamica, text="Contenido", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(pady=(0, 2), anchor="w")
        self._campo_texto = ctk.CTkTextbox(
            self._area_dinamica, width=500, height=220, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        self._campo_texto.pack()

    def _construir_area_archivo(self, etiqueta_archivo: str, texto_boton: str, tipos_archivo: list):
        ctk.CTkLabel(
            self._area_dinamica, text="Descripción (opcional)", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(pady=(0, 2), anchor="w")
        self._campo_texto = ctk.CTkTextbox(
            self._area_dinamica, width=500, height=100, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=1, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        self._campo_texto.pack(pady=(0, 10))

        ctk.CTkLabel(
            self._area_dinamica, text=etiqueta_archivo, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(pady=(0, 2), anchor="w")
        fila_archivo = ctk.CTkFrame(self._area_dinamica, fg_color="transparent")
        fila_archivo.pack(fill="x")
        self._etiqueta_archivo = ctk.CTkLabel(
            fila_archivo, text="Ningún archivo seleccionado.", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._etiqueta_archivo.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            fila_archivo, text=texto_boton, width=140, height=32, corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_PRIMARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda: self._elegir_archivo(tipos_archivo),
        ).pack(side="left")

    def _elegir_archivo(self, tipos_archivo: list):
        ruta = filedialog.askopenfilename(title="Selecciona un archivo", filetypes=tipos_archivo)
        if ruta:
            self._ruta_archivo_seleccionado = ruta
            self._etiqueta_archivo.configure(text=ruta.split("/")[-1].split("\\")[-1])

    def _precargar_datos(self, contenido: Contenido):
        self._campo_titulo.insert(0, contenido.titulo)
        if contenido.contenido_texto:
            self._campo_texto.insert("1.0", contenido.contenido_texto)

        if contenido.tipo_contenido == TIPO_PDF:
            for hijo in self._area_dinamica.winfo_children():
                hijo.destroy()
            self._construir_area_archivo("Archivo PDF", "Elegir PDF…", [("Archivos PDF", "*.pdf")])
            if contenido.contenido_texto:
                self._campo_texto.insert("1.0", contenido.contenido_texto)
            self._etiqueta_archivo.configure(text="Archivo ya cargado (no se puede reemplazar aquí; elimina y crea de nuevo).")
        elif contenido.tipo_contenido == TIPO_IMAGEN:
            for hijo in self._area_dinamica.winfo_children():
                hijo.destroy()
            self._construir_area_archivo(
                "Archivo de imagen", "Elegir imagen…", [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")],
            )
            if contenido.contenido_texto:
                self._campo_texto.insert("1.0", contenido.contenido_texto)
            self._etiqueta_archivo.configure(text="Archivo ya cargado (no se puede reemplazar aquí; elimina y crea de nuevo).")

    def _guardar(self):
        titulo = self._campo_titulo.get()
        texto = self._campo_texto.get("1.0", "end").strip()

        try:
            if self._contenido_existente:
                self._controlador.actualizar_contenido(
                    self._contenido_existente.id_contenido, titulo, texto, self._contenido_existente.orden
                )
            elif self._tipo_seleccionado == TIPO_PDF:
                self._controlador.crear_contenido_pdf(self._id_curso, titulo, texto, self._ruta_archivo_seleccionado)
            elif self._tipo_seleccionado == TIPO_IMAGEN:
                self._controlador.crear_contenido_imagen(self._id_curso, titulo, texto, self._ruta_archivo_seleccionado)
            else:
                self._controlador.crear_contenido_texto(self._id_curso, titulo, texto)
        except DatosContenidoInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()
