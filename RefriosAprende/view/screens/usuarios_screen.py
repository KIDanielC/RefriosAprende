"""Pantalla de Gestión de Usuarios (CRUD). Solo lógica de presentación."""
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from config.settings import (
    COLOR_AMARILLO,
    COLOR_AZUL_PRIMARIO,
    COLOR_AZUL_SECUNDARIO,
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
from controller.usuario_controller import DatosInvalidosError, UsuarioController
from model.entities.usuario import Usuario


class UsuariosScreen(ctk.CTkFrame):
    """Sección completa de gestión de usuarios: tabla + acciones + formulario modal."""

    def __init__(self, master, usuario_sesion: Usuario):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._controlador = UsuarioController()
        self._usuario_seleccionado: Usuario | None = None
        self._texto_filtro = tk.StringVar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_barra_herramientas()
        self._construir_barra_acciones()
        self._construir_tabla()
        self._cargar_usuarios()

    # ------------------------------------------------------------------
    def _construir_barra_herramientas(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        barra.grid_columnconfigure(1, weight=1)

        campo_busqueda = ctk.CTkEntry(
            barra,
            textvariable=self._texto_filtro,
            placeholder_text="Buscar por nombre, documento o usuario…",
            width=340,
            height=40,
            corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA,
            border_color=COLOR_BORDE_SUTIL,
            border_width=1,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        campo_busqueda.grid(row=0, column=0, sticky="w")
        self._texto_filtro.trace_add("write", lambda *args: self._cargar_usuarios())

        ctk.CTkButton(
            barra,
            text="+  Nuevo usuario",
            height=40,
            corner_radius=4,
            fg_color=COLOR_AZUL_PRIMARIO,
            hover_color=COLOR_AZUL_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"),
            command=self._abrir_formulario_creacion,
        ).grid(row=0, column=2, sticky="e")

    def _construir_barra_acciones(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))

        self._boton_editar = ctk.CTkButton(
            barra,
            text="Editar",
            width=120,
            height=34,
            corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA,
            hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1,
            border_color=COLOR_AZUL_SECUNDARIO,
            font=(FONT_FAMILY, 12),
            state="disabled",
            command=self._abrir_formulario_edicion,
        )
        self._boton_editar.pack(side="left", padx=(0, 8))

        self._boton_estado = ctk.CTkButton(
            barra,
            text="Activar / Desactivar",
            width=160,
            height=34,
            corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA,
            hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1,
            border_color=COLOR_AMARILLO,
            font=(FONT_FAMILY, 12),
            state="disabled",
            command=self._cambiar_estado_usuario,
        )
        self._boton_estado.pack(side="left", padx=8)

        self._boton_contrasena = ctk.CTkButton(
            barra,
            text="Restablecer contraseña",
            width=190,
            height=34,
            corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA,
            hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=1,
            border_color=COLOR_AZUL_SECUNDARIO,
            font=(FONT_FAMILY, 12),
            state="disabled",
            command=self._abrir_formulario_contrasena,
        )
        self._boton_contrasena.pack(side="left", padx=8)

        self._boton_eliminar = ctk.CTkButton(
            barra,
            text="Eliminar",
            width=120,
            height=34,
            corner_radius=4,
            fg_color=COLOR_FONDO_TARJETA,
            hover_color="#3A1414",
            border_width=1,
            border_color=COLOR_ERROR,
            text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12),
            state="disabled",
            command=self._eliminar_usuario,
        )
        self._boton_eliminar.pack(side="left", padx=8)

        self._etiqueta_mensaje = ctk.CTkLabel(
            barra, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR
        )
        self._etiqueta_mensaje.pack(side="left", padx=16)

    def _construir_tabla(self):
        contenedor = ctk.CTkFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_BORDE_SUTIL
        )
        contenedor.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_rowconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Usuarios.Treeview",
            background=COLOR_FONDO_TARJETA,
            fieldbackground=COLOR_FONDO_TARJETA,
            foreground=COLOR_TEXTO_PRIMARIO,
            rowheight=34,
            borderwidth=0,
            font=(FONT_FAMILY, 12),
        )
        estilo.configure(
            "Usuarios.Treeview.Heading",
            background=COLOR_FONDO_PANEL,
            foreground=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"),
            borderwidth=0,
            relief="flat",
        )
        estilo.map(
            "Usuarios.Treeview",
            background=[("selected", COLOR_AZUL_PRIMARIO)],
            foreground=[("selected", COLOR_TEXTO_PRIMARIO)],
        )

        columnas = ("nombre", "documento", "correo", "usuario", "rol", "estado")
        self._tabla = ttk.Treeview(
            contenedor, columns=columnas, show="headings", style="Usuarios.Treeview", selectmode="browse"
        )
        titulos = {
            "nombre": "Nombre completo",
            "documento": "Documento",
            "correo": "Correo",
            "usuario": "Usuario",
            "rol": "Rol",
            "estado": "Estado",
        }
        anchos = {"nombre": 220, "documento": 110, "correo": 200, "usuario": 120, "rol": 130, "estado": 90}
        for columna in columnas:
            self._tabla.heading(columna, text=titulos[columna])
            self._tabla.column(columna, width=anchos[columna], anchor="w")

        self._tabla.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

        barra_scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=barra_scroll.set)
        barra_scroll.grid(row=0, column=1, sticky="ns")

    # ------------------------------------------------------------------
    def _cargar_usuarios(self):
        filtro = self._texto_filtro.get().strip().lower()
        self._tabla.delete(*self._tabla.get_children())
        self._usuarios_por_fila = {}

        for usuario in self._controlador.listar_usuarios():
            texto_busqueda = f"{usuario.nombre_completo} {usuario.documento} {usuario.usuario}".lower()
            if filtro and filtro not in texto_busqueda:
                continue
            fila_id = self._tabla.insert(
                "",
                "end",
                values=(
                    usuario.nombre_completo,
                    usuario.documento,
                    usuario.correo,
                    usuario.usuario,
                    usuario.nombre_rol.title(),
                    "Activo" if usuario.activo else "Inactivo",
                ),
            )
            self._usuarios_por_fila[fila_id] = usuario

        self._usuario_seleccionado = None
        self._actualizar_estado_botones()

    def _al_seleccionar_fila(self, evento=None):
        seleccion = self._tabla.selection()
        self._usuario_seleccionado = self._usuarios_por_fila.get(seleccion[0]) if seleccion else None
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self):
        estado = "normal" if self._usuario_seleccionado else "disabled"
        self._boton_editar.configure(state=estado)
        self._boton_estado.configure(state=estado)
        self._boton_contrasena.configure(state=estado)
        self._boton_eliminar.configure(state=estado)
        self._etiqueta_mensaje.configure(text="")

    # ------------------------------------------------------------------
    def _cambiar_estado_usuario(self):
        usuario = self._usuario_seleccionado
        if usuario is None:
            return
        if usuario.id_usuario == self._usuario_sesion.id_usuario:
            self._etiqueta_mensaje.configure(text="No puedes desactivar tu propio usuario.")
            return

        self._controlador.actualizar_usuario(
            usuario.id_usuario,
            usuario.nombre_completo,
            usuario.documento,
            usuario.correo,
            usuario.id_rol,
            not usuario.activo,
        )
        self._cargar_usuarios()

    def _eliminar_usuario(self):
        usuario = self._usuario_seleccionado
        if usuario is None:
            return
        if usuario.id_usuario == self._usuario_sesion.id_usuario:
            self._etiqueta_mensaje.configure(text="No puedes eliminar tu propio usuario.")
            return

        DialogoConfirmacion(
            self,
            titulo="Eliminar usuario",
            mensaje=f"¿Eliminar permanentemente a «{usuario.nombre_completo}»? Esta acción no se puede deshacer.",
            al_confirmar=lambda: self._confirmar_eliminacion(usuario.id_usuario),
        )

    def _confirmar_eliminacion(self, id_usuario: int):
        self._controlador.eliminar_usuario(id_usuario)
        self._cargar_usuarios()

    # ------------------------------------------------------------------
    def _abrir_formulario_creacion(self):
        FormularioUsuario(self, controlador=self._controlador, al_guardar=self._cargar_usuarios)

    def _abrir_formulario_edicion(self):
        if self._usuario_seleccionado is not None:
            FormularioUsuario(
                self,
                controlador=self._controlador,
                al_guardar=self._cargar_usuarios,
                usuario_existente=self._usuario_seleccionado,
            )

    def _abrir_formulario_contrasena(self):
        if self._usuario_seleccionado is not None:
            FormularioContrasena(
                self, controlador=self._controlador, usuario_existente=self._usuario_seleccionado
            )


class DialogoConfirmacion(ctk.CTkToplevel):
    """Diálogo modal genérico de confirmación (sí/no)."""

    def __init__(self, master, titulo: str, mensaje: str, al_confirmar):
        super().__init__(master)
        self._al_confirmar = al_confirmar

        self.title(titulo)
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("420x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(
            self, text=mensaje, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_PRIMARIO, wraplength=360, justify="left"
        ).pack(padx=24, pady=(24, 20))

        contenedor_botones = ctk.CTkFrame(self, fg_color="transparent")
        contenedor_botones.pack(pady=(0, 20))

        ctk.CTkButton(
            contenedor_botones, text="Cancelar", width=110, fg_color=COLOR_FONDO_TARJETA_HOVER,
            command=self.destroy,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            contenedor_botones, text="Eliminar", width=110, fg_color=COLOR_ERROR, hover_color="#E14545",
            command=self._confirmar,
        ).pack(side="left", padx=8)

    def _confirmar(self):
        self.destroy()
        self._al_confirmar()


class FormularioUsuario(ctk.CTkToplevel):
    """Formulario modal para crear o editar un usuario."""

    def __init__(self, master, controlador: UsuarioController, al_guardar, usuario_existente: Usuario = None):
        super().__init__(master)
        self._controlador = controlador
        self._al_guardar = al_guardar
        self._usuario_existente = usuario_existente
        self._roles = controlador.listar_roles()

        self.title("Editar usuario" if usuario_existente else "Nuevo usuario")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("480x700")
        self.minsize(480, 700)
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        if usuario_existente:
            self._precargar_datos(usuario_existente)

    def _construir_formulario(self):
        ctk.CTkLabel(
            self,
            text="Editar usuario" if self._usuario_existente else "Nuevo usuario",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=28, pady=(24, 16), anchor="w")

        self._campo_nombre = self._crear_campo("Nombre completo")
        self._campo_documento = self._crear_campo("Documento")
        self._campo_correo = self._crear_campo("Correo electrónico")
        self._campo_usuario = self._crear_campo("Usuario")
        if not self._usuario_existente:
            self._campo_contrasena = self._crear_campo("Contraseña", oculto=True)

        ctk.CTkLabel(
            self, text="Rol", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        nombres_roles = [rol.nombre_rol.title() for rol in self._roles]
        self._combo_rol = ctk.CTkComboBox(
            self, values=nombres_roles, width=380, height=40, corner_radius=4,
            fg_color=COLOR_FONDO_APP, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            button_color=COLOR_AZUL_PRIMARIO, button_hover_color=COLOR_AZUL_SECUNDARIO,
            dropdown_fg_color=COLOR_FONDO_TARJETA,
        )
        self._combo_rol.set(nombres_roles[0] if nombres_roles else "")
        self._combo_rol.pack(padx=28, pady=(0, 10))

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=380
        )
        self._etiqueta_error.pack(padx=28, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=380, height=44, corner_radius=4,
            fg_color=COLOR_AZUL_PRIMARIO, hover_color=COLOR_AZUL_SECUNDARIO,
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(16, 24))

    def _crear_campo(self, etiqueta: str, oculto: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(
            self, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            self, width=380, height=40, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            show="•" if oculto else "",
        )
        campo.pack(padx=28, pady=(0, 2))
        return campo

    def _precargar_datos(self, usuario: Usuario):
        self._campo_nombre.insert(0, usuario.nombre_completo)
        self._campo_documento.insert(0, usuario.documento)
        self._campo_correo.insert(0, usuario.correo)
        self._campo_usuario.insert(0, usuario.usuario)
        self._campo_usuario.configure(state="disabled")
        self._combo_rol.set(usuario.nombre_rol.title())

    def _guardar(self):
        rol_seleccionado = next(
            (rol for rol in self._roles if rol.nombre_rol.title() == self._combo_rol.get()), None
        )
        if rol_seleccionado is None:
            self._etiqueta_error.configure(text="Selecciona un rol válido.")
            return

        try:
            if self._usuario_existente:
                self._controlador.actualizar_usuario(
                    self._usuario_existente.id_usuario,
                    self._campo_nombre.get(),
                    self._campo_documento.get(),
                    self._campo_correo.get(),
                    rol_seleccionado.id_rol,
                    self._usuario_existente.activo,
                )
            else:
                self._controlador.crear_usuario(
                    self._campo_nombre.get(),
                    self._campo_documento.get(),
                    self._campo_correo.get(),
                    self._campo_usuario.get(),
                    self._campo_contrasena.get(),
                    rol_seleccionado.id_rol,
                )
        except DatosInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self.destroy()
        self._al_guardar()


class FormularioContrasena(ctk.CTkToplevel):
    """Formulario modal para restablecer la contraseña de un usuario."""

    def __init__(self, master, controlador: UsuarioController, usuario_existente: Usuario):
        super().__init__(master)
        self._controlador = controlador
        self._usuario = usuario_existente

        self.title("Restablecer contraseña")
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("400x260")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text=f"Nueva contraseña para\n{usuario_existente.nombre_completo}",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
            justify="left",
        ).pack(padx=26, pady=(24, 16), anchor="w")

        self._campo_contrasena = ctk.CTkEntry(
            self, width=340, height=42, corner_radius=4, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO, show="•",
            placeholder_text="Mínimo 6 caracteres",
        )
        self._campo_contrasena.pack(padx=26)

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=340
        )
        self._etiqueta_error.pack(padx=26, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=340, height=42, corner_radius=4,
            fg_color=COLOR_AZUL_PRIMARIO, hover_color=COLOR_AZUL_SECUNDARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self._guardar,
        ).pack(padx=26, pady=(18, 20))

    def _guardar(self):
        try:
            self._controlador.cambiar_contrasena(self._usuario.id_usuario, self._campo_contrasena.get())
        except DatosInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return
        self.destroy()
