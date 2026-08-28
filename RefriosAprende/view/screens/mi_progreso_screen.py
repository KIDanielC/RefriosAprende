"""Pantalla del Aprendiz: seguimiento de su avance en cada curso activo."""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_PRIMARIO,
    COLOR_BORDE_SUTIL,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_TARJETA,
)
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from model.entities.progreso import COMPLETADO, EN_PROGRESO
from model.entities.usuario import Usuario

_TEXTOS_ESTADO = {
    "NO_INICIADO": "Sin iniciar",
    EN_PROGRESO: "En progreso",
    COMPLETADO: "Completado",
}
_COLORES_ESTADO = {
    "NO_INICIADO": COLOR_TEXTO_SECUNDARIO,
    EN_PROGRESO: COLOR_ACENTO_PRIMARIO,
    COMPLETADO: COLOR_EXITO,
}


class MiProgresoScreen(ctk.CTkFrame):
    """Muestra, por cada curso activo, el porcentaje de avance y el estado del aprendiz."""

    def __init__(self, master, usuario_sesion: Usuario):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._inscripcion_controlador = InscripcionController()
        self._progreso_controlador = ProgresoController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir()

    def _construir(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        contenedor.grid_columnconfigure(0, weight=1)

        cursos = self._inscripcion_controlador.listar_cursos_matriculados(self._usuario_sesion.id_usuario)
        if not cursos:
            ctk.CTkLabel(
                contenedor, text="Todavía no estás matriculado en ningún curso.", font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, curso in enumerate(cursos):
            progreso = self._progreso_controlador.obtener_progreso(self._usuario_sesion.id_usuario, curso.id_curso)
            porcentaje = progreso.porcentaje_avance if progreso else 0.0
            estado = progreso.estado if progreso else "NO_INICIADO"
            self._construir_tarjeta(contenedor, indice, curso.nombre_curso, porcentaje, estado)

    def _construir_tarjeta(self, contenedor, fila: int, nombre_curso: str, porcentaje: float, estado: str):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))
        encabezado.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado, text=nombre_curso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            encabezado, text=_TEXTOS_ESTADO.get(estado, estado), font=(FONT_FAMILY, 12, "bold"),
            text_color=_COLORES_ESTADO.get(estado, COLOR_TEXTO_SECUNDARIO),
        ).grid(row=0, column=1, sticky="e")

        barra = ctk.CTkProgressBar(
            tarjeta, height=10, corner_radius=99, fg_color=COLOR_BORDE_SUTIL,
            progress_color=_COLORES_ESTADO.get(estado, COLOR_ACENTO_PRIMARIO),
        )
        barra.set(porcentaje / 100)
        barra.grid(row=1, column=0, sticky="ew", padx=18, pady=(4, 6))

        ctk.CTkLabel(
            tarjeta, text=f"{porcentaje:.0f}% de contenidos vistos", font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 14))
