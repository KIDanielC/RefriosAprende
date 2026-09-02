"""Pantallas de acceso directo (menú lateral) a Evaluaciones y Simulaciones.

La lógica y las ventanas de gestión/presentación ya existían desde el Sprint 3
(EvaluacionFinalWindow, SimulacionesWindow, PresentarEvaluacionWindow,
ListaSimulacionesWindow); estas pantallas solo listan los cursos relevantes
según el rol y abren esas ventanas, para que "Evaluaciones"/"Simulaciones" del
menú dejen de caer en el placeholder "se construirá en un sprint posterior".
"""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
)
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.inscripcion_controller import InscripcionController
from model.dao.resultado_dao import ResultadoDAO
from model.entities.curso import Curso
from view.screens.evaluacion_final_screen import EvaluacionFinalWindow
from view.screens.presentar_evaluacion_screen import PresentarEvaluacionWindow
from view.screens.presentar_simulacion_screen import ListaSimulacionesWindow
from view.screens.simulaciones_screen import SimulacionesWindow


class _ListaCursosBase(ctk.CTkFrame):
    """Base común: tarjeta scrollable con un mensaje de vacío configurable."""

    def __init__(self, master, mensaje_vacio: str):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._mensaje_vacio = mensaje_vacio
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self._lista.grid_columnconfigure(0, weight=1)

    def _mostrar_vacio(self):
        ctk.CTkLabel(
            self._lista, text=self._mensaje_vacio, font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=0, column=0, pady=20)

    def _crear_tarjeta(self, fila: int) -> ctk.CTkFrame:
        tarjeta = ctk.CTkFrame(
            self._lista, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=8)
        tarjeta.grid_columnconfigure(0, weight=1)
        return tarjeta


class EvaluacionesAdminScreen(_ListaCursosBase):
    """Administrador: acceso directo a configurar la evaluación final y las
    simulaciones de cualquier curso activo, sin pasar por Gestión de Cursos."""

    def __init__(self, master, usuario_sesion=None):
        super().__init__(master, "Todavía no hay cursos activos. Crea uno en Gestión de Cursos.")
        self._curso_controlador = CursoController()
        self._evaluacion_controlador = EvaluacionController()
        self._cargar()

    def _cargar(self):
        cursos = self._curso_controlador.listar_cursos_activos()
        if not cursos:
            self._mostrar_vacio()
            return
        for indice, curso in enumerate(cursos):
            self._construir_tarjeta_curso(indice, curso)

    def _construir_tarjeta_curso(self, fila: int, curso: Curso):
        tarjeta = self._crear_tarjeta(fila)

        ctk.CTkLabel(
            tarjeta, text=curso.nombre_curso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 2))

        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
        estado_texto = "Evaluación final configurada" if evaluacion_final else "Sin evaluación final todavía"
        ctk.CTkLabel(
            tarjeta, text=estado_texto, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 16))

        ctk.CTkButton(
            botones, text="Evaluación final", height=36, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 13, "bold"),
            command=lambda c=curso: EvaluacionFinalWindow(self, curso=c),
        ).pack(side="left")

        ctk.CTkButton(
            botones, text="Simulaciones", height=36, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_ALTERNO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 13, "bold"),
            command=lambda c=curso: SimulacionesWindow(self, curso=c),
        ).pack(side="left", padx=(10, 0))


class EvaluacionesAprendizScreen(_ListaCursosBase):
    """Aprendiz: presenta directamente la evaluación final de cualquiera de sus
    cursos matriculados, sin tener que entrar primero al lector de contenido."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, "Todavía no estás matriculado en ningún curso.")
        self._usuario_sesion = usuario_sesion
        self._inscripcion_controlador = InscripcionController()
        self._evaluacion_controlador = EvaluacionController()
        self._resultado_dao = ResultadoDAO()
        self._cargar()

    def _cargar(self):
        cursos = self._inscripcion_controlador.listar_cursos_matriculados(self._usuario_sesion.id_usuario)
        if not cursos:
            self._mostrar_vacio()
            return
        for indice, curso in enumerate(cursos):
            self._construir_tarjeta_curso(indice, curso)

    def _construir_tarjeta_curso(self, fila: int, curso: Curso):
        tarjeta = self._crear_tarjeta(fila)

        ctk.CTkLabel(
            tarjeta, text=curso.nombre_curso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 2))

        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(curso.id_curso)
        if evaluacion_final is None:
            ctk.CTkLabel(
                tarjeta, text="Este curso todavía no tiene evaluación final.", font=(FONT_FAMILY, 12),
                text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
            return

        intentos_usados = self._evaluacion_controlador.intentos_usados(
            self._usuario_sesion.id_usuario, evaluacion_final.id_evaluacion
        )
        aprobado = self._resultado_dao.existe_aprobado(self._usuario_sesion.id_usuario, evaluacion_final.id_evaluacion)
        color_estado = COLOR_EXITO if aprobado else COLOR_TEXTO_SECUNDARIO
        texto_estado = "✓ Aprobada" if aprobado else f"Intentos usados: {intentos_usados} / {evaluacion_final.intentos_permitidos}"
        ctk.CTkLabel(
            tarjeta, text=texto_estado, font=(FONT_FAMILY, 12), text_color=color_estado, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        agotados = intentos_usados >= evaluacion_final.intentos_permitidos
        boton = ctk.CTkButton(
            tarjeta, text="Presentar evaluación", height=36, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 13, "bold"),
            command=lambda e=evaluacion_final: PresentarEvaluacionWindow(self, evaluacion=e, usuario_sesion=self._usuario_sesion),
        )
        boton.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 16))
        if aprobado or agotados:
            boton.configure(state="disabled")


class SimulacionesAprendizScreen(_ListaCursosBase):
    """Aprendiz: acceso directo a practicar los casos de simulación de cualquiera
    de sus cursos matriculados."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, "Todavía no estás matriculado en ningún curso.")
        self._usuario_sesion = usuario_sesion
        self._inscripcion_controlador = InscripcionController()
        self._cargar()

    def _cargar(self):
        cursos = self._inscripcion_controlador.listar_cursos_matriculados(self._usuario_sesion.id_usuario)
        if not cursos:
            self._mostrar_vacio()
            return
        for indice, curso in enumerate(cursos):
            self._construir_tarjeta_curso(indice, curso)

    def _construir_tarjeta_curso(self, fila: int, curso: Curso):
        tarjeta = self._crear_tarjeta(fila)

        ctk.CTkLabel(
            tarjeta, text=curso.nombre_curso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 12))

        ctk.CTkButton(
            tarjeta, text="Ver casos de simulación", height=36, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_ALTERNO, hover_color=COLOR_ACENTO_PRIMARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 13, "bold"),
            command=lambda c=curso: ListaSimulacionesWindow(self, curso=c, usuario_sesion=self._usuario_sesion),
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 16))
