"""Pantalla de Reportes (Administrador): resumen general y detalle por curso."""
from tkinter import ttk

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch

from config.settings import (
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    RADIO_TARJETA,
    GROSOR_BORDE_SUTIL,
    COLOR_BORDE_SUTIL,
    COLOR_FONDO_TARJETA_HOVER,
    FONT_FAMILY,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_TEXTO_PRIMARIO,
    COLOR_EXITO,
    COLOR_ERROR,
    COLOR_ACENTO_PRIMARIO,
    COLOR_FONDO_PANEL,
    RADIO_BOTON,
)
from controller.reporte_controller import (
    SEMAFORO_AMARILLO,
    SEMAFORO_ROJO,
    SEMAFORO_VERDE,
    ReporteController,
)

_COLOR_SEMAFORO = {SEMAFORO_VERDE: COLOR_EXITO, SEMAFORO_AMARILLO: "#B8860B", SEMAFORO_ROJO: COLOR_ERROR}
_ETIQUETA_SEMAFORO = {SEMAFORO_VERDE: "Al día", SEMAFORO_AMARILLO: "Atención", SEMAFORO_ROJO: "Crítico"}
_ORDEN_SEMAFORO = {SEMAFORO_ROJO: 0, SEMAFORO_AMARILLO: 1, SEMAFORO_VERDE: 2}


class ReportesScreen(ctk.CTkFrame):
    """Reportes ordenados por importancia: primero lo crítico (aprendices en riesgo) y el
    semáforo de seguimiento, después los indicadores y tablas generales. Todo en números,
    gráficas y tablas; sin párrafos explicativos."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._usuario_sesion = usuario_sesion
        self._controlador = ReporteController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        contenedor.grid_columnconfigure(0, weight=1)

        self._construir_aprendices_criticos(contenedor)
        self._construir_grafica_semaforo(contenedor)
        self._construir_resumen(contenedor)
        self._construir_grafica_progreso(contenedor)
        self._construir_detalle_cursos(contenedor)
        self._construir_avance_por_estudiante(contenedor)

    # -- Utilidad: hace clickeable cualquier widget (y sus hijos), con cursor de mano --------
    def _hacer_clickeable(self, widget, comando):
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass
        widget.bind("<Button-1>", lambda evento: comando())
        for hijo in widget.winfo_children():
            self._hacer_clickeable(hijo, comando)

    def _abrir_detalle_seguimiento(self):
        filas = self._controlador.avance_por_estudiante(self._usuario_sesion.id_usuario)
        DetalleSeguimientoWindow(self, filas=filas)

    # -- 1. Lo más importante: aprendices críticos, como KPI + gráfica ----------------------
    def _construir_aprendices_criticos(self, contenedor):
        en_riesgo = self._controlador.estudiantes_en_riesgo(self._usuario_sesion.id_usuario)

        tarjeta_kpi = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA, height=100,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ERROR if en_riesgo else COLOR_BORDE_SUTIL,
        )
        tarjeta_kpi.pack(fill="x", pady=(0, 4))
        tarjeta_kpi.pack_propagate(False)
        fila_kpi = ctk.CTkFrame(tarjeta_kpi, fg_color="transparent")
        fila_kpi.pack(expand=True, fill="x", anchor="w", padx=20)
        ctk.CTkLabel(
            fila_kpi, text=str(len(en_riesgo)), font=(FONT_FAMILY, 40, "bold"),
            text_color=COLOR_ERROR if en_riesgo else COLOR_EXITO,
        ).pack(side="left")
        ctk.CTkLabel(
            fila_kpi, text="🔴  Aprendices críticos", font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left", padx=(16, 0))
        ctk.CTkLabel(
            fila_kpi, text="Ver todos ›", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_ACENTO_PRIMARIO,
        ).pack(side="right")
        self._hacer_clickeable(tarjeta_kpi, self._abrir_detalle_seguimiento)

        if not en_riesgo:
            return

        panel = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_ERROR,
        )
        panel.pack(fill="x", pady=(12, 20))

        etiquetas = [f"{f['nombre_estudiante']} — {f['nombre_curso']}" for f in en_riesgo]
        valores = [f["porcentaje_avance"] for f in en_riesgo]
        dias = [f["dias_matriculado"] for f in en_riesgo]

        alto = max(1.6, 0.5 * len(etiquetas) + 0.5)
        figura = Figure(figsize=(7.2, alto), dpi=100, facecolor=COLOR_FONDO_TARJETA)
        eje = figura.add_subplot(111)
        eje.set_facecolor(COLOR_FONDO_TARJETA)

        posiciones = range(len(etiquetas))
        barras = eje.barh(list(posiciones), valores, color=COLOR_ERROR, height=0.55, zorder=3)
        eje.bar_label(
            barras, labels=[f"{v:.0f}%  ·  {d} d" for v, d in zip(valores, dias)],
            padding=6, color=COLOR_TEXTO_PRIMARIO, fontsize=9,
        )

        eje.set_yticks(list(posiciones))
        eje.set_yticklabels(etiquetas, color=COLOR_TEXTO_SECUNDARIO, fontsize=8.5)
        eje.invert_yaxis()
        eje.set_xlim(0, 110)
        eje.tick_params(axis="x", colors=COLOR_TEXTO_SECUNDARIO, labelsize=8)
        eje.tick_params(axis="y", length=0)
        for lado in ("top", "right", "left"):
            eje.spines[lado].set_visible(False)
        eje.spines["bottom"].set_color(COLOR_BORDE_SUTIL)
        eje.grid(axis="x", color=COLOR_BORDE_SUTIL, linewidth=0.6, alpha=0.6, zorder=0)

        figura.tight_layout()
        lienzo = FigureCanvasTkAgg(figura, master=panel)
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="x", padx=14, pady=14)

    def _construir_resumen(self, contenedor):
        resumen = self._controlador.resumen_general()

        area_tarjetas = ctk.CTkFrame(contenedor, fg_color="transparent")
        area_tarjetas.pack(fill="x", pady=(0, 20))
        for indice in range(5):
            area_tarjetas.grid_columnconfigure(indice, weight=1)

        tarjetas = (
            ("📚", "Cursos activos", str(resumen["total_cursos_activos"])),
            ("👥", "Aprendices registrados", str(resumen["total_aprendices"])),
            ("📝", "Evaluaciones presentadas", str(resumen["total_evaluaciones_presentadas"])),
            ("✅", "% de aprobación", f"{resumen['porcentaje_aprobacion']:.0f}%"),
            ("📈", "Progreso promedio", f"{resumen['progreso_promedio_general']:.0f}%"),
        )
        for indice, (icono, titulo, valor) in enumerate(tarjetas):
            tarjeta = ctk.CTkFrame(
                area_tarjetas, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA, height=110,
                border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.grid(row=0, column=indice, padx=6, sticky="ew")
            tarjeta.grid_propagate(False)
            insignia = ctk.CTkFrame(tarjeta, fg_color=COLOR_FONDO_TARJETA_HOVER, corner_radius=RADIO_BOTON, width=32, height=32)
            insignia.pack(anchor="w", padx=18, pady=(16, 0))
            insignia.pack_propagate(False)
            ctk.CTkLabel(insignia, text=icono, font=(FONT_FAMILY, 14)).pack(expand=True)
            ctk.CTkLabel(
                tarjeta, text=titulo, font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).pack(anchor="w", padx=18, pady=(10, 2), fill="x")
            ctk.CTkLabel(
                tarjeta, text=valor, font=(FONT_FAMILY, 22, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
            ).pack(anchor="w", padx=18)

    def _construir_grafica_progreso(self, contenedor):
        filas = self._controlador.detalle_por_curso()
        if not filas:
            return

        panel = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        panel.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            panel, text="Progreso promedio por curso", font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        nombres = [fila["nombre_curso"] for fila in filas]
        valores = [fila["progreso_promedio"] for fila in filas]
        colores = [COLOR_EXITO if v >= 100 else COLOR_ACENTO_PRIMARIO for v in valores]

        alto = max(2.0, 0.55 * len(nombres) + 0.6)
        figura = Figure(figsize=(7.2, alto), dpi=100, facecolor=COLOR_FONDO_TARJETA)
        eje = figura.add_subplot(111)
        eje.set_facecolor(COLOR_FONDO_TARJETA)

        posiciones = range(len(nombres))
        barras = eje.barh(list(posiciones), valores, color=colores, height=0.55, zorder=3)
        eje.bar_label(barras, labels=[f"{v:.0f}%" for v in valores], padding=6, color=COLOR_TEXTO_PRIMARIO, fontsize=9)

        eje.set_yticks(list(posiciones))
        eje.set_yticklabels(nombres, color=COLOR_TEXTO_SECUNDARIO, fontsize=9)
        eje.invert_yaxis()
        eje.set_xlim(0, 110)
        eje.tick_params(axis="x", colors=COLOR_TEXTO_SECUNDARIO, labelsize=8)
        eje.tick_params(axis="y", length=0)
        for lado in ("top", "right", "left"):
            eje.spines[lado].set_visible(False)
        eje.spines["bottom"].set_color(COLOR_BORDE_SUTIL)
        eje.grid(axis="x", color=COLOR_BORDE_SUTIL, linewidth=0.6, alpha=0.6, zorder=0)

        figura.tight_layout()
        lienzo = FigureCanvasTkAgg(figura, master=panel)
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="x", padx=14, pady=(0, 16))

    def _construir_detalle_cursos(self, contenedor):
        ctk.CTkLabel(
            contenedor, text="Detalle por curso", font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", pady=(10, 10))

        marco = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        marco.pack(fill="both", expand=True)
        marco.grid_columnconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Reportes.Treeview", background=COLOR_FONDO_TARJETA, fieldbackground=COLOR_FONDO_TARJETA,
            foreground=COLOR_TEXTO_PRIMARIO, rowheight=34, borderwidth=0, font=(FONT_FAMILY, 12),
        )
        estilo.configure(
            "Reportes.Treeview.Heading", background=COLOR_FONDO_PANEL, foreground=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), borderwidth=0, relief="flat",
        )
        estilo.map(
            "Reportes.Treeview", background=[("selected", COLOR_ACENTO_PRIMARIO)],
            foreground=[("selected", "#FFFFFF")],
        )

        columnas = ("curso", "inscritos", "progreso", "evaluaciones", "aprobacion")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", style="Reportes.Treeview", height=10)
        titulos = {
            "curso": "Curso", "inscritos": "Aprendices inscritos", "progreso": "Progreso promedio",
            "evaluaciones": "Evaluaciones presentadas", "aprobacion": "% Aprobación",
        }
        anchos = {"curso": 260, "inscritos": 150, "progreso": 140, "evaluaciones": 170, "aprobacion": 120}
        for columna in columnas:
            tabla.heading(columna, text=titulos[columna])
            tabla.column(columna, width=anchos[columna], anchor="w")
        tabla.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        filas = self._controlador.detalle_por_curso()
        for fila in filas:
            aprobacion = "—" if fila["porcentaje_aprobacion"] is None else f"{fila['porcentaje_aprobacion']:.0f}%"
            tabla.insert(
                "", "end",
                values=(
                    fila["nombre_curso"], fila["aprendices_inscritos"], f"{fila['progreso_promedio']:.0f}%",
                    fila["evaluaciones_presentadas"], aprobacion,
                ),
            )

        if not filas:
            ctk.CTkLabel(
                contenedor, text="Todavía no hay cursos activos para reportar.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=16)

    # -- 2. Gráfica semafórica de seguimiento (todos los estudiantes de este instructor) -----
    def _construir_grafica_semaforo(self, contenedor):
        filas = self._controlador.avance_por_estudiante(self._usuario_sesion.id_usuario)
        if not filas:
            return

        panel = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        panel.pack(fill="x", pady=(0, 20))

        etiquetas = [f"{f['nombre_estudiante']} — {f['nombre_curso']}" for f in filas]
        valores = [f["porcentaje_avance"] for f in filas]
        colores = [_COLOR_SEMAFORO[f["semaforo"]] for f in filas]

        alto = max(2.0, 0.5 * len(etiquetas) + 0.6)
        figura = Figure(figsize=(7.2, alto), dpi=100, facecolor=COLOR_FONDO_TARJETA)
        eje = figura.add_subplot(111)
        eje.set_facecolor(COLOR_FONDO_TARJETA)

        posiciones = range(len(etiquetas))
        barras = eje.barh(list(posiciones), valores, color=colores, height=0.55, zorder=3)
        eje.bar_label(barras, labels=[f"{v:.0f}%" for v in valores], padding=6, color=COLOR_TEXTO_PRIMARIO, fontsize=9)

        eje.set_yticks(list(posiciones))
        eje.set_yticklabels(etiquetas, color=COLOR_TEXTO_SECUNDARIO, fontsize=8.5)
        eje.invert_yaxis()
        eje.set_xlim(0, 110)
        eje.tick_params(axis="x", colors=COLOR_TEXTO_SECUNDARIO, labelsize=8)
        eje.tick_params(axis="y", length=0)
        for lado in ("top", "right", "left"):
            eje.spines[lado].set_visible(False)
        eje.spines["bottom"].set_color(COLOR_BORDE_SUTIL)
        eje.grid(axis="x", color=COLOR_BORDE_SUTIL, linewidth=0.6, alpha=0.6, zorder=0)

        parches = [Patch(facecolor=_COLOR_SEMAFORO[clave], label=_ETIQUETA_SEMAFORO[clave]) for clave in (SEMAFORO_VERDE, SEMAFORO_AMARILLO, SEMAFORO_ROJO)]
        leyenda = eje.legend(
            handles=parches, loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=False,
            fontsize=8.5, handlelength=1.0, handleheight=1.0, columnspacing=1.2,
        )
        for texto in leyenda.get_texts():
            texto.set_color(COLOR_TEXTO_SECUNDARIO)

        figura.tight_layout()
        lienzo = FigureCanvasTkAgg(figura, master=panel)
        lienzo.draw()
        widget_lienzo = lienzo.get_tk_widget()
        widget_lienzo.pack(fill="x", padx=14, pady=(20, 16))
        self._hacer_clickeable(widget_lienzo, self._abrir_detalle_seguimiento)

    # -- Avance por estudiante: % de avance y horas reales vs. duración estimada ------------
    def _construir_avance_por_estudiante(self, contenedor):
        ctk.CTkLabel(
            contenedor, text="Avance por estudiante", font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).pack(anchor="w", pady=(10, 10))

        marco = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        marco.pack(fill="both", expand=True)
        marco.grid_columnconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "ReportesEstudiantes.Treeview", background=COLOR_FONDO_TARJETA, fieldbackground=COLOR_FONDO_TARJETA,
            foreground=COLOR_TEXTO_PRIMARIO, rowheight=34, borderwidth=0, font=(FONT_FAMILY, 12),
        )
        estilo.configure(
            "ReportesEstudiantes.Treeview.Heading", background=COLOR_FONDO_PANEL, foreground=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), borderwidth=0, relief="flat",
        )
        estilo.map(
            "ReportesEstudiantes.Treeview", background=[("selected", COLOR_ACENTO_PRIMARIO)],
            foreground=[("selected", "#FFFFFF")],
        )

        columnas = ("estudiante", "curso", "dias", "avance", "horas", "estado")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", style="ReportesEstudiantes.Treeview", height=10)
        titulos = {
            "estudiante": "Estudiante", "curso": "Curso", "dias": "Días matriculado",
            "avance": "% Avance", "horas": "Horas de uso vs. estimadas", "estado": "Seguimiento",
        }
        anchos = {"estudiante": 180, "curso": 220, "dias": 120, "avance": 90, "horas": 190, "estado": 110}
        for columna in columnas:
            tabla.heading(columna, text=titulos[columna])
            tabla.column(columna, width=anchos[columna], anchor="w")

        tabla.tag_configure(SEMAFORO_ROJO, foreground=COLOR_ERROR)
        tabla.tag_configure(SEMAFORO_AMARILLO, foreground="#B8860B")
        tabla.tag_configure(SEMAFORO_VERDE, foreground=COLOR_TEXTO_PRIMARIO)
        tabla.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        filas = self._controlador.avance_por_estudiante(self._usuario_sesion.id_usuario)
        for fila in filas:
            horas_texto = (
                f"{fila['horas_acumuladas']:.1f} / {fila['horas_esperadas']:.0f} h"
                if fila["horas_esperadas"] else f"{fila['horas_acumuladas']:.1f} h (sin estimar)"
            )
            tabla.insert(
                "", "end",
                values=(
                    fila["nombre_estudiante"], fila["nombre_curso"], fila["dias_matriculado"],
                    f"{fila['porcentaje_avance']:.0f}%", horas_texto, _ETIQUETA_SEMAFORO[fila["semaforo"]],
                ),
                tags=(fila["semaforo"],),
            )

        if not filas:
            ctk.CTkLabel(
                contenedor, text="Todavía no tienes estudiantes matriculados en tus cursos.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=16)


class DetalleSeguimientoWindow(ctk.CTkToplevel):
    """Quién está crítico y quién no, todos a la vista y ordenados de más a menos urgente
    (en vez de tener que confiar solo en el número agregado del KPI)."""

    def __init__(self, master, filas: list):
        super().__init__(master)
        self._filas = sorted(filas, key=lambda f: (_ORDEN_SEMAFORO[f["semaforo"]], f["nombre_estudiante"]))

        self.title("Seguimiento por estudiante")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("740x560")
        self.minsize(660, 420)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_contadores()
        self._construir_tabla()

    def _construir_contadores(self):
        conteo = {SEMAFORO_ROJO: 0, SEMAFORO_AMARILLO: 0, SEMAFORO_VERDE: 0}
        for fila in self._filas:
            conteo[fila["semaforo"]] += 1

        fila_contadores = ctk.CTkFrame(self, fg_color="transparent")
        fila_contadores.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        for clave in (SEMAFORO_ROJO, SEMAFORO_AMARILLO, SEMAFORO_VERDE):
            bloque = ctk.CTkFrame(
                fila_contadores, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
                border_width=GROSOR_BORDE_SUTIL, border_color=_COLOR_SEMAFORO[clave],
            )
            bloque.pack(side="left", expand=True, fill="x", padx=6)
            ctk.CTkLabel(
                bloque, text=str(conteo[clave]), font=(FONT_FAMILY, 26, "bold"), text_color=_COLOR_SEMAFORO[clave],
            ).pack(pady=(12, 0))
            ctk.CTkLabel(
                bloque, text=_ETIQUETA_SEMAFORO[clave], font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=(0, 12))

    def _construir_tabla(self):
        marco = ctk.CTkFrame(
            self, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        marco.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "DetalleSeguimiento.Treeview", background=COLOR_FONDO_TARJETA, fieldbackground=COLOR_FONDO_TARJETA,
            foreground=COLOR_TEXTO_PRIMARIO, rowheight=32, borderwidth=0, font=(FONT_FAMILY, 12),
        )
        estilo.configure(
            "DetalleSeguimiento.Treeview.Heading", background=COLOR_FONDO_PANEL, foreground=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 12, "bold"), borderwidth=0, relief="flat",
        )
        estilo.map(
            "DetalleSeguimiento.Treeview", background=[("selected", COLOR_ACENTO_PRIMARIO)],
            foreground=[("selected", "#FFFFFF")],
        )

        columnas = ("estudiante", "curso", "dias", "avance", "horas")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", style="DetalleSeguimiento.Treeview")
        titulos = {
            "estudiante": "Estudiante", "curso": "Curso", "dias": "Días",
            "avance": "% Avance", "horas": "Horas uso/estimadas",
        }
        anchos = {"estudiante": 170, "curso": 210, "dias": 70, "avance": 90, "horas": 160}
        for columna in columnas:
            tabla.heading(columna, text=titulos[columna])
            tabla.column(columna, width=anchos[columna], anchor="w")

        tabla.tag_configure(SEMAFORO_ROJO, foreground=COLOR_ERROR)
        tabla.tag_configure(SEMAFORO_AMARILLO, foreground="#B8860B")
        tabla.tag_configure(SEMAFORO_VERDE, foreground=COLOR_EXITO)
        tabla.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        for fila in self._filas:
            horas_texto = (
                f"{fila['horas_acumuladas']:.1f}/{fila['horas_esperadas']:.0f} h"
                if fila["horas_esperadas"] else f"{fila['horas_acumuladas']:.1f} h"
            )
            tabla.insert(
                "", "end",
                values=(
                    fila["nombre_estudiante"], fila["nombre_curso"], fila["dias_matriculado"],
                    f"{fila['porcentaje_avance']:.0f}%", horas_texto,
                ),
                tags=(fila["semaforo"],),
            )

        if not self._filas:
            ctk.CTkLabel(
                marco, text="Sin estudiantes matriculados todavía.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
