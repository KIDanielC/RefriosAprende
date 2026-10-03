"""Pantalla de Gestión de Usuarios (CRUD). Solo lógica de presentación."""
import tkinter as tk

import customtkinter as ctk

from config.settings import (
    COLOR_FONDO_APP,
    FONT_FAMILY,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    RADIO_BOTON,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_FONDO_TARJETA,
    COLOR_BORDE_SUTIL,
    GROSOR_BORDE_SUTIL,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_ACENTO_ALTERNO,
    COLOR_ERROR,
    RADIO_TARJETA,
)
from controller.usuario_controller import UsuarioController, UltimoAdministradorError, DatosInvalidosError
from model.entities.usuario import Usuario
from view.components.avatar import cargar_imagen_perfil

_COLUMNAS_GALERIA = 6
_LADO_BOLA = 76
_LADO_FOTO = 68


def _iniciales(nombre_completo: str) -> str:
    return "".join(parte[0] for parte in nombre_completo.split()[:2]).upper()


class UsuariosScreen(ctk.CTkFrame):
    """Sección completa de gestión de usuarios: galería de fichas + formulario modal.

    Cada aprendiz/administrador se muestra como una ficha con su foto de perfil (o sus
    iniciales si no tiene una); al oprimirla se despliega un menú con las acciones
    disponibles, en vez de una tabla de texto con una barra de botones aparte.
    """

    def __init__(self, master, usuario_sesion: Usuario):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._controlador = UsuarioController()
        self._texto_filtro = tk.StringVar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_barra_herramientas()
        self._construir_galeria()
        self._cargar_galeria()

    # ------------------------------------------------------------------
    def _construir_barra_herramientas(self):
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 4))
        encabezado.grid_columnconfigure(0, weight=1)

        bloque_titulo = ctk.CTkFrame(encabezado, fg_color="transparent")
        bloque_titulo.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            bloque_titulo, text="Gestión de Usuarios", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(anchor="w")
        self._etiqueta_conteo = ctk.CTkLabel(
            bloque_titulo, text="", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        )
        self._etiqueta_conteo.pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            encabezado, text="+  Nuevo usuario", height=38, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 13, "bold"), command=self._abrir_formulario_creacion,
        ).grid(row=0, column=1, sticky="e")

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=28, pady=(14, 16))

        campo_busqueda = ctk.CTkEntry(
            barra,
            textvariable=self._texto_filtro,
            placeholder_text="🔍  Buscar por nombre, documento o usuario…",
            width=360,
            height=38,
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_TARJETA,
            border_color=COLOR_BORDE_SUTIL,
            border_width=GROSOR_BORDE_SUTIL,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        campo_busqueda.pack(side="left")
        self._texto_filtro.trace_add("write", lambda *args: self._cargar_galeria())

        self._etiqueta_mensaje = ctk.CTkLabel(
            barra, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR
        )
        self._etiqueta_mensaje.pack(side="left", padx=16)

    def _construir_galeria(self):
        self._galeria = ctk.CTkScrollableFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        self._galeria.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        for columna in range(_COLUMNAS_GALERIA):
            self._galeria.grid_columnconfigure(columna, weight=1)

    # ------------------------------------------------------------------
    def _cargar_galeria(self):
        for hijo in self._galeria.winfo_children():
            hijo.destroy()
        self._etiqueta_mensaje.configure(text="")

        filtro = self._texto_filtro.get().strip().lower()
        total_usuarios = 0
        usuarios_mostrados = 0
        for usuario in self._controlador.listar_usuarios():
            total_usuarios += 1
            texto_busqueda = f"{usuario.nombre_completo} {usuario.documento} {usuario.usuario}".lower()
            if filtro and filtro not in texto_busqueda:
                continue
            fila, columna = divmod(usuarios_mostrados, _COLUMNAS_GALERIA)
            self._construir_ficha_usuario(usuario, fila, columna)
            usuarios_mostrados += 1

        if usuarios_mostrados == 0:
            texto_vacio = "No hay usuarios que coincidan con la búsqueda." if filtro else "Todavía no hay usuarios registrados."
            ctk.CTkLabel(
                self._galeria, text=texto_vacio, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, columnspan=_COLUMNAS_GALERIA, pady=40)

        plural = "s" if total_usuarios != 1 else ""
        self._etiqueta_conteo.configure(text=f"{total_usuarios} usuario{plural} registrado{plural}")

    def _construir_ficha_usuario(self, usuario: Usuario, fila: int, columna: int):
        ficha = ctk.CTkFrame(self._galeria, fg_color="transparent", width=132)
        ficha.grid(row=fila, column=columna, padx=8, pady=16)

        if not usuario.activo:
            color_anillo = COLOR_TEXTO_SECUNDARIO
        elif usuario.es_administrador():
            color_anillo = COLOR_ACENTO_ALTERNO
        else:
            color_anillo = COLOR_ACENTO_PRIMARIO

        imagen = cargar_imagen_perfil(usuario.foto_perfil, _LADO_FOTO)
        bola = ctk.CTkButton(
            ficha,
            text="" if imagen else _iniciales(usuario.nombre_completo),
            image=imagen,
            width=_LADO_BOLA,
            height=_LADO_BOLA,
            corner_radius=_LADO_BOLA // 2,
            fg_color=COLOR_FONDO_TARJETA_HOVER,
            hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=3,
            border_color=color_anillo,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 17, "bold"),
        )
        bola.pack()
        bola.configure(command=lambda u=usuario, w=bola: self._abrir_menu_usuario(u, w))

        ctk.CTkLabel(
            ficha,
            text=usuario.nombre_completo,
            font=(FONT_FAMILY, 11, "bold" if usuario.activo else "normal"),
            text_color=COLOR_TEXTO_PRIMARIO if usuario.activo else COLOR_TEXTO_SECUNDARIO,
            wraplength=124,
            justify="center",
        ).pack(pady=(8, 0))
        ctk.CTkLabel(
            ficha,
            text=usuario.nombre_rol.title() if usuario.activo else f"{usuario.nombre_rol.title()} · Inactivo",
            font=(FONT_FAMILY, 10),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack()

    # ------------------------------------------------------------------
    def _abrir_menu_usuario(self, usuario: Usuario, ancla: ctk.CTkButton):
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=COLOR_FONDO_TARJETA,
            fg=COLOR_TEXTO_PRIMARIO,
            activebackground=COLOR_FONDO_TARJETA_HOVER,
            activeforeground=COLOR_TEXTO_PRIMARIO,
            disabledforeground=COLOR_TEXTO_SECUNDARIO,
            relief="flat",
            borderwidth=1,
            font=(FONT_FAMILY, 11),
        )
        menu.add_command(label="✏  Editar", command=lambda: self._abrir_formulario_edicion(usuario))
        menu.add_command(
            label="○  Desactivar" if usuario.activo else "●  Activar",
            command=lambda: self._cambiar_estado_usuario(usuario),
        )
        menu.add_command(label="🔒  Restablecer contraseña", command=lambda: self._abrir_formulario_contrasena(usuario))
        menu.add_separator()
        menu.add_command(label="🗑  Eliminar", foreground=COLOR_ERROR, command=lambda: self._eliminar_usuario(usuario))

        x = ancla.winfo_rootx()
        y = ancla.winfo_rooty() + ancla.winfo_height() + 4
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    # ------------------------------------------------------------------
    def _cambiar_estado_usuario(self, usuario: Usuario):
        if usuario.id_usuario == self._usuario_sesion.id_usuario:
            self._etiqueta_mensaje.configure(text="No puedes desactivar tu propio usuario.")
            return

        try:
            self._controlador.actualizar_usuario(
                usuario.id_usuario,
                usuario.nombre_completo,
                usuario.documento,
                usuario.correo,
                usuario.id_rol,
                not usuario.activo,
            )
        except UltimoAdministradorError as error:
            self._etiqueta_mensaje.configure(text=str(error))
            return
        self._cargar_galeria()

    def _eliminar_usuario(self, usuario: Usuario):
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
        try:
            self._controlador.eliminar_usuario(id_usuario)
        except (UltimoAdministradorError, DatosInvalidosError) as error:
            self._etiqueta_mensaje.configure(text=str(error))
            return
        self._cargar_galeria()

    # ------------------------------------------------------------------
    def _abrir_formulario_creacion(self):
        FormularioUsuario(self, controlador=self._controlador, al_guardar=self._cargar_galeria)

    def _abrir_formulario_edicion(self, usuario: Usuario):
        FormularioUsuario(
            self, controlador=self._controlador, al_guardar=self._cargar_galeria, usuario_existente=usuario,
        )

    def _abrir_formulario_contrasena(self, usuario: Usuario):
        FormularioContrasena(self, controlador=self._controlador, usuario_existente=usuario)


class DialogoConfirmacion(ctk.CTkToplevel):
    """Diálogo modal genérico de confirmación (sí/no)."""

    def __init__(self, master, titulo: str, mensaje: str, al_confirmar):
        super().__init__(master)
        self._al_confirmar = al_confirmar

        self.title(titulo)
        self.configure(fg_color=COLOR_FONDO_TARJETA)
        self.geometry("420x190")
        self.minsize(420, 190)
        self.resizable(True, True)
        self.grab_set()

        ctk.CTkLabel(
            self, text=titulo, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=24, pady=(24, 4), anchor="w")
        ctk.CTkLabel(
            self, text=mensaje, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO, wraplength=360, justify="left"
        ).pack(padx=24, pady=(0, 20), anchor="w")

        contenedor_botones = ctk.CTkFrame(self, fg_color="transparent")
        contenedor_botones.pack(pady=(0, 20))

        ctk.CTkButton(
            contenedor_botones, text="Cancelar", width=110, height=38, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self.destroy,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            contenedor_botones, text="Eliminar", width=110, height=38, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ERROR, hover_color="#C2352B", text_color="#FFFFFF",
            font=(FONT_FAMILY, 13, "bold"), command=self._confirmar,
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
        self.resizable(True, True)
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
        self._selector_rol = ctk.CTkSegmentedButton(
            self, values=nombres_roles, width=380, height=40, corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP, selected_color=COLOR_BORDE_SUTIL,
            selected_hover_color=COLOR_FONDO_TARJETA_HOVER, unselected_color=COLOR_FONDO_APP,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 13, "bold"),
        )
        self._selector_rol.set(nombres_roles[0] if nombres_roles else "")
        self._selector_rol.pack(padx=28, pady=(0, 10))

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=380
        )
        self._etiqueta_error.pack(padx=28, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=380, height=44, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).pack(padx=28, pady=(16, 24))

    def _crear_campo(self, etiqueta: str, oculto: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(
            self, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(padx=28, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            self, width=380, height=40, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
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
        self._selector_rol.set(usuario.nombre_rol.title())

    def _guardar(self):
        rol_seleccionado = next(
            (rol for rol in self._roles if rol.nombre_rol.title() == self._selector_rol.get()), None
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
        self.minsize(400, 260)
        self.resizable(True, True)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text=f"Nueva contraseña para\n{usuario_existente.nombre_completo}",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
            justify="left",
        ).pack(padx=26, pady=(24, 16), anchor="w")

        self._campo_contrasena = ctk.CTkEntry(
            self, width=340, height=42, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO, show="•",
            placeholder_text="Mínimo 6 caracteres",
        )
        self._campo_contrasena.pack(padx=26)

        self._etiqueta_error = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=340
        )
        self._etiqueta_error.pack(padx=26, pady=(6, 0))

        ctk.CTkButton(
            self, text="Guardar", width=340, height=42, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 13, "bold"), command=self._guardar,
        ).pack(padx=26, pady=(18, 20))

    def _guardar(self):
        try:
            self._controlador.cambiar_contrasena(self._usuario.id_usuario, self._campo_contrasena.get())
        except DatosInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return
        self.destroy()
