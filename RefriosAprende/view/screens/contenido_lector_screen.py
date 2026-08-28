"""Pantalla del Aprendiz: lectura de contenidos de un curso, acceso al cuestionario de
validación por contenido, a la evaluación final del curso y a sus simulaciones."""
import os
import subprocess
import sys

import customtkinter as ctk
from PIL import Image

from config.settings import (
    BASE_DIR,
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
)
from controller.contenido_controller import TIPO_IMAGEN, TIPO_PDF, ContenidoController
from controller.evaluacion_controller import EvaluacionController
from controller.progreso_controller import ProgresoController
from controller.simulacion_controller import SimulacionController
from controller.validacion_controller import ValidacionController
from model.entities.contenido import Contenido
from model.entities.curso import Curso
from model.entities.usuario import Usuario
from view.screens.presentar_evaluacion_screen import PresentarEvaluacionWindow
from view.screens.presentar_simulacion_screen import ListaSimulacionesWindow
from view.screens.responder_quiz_screen import ResponderQuizWindow


class ContenidoLectorScreen(ctk.CTkFrame):
    """Lista los contenidos de un curso en modo lectura y da acceso a evaluación/simulaciones."""

    def __init__(self, master, curso: Curso, usuario_sesion: Usuario, al_volver):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._curso = curso
        self._usuario_sesion = usuario_sesion
        self._al_volver = al_volver
        self._controlador = ContenidoController()
        self._validacion_controlador = ValidacionController()
        self._evaluacion_controlador = EvaluacionController()
        self._simulacion_controlador = SimulacionController()
        self._progreso_controlador = ProgresoController()
        self._imagenes_cargadas = []  # referencias vivas: evita que el GC libere las CTkImage en pantalla

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado()
        self._construir_lista()
        self._construir_pie_evaluacion()

    # ------------------------------------------------------------------
    def _construir_encabezado(self):
        ctk.CTkButton(
            self, text="←  Volver a mis cursos", fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            text_color=COLOR_ACENTO_SECUNDARIO, font=(FONT_FAMILY, 13, "bold"), width=170, height=32,
            command=self._al_volver,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 4))

        ctk.CTkLabel(
            self, text=self._curso.nombre_curso, font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(4, 12))

    def _construir_lista(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))
        contenedor.grid_columnconfigure(0, weight=1)

        contenidos = self._controlador.listar_por_curso(self._curso.id_curso)
        if not contenidos:
            ctk.CTkLabel(
                contenedor, text="Este curso aún no tiene contenidos publicados.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, contenido in enumerate(contenidos):
            self._construir_tarjeta_contenido(contenedor, indice, contenido)
            # Ver el contenido en esta pantalla cuenta como "leído" para el seguimiento.
            self._progreso_controlador.registrar_contenido_visto(self._usuario_sesion.id_usuario, contenido)

    def _construir_tarjeta_contenido(self, contenedor, fila: int, contenido: Contenido):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=4,
            border_width=1, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=f"{contenido.orden}. {contenido.titulo}", font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))

        fila_siguiente = 1
        if contenido.contenido_texto:
            ctk.CTkLabel(
                tarjeta, text=contenido.contenido_texto, font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
                anchor="w", justify="left", wraplength=760,
            ).grid(row=fila_siguiente, column=0, sticky="ew", padx=18, pady=(0, 12))
            fila_siguiente += 1

        if contenido.tipo_contenido == TIPO_IMAGEN:
            widget_imagen = self._construir_imagen(tarjeta, contenido)
            if widget_imagen is not None:
                widget_imagen.grid(row=fila_siguiente, column=0, sticky="w", padx=18, pady=(0, 12))
                fila_siguiente += 1

        if contenido.tipo_contenido == TIPO_PDF:
            ctk.CTkButton(
                tarjeta, text="📄  Abrir PDF", height=34, corner_radius=4,
                fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
                text_color="#FFFFFF", font=(FONT_FAMILY, 12, "bold"),
                command=lambda c=contenido: self._abrir_pdf(c),
            ).grid(row=fila_siguiente, column=0, sticky="w", padx=18, pady=(0, 12))
            fila_siguiente += 1

        total_preguntas = len(self._validacion_controlador.listar_preguntas(contenido))
        if total_preguntas > 0:
            ctk.CTkButton(
                tarjeta, text=f"Responder preguntas de validación ({total_preguntas})", height=34, corner_radius=4,
                fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_ALTERNO,
                text_color=COLOR_ACENTO_ALTERNO, font=(FONT_FAMILY, 12, "bold"),
                command=lambda c=contenido: self._abrir_quiz(c),
            ).grid(row=fila_siguiente, column=0, sticky="w", padx=18, pady=(0, 14))

    def _construir_pie_evaluacion(self):
        pie = ctk.CTkFrame(self, fg_color=COLOR_FONDO_TARJETA, corner_radius=4, border_width=1, border_color=COLOR_BORDE_SUTIL)
        pie.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 24))
        pie.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            pie, text="¿Ya estudiaste todo el curso?", font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, padx=(18, 12), pady=16, sticky="w")

        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(self._curso.id_curso)
        if evaluacion_final is not None:
            ctk.CTkButton(
                pie, text="Presentar evaluación final", height=36, corner_radius=4,
                fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
                font=(FONT_FAMILY, 12, "bold"), command=self._abrir_evaluacion_final,
            ).grid(row=0, column=1, padx=8, pady=16)

        casos = self._simulacion_controlador.listar_casos_por_curso(self._curso.id_curso)
        if casos:
            ctk.CTkButton(
                pie, text=f"Practicar simulaciones ({len(casos)})", height=36, corner_radius=4,
                fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=1, border_color=COLOR_ACENTO_ALTERNO,
                text_color=COLOR_ACENTO_ALTERNO, font=(FONT_FAMILY, 12, "bold"), command=self._abrir_simulaciones,
            ).grid(row=0, column=2, padx=8, pady=16, sticky="w")

        if evaluacion_final is None and not casos:
            ctk.CTkLabel(
                pie, text="Este curso todavía no tiene evaluación final ni simulaciones publicadas.",
                font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=1, padx=8, pady=16, sticky="w")

    # ------------------------------------------------------------------
    def _construir_imagen(self, tarjeta, contenido: Contenido):
        ruta_absoluta = os.path.join(BASE_DIR, contenido.ruta_archivo)
        if not os.path.isfile(ruta_absoluta):
            return None

        with Image.open(ruta_absoluta) as archivo_imagen:
            imagen_pil = archivo_imagen.copy()  # copia en memoria: libera el archivo en disco de inmediato

        ancho_maximo = 700
        if imagen_pil.width > ancho_maximo:
            alto_proporcional = int(imagen_pil.height * (ancho_maximo / imagen_pil.width))
            tamano = (ancho_maximo, alto_proporcional)
        else:
            tamano = (imagen_pil.width, imagen_pil.height)

        imagen_ctk = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=tamano)
        self._imagenes_cargadas.append(imagen_ctk)
        return ctk.CTkLabel(tarjeta, image=imagen_ctk, text="")

    def _abrir_pdf(self, contenido: Contenido):
        ruta_absoluta = os.path.join(BASE_DIR, contenido.ruta_archivo)
        if not os.path.isfile(ruta_absoluta):
            return
        if sys.platform.startswith("win"):
            os.startfile(ruta_absoluta)
        elif sys.platform == "darwin":
            subprocess.run(["open", ruta_absoluta], check=False)
        else:
            subprocess.run(["xdg-open", ruta_absoluta], check=False)

    def _abrir_quiz(self, contenido: Contenido):
        ResponderQuizWindow(self, contenido=contenido)

    def _abrir_evaluacion_final(self):
        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(self._curso.id_curso)
        PresentarEvaluacionWindow(self, evaluacion=evaluacion_final, usuario_sesion=self._usuario_sesion)

    def _abrir_simulaciones(self):
        ListaSimulacionesWindow(self, curso=self._curso, usuario_sesion=self._usuario_sesion)
