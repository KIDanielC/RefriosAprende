"""Pantalla del Aprendiz: vista única de un curso, combinando la guía de aprendizaje (texto
pedagógico) con el contenido real y las acciones de practicar/presentar — un solo lugar en vez
de dos ventanas separadas ("Guía de aprendizaje" + "Ver contenido del curso"). Organizada según
la metodología: aprender -> practicar -> simular -> evaluar."""
import os
import subprocess
import sys

import customtkinter as ctk
from PIL import Image

from config.settings import (
    BASE_DIR,
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_ALTERNO_GLOW,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
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
from controller.contenido_controller import TIPO_IMAGEN, TIPO_PDF, ContenidoController
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.progreso_controller import ProgresoController
from controller.simulacion_controller import SimulacionController
from controller.validacion_controller import ValidacionController
from model.dao.resultado_dao import ResultadoDAO
from model.entities.contenido import Contenido
from model.entities.curso import Curso
from model.entities.usuario import Usuario
from utils.texto_enriquecido import texto_plano_desde_markup
from view.components.editor_texto_enriquecido import EditorTextoEnriquecido
from view.screens.presentar_evaluacion_screen import PresentarEvaluacionWindow
from view.screens.presentar_simulacion_screen import PresentarCasoWindow
from view.screens.responder_quiz_screen import ResponderQuizWindow


class CursoAprendizScreen(ctk.CTkFrame):
    """Vista de página completa del curso para el aprendiz: guía + contenido + acciones."""

    def __init__(self, master, curso: Curso, usuario_sesion: Usuario, al_volver):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._curso = curso
        self._usuario_sesion = usuario_sesion
        self._al_volver = al_volver

        self._contenido_controlador = ContenidoController()
        self._validacion_controlador = ValidacionController()
        self._evaluacion_controlador = EvaluacionController()
        self._simulacion_controlador = SimulacionController()
        self._progreso_controlador = ProgresoController()
        self._guia_controlador = GuiaAprendizajeController()
        self._resultado_dao = ResultadoDAO()

        self._imagenes_cargadas = []  # referencias vivas: evita que el GC libere las CTkImage en pantalla
        self._casillas_visto = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        guia = self._guia_controlador.obtener_guia(self._curso.id_curso)
        self._construir_encabezado()
        self._construir_resumen_guia(guia)

        pestanas = ctk.CTkTabview(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            segmented_button_selected_color=COLOR_ACENTO_PRIMARIO,
            segmented_button_selected_hover_color=COLOR_ACENTO_SECUNDARIO,
            segmented_button_unselected_color=COLOR_FONDO_APP,
            text_color=COLOR_TEXTO_PRIMARIO,
        )
        pestanas.grid(row=3, column=0, sticky="nsew", padx=24, pady=(4, 24))

        for nombre in ("Aprender", "Practicar", "Simular", "Evaluar"):
            pestanas.add(nombre)

        self._construir_pestana_aprender(pestanas.tab("Aprender"), guia)
        self._construir_pestana_practicar(pestanas.tab("Practicar"), guia)
        self._construir_pestana_simular(pestanas.tab("Simular"))
        self._construir_pestana_evaluar(pestanas.tab("Evaluar"), guia)

    def _construir_encabezado(self):
        ctk.CTkButton(
            self, text="←  Volver a mis cursos", fg_color="transparent", hover_color=COLOR_FONDO_TARJETA_HOVER,
            text_color=COLOR_ACENTO_SECUNDARIO, font=(FONT_FAMILY, 13, "bold"), width=170, height=32,
            command=self._al_volver,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 4))

        fila_titulo = ctk.CTkFrame(self, fg_color="transparent")
        fila_titulo.grid(row=1, column=0, sticky="ew", padx=24, pady=(4, 12))
        ctk.CTkLabel(
            fila_titulo, text=self._curso.nombre_curso, font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).pack(side="left")

        progreso = self._progreso_controlador.obtener_progreso(self._usuario_sesion.id_usuario, self._curso.id_curso)
        porcentaje = progreso.porcentaje_avance if progreso else 0.0
        ctk.CTkLabel(
            fila_titulo, text=f"· {porcentaje:.0f}% completado", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_ACENTO_PRIMARIO,
        ).pack(side="left", padx=(14, 0))
        info = f"Instructor: {self._curso.nombre_instructor or '—'}"
        if self._curso.nombre_categoria:
            info += f"  ·  {self._curso.nombre_categoria}"
        ctk.CTkLabel(
            fila_titulo, text=info, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left", padx=(14, 0))

    def _construir_resumen_guia(self, guia):
        """Objetivos, competencias y duración: lo primero que el aprendiz debe leer del curso,
        visible de una vez al entrar — sin abrir nada aparte ni cambiar de pestaña."""
        campos = (
            ("objetivo_general", "Objetivo general"),
            ("objetivos_especificos", "Objetivos específicos"),
            ("competencias", "Competencias a desarrollar"),
        )
        valores = [(etiqueta, texto_plano_desde_markup(getattr(guia, clave, "") or "").strip()) for clave, etiqueta in campos]
        valores = [(etiqueta, valor) for etiqueta, valor in valores if valor]
        duracion = guia.duracion_horas if guia and guia.duracion_horas else None

        if not valores and not duracion:
            return

        tarjeta = ctk.CTkFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        tarjeta.grid_columnconfigure(tuple(range(len(valores) + (1 if duracion else 0))), weight=1)

        columna = 0
        for etiqueta, valor in valores:
            bloque = ctk.CTkFrame(tarjeta, fg_color="transparent")
            bloque.grid(row=0, column=columna, sticky="new", padx=18, pady=14)
            ctk.CTkLabel(
                bloque, text=etiqueta.upper(), font=(FONT_FAMILY, 10, "bold"), text_color=COLOR_TEXTO_SECUNDARIO,
                anchor="w",
            ).pack(anchor="w", pady=(0, 4))
            ctk.CTkLabel(
                bloque, text=valor, font=(FONT_FAMILY, 12.5), text_color=COLOR_TEXTO_PRIMARIO,
                anchor="w", justify="left", wraplength=260,
            ).pack(anchor="w")
            columna += 1

        if duracion:
            bloque = ctk.CTkFrame(tarjeta, fg_color="transparent")
            bloque.grid(row=0, column=columna, sticky="new", padx=18, pady=14)
            ctk.CTkLabel(
                bloque, text="DURACIÓN", font=(FONT_FAMILY, 10, "bold"), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).pack(anchor="w", pady=(0, 4))
            ctk.CTkLabel(
                bloque, text=f"{duracion} horas", font=(FONT_FAMILY, 12.5), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
            ).pack(anchor="w")

    # -- Aprender: contexto + contenido real -----------------------------------------------
    def _construir_pestana_aprender(self, tab, guia):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        contenedor.grid_columnconfigure(0, weight=1)

        self._agregar_texto_opcional(contenedor, guia, "introduccion", "Introducción")
        self._agregar_texto_opcional(contenedor, guia, "conocimientos_previos", "Conocimientos previos")

        contenidos = self._contenido_controlador.listar_por_curso(self._curso.id_curso)
        if not contenidos:
            ctk.CTkLabel(
                contenedor, text="Este curso aún no tiene contenidos publicados.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=20)
        for contenido in contenidos:
            self._construir_tarjeta_contenido(contenedor, contenido)

        self._agregar_texto_opcional(contenedor, guia, "glosario", "Glosario")
        self._agregar_texto_opcional(contenedor, guia, "referencias", "Referencias")

    def _construir_tarjeta_contenido(self, contenedor, contenido: Contenido):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.pack(fill="x", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
        encabezado.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            encabezado, text=f"{contenido.orden}. {contenido.titulo}", font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        if self._progreso_controlador.contenido_bloqueado(self._usuario_sesion.id_usuario, contenido, self._curso):
            ctk.CTkLabel(
                tarjeta, text="🔒  Completa el contenido anterior para desbloquear este.",
                font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))
            return

        casilla_vista = ctk.CTkCheckBox(
            encabezado, text="Ya lo vi", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_SECUNDARIO,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, border_color=COLOR_BORDE_SUTIL,
            checkmark_color="#FFFFFF", width=20, height=20,
            command=lambda c=contenido: self._alternar_visto(c),
        )
        if self._progreso_controlador.ya_visto(self._usuario_sesion.id_usuario, contenido):
            casilla_vista.select()
        casilla_vista.grid(row=0, column=1, sticky="e")
        self._casillas_visto[contenido.id_contenido] = casilla_vista

        fila_siguiente = 1
        if texto_plano_desde_markup(contenido.contenido_texto or "").strip():
            EditorTextoEnriquecido(
                tarjeta, valor_inicial=contenido.contenido_texto, solo_lectura=True,
            ).grid(row=fila_siguiente, column=0, sticky="ew", padx=18, pady=(0, 12))
            fila_siguiente += 1

        if contenido.tipo_contenido == TIPO_IMAGEN:
            widget_imagen = self._construir_imagen(tarjeta, contenido)
            if widget_imagen is not None:
                widget_imagen.grid(row=fila_siguiente, column=0, sticky="w", padx=18, pady=(0, 12))
                fila_siguiente += 1

        if contenido.tipo_contenido == TIPO_PDF:
            ctk.CTkButton(
                tarjeta, text="📄  Abrir PDF", height=34, corner_radius=RADIO_BOTON,
                fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
                text_color="#FFFFFF", font=(FONT_FAMILY, 12, "bold"),
                command=lambda c=contenido: self._abrir_pdf(c),
            ).grid(row=fila_siguiente, column=0, sticky="w", padx=18, pady=(0, 12))
            fila_siguiente += 1

        total_preguntas = len(self._validacion_controlador.listar_preguntas(contenido))
        if total_preguntas > 0:
            ctk.CTkButton(
                tarjeta, text=f"Responder preguntas de validación ({total_preguntas})", height=34, corner_radius=RADIO_BOTON,
                fg_color=COLOR_FONDO_TARJETA_HOVER, border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_ALTERNO,
                text_color=COLOR_ACENTO_ALTERNO, font=(FONT_FAMILY, 12, "bold"),
                command=lambda c=contenido: ResponderQuizWindow(self, contenido=c),
            ).grid(row=fila_siguiente, column=0, sticky="w", padx=18, pady=(0, 14))

    def _alternar_visto(self, contenido: Contenido):
        casilla = self._casillas_visto[contenido.id_contenido]
        if casilla.get():
            self._progreso_controlador.registrar_contenido_visto(self._usuario_sesion.id_usuario, contenido)
        else:
            self._progreso_controlador.desregistrar_contenido_visto(self._usuario_sesion.id_usuario, contenido)

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

    # -- Practicar: contexto pedagógico -----------------------------------------------------
    def _construir_pestana_practicar(self, tab, guia):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        contenedor.grid_columnconfigure(0, weight=1)

        claves = (
            ("procedimiento_paso_a_paso", "Procedimiento paso a paso"),
            ("normas_seguridad", "Normas de seguridad"),
            ("ejemplos_practicos", "Ejemplos prácticos"),
            ("actividades_interactivas", "Actividades interactivas"),
        )
        hay_contenido = False
        for clave, etiqueta in claves:
            if self._agregar_texto_opcional(contenedor, guia, clave, etiqueta):
                hay_contenido = True
        if not hay_contenido:
            ctk.CTkLabel(
                contenedor, text="El instructor todavía no ha publicado esta sección.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=20)

    # -- Simular: casos reales con acción de practicar ---------------------------------------
    def _construir_pestana_simular(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        contenedor.grid_columnconfigure(0, weight=1)

        casos = self._simulacion_controlador.listar_casos_por_curso(self._curso.id_curso)
        if not casos:
            ctk.CTkLabel(
                contenedor, text="Este curso todavía no tiene casos de simulación.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=20)
            return

        for evaluacion, simulacion in casos:
            tarjeta = ctk.CTkFrame(
                contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
                border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.pack(fill="x", pady=8)
            ctk.CTkLabel(
                tarjeta, text=simulacion.titulo_caso, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
                anchor="w",
            ).pack(anchor="w", padx=18, pady=(14, 4))
            ctk.CTkLabel(
                tarjeta, text=simulacion.descripcion_escenario, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
                anchor="w", justify="left", wraplength=700,
            ).pack(anchor="w", padx=18, pady=(0, 10))
            ctk.CTkButton(
                tarjeta, text="Practicar este caso", height=34, corner_radius=RADIO_BOTON,
                fg_color=COLOR_ACENTO_ALTERNO, hover_color=COLOR_ACENTO_ALTERNO_GLOW, text_color="#FFFFFF",
                font=(FONT_FAMILY, 12, "bold"),
                command=lambda e=evaluacion, s=simulacion: PresentarCasoWindow(
                    self, evaluacion=e, simulacion=s, usuario_sesion=self._usuario_sesion
                ),
            ).pack(anchor="w", padx=18, pady=(0, 14))

    # -- Evaluar: evaluación final real con acción de presentar ------------------------------
    def _construir_pestana_evaluar(self, tab, guia):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        contenedor.grid_columnconfigure(0, weight=1)

        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(self._curso.id_curso)
        if evaluacion_final is None:
            ctk.CTkLabel(
                contenedor, text="Este curso todavía no tiene evaluación final.",
                font=(FONT_FAMILY, 14), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=20)
            return

        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.pack(fill="x", pady=8)
        ctk.CTkLabel(
            tarjeta, text=evaluacion_final.titulo, font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
            anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        intentos_usados = self._evaluacion_controlador.intentos_usados(self._usuario_sesion.id_usuario, evaluacion_final.id_evaluacion)
        aprobado = self._resultado_dao.existe_aprobado(self._usuario_sesion.id_usuario, evaluacion_final.id_evaluacion)
        color_estado = COLOR_EXITO if aprobado else COLOR_TEXTO_SECUNDARIO
        texto_estado = "✓ Aprobada" if aprobado else f"Intentos usados: {intentos_usados} / {evaluacion_final.intentos_permitidos}"
        ctk.CTkLabel(
            tarjeta, text=f"Nota mínima: {evaluacion_final.nota_minima_aprobar:.1f} / 5.0  ·  {texto_estado}",
            font=(FONT_FAMILY, 12), text_color=color_estado, anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        agotados = intentos_usados >= evaluacion_final.intentos_permitidos
        boton = ctk.CTkButton(
            tarjeta, text="Presentar evaluación", height=34, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO, text_color="#FFFFFF",
            font=(FONT_FAMILY, 12, "bold"),
            command=lambda e=evaluacion_final: PresentarEvaluacionWindow(self, evaluacion=e, usuario_sesion=self._usuario_sesion),
        )
        boton.pack(anchor="w", padx=18, pady=(0, 14))
        if aprobado or agotados:
            boton.configure(state="disabled")

        self._agregar_texto_opcional(contenedor, guia, "criterios_evaluacion", "Criterios de aprobación")

    # -- Helper: sección de texto de la guía, se omite por completo si está vacía -----------
    def _agregar_texto_opcional(self, contenedor, guia, clave: str, etiqueta: str) -> bool:
        valor = (getattr(guia, clave, "") if guia else "") or ""
        if not texto_plano_desde_markup(valor).strip():
            return False

        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        fila.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(
            fila, text=etiqueta, font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(0, 6))
        tarjeta = ctk.CTkFrame(
            fila, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.pack(fill="x")
        EditorTextoEnriquecido(tarjeta, valor_inicial=valor, solo_lectura=True).pack(fill="x", padx=12, pady=8)
        return True
