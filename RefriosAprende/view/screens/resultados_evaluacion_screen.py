"""Ventana modal: notas e intentos de los aprendices en una evaluación final o un caso de
simulación (Administrador). Reutilizable para ambas, ya que las dos guardan sus intentos en
la misma tabla `resultados` (ver `EvaluacionController`/`SimulacionController`.
`listar_resultados_detalle`)."""
import customtkinter as ctk

from config.settings import (
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_TARJETA,
)


class ResultadosEvaluacionWindow(ctk.CTkToplevel):
    def __init__(self, master, titulo: str, resultados: list[tuple[str, float, bool, str]], nota_minima: float):
        super().__init__(master)
        self._resultados = resultados
        self._nota_minima = nota_minima

        self.title(f"Resultados — {titulo}")
        self.configure(fg_color=COLOR_FONDO_APP)
        self.geometry("620x560")
        self.minsize(520, 420)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado(titulo)
        self._construir_resumen()
        self._construir_lista()

    # ------------------------------------------------------------------
    def _construir_encabezado(self, titulo: str):
        ctk.CTkLabel(
            self, text=titulo, font=(FONT_FAMILY, 17, "bold"), text_color=COLOR_TEXTO_PRIMARIO,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 4))

    def _construir_resumen(self):
        if self._resultados:
            estudiantes = {nombre for nombre, _nota, _aprobado, _fecha in self._resultados}
            aprobados = {nombre for nombre, _nota, aprobado, _fecha in self._resultados if aprobado}
            texto = (
                f"{len(self._resultados)} intento(s) de {len(estudiantes)} estudiante(s)  ·  "
                f"{len(aprobados)} aprobado(s)  ·  Nota mínima: {self._nota_minima:.1f} / 5.0"
            )
        else:
            texto = f"Todavía no hay ningún intento registrado.  ·  Nota mínima: {self._nota_minima:.1f} / 5.0"

        ctk.CTkLabel(
            self, text=texto, font=(FONT_FAMILY, 12), text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 12))

    def _construir_lista(self):
        lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        lista.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        lista.grid_columnconfigure(0, weight=1)

        if not self._resultados:
            ctk.CTkLabel(
                lista, text="Ningún aprendiz lo ha presentado todavía.",
                font=(FONT_FAMILY, 13), text_color=COLOR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, (nombre, nota, aprobado, fecha) in enumerate(self._resultados):
            self._construir_fila(lista, indice, nombre, nota, aprobado, fecha)

    def _construir_fila(self, contenedor, fila: int, nombre: str, nota: float, aprobado: bool, fecha: str):
        tarjeta = ctk.CTkFrame(
            contenedor, fg_color=COLOR_FONDO_TARJETA, corner_radius=RADIO_TARJETA,
            border_width=GROSOR_BORDE_SUTIL, border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.grid(row=fila, column=0, sticky="ew", pady=4)
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text=nombre, font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXTO_PRIMARIO, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(10, 0))
        ctk.CTkLabel(
            tarjeta, text=fecha or "—", font=(FONT_FAMILY, 11), text_color=COLOR_TEXTO_SECUNDARIO, anchor="e",
        ).grid(row=0, column=1, sticky="e", padx=16, pady=(10, 0))

        color = COLOR_EXITO if aprobado else COLOR_ERROR
        estado = "✓ Aprobado" if aprobado else "✗ No aprobado"
        ctk.CTkLabel(
            tarjeta, text=f"Nota: {nota:.1f} / 5.0   ·   {estado}", font=(FONT_FAMILY, 12, "bold"),
            text_color=color, anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(2, 10))
