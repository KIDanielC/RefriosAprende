"""Vista de inicio de sesión. No contiene lógica de negocio."""
import os
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from config.settings import (
    APP_NAME,
    COLOR_AZUL_OSCURO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_NEGRO,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    IMAGES_DIR,
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
        """Usa un Canvas (no widgets apilados) para poder dibujar la imagen de fondo
        y el texto realmente superpuestos, sin ninguna caja opaca entre ambos —
        Tkinter no permite transparencia real entre widgets normales, solo en un Canvas."""
        panel = ctk.CTkFrame(self, fg_color=COLOR_FONDO_PANEL, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")

        lienzo = tk.Canvas(panel, bg=COLOR_FONDO_PANEL, highlightthickness=0, bd=0)
        lienzo.place(relx=0, rely=0, relwidth=1, relheight=1)

        id_imagen = self._preparar_imagen_fondo(lienzo)

        lineas = [
            ("❄", (FONT_FAMILY, 40), COLOR_AZUL_OSCURO, -170),
            ("REFRIOS", (FONT_FAMILY, 52, "bold"), COLOR_NEGRO, -100),
            ("APRENDE", (FONT_FAMILY, 52, "bold"), COLOR_AZUL_OSCURO, -30),
            ("Plataforma de gestión de capacitaciones", (FONT_FAMILY, 17), COLOR_NEGRO, 45),
            ("Diagnóstico y mantenimiento de A/C automotriz", (FONT_FAMILY, 15), COLOR_AZUL_OSCURO, 78),
        ]
        # Halo blanco detrás de cada línea: mantiene el texto legible sin importar
        # qué tan clara u oscura sea la zona de la foto original sobre la que caiga.
        ids_halo = [
            [
                lienzo.create_text(0, 0, text=texto, font=fuente, fill=COLOR_FONDO_PANEL, anchor="center")
                for _ in range(8)
            ]
            for texto, fuente, _color, _y in lineas
        ]
        ids_texto = [
            (lienzo.create_text(0, 0, text=texto, font=fuente, fill=color, anchor="center"), y_offset)
            for texto, fuente, color, y_offset in lineas
        ]

        _DESPLAZAMIENTOS_HALO = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)]

        def _recentrar(_evento=None):
            centro_x, centro_y = lienzo.winfo_width() // 2, lienzo.winfo_height() // 2
            if id_imagen is not None:
                lienzo.coords(id_imagen, centro_x, centro_y)
            for indice, (id_item, y_offset) in enumerate(ids_texto):
                lienzo.coords(id_item, centro_x, centro_y + y_offset)
                for id_halo, (dx, dy) in zip(ids_halo[indice], _DESPLAZAMIENTOS_HALO):
                    lienzo.coords(id_halo, centro_x + dx, centro_y + y_offset + dy)

        lienzo.bind("<Configure>", _recentrar)

        # Doble línea de acento vertical estilo "circuito" (glow futurista), encima del lienzo
        acento_glow = ctk.CTkFrame(panel, fg_color=COLOR_ACENTO_SECUNDARIO, width=1, corner_radius=0)
        acento_glow.place(relx=1.0, rely=0, relheight=1.0, anchor="ne", x=-4)
        acento = ctk.CTkFrame(panel, fg_color=COLOR_ACENTO_PRIMARIO, width=4, corner_radius=0)
        acento.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

    def _preparar_imagen_fondo(self, lienzo: tk.Canvas):
        ruta_fondo = os.path.join(IMAGES_DIR, "fondo_login.png")
        if not os.path.isfile(ruta_fondo):
            return None

        imagen_pil = Image.open(ruta_fondo)
        self._foto_fondo_marca = ImageTk.PhotoImage(imagen_pil)  # referencia viva: evita que el GC la elimine
        return lienzo.create_image(0, 0, image=self._foto_fondo_marca, anchor="center")

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
            border_color=COLOR_ACENTO_PRIMARIO,
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
            fg_color=COLOR_ACENTO_PRIMARIO,
            hover_color=COLOR_ACENTO_SECUNDARIO,
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
