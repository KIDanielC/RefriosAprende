"""Pantalla de Reportes (Administrador): resumen general y detalle por curso."""
from tkinter import ttk

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config.settings import (
    COLOR_ACENTO_PRIMARIO,
    COLOR_BORDE_SUTIL,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_TARJETA,
)
from controller.reporte_controller import ReporteController


class ReportesScreen(ctk.CTkFrame):
    """Resumen general de indicadores y detalle de desempeño por curso."""

    def __init__(self, master, usuario_sesion):
        super().__init__(master, fg_color=COLOR_FONDO_APP, corner_radius=0)
        self._controlador = ReporteController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        contenedor.grid_columnconfigure(0, weight=1)

        self._construir_resumen(contenedor)
        self._construir_grafica_progreso(contenedor)
        self._construir_detalle_cursos(contenedor)

    def _construir_resumen(self, contenedor):
        resumen = self._controlador.resumen_general()

        area_tarjetas = ctk.CTkFrame(contenedor, fg_color="transparent")
        area_tarjetas.pack(fill="x", pady=(0, 20))
        for indice in range(4):
            area_tarjetas.grid_columnconfigure(indice, weight=1)

        tarjetas = (
            ("📚", "Cursos activos", str(resumen["total_cursos_activos"])),
            ("👥", "Aprendices registrados", str(resumen["total_aprendices"])),
            ("📝", "Evaluaciones presentadas", str(resumen["total_evaluaciones_presentadas"])),
            ("✅", "% de aprobación", f"{resumen['porcentaje_aprobacion']:.0f}%"),
        )
        for indice, (icono, titulo, valor) in enumerate(tarjetas):
            tarjeta = ctk.CTkFrame(
                area_tarjetas, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA, height=110,
                border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
            )
            tarjeta.grid(row=0, column=indice, padx=6, sticky="ew")
            tarjeta.grid_propagate(False)
            insignia = ctk.CTkFrame(tarjeta, fg_color=COLOR_FONDO_TARJETA_HOVER, corner_radius=9, width=32, height=32)
            insignia.pack(anchor="w", padx=18, pady=(16, 0))
            insignia.pack_propagate(False)
            ctk.CTkLabel(insignia, text=icono, font=(FONT_FAMILY, 14)).pack(expand=True)
            ctk.CTkLabel(
                tarjeta, text=titulo, font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="w",
            ).pack(anchor="w", padx=18, pady=(10, 2), fill="x")
            ctk.CTkLabel(
                tarjeta, text=valor, font=(FONT_FAMILY, 22, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
            ).pack(anchor="w", padx=18)

        ctk.CTkLabel(
            contenedor,
            text=f"Progreso promedio general: {resumen['progreso_promedio_general']:.0f}%",
            font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_EXITO, anchor="w",
        ).pack(anchor="w", pady=(0, 4))

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
            foreground=[("selected", COLOR_TEXTO_PRIMARIO)],
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
