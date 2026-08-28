"""Vista de inicio de sesión. No contiene lógica de negocio."""
import customtkinter as ctk

from config.settings import (
    APP_NAME,
    COLOR_AMARILLO,
    COLOR_AZUL_PRIMARIO,
    COLOR_AZUL_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    VENTANA_ALTO,
    VENTANA_ANCHO,
)
from controller.autenticacion_controller import (
    AutenticacionController,
    CredencialesInvalidasError,
    UsuarioInactivoError,
)


class LoginView(ctk.CTk):
    """Ventana de autenticación. Al validar credenciales, invoca `al_iniciar_sesion`."""

    def __init__(self, al_iniciar_sesion):
        super().__init__()
        self._al_iniciar_sesion = al_iniciar_sesion
        self._controlador = AutenticacionController()

        self.title(APP_NAME)
        self.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}")
        self.minsize(1000, 640)
        self.configure(fg_color=COLOR_FONDO_APP)

        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_marca()
        self._construir_panel_formulario()

    # ------------------------------------------------------------------
    def _construir_panel_marca(self):
        panel = ctk.CTkFrame(self, fg_color=COLOR_FONDO_PANEL, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # Doble línea de acento vertical estilo "circuito" (glow futurista)
        acento_glow = ctk.CTkFrame(panel, fg_color=COLOR_AZUL_SECUNDARIO, width=1, corner_radius=0)
        acento_glow.place(relx=1.0, rely=0, relheight=1.0, anchor="ne", x=-4)
        acento = ctk.CTkFrame(panel, fg_color=COLOR_AZUL_PRIMARIO, width=4, corner_radius=0)
        acento.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        contenedor = ctk.CTkFrame(panel, fg_color="transparent")
        contenedor.grid(row=0, column=0)

        ctk.CTkLabel(
            contenedor,
            text="❄",
            font=(FONT_FAMILY, 40),
            text_color=COLOR_AZUL_SECUNDARIO,
        ).pack(pady=(0, 14))

        ctk.CTkLabel(
            contenedor,
            text="REFRIOS",
            font=(FONT_FAMILY, 52, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        ).pack()
        ctk.CTkLabel(
            contenedor,
            text="APRENDE",
            font=(FONT_FAMILY, 52, "bold"),
            text_color=COLOR_AMARILLO,
        ).pack(pady=(0, 26))
        ctk.CTkLabel(
            contenedor,
            text="Plataforma de gestión de capacitaciones",
            font=(FONT_FAMILY, 17),
            text_color=COLOR_TEXTO_SECUNDARIO,
            justify="center",
        ).pack()
        ctk.CTkLabel(
            contenedor,
            text="Diagnóstico y mantenimiento de A/C automotriz",
            font=(FONT_FAMILY, 15),
            text_color=COLOR_AZUL_SECUNDARIO,
            justify="center",
        ).pack(pady=(4, 0))

    def _construir_panel_formulario(self):
        panel = ctk.CTkFrame(self, fg_color=COLOR_FONDO_APP, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            panel,
            fg_color=COLOR_FONDO_TARJETA,
            corner_radius=4,
            width=440,
            border_width=2,
            border_color=COLOR_AZUL_PRIMARIO,
        )
        tarjeta.grid(row=0, column=0)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text="Iniciar sesión", font=(FONT_FAMILY, 28, "bold"), text_color=COLOR_TEXTO_PRIMARIO
        ).grid(row=0, column=0, padx=44, pady=(40, 8), sticky="w")
        ctk.CTkLabel(
            tarjeta,
            text="Ingresa tus credenciales para continuar",
            font=(FONT_FAMILY, 15),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=1, column=0, padx=44, pady=(0, 28), sticky="w")

        self._campo_usuario = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Usuario",
            width=350,
            height=48,
            corner_radius=4,
            fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL,
            border_width=1,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 15),
        )
        self._campo_usuario.grid(row=2, column=0, padx=44, pady=10)

        self._campo_contrasena = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Contraseña",
            show="•",
            width=350,
            height=48,
            corner_radius=4,
            fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL,
            border_width=1,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 15),
        )
        self._campo_contrasena.grid(row=3, column=0, padx=44, pady=10)
        self._campo_contrasena.bind("<Return>", lambda evento: self._manejar_inicio_sesion())

        self._etiqueta_error = ctk.CTkLabel(
            tarjeta, text="", font=(FONT_FAMILY, 13), text_color=COLOR_ERROR, wraplength=350
        )
        self._etiqueta_error.grid(row=4, column=0, padx=44, pady=(6, 0))

        self._boton_ingresar = ctk.CTkButton(
            tarjeta,
            text="INGRESAR",
            width=350,
            height=50,
            corner_radius=4,
            fg_color=COLOR_AZUL_PRIMARIO,
            hover_color=COLOR_AZUL_SECUNDARIO,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 16, "bold"),
            command=self._manejar_inicio_sesion,
        )
        self._boton_ingresar.grid(row=5, column=0, padx=44, pady=(24, 14))

        ctk.CTkLabel(
            tarjeta,
            text="Acceso exclusivo para personal autorizado de Refrios",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=6, column=0, padx=44, pady=(0, 32))

    # ------------------------------------------------------------------
    def _manejar_inicio_sesion(self):
        usuario = self._campo_usuario.get()
        contrasena = self._campo_contrasena.get()

        try:
            entidad_usuario = self._controlador.iniciar_sesion(usuario, contrasena)
        except (CredencialesInvalidasError, UsuarioInactivoError) as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self._etiqueta_error.configure(text="")
        self.destroy()
        self._al_iniciar_sesion(entidad_usuario)
