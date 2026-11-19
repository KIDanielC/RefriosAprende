"""Ventana de primer arranque: se muestra cuando todavía no existe ningún administrador
activo en la base de datos, para que quien instala la aplicación cree la primera cuenta con
su propia contraseña, en vez de depender de una cuenta y una clave de fábrica escritas en el
código. No contiene lógica de negocio."""
import customtkinter as ctk

from config.settings import (
    APP_NAME,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
)
from controller.usuario_controller import DatosInvalidosError, UsuarioController

_NOMBRE_ROL_ADMINISTRADOR = "ADMINISTRADOR"


class PrimerAdministradorView(ctk.CTk):
    def __init__(self, al_crear_administrador):
        super().__init__()
        self._al_crear_administrador = al_crear_administrador
        self._controlador = UsuarioController()

        self.title(APP_NAME)
        self.geometry("520x680")
        self.minsize(480, 640)
        self.configure(fg_color=COLOR_FONDO_APP)

        self._construir()

    def _construir(self):
        tarjeta = ctk.CTkFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            tarjeta, text="Configuración inicial", font=(FONT_FAMILY, 20, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(padx=36, pady=(32, 4), anchor="w")
        ctk.CTkLabel(
            tarjeta,
            text="Todavía no hay ningún administrador registrado. Crea la primera\ncuenta "
            "para empezar a usar Refrios Aprende.",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, justify="left",
        ).pack(padx=36, pady=(0, 20), anchor="w")

        self._campo_nombre = self._crear_campo(tarjeta, "Nombre completo")
        self._campo_documento = self._crear_campo(tarjeta, "Documento")
        self._campo_correo = self._crear_campo(tarjeta, "Correo electrónico")
        self._campo_usuario = self._crear_campo(tarjeta, "Usuario")
        self._campo_contrasena = self._crear_campo(tarjeta, "Contraseña", oculto=True)
        self._campo_confirmar = self._crear_campo(tarjeta, "Confirmar contraseña", oculto=True)

        self._etiqueta_error = ctk.CTkLabel(
            tarjeta, text="", font=(FONT_FAMILY, 12), text_color=COLOR_ERROR, wraplength=380, justify="left",
        )
        self._etiqueta_error.pack(padx=36, pady=(6, 0), anchor="w")

        ctk.CTkButton(
            tarjeta, text="Crear administrador", width=380, height=44, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 14, "bold"), command=self._crear,
        ).pack(padx=36, pady=(18, 32))

    def _crear_campo(self, master, etiqueta: str, oculto: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(
            master, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(padx=36, pady=(6, 2), anchor="w")
        campo = ctk.CTkEntry(
            master, width=380, height=40, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            show="•" if oculto else "",
        )
        campo.pack(padx=36, pady=(0, 2))
        return campo

    def _crear(self):
        if self._campo_contrasena.get() != self._campo_confirmar.get():
            self._etiqueta_error.configure(text="Las contraseñas no coinciden.")
            return

        rol_admin = next(
            (rol for rol in self._controlador.listar_roles() if rol.nombre_rol == _NOMBRE_ROL_ADMINISTRADOR), None
        )
        if rol_admin is None:
            self._etiqueta_error.configure(text="No se encontró el rol Administrador en la base de datos.")
            return

        try:
            self._controlador.crear_usuario(
                self._campo_nombre.get(),
                self._campo_documento.get(),
                self._campo_correo.get(),
                self._campo_usuario.get(),
                self._campo_contrasena.get(),
                rol_admin.id_rol,
            )
        except DatosInvalidosError as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self._etiqueta_error.configure(text="")
        self.destroy()
        self._al_crear_administrador()
