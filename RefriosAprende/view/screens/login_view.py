"""Vista de inicio de sesión. No contiene lógica de negocio."""
import customtkinter as ctk

from config.settings import (
    APP_NAME,
    COLOR_ACENTO_GLOW,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_NAV_BORDE,
    COLOR_NAV_FONDO,
    COLOR_NAV_TEXTO,
    COLOR_NAV_TEXTO_SECUNDARIO,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
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
        panel = ctk.CTkFrame(self, fg_color=COLOR_NAV_FONDO, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=0)
        panel.grid_columnconfigure(0, weight=1)

        contenido = ctk.CTkFrame(panel, fg_color="transparent")
        contenido.grid(row=0, column=0, sticky="nsew", padx=56, pady=(60, 20))
        contenido.grid_rowconfigure(0, weight=1)

        cuerpo = ctk.CTkFrame(contenido, fg_color="transparent")
        cuerpo.pack(anchor="w", fill="x")

        insignia = ctk.CTkFrame(cuerpo, fg_color=COLOR_ACENTO_PRIMARIO, corner_radius=13, width=52, height=52)
        insignia.pack(anchor="w")
        insignia.pack_propagate(False)
        ctk.CTkLabel(insignia, text="RA", font=(FONT_FAMILY, 20, "bold"), text_color="#FFFFFF").pack(expand=True)

        ctk.CTkLabel(
            cuerpo,
            text="Formación técnica que\nse mide, no se supone.",
            font=(FONT_FAMILY, 30, "bold"),
            text_color=COLOR_NAV_TEXTO,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(26, 14))

        ctk.CTkLabel(
            cuerpo,
            text=(
                "Cursos, evaluaciones y simulaciones de diagnóstico para el\n"
                "equipo técnico de Refrios — con seguimiento de avance\n"
                "en tiempo real."
            ),
            font=(FONT_FAMILY, 13.5),
            text_color=COLOR_NAV_TEXTO_SECUNDARIO,
            justify="left",
            anchor="w",
        ).pack(anchor="w")

        pie = ctk.CTkFrame(panel, fg_color="transparent")
        pie.grid(row=1, column=0, sticky="ew", padx=56, pady=(10, 44))
        separador = ctk.CTkFrame(pie, fg_color=COLOR_NAV_BORDE, height=1, corner_radius=0)
        separador.pack(fill="x", pady=(0, 18))
        fila_stats = ctk.CTkFrame(pie, fg_color="transparent")
        fila_stats.pack(anchor="w")
        for valor, etiqueta in (("18", "Cursos activos"), ("92%", "Aprobación"), ("236", "Aprendices")):
            estadistica = ctk.CTkFrame(fila_stats, fg_color="transparent")
            estadistica.pack(side="left", padx=(0, 34))
            ctk.CTkLabel(
                estadistica, text=valor, font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_ACENTO_GLOW, anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                estadistica, text=etiqueta, font=(FONT_FAMILY, 10.5), text_color=COLOR_NAV_TEXTO_SECUNDARIO, anchor="w",
            ).pack(anchor="w")

    def _construir_panel_formulario(self):
        panel = ctk.CTkFrame(self, fg_color=COLOR_FONDO_APP, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            panel,
            fg_color=COLOR_FONDO_TARJETA,
            corner_radius=RADIO_TARJETA + 4,
            width=440,
            border_width=GROSOR_BORDE_SUTIL,
            border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=0, column=0)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text="Bienvenido de nuevo", font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXTO_PRIMARIO
        ).grid(row=0, column=0, padx=44, pady=(40, 8), sticky="w")
        ctk.CTkLabel(
            tarjeta,
            text="Ingresa tus credenciales para continuar tu formación.",
            font=(FONT_FAMILY, 13.5),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=1, column=0, padx=44, pady=(0, 28), sticky="w")

        self._campo_usuario = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Usuario",
            width=350,
            height=48,
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL,
            border_width=GROSOR_BORDE_SUTIL,
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
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL,
            border_width=GROSOR_BORDE_SUTIL,
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
            text="Iniciar sesión",
            width=350,
            height=50,
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO,
            hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF",
            font=(FONT_FAMILY, 16, "bold"),
            command=self._manejar_inicio_sesion,
        )
        self._boton_ingresar.grid(row=5, column=0, padx=44, pady=(24, 14))

        ctk.CTkLabel(
            tarjeta,
            text="¿Olvidaste tu contraseña? Contacta a un administrador.",
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
