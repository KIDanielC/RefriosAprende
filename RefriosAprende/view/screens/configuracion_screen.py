"""Pantalla de Configuración: datos de la propia cuenta del administrador en sesión."""
from tkinter import filedialog

import customtkinter as ctk

from config.settings import (
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    RADIO_TARJETA,
    GROSOR_BORDE_SUTIL,
    COLOR_BORDE_SUTIL,
    FONT_FAMILY,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    RADIO_BOTON,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_ACENTO_ALTERNO,
    COLOR_ERROR,
    COLOR_EXITO,
)
from controller.usuario_controller import UsuarioController, DatosInvalidosError
from model.entities.usuario import Usuario
from view.components.avatar import cargar_imagen_perfil

_LADO_AVATAR = 72


class ConfiguracionScreen(ctk.CTkFrame):
    """Permite al usuario en sesión actualizar sus propios datos, foto de perfil y contraseña."""

    def __init__(self, master, usuario_sesion: Usuario, al_actualizar_perfil=None):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._al_actualizar_perfil = al_actualizar_perfil
        self._controlador = UsuarioController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        contenedor.grid_columnconfigure(0, weight=1)

        tarjeta_datos = self._construir_tarjeta_datos(contenedor)
        tarjeta_datos.pack(fill="x", pady=(0, 16))

        tarjeta_contrasena = self._construir_tarjeta_contrasena(contenedor)
        tarjeta_contrasena.pack(fill="x")

    def _construir_tarjeta_datos(self, contenedor) -> ctk.CTkFrame:
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        ctk.CTkLabel(
            tarjeta, text="Mis datos", font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", padx=24, pady=(20, 2))
        ctk.CTkLabel(
            tarjeta, text=f"Usuario: {self._usuario_sesion.usuario}  ·  Rol: {self._usuario_sesion.nombre_rol.title()}",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", padx=24, pady=(0, 16))

        self._construir_seccion_foto(tarjeta)

        self._campo_nombre = self._crear_campo(tarjeta, "Nombre completo", self._usuario_sesion.nombre_completo)
        self._campo_documento = self._crear_campo(tarjeta, "Documento", self._usuario_sesion.documento)
        self._campo_correo = self._crear_campo(tarjeta, "Correo electrónico", self._usuario_sesion.correo)

        self._etiqueta_estado_datos = ctk.CTkLabel(tarjeta, text="", font=(FONT_FAMILY, 12, "bold"))
        self._etiqueta_estado_datos.pack(anchor="w", padx=24, pady=(4, 0))

        ctk.CTkButton(
            tarjeta, text="Guardar cambios", width=200, height=42, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 13, "bold"), command=self._guardar_datos,
        ).pack(anchor="w", padx=24, pady=(14, 22))
        return tarjeta

    def _construir_tarjeta_contrasena(self, contenedor) -> ctk.CTkFrame:
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        ctk.CTkLabel(
            tarjeta, text="Cambiar contraseña", font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", padx=24, pady=(20, 16))

        self._campo_contrasena_nueva = self._crear_campo(tarjeta, "Contraseña nueva", "", oculto=True)
        self._campo_contrasena_confirmar = self._crear_campo(tarjeta, "Confirmar contraseña nueva", "", oculto=True)

        self._etiqueta_estado_contrasena = ctk.CTkLabel(tarjeta, text="", font=(FONT_FAMILY, 12, "bold"))
        self._etiqueta_estado_contrasena.pack(anchor="w", padx=24, pady=(4, 0))

        ctk.CTkButton(
            tarjeta, text="Actualizar contraseña", width=200, height=42, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_PRIMARIO, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13, "bold"), command=self._guardar_contrasena,
        ).pack(anchor="w", padx=24, pady=(14, 22))
        return tarjeta

    def _construir_seccion_foto(self, contenedor):
        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        fila.pack(anchor="w", padx=24, pady=(0, 16))

        self._avatar = ctk.CTkLabel(
            fila, text="", width=_LADO_AVATAR, height=_LADO_AVATAR, corner_radius=_LADO_AVATAR // 2,
            fg_color=COLOR_ACENTO_ALTERNO,
        )
        self._avatar.pack(side="left")
        self._refrescar_avatar()

        columna_boton = ctk.CTkFrame(fila, fg_color="transparent")
        columna_boton.pack(side="left", padx=(16, 0))
        ctk.CTkButton(
            columna_boton, text="Subir foto (PNG)", width=160, height=32, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_APP, border_width=GROSOR_BORDE_SUTIL,
            border_color=COLOR_ACENTO_PRIMARIO, text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=self._subir_foto,
        ).pack(anchor="w")
        self._etiqueta_estado_foto = ctk.CTkLabel(columna_boton, text="", font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w")
        self._etiqueta_estado_foto.pack(anchor="w", pady=(4, 0))

    def _refrescar_avatar(self):
        imagen = cargar_imagen_perfil(self._usuario_sesion.foto_perfil, _LADO_AVATAR)
        if imagen is not None:
            self._avatar.configure(image=imagen, text="")
        else:
            iniciales = "".join(parte[0] for parte in self._usuario_sesion.nombre_completo.split()[:2]).upper()
            self._avatar.configure(image=None, text=iniciales, font=(FONT_FAMILY, 18, "bold"), text_color="#FFFFFF")

    def _subir_foto(self):
        ruta = filedialog.askopenfilename(title="Selecciona una foto de perfil", filetypes=[("Imagen PNG", "*.png")])
        if not ruta:
            return
        try:
            usuario_actualizado = self._controlador.actualizar_foto_perfil(self._usuario_sesion.id_usuario, ruta)
        except DatosInvalidosError as error:
            self._etiqueta_estado_foto.configure(text=str(error), text_color=COLOR_ERROR)
            return

        self._usuario_sesion.foto_perfil = usuario_actualizado.foto_perfil
        self._refrescar_avatar()
        self._etiqueta_estado_foto.configure(text="✓ Foto actualizada", text_color=COLOR_EXITO)
        if self._al_actualizar_perfil:
            self._al_actualizar_perfil()

    def _crear_campo(self, contenedor, etiqueta: str, valor_inicial: str, oculto: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(
            contenedor, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", padx=24, pady=(6, 4))
        campo = ctk.CTkEntry(
            contenedor, width=380, height=42, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13), show="•" if oculto else "",
        )
        if valor_inicial:
            campo.insert(0, valor_inicial)
        campo.pack(anchor="w", padx=24)
        return campo

    # ------------------------------------------------------------------
    def _guardar_datos(self):
        try:
            usuario_actualizado = self._controlador.actualizar_usuario(
                self._usuario_sesion.id_usuario,
                self._campo_nombre.get(),
                self._campo_documento.get(),
                self._campo_correo.get(),
                self._usuario_sesion.id_rol,
                self._usuario_sesion.activo,
            )
        except DatosInvalidosError as error:
            self._etiqueta_estado_datos.configure(text=str(error), text_color=COLOR_ERROR)
            return

        self._usuario_sesion.nombre_completo = usuario_actualizado.nombre_completo
        self._usuario_sesion.documento = usuario_actualizado.documento
        self._usuario_sesion.correo = usuario_actualizado.correo
        self._etiqueta_estado_datos.configure(text="✓ Datos actualizados correctamente", text_color=COLOR_EXITO)

    def _guardar_contrasena(self):
        nueva = self._campo_contrasena_nueva.get()
        confirmar = self._campo_contrasena_confirmar.get()

        if nueva != confirmar:
            self._etiqueta_estado_contrasena.configure(text="Las contraseñas no coinciden.", text_color=COLOR_ERROR)
            return

        try:
            self._controlador.cambiar_contrasena(self._usuario_sesion.id_usuario, nueva)
        except DatosInvalidosError as error:
            self._etiqueta_estado_contrasena.configure(text=str(error), text_color=COLOR_ERROR)
            return

        self._campo_contrasena_nueva.delete(0, "end")
        self._campo_contrasena_confirmar.delete(0, "end")
        self._etiqueta_estado_contrasena.configure(text="✓ Contraseña actualizada correctamente", text_color=COLOR_EXITO)
