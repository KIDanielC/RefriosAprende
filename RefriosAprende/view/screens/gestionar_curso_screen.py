"""Ventana única de gestión de un curso (administrador): un solo punto de entrada
("Gestionar curso") en vez de botones sueltos para Estudiantes / Guía / Contenidos /
Evaluación / Simulaciones. Organizada según la metodología de la empresa: aprender ->
practicar -> simular -> evaluar.

Cuatro secciones (Contenido teórico, Recursos visuales, Simulación básica, Evaluación) no se
escriben como texto libre: se calculan en vivo desde los controladores reales, y cada una trae
su propio botón para crear/editar ese dato real — el instructor no tiene que salir de esta
ventana para armar el curso completo.

El aprendiz consulta esta misma información, ya combinada con el contenido real y las acciones
de practicar/presentar, en `view.screens.curso_aprendiz_screen.CursoAprendizScreen`."""
import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
)
from controller.contenido_controller import TIPO_IMAGEN, TIPO_PDF, TIPO_TEXTO, ContenidoController
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import DatosGuiaInvalidosError, GuiaAprendizajeController
from controller.simulacion_controller import SimulacionController
from model.entities.curso import Curso
from view.screens.contenidos_screen import ContenidosScreen
from view.screens.evaluacion_final_screen import EvaluacionFinalWindow
from view.screens.matricula_screen import MatriculaWindow
from view.screens.simulaciones_screen import SimulacionesWindow

_CAMPOS_ENCABEZADO = (
    ("objetivo_general", "Objetivo general"),
    ("objetivos_especificos", "Objetivos específicos"),
    ("competencias", "Competencias a desarrollar"),
)


class GestionarCursoWindow(ctk.CTkToplevel):
    """Punto de entrada único del administrador a todo lo pedagógico de un curso."""

    def __init__(self, master, curso: Curso):
        super().__init__(master)
        self._curso = curso
        self._controlador = GuiaAprendizajeController()
        self._contenido_controlador = ContenidoController()
        self._simulacion_controlador = SimulacionController()
        self._evaluacion_controlador = EvaluacionController()
        self._cajas_texto = {}

        self.title(f"Gestionar curso — {curso.nombre_curso}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("920x740")
        self.minsize(780, 580)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        guia = self._controlador.obtener_guia(self._curso.id_curso)
        self._construir_encabezado(guia)

        pestanas = ctk.CTkTabview(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            segmented_button_selected_color=COLOR_ACENTO_PRIMARIO,
            segmented_button_selected_hover_color=COLOR_ACENTO_SECUNDARIO,
            segmented_button_unselected_color=COLOR_FONDO_APP,
            text_color=COLOR_TEXTO_PRIMARIO,
        )
        pestanas.grid(row=1, column=0, sticky="nsew", padx=24, pady=(4, 4))

        for nombre in ("Aprender", "Practicar", "Simular", "Evaluar"):
            pestanas.add(nombre)

        self._construir_pestana_aprender(pestanas.tab("Aprender"), guia)
        self._construir_pestana_practicar(pestanas.tab("Practicar"), guia)
        self._construir_pestana_simular(pestanas.tab("Simular"))
        self._construir_pestana_evaluar(pestanas.tab("Evaluar"), guia)

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=2, column=0, sticky="ew", padx=24, pady=(4, 18))
        pie.grid_columnconfigure(0, weight=1)

        self._etiqueta_estado = ctk.CTkLabel(pie, text="", font=(FONT_FAMILY, 12, "bold"))
        self._etiqueta_estado.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pie, text="Guardar guía", width=160, height=42, corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO, hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF", font=(FONT_FAMILY, 14, "bold"), command=self._guardar,
        ).grid(row=0, column=1, sticky="e")

    # -- Encabezado fijo: info del curso + lo transversal a toda la metodología ------------
    def _construir_encabezado(self, guia):
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 6))
        encabezado.grid_columnconfigure(0, weight=1)

        fila_titulo = ctk.CTkFrame(encabezado, fg_color="transparent")
        fila_titulo.grid(row=0, column=0, sticky="ew")
        fila_titulo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            fila_titulo, text=self._curso.nombre_curso, font=(FONT_FAMILY, 18, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            fila_titulo, text="Estudiantes", height=32, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_PRIMARIO,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
            command=lambda: MatriculaWindow(self, curso=self._curso),
        ).grid(row=0, column=1, sticky="e")

        info = f"Instructor: {self._curso.nombre_instructor or '—'}  ·  Categoría: {self._curso.nombre_categoria or 'Sin categoría'}"
        ctk.CTkLabel(
            encabezado, text=info, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        cuerpo = ctk.CTkScrollableFrame(encabezado, fg_color="transparent", height=120)
        cuerpo.grid(row=2, column=0, sticky="ew")
        cuerpo.grid_columnconfigure((0, 1, 2), weight=1)

        for indice, (clave, etiqueta) in enumerate(_CAMPOS_ENCABEZADO):
            columna = ctk.CTkFrame(cuerpo, fg_color="transparent")
            columna.grid(row=0, column=indice, sticky="new", padx=(0 if indice == 0 else 10, 0))
            valor = getattr(guia, clave, "") if guia else ""
            self._cajas_texto[clave] = self._construir_seccion(columna, etiqueta, valor or "", alto=70)

        self._campo_duracion = self._construir_campo_duracion(encabezado, guia)
        self._campo_duracion.master.grid(row=3, column=0, sticky="w", pady=(6, 0))

    def _construir_campo_duracion(self, contenedor, guia):
        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        ctk.CTkLabel(
            fila, text="Duración estimada (horas)", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(0, 6))
        campo = ctk.CTkEntry(
            fila, width=140, height=38, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13),
        )
        campo.pack(anchor="w")
        if guia and guia.duracion_horas:
            campo.insert(0, str(guia.duracion_horas))
        return campo

    # -- Pestañas de la metodología -----------------------------------------------------
    def _construir_pestana_aprender(self, tab, guia):
        tab.grid_columnconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        tab.grid_rowconfigure(0, weight=1)

        self._agregar_campo(contenedor, guia, "introduccion", "Introducción")
        self._agregar_campo(contenedor, guia, "conocimientos_previos", "Conocimientos previos")

        contenidos = self._contenido_controlador.listar_por_curso(self._curso.id_curso)
        teoricos = [f"{c.orden}. {c.titulo}" for c in contenidos if c.tipo_contenido == TIPO_TEXTO]
        visuales = [f"{c.orden}. {c.titulo} ({c.tipo_contenido})" for c in contenidos if c.tipo_contenido in (TIPO_IMAGEN, TIPO_PDF)]
        self._construir_seccion_computada(
            contenedor, "Contenido teórico y recursos visuales", teoricos + visuales,
            texto_boton="Gestionar contenidos",
            comando_boton=self._abrir_contenidos,
        )

        self._agregar_campo(contenedor, guia, "glosario", "Glosario")
        self._agregar_campo(contenedor, guia, "referencias", "Referencias")

    def _construir_pestana_practicar(self, tab, guia):
        tab.grid_columnconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        tab.grid_rowconfigure(0, weight=1)

        self._agregar_campo(contenedor, guia, "procedimiento_paso_a_paso", "Procedimiento paso a paso")
        self._agregar_campo(contenedor, guia, "normas_seguridad", "Normas de seguridad")
        self._agregar_campo(contenedor, guia, "ejemplos_practicos", "Ejemplos prácticos")
        self._agregar_campo(contenedor, guia, "actividades_interactivas", "Actividades interactivas")

    def _construir_pestana_simular(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        tab.grid_rowconfigure(0, weight=1)

        casos = self._simulacion_controlador.listar_casos_por_curso(self._curso.id_curso)
        lineas = [simulacion.titulo_caso for _evaluacion, simulacion in casos]
        self._construir_seccion_computada(
            contenedor, "Casos de simulación básica", lineas,
            texto_boton="Gestionar simulaciones",
            comando_boton=self._abrir_simulaciones,
        )

    def _construir_pestana_evaluar(self, tab, guia):
        tab.grid_columnconfigure(0, weight=1)
        contenedor = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        tab.grid_rowconfigure(0, weight=1)

        evaluacion_final = self._evaluacion_controlador.obtener_evaluacion_final(self._curso.id_curso)
        lineas = []
        if evaluacion_final is not None:
            lineas = [
                evaluacion_final.titulo,
                f"Nota mínima para aprobar: {evaluacion_final.nota_minima_aprobar:.1f} / 5.0",
                f"Intentos permitidos: {evaluacion_final.intentos_permitidos}",
            ]
        self._construir_seccion_computada(
            contenedor, "Evaluación final", lineas,
            texto_boton="Gestionar evaluación final",
            comando_boton=self._abrir_evaluacion_final,
        )
        self._agregar_campo(contenedor, guia, "criterios_evaluacion", "Criterios de aprobación")

    # -- Helpers compartidos ---------------------------------------------------------------
    def _abrir_contenidos(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title(f"Contenidos — {self._curso.nombre_curso}")
        ventana.configure(fg_color=COLOR_FONDO_APP)
        ventana.geometry("820x640")
        ventana.minsize(680, 480)
        ventana.transient(self)
        ventana.grab_set()
        ventana.grid_columnconfigure(0, weight=1)
        ventana.grid_rowconfigure(0, weight=1)
        ContenidosScreen(ventana, curso=self._curso, al_volver=ventana.destroy).grid(row=0, column=0, sticky="nsew")

    def _abrir_simulaciones(self):
        SimulacionesWindow(self, curso=self._curso)

    def _abrir_evaluacion_final(self):
        EvaluacionFinalWindow(self, curso=self._curso)

    def _agregar_campo(self, contenedor, guia, clave: str, etiqueta: str):
        valor = getattr(guia, clave, "") if guia else ""
        self._cajas_texto[clave] = self._construir_seccion(contenedor, etiqueta, valor or "")

    def _construir_seccion(self, contenedor, etiqueta: str, valor: str, alto: int = 80) -> ctk.CTkTextbox:
        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        fila.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(
            fila, text=etiqueta, font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        caja = ctk.CTkTextbox(
            fila, height=alto, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 13), wrap="word",
        )
        caja.pack(fill="x")
        if valor:
            caja.insert("1.0", valor)
        return caja

    def _construir_seccion_computada(self, contenedor, etiqueta: str, lineas: list, texto_boton: str = None, comando_boton=None):
        """Tarjeta de solo lectura con datos reales (contenidos/simulaciones/evaluación), con
        un botón que abre la herramienta real donde se crean/editan — sin salir de esta ventana."""
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

        if lineas:
            for linea in lineas:
                ctk.CTkLabel(
                    tarjeta, text=f"•  {linea}", font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_PRIMARIO,
                    anchor="w", justify="left", wraplength=520,
                ).pack(anchor="w", padx=16, pady=(10, 0))
        else:
            ctk.CTkLabel(
                tarjeta, text="Sin definir todavía.", font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
                anchor="w",
            ).pack(anchor="w", padx=16, pady=(10, 0))

        if texto_boton and comando_boton:
            ctk.CTkButton(
                tarjeta, text=texto_boton, height=32, corner_radius=RADIO_BOTON,
                fg_color="transparent", hover_color=COLOR_FONDO_APP,
                border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ACENTO_ALTERNO,
                text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, 12, "bold"),
                command=comando_boton,
            ).pack(anchor="w", padx=16, pady=(10, 14))
        else:
            ctk.CTkFrame(tarjeta, fg_color="transparent", height=6).pack()

    # ------------------------------------------------------------------
    def _guardar(self):
        valores = {clave: caja.get("1.0", "end").strip() for clave, caja in self._cajas_texto.items()}
        duracion = self._campo_duracion.get()

        try:
            self._controlador.guardar_guia(self._curso.id_curso, valores, duracion)
        except DatosGuiaInvalidosError as error:
            self._etiqueta_estado.configure(text=str(error), text_color=COLOR_ERROR)
            return

        self._etiqueta_estado.configure(text="✓ Guía guardada correctamente", text_color=COLOR_EXITO)
