"""Vista de Dashboard principal (post-login). Sidebar + área de contenido dinámica."""
import customtkinter as ctk

from config.settings import (
    APP_NAME,
    COLOR_AMARILLO,
    COLOR_AZUL_PRIMARIO,
    COLOR_AZUL_SECUNDARIO,
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    VENTANA_ALTO,
    VENTANA_ANCHO,
)
from model.entities.usuario import Usuario
from view.screens.usuarios_screen import UsuariosScreen

_SECCION_DASHBOARD = "Dashboard"
_SECCION_USUARIOS = "Gestión de Usuarios"


class DashboardView(ctk.CTk):
    """Ventana principal tras autenticarse. Contiene sidebar de navegación y área de contenido."""

    def __init__(self, usuario: Usuario, al_cerrar_sesion):
        super().__init__()
        self._usuario = usuario
        self._al_cerrar_sesion = al_cerrar_sesion
        self._botones_menu = {}
        self._frame_seccion_actual = None

        self.title(f"{APP_NAME} - {usuario.nombre_completo}")
        self.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}")
        self.minsize(1100, 680)
        self.configure(fg_color=COLOR_FONDO_APP)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_sidebar()
        self._construir_area_contenido()
        self._mostrar_seccion(_SECCION_DASHBOARD)

    # ------------------------------------------------------------------
    def _opciones_menu(self):
        if self._usuario.es_administrador():
            return [
                ("🏠", _SECCION_DASHBOARD),
                ("👥", _SECCION_USUARIOS),
                ("📚", "Gestión de Cursos"),
                ("📄", "Gestión de Contenidos"),
                ("📝", "Evaluaciones"),
                ("📊", "Reportes"),
                ("⚙", "Configuración"),
            ]
        return [
            ("🏠", _SECCION_DASHBOARD),
            ("📚", "Cursos"),
            ("📝", "Evaluaciones"),
            ("🧪", "Simulaciones"),
            ("📈", "Mi Progreso"),
            ("👤", "Mi Perfil"),
        ]

    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=COLOR_FONDO_PANEL, corner_radius=0, width=270)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        acento_glow = ctk.CTkFrame(sidebar, fg_color=COLOR_AZUL_SECUNDARIO, width=1, corner_radius=0)
        acento_glow.place(relx=1.0, rely=0, relheight=1.0, anchor="ne", x=-3)
        acento = ctk.CTkFrame(sidebar, fg_color=COLOR_AZUL_PRIMARIO, width=3, corner_radius=0)
        acento.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        ctk.CTkLabel(
            sidebar, text="❄ Refrios Aprende", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXTO_PRIMARIO
        ).pack(pady=(30, 6), padx=24, anchor="w")

        insignia = ctk.CTkFrame(
            sidebar, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_AMARILLO
        )
        insignia.pack(padx=24, pady=(2, 28), anchor="w")
        ctk.CTkLabel(
            insignia,
            text=self._usuario.nombre_rol.title(),
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_AMARILLO,
        ).pack(padx=14, pady=6)

        for icono, opcion in self._opciones_menu():
            boton = ctk.CTkButton(
                sidebar,
                text=f"  {icono}   {opcion}",
                anchor="w",
                fg_color="transparent",
                hover_color=COLOR_FONDO_TARJETA_HOVER,
                text_color=COLOR_TEXTO_PRIMARIO,
                font=(FONT_FAMILY, 15),
                height=46,
                corner_radius=4,
                command=lambda nombre=opcion: self._mostrar_seccion(nombre),
            )
            boton.pack(fill="x", padx=16, pady=3)
            self._botones_menu[opcion] = boton

        ctk.CTkButton(
            sidebar,
            text="⏻  Cerrar sesión",
            fg_color=COLOR_ERROR,
            hover_color="#E14545",
            text_color="#1A0000",
            font=(FONT_FAMILY, 15, "bold"),
            height=46,
            corner_radius=4,
            command=self._manejar_cierre_sesion,
        ).pack(side="bottom", fill="x", padx=16, pady=22)

    def _construir_area_contenido(self):
        contenido = ctk.CTkFrame(self, fg_color=COLOR_FONDO_APP, corner_radius=0)
        contenido.grid(row=0, column=1, sticky="nsew")
        contenido.grid_columnconfigure(0, weight=1)
        contenido.grid_rowconfigure(1, weight=1)
        self._contenedor_principal = contenido

        self._barra_superior = ctk.CTkFrame(
            contenido, fg_color=COLOR_FONDO_PANEL, height=68, corner_radius=0, border_width=0
        )
        self._barra_superior.grid(row=0, column=0, sticky="ew")

        self._etiqueta_titulo_seccion = ctk.CTkLabel(
            self._barra_superior,
            text=_SECCION_DASHBOARD,
            font=(FONT_FAMILY, 17, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO,
        )
        self._etiqueta_titulo_seccion.pack(side="left", padx=28, pady=18)

        ctk.CTkLabel(
            self._barra_superior,
            text="● Sesión activa",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_EXITO,
        ).pack(side="right", padx=28)

        self._area_seccion = ctk.CTkFrame(contenido, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._area_seccion.grid(row=1, column=0, sticky="nsew")
        self._area_seccion.grid_columnconfigure(0, weight=1)
        self._area_seccion.grid_rowconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _mostrar_seccion(self, nombre_seccion: str):
        for nombre, boton in self._botones_menu.items():
            boton.configure(fg_color=COLOR_FONDO_TARJETA_HOVER if nombre == nombre_seccion else "transparent")

        self._etiqueta_titulo_seccion.configure(text=nombre_seccion)

        if self._frame_seccion_actual is not None:
            self._frame_seccion_actual.destroy()

        if nombre_seccion == _SECCION_DASHBOARD:
            self._frame_seccion_actual = self._construir_seccion_dashboard(self._area_seccion)
        elif nombre_seccion == _SECCION_USUARIOS and self._usuario.es_administrador():
            self._frame_seccion_actual = UsuariosScreen(self._area_seccion, usuario_sesion=self._usuario)
        else:
            self._frame_seccion_actual = self._construir_seccion_en_construccion(self._area_seccion, nombre_seccion)

        self._frame_seccion_actual.grid(row=0, column=0, sticky="nsew")

    def _construir_seccion_dashboard(self, contenedor):
        frame = ctk.CTkFrame(contenedor, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        area_tarjetas = ctk.CTkFrame(frame, fg_color="transparent")
        area_tarjetas.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=28, pady=28)
        for indice in range(3):
            area_tarjetas.grid_columnconfigure(indice, weight=1)

        tarjetas = [
            ("📚", "Cursos disponibles", "—"),
            ("📝", "Evaluaciones pendientes", "—"),
            ("📈", "Progreso general", "—"),
        ]
        for indice, (icono, titulo, valor) in enumerate(tarjetas):
            tarjeta = ctk.CTkFrame(
                area_tarjetas,
                fg_color=COLOR_FONDO_TARJETA,
                corner_radius=4,
                height=130,
                border_width=2,
                border_color=COLOR_AZUL_PRIMARIO,
            )
            tarjeta.grid(row=0, column=indice, padx=10, sticky="ew")
            ctk.CTkLabel(tarjeta, text=icono, font=(FONT_FAMILY, 24)).pack(anchor="w", padx=20, pady=(18, 0))
            ctk.CTkLabel(
                tarjeta, text=titulo, font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO
            ).pack(anchor="w", padx=20, pady=(6, 4))
            ctk.CTkLabel(
                tarjeta, text=valor, font=(FONT_FAMILY, 30, "bold"), text_color=COLOR_AZUL_SECUNDARIO
            ).pack(anchor="w", padx=20)

        return frame

    def _construir_seccion_en_construccion(self, contenedor, nombre_seccion):
        frame = ctk.CTkFrame(contenedor, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(
            frame,
            text=f"El módulo «{nombre_seccion}» se construirá en un sprint posterior.",
            font=(FONT_FAMILY, 16),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=0, column=0)
        return frame

    # ------------------------------------------------------------------
    def _manejar_cierre_sesion(self):
        self.destroy()
        self._al_cerrar_sesion()
