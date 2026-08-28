"""Vista de Dashboard principal (post-login). Sidebar + área de contenido dinámica."""
import customtkinter as ctk

from config.settings import (
    APP_NAME,
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_GLOW,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_NAV_BORDE,
    COLOR_NAV_FONDO,
    COLOR_NAV_FONDO_HOVER,
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
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.progreso_controller import ProgresoController
from controller.usuario_controller import UsuarioController
from model.dao.resultado_dao import ResultadoDAO
from model.entities.usuario import Usuario
from view.screens.cursos_screen import CursosScreen
from view.screens.mi_progreso_screen import MiProgresoScreen
from view.screens.mis_cursos_screen import MisCursosScreen
from view.screens.usuarios_screen import UsuariosScreen

_SECCION_DASHBOARD = "Dashboard"
_SECCION_USUARIOS = "Gestión de Usuarios"
_SECCION_CURSOS = "Gestión de Cursos"
_SECCION_MIS_CURSOS = "Cursos"
_SECCION_MI_PROGRESO = "Mi Progreso"


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
                ("📚", _SECCION_CURSOS),
                ("📝", "Evaluaciones"),
                ("📊", "Reportes"),
                ("⚙", "Configuración"),
            ]
        return [
            ("🏠", _SECCION_DASHBOARD),
            ("📚", _SECCION_MIS_CURSOS),
            ("📝", "Evaluaciones"),
            ("🧪", "Simulaciones"),
            ("📈", _SECCION_MI_PROGRESO),
            ("👤", "Mi Perfil"),
        ]

    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=COLOR_NAV_FONDO, corner_radius=0, width=252)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        marca = ctk.CTkFrame(sidebar, fg_color="transparent", border_width=0)
        marca.pack(pady=(24, 18), padx=20, anchor="w", fill="x")
        insignia_marca = ctk.CTkFrame(
            marca, fg_color=COLOR_ACENTO_PRIMARIO, corner_radius=10, width=36, height=36,
        )
        insignia_marca.pack(side="left")
        insignia_marca.pack_propagate(False)
        ctk.CTkLabel(
            insignia_marca, text="RA", font=(FONT_FAMILY, 13, "bold"), text_color="#FFFFFF",
        ).pack(expand=True)
        texto_marca = ctk.CTkFrame(marca, fg_color="transparent")
        texto_marca.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            texto_marca, text="Refrios Aprende", font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_NAV_TEXTO, anchor="w",
        ).pack(anchor="w")

        separador = ctk.CTkFrame(sidebar, fg_color=COLOR_NAV_BORDE, height=1, corner_radius=0)
        separador.pack(fill="x", padx=20, pady=(0, 14))

        for icono, opcion in self._opciones_menu():
            boton = ctk.CTkButton(
                sidebar,
                text=f"  {icono}   {opcion}",
                anchor="w",
                fg_color="transparent",
                hover_color=COLOR_NAV_FONDO_HOVER,
                text_color=COLOR_NAV_TEXTO_SECUNDARIO,
                font=(FONT_FAMILY, 13, "bold"),
                height=42,
                corner_radius=RADIO_BOTON,
                command=lambda nombre=opcion: self._mostrar_seccion(nombre),
            )
            boton.pack(fill="x", padx=12, pady=2)
            self._botones_menu[opcion] = boton

        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)

        pie = ctk.CTkFrame(sidebar, fg_color="transparent", border_width=0)
        pie.pack(fill="x", padx=20, pady=(0, 4))
        separador_pie = ctk.CTkFrame(sidebar, fg_color=COLOR_NAV_BORDE, height=1, corner_radius=0)
        separador_pie.pack(fill="x", padx=20, pady=(0, 14))

        avatar = ctk.CTkFrame(pie, fg_color=COLOR_ACENTO_ALTERNO, corner_radius=16, width=32, height=32)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        iniciales = "".join(parte[0] for parte in self._usuario.nombre_completo.split()[:2]).upper()
        ctk.CTkLabel(avatar, text=iniciales, font=(FONT_FAMILY, 11, "bold"), text_color="#FFFFFF").pack(expand=True)
        texto_pie = ctk.CTkFrame(pie, fg_color="transparent")
        texto_pie.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            texto_pie, text=self._usuario.nombre_completo, font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_NAV_TEXTO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            texto_pie, text=self._usuario.nombre_rol.title(), font=(FONT_FAMILY, 10.5),
            text_color=COLOR_NAV_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w")

        ctk.CTkButton(
            sidebar,
            text="⏻  Cerrar sesión",
            fg_color="transparent",
            hover_color=COLOR_ERROR,
            border_width=GROSOR_BORDE_SUTIL,
            border_color=COLOR_ERROR,
            text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 13, "bold"),
            height=40,
            corner_radius=RADIO_BOTON,
            command=self._manejar_cierre_sesion,
        ).pack(side="bottom", fill="x", padx=12, pady=(0, 16))

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
            activo = nombre == nombre_seccion
            boton.configure(
                fg_color=COLOR_NAV_FONDO_HOVER if activo else "transparent",
                text_color=COLOR_ACENTO_GLOW if activo else COLOR_NAV_TEXTO_SECUNDARIO,
                border_width=GROSOR_BORDE_SUTIL if activo else 0,
                border_color=COLOR_ACENTO_PRIMARIO,
            )

        self._etiqueta_titulo_seccion.configure(text=nombre_seccion)

        if self._frame_seccion_actual is not None:
            self._frame_seccion_actual.destroy()

        if nombre_seccion == _SECCION_DASHBOARD:
            self._frame_seccion_actual = self._construir_seccion_dashboard(self._area_seccion)
        elif nombre_seccion == _SECCION_USUARIOS and self._usuario.es_administrador():
            self._frame_seccion_actual = UsuariosScreen(self._area_seccion, usuario_sesion=self._usuario)
        elif nombre_seccion == _SECCION_CURSOS and self._usuario.es_administrador():
            self._frame_seccion_actual = CursosScreen(self._area_seccion, usuario_sesion=self._usuario)
        elif nombre_seccion == _SECCION_MIS_CURSOS and not self._usuario.es_administrador():
            self._frame_seccion_actual = MisCursosScreen(self._area_seccion, usuario_sesion=self._usuario)
        elif nombre_seccion == _SECCION_MI_PROGRESO and not self._usuario.es_administrador():
            self._frame_seccion_actual = MiProgresoScreen(self._area_seccion, usuario_sesion=self._usuario)
        else:
            self._frame_seccion_actual = self._construir_seccion_en_construccion(self._area_seccion, nombre_seccion)

        self._frame_seccion_actual.grid(row=0, column=0, sticky="nsew")

    def _construir_seccion_dashboard(self, contenedor):
        frame = ctk.CTkScrollableFrame(contenedor, fg_color=COLOR_FONDO_APP, corner_radius=0)
        frame.grid_columnconfigure(0, weight=1)

        saludo = ctk.CTkFrame(frame, fg_color="transparent")
        saludo.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 4))
        ctk.CTkLabel(
            saludo, text=f"Hola, {self._usuario.nombre_completo.split()[0]}", font=(FONT_FAMILY, 21, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            saludo, text="Esto es lo que pasa en tu formación esta semana.", font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        area_tarjetas = ctk.CTkFrame(frame, fg_color="transparent")
        area_tarjetas.grid(row=1, column=0, sticky="nsew", padx=24, pady=(18, 10))
        tarjetas = self._calcular_tarjetas_dashboard()
        for indice in range(len(tarjetas)):
            area_tarjetas.grid_columnconfigure(indice, weight=1)

        for indice, (icono, titulo, valor) in enumerate(tarjetas):
            tarjeta = ctk.CTkFrame(
                area_tarjetas,
                fg_color=COLOR_FONDO_TARJETA,
                corner_radius=RADIO_TARJETA,
                height=118,
                border_width=GROSOR_BORDE_SUTIL,
                border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.grid(row=0, column=indice, padx=6, sticky="ew")
            tarjeta.grid_propagate(False)
            encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
            encabezado.pack(anchor="w", padx=18, pady=(16, 0), fill="x")
            insignia = ctk.CTkFrame(encabezado, fg_color=COLOR_FONDO_TARJETA_HOVER, corner_radius=9, width=32, height=32)
            insignia.pack(side="left")
            insignia.pack_propagate(False)
            ctk.CTkLabel(insignia, text=icono, font=(FONT_FAMILY, 14)).pack(expand=True)
            ctk.CTkLabel(
                tarjeta, text=titulo, font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).pack(anchor="w", padx=18, pady=(10, 2), fill="x")
            ctk.CTkLabel(
                tarjeta, text=valor, font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
            ).pack(anchor="w", padx=18)

        detalle = ctk.CTkFrame(frame, fg_color="transparent")
        detalle.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 24))
        detalle.grid_columnconfigure(0, weight=3)
        detalle.grid_columnconfigure(1, weight=2)

        panel_avance = ctk.CTkFrame(
            detalle, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        panel_avance.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(
            panel_avance, text="Avance por curso", font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(
            panel_avance, text="Porcentaje de contenidos completados", font=(FONT_FAMILY, 11.5),
            text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        for nombre_curso, porcentaje in self._calcular_avance_por_curso():
            fila = ctk.CTkFrame(panel_avance, fg_color="transparent")
            fila.pack(fill="x", padx=20, pady=6)
            fila.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                fila, text=nombre_curso, font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
                anchor="w", width=170,
            ).grid(row=0, column=0, sticky="w")
            barra = ctk.CTkProgressBar(
                fila, height=8, corner_radius=99, fg_color=COLOR_BORDE_SUTIL, progress_color=COLOR_ACENTO_PRIMARIO,
            )
            barra.set(porcentaje / 100)
            barra.grid(row=0, column=1, sticky="ew", padx=12)
            ctk.CTkLabel(
                fila, text=f"{porcentaje:.0f}%", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_SECUNDARIO,
                width=36,
            ).grid(row=0, column=2, sticky="e")
        ctk.CTkFrame(panel_avance, fg_color="transparent", height=14).pack()

        panel_estado = ctk.CTkFrame(
            detalle, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        panel_estado.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(
            panel_estado, text="Estado general", font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", padx=20, pady=(18, 10))
        for etiqueta, valor in self._calcular_estado_general():
            fila = ctk.CTkFrame(panel_estado, fg_color="transparent")
            fila.pack(fill="x", padx=20, pady=7)
            ctk.CTkLabel(
                fila, text=etiqueta, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                fila, text=valor, font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="e",
            ).pack(side="right")
        ctk.CTkFrame(panel_estado, fg_color="transparent", height=14).pack()

        return frame

    def _calcular_avance_por_curso(self):
        curso_controlador = CursoController()
        progreso_controlador = ProgresoController()
        cursos_activos = curso_controlador.listar_cursos_activos()

        resultado = []
        for curso in cursos_activos:
            if self._usuario.es_administrador():
                porcentajes = [
                    (progreso_controlador.obtener_progreso(u.id_usuario, curso.id_curso) or None)
                    for u in UsuarioController().listar_usuarios() if not u.es_administrador()
                ]
                valores = [p.porcentaje_avance for p in porcentajes if p is not None]
                porcentaje = sum(valores) / len(valores) if valores else 0.0
            else:
                progreso = progreso_controlador.obtener_progreso(self._usuario.id_usuario, curso.id_curso)
                porcentaje = progreso.porcentaje_avance if progreso else 0.0
            resultado.append((curso.nombre_curso, porcentaje))
        return resultado[:6]

    def _calcular_estado_general(self):
        if self._usuario.es_administrador():
            total_aprendices = sum(1 for u in UsuarioController().listar_usuarios() if not u.es_administrador())
            return [
                ("Aprendices activos", str(total_aprendices)),
                ("Rol de sesión", self._usuario.nombre_rol.title()),
            ]

        curso_controlador = CursoController()
        evaluacion_controlador = EvaluacionController()
        progreso_controlador = ProgresoController()
        resultado_dao = ResultadoDAO()
        cursos_activos = curso_controlador.listar_cursos_activos()

        cursos_completados = 0
        evaluaciones_aprobadas = 0
        for curso in cursos_activos:
            progreso = progreso_controlador.obtener_progreso(self._usuario.id_usuario, curso.id_curso)
            if progreso and progreso.porcentaje_avance >= 100:
                cursos_completados += 1
            evaluacion_final = evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
            if evaluacion_final and resultado_dao.existe_aprobado(self._usuario.id_usuario, evaluacion_final.id_evaluacion):
                evaluaciones_aprobadas += 1

        return [
            ("Cursos completados", str(cursos_completados)),
            ("Evaluaciones aprobadas", str(evaluaciones_aprobadas)),
        ]

    def _calcular_tarjetas_dashboard(self):
        curso_controlador = CursoController()
        cursos_activos = curso_controlador.listar_cursos_activos()

        if self._usuario.es_administrador():
            evaluacion_controlador = EvaluacionController()
            total_evaluaciones = sum(
                1 for curso in cursos_activos if evaluacion_controlador.obtener_evaluacion_final(curso.id_curso) is not None
            )
            total_aprendices = sum(1 for u in UsuarioController().listar_usuarios() if not u.es_administrador())
            return [
                ("📚", "Cursos activos", str(len(cursos_activos))),
                ("📝", "Evaluaciones finales creadas", str(total_evaluaciones)),
                ("👥", "Aprendices registrados", str(total_aprendices)),
            ]

        evaluacion_controlador = EvaluacionController()
        progreso_controlador = ProgresoController()
        resultado_dao = ResultadoDAO()

        evaluaciones_pendientes = 0
        porcentajes = []
        for curso in cursos_activos:
            progreso = progreso_controlador.obtener_progreso(self._usuario.id_usuario, curso.id_curso)
            porcentajes.append(progreso.porcentaje_avance if progreso else 0.0)

            evaluacion_final = evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
            if evaluacion_final is not None and not resultado_dao.existe_aprobado(self._usuario.id_usuario, evaluacion_final.id_evaluacion):
                evaluaciones_pendientes += 1

        progreso_promedio = sum(porcentajes) / len(porcentajes) if porcentajes else 0.0

        return [
            ("📚", "Cursos disponibles", str(len(cursos_activos))),
            ("📝", "Evaluaciones pendientes", str(evaluaciones_pendientes)),
            ("📈", "Progreso general", f"{progreso_promedio:.0f}%"),
        ]

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
