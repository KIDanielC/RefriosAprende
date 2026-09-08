"""Editor de texto con formato básico: fuente, tamaño, negrita, cursiva, alineación y enlaces.

Se guarda como un JSON simple (ver `utils.texto_enriquecido`) en la misma columna TEXT que
antes guardaba texto plano, así que los datos ya existentes (texto plano, sin formato) se
siguen leyendo sin ningún problema: si el valor no es JSON con la marca esperada, se trata
como texto sin formato. Esto evita tocar el esquema de la base de datos: para los DAO sigue
siendo "una cadena de texto" como siempre; los controladores que validan longitud mínima usan
`texto_plano_desde_markup()` para no contar los caracteres del JSON.

También sirve como visor de solo lectura (`solo_lectura=True`) para que el aprendiz vea el
mismo formato que definió el instructor, con los enlaces funcionando (abren el navegador).
"""
import json
import tkinter as tk
import tkinter.font as tkfont
import webbrowser

import customtkinter as ctk

from config.settings import (
    COLOR_ACENTO_ALTERNO,
    COLOR_BORDE_SUTIL,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA_HOVER,
    COLOR_TEXTO_PRIMARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
)
from utils.texto_enriquecido import MARCA_FORMATO, analizar, texto_plano_desde_markup

_FUENTES_DISPONIBLES = [FONT_FAMILY, "Arial", "Georgia", "Consolas", "Verdana"]
_TAMANOS_DISPONIBLES = ["11", "12", "13", "14", "16", "18", "20", "24"]
_TAMANO_DEFECTO = 13
_PADDING_VERTICAL_PX = 18

__all__ = ["EditorTextoEnriquecido", "texto_plano_desde_markup"]


class EditorTextoEnriquecido(ctk.CTkFrame):
    """Área de texto que se ajusta de alto automáticamente al contenido. Con
    `con_formato=True` (por defecto) agrega una barra con fuente, tamaño, negrita,
    cursiva, alineación y enlaces. Con `solo_lectura=True` se usa como visor: sin barra,
    sin edición, pero los enlaces siguen siendo clicables."""

    def __init__(
        self,
        master,
        valor_inicial: str = "",
        con_formato: bool = True,
        solo_lectura: bool = False,
        altura_minima_lineas: int = 3,
        altura_maxima_lineas: int = 18,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._solo_lectura = solo_lectura
        self._con_formato = con_formato and not solo_lectura
        self._altura_minima_lineas = altura_minima_lineas
        self._altura_maxima_lineas = altura_maxima_lineas
        self._fuentes_configuradas = set()
        self._enlaces = {}
        self._contador_enlaces = 0
        self._alto_actual_px = None

        self.grid_columnconfigure(0, weight=1)
        fila_caja = 0
        if self._con_formato:
            self._construir_barra_herramientas()
            fila_caja = 1

        self._caja = ctk.CTkTextbox(
            self, height=1, corner_radius=RADIO_BOTON, fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL, border_width=GROSOR_BORDE_SUTIL,
            text_color=COLOR_TEXTO_PRIMARIO, font=(FONT_FAMILY, _TAMANO_DEFECTO), wrap="word",
            activate_scrollbars=False,
        )
        self._caja.grid(row=fila_caja, column=0, sticky="ew")
        # CTkTextbox no expone dump()/count(): se necesitan para serializar el formato y
        # para calcular el alto automático, así que se usa el tkinter.Text real por debajo.
        self._texto = self._caja._textbox

        self._configurar_tags_base()
        self.cargar_markup(valor_inicial)

        self._texto.bind("<<Modified>>", self._al_modificar_contenido, add=True)
        self._texto.bind("<Configure>", lambda _evento: self._ajustar_altura(), add=True)

        if self._solo_lectura:
            self._texto.configure(state="disabled", cursor="arrow")

        self.after(30, self._ajustar_altura)

    # -- Barra de herramientas -------------------------------------------------------------
    def _construir_barra_herramientas(self):
        barra = ctk.CTkFrame(self, fg_color=COLOR_FONDO_TARJETA_HOVER, corner_radius=RADIO_BOTON)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self._menu_fuente = ctk.CTkOptionMenu(
            barra, values=_FUENTES_DISPONIBLES, width=100, height=24, font=(FONT_FAMILY, 10),
            fg_color=COLOR_FONDO_APP, button_color=COLOR_ACENTO_ALTERNO,
            text_color=COLOR_TEXTO_PRIMARIO, dropdown_font=(FONT_FAMILY, 11),
            command=self._aplicar_fuente,
        )
        self._menu_fuente.set(FONT_FAMILY)
        self._menu_fuente.pack(side="left", padx=(4, 3), pady=4)

        self._menu_tamano = ctk.CTkOptionMenu(
            barra, values=_TAMANOS_DISPONIBLES, width=44, height=24, font=(FONT_FAMILY, 10),
            fg_color=COLOR_FONDO_APP, button_color=COLOR_ACENTO_ALTERNO,
            text_color=COLOR_TEXTO_PRIMARIO, dropdown_font=(FONT_FAMILY, 11),
            command=self._aplicar_tamano,
        )
        self._menu_tamano.set(str(_TAMANO_DEFECTO))
        self._menu_tamano.pack(side="left", padx=(0, 6), pady=4)

        self._boton_herramienta(barra, "N", self._aplicar_negrita, ancho=24, fuente=(FONT_FAMILY, 12, "bold"))
        self._boton_herramienta(barra, "K", self._aplicar_cursiva, ancho=24, fuente=(FONT_FAMILY, 12, "italic"))
        self._separador(barra)
        self._boton_herramienta(barra, "Izq.", lambda: self._aplicar_alineacion("left"), ancho=32)
        self._boton_herramienta(barra, "Centro", lambda: self._aplicar_alineacion("center"), ancho=42)
        self._boton_herramienta(barra, "Der.", lambda: self._aplicar_alineacion("right"), ancho=32)
        self._separador(barra)
        self._boton_herramienta(barra, "🔗", self._insertar_enlace, ancho=28)

    def _separador(self, contenedor):
        ctk.CTkFrame(contenedor, fg_color=COLOR_BORDE_SUTIL, width=1, height=18).pack(side="left", padx=3, pady=3)

    def _boton_herramienta(self, contenedor, texto, comando, ancho=28, fuente=None):
        boton = ctk.CTkButton(
            contenedor, text=texto, width=ancho, height=24, corner_radius=RADIO_BOTON,
            fg_color="transparent", hover_color=COLOR_FONDO_APP, border_width=GROSOR_BORDE_SUTIL,
            border_color=COLOR_BORDE_SUTIL, text_color=COLOR_TEXTO_PRIMARIO,
            font=fuente or (FONT_FAMILY, 11, "bold"), command=comando,
        )
        boton.pack(side="left", padx=1, pady=4)
        return boton

    # -- Tags base (alineación) — las de fuente se crean bajo demanda, hay muchas combinaciones ---
    def _configurar_tags_base(self):
        self._texto.tag_configure("al::center", justify="center")
        self._texto.tag_configure("al::right", justify="right")

    def _tag_fuente(self, familia: str, tamano: int, negrita: bool, cursiva: bool) -> str:
        familia = familia or FONT_FAMILY
        tamano = tamano or _TAMANO_DEFECTO
        clave = f"fnt::{familia}::{tamano}::{1 if negrita else 0}::{1 if cursiva else 0}"
        if clave not in self._fuentes_configuradas:
            estilo = " ".join(filter(None, ["bold" if negrita else "", "italic" if cursiva else ""])) or "normal"
            self._texto.tag_configure(clave, font=(familia, tamano, estilo))
            self._fuentes_configuradas.add(clave)
        return clave

    def _nuevo_tag_url(self, href: str) -> str:
        self._contador_enlaces += 1
        nombre = f"url::{self._contador_enlaces}"
        self._enlaces[nombre] = href
        self._texto.tag_configure(nombre, foreground=COLOR_ACENTO_ALTERNO, underline=True)
        self._texto.tag_bind(nombre, "<Button-1>", lambda _e, url=href: webbrowser.open(url))
        self._texto.tag_bind(nombre, "<Enter>", lambda _e: self._texto.configure(cursor="hand2"))
        self._texto.tag_bind(nombre, "<Leave>", lambda _e: self._texto.configure(cursor="arrow" if self._solo_lectura else "xterm"))
        return nombre

    # -- Selección: si no hay nada seleccionado, se usa la palabra bajo el cursor -------------
    def _rango_objetivo(self):
        try:
            return self._texto.index("sel.first"), self._texto.index("sel.last")
        except tk.TclError:
            pass
        inicio, fin = self._texto.index("insert wordstart"), self._texto.index("insert wordend")
        return None if inicio == fin else (inicio, fin)

    def _leer_formato_en(self, indice: str):
        for nombre in self._texto.tag_names(indice):
            if nombre.startswith("fnt::"):
                _, familia, tamano, negrita, cursiva = nombre.split("::")
                return familia, int(tamano), negrita == "1", cursiva == "1"
        return FONT_FAMILY, _TAMANO_DEFECTO, False, False

    def _reemplazar_tag_fuente(self, inicio, fin, familia, tamano, negrita, cursiva):
        for nombre in list(self._texto.tag_names()):
            if nombre.startswith("fnt::"):
                self._texto.tag_remove(nombre, inicio, fin)
        self._texto.tag_add(self._tag_fuente(familia, tamano, negrita, cursiva), inicio, fin)
        self._ajustar_altura()

    # -- Acciones de la barra ---------------------------------------------------------------
    def _aplicar_negrita(self):
        rango = self._rango_objetivo()
        if not rango:
            return
        familia, tamano, negrita, cursiva = self._leer_formato_en(rango[0])
        self._reemplazar_tag_fuente(*rango, familia, tamano, not negrita, cursiva)

    def _aplicar_cursiva(self):
        rango = self._rango_objetivo()
        if not rango:
            return
        familia, tamano, negrita, cursiva = self._leer_formato_en(rango[0])
        self._reemplazar_tag_fuente(*rango, familia, tamano, negrita, not cursiva)

    def _aplicar_fuente(self, familia: str):
        rango = self._rango_objetivo()
        if not rango:
            return
        _, tamano, negrita, cursiva = self._leer_formato_en(rango[0])
        self._reemplazar_tag_fuente(*rango, familia, tamano, negrita, cursiva)

    def _aplicar_tamano(self, texto_tamano: str):
        rango = self._rango_objetivo()
        if not rango:
            return
        familia, _, negrita, cursiva = self._leer_formato_en(rango[0])
        self._reemplazar_tag_fuente(*rango, familia, int(texto_tamano), negrita, cursiva)

    def _aplicar_alineacion(self, valor: str):
        try:
            inicio = self._texto.index("sel.first linestart")
            fin = self._texto.index("sel.last lineend")
        except tk.TclError:
            inicio = self._texto.index("insert linestart")
            fin = self._texto.index("insert lineend")
        self._texto.tag_remove("al::center", inicio, fin)
        self._texto.tag_remove("al::right", inicio, fin)
        if valor != "left":
            self._texto.tag_add(f"al::{valor}", inicio, fin)
        self._ajustar_altura()

    def _insertar_enlace(self):
        rango = self._rango_objetivo()
        dialogo = ctk.CTkInputDialog(text="URL del enlace (por ejemplo: https://...):", title="Agregar enlace")
        href = (dialogo.get_input() or "").strip()
        if not href:
            return
        if not href.startswith(("http://", "https://")):
            href = "https://" + href
        nombre_tag = self._nuevo_tag_url(href)
        if rango:
            self._texto.tag_add(nombre_tag, *rango)
        else:
            self._texto.insert("insert", href, (nombre_tag,))
        self._ajustar_altura()

    # -- Alto automático ----------------------------------------------------------------------
    def _al_modificar_contenido(self, _evento=None):
        if not self._texto.edit_modified():
            return
        self._texto.edit_modified(False)
        self._ajustar_altura()

    def _ajustar_altura(self):
        if not self._texto.winfo_exists():
            return
        self._texto.update_idletasks()
        try:
            lineas_visibles = self._texto.count("1.0", "end-1c", "displaylines")[0]
        except (TypeError, tk.TclError):
            lineas_visibles = 1
        lineas = max(self._altura_minima_lineas, min(lineas_visibles + 1, self._altura_maxima_lineas))
        alto_linea = tkfont.Font(font=self._texto.cget("font")).metrics("linespace")
        nuevo_alto = lineas * alto_linea + _PADDING_VERTICAL_PX

        if nuevo_alto != self._alto_actual_px:
            self._alto_actual_px = nuevo_alto
            self._caja.configure(height=nuevo_alto)

    # -- Guardar / cargar ---------------------------------------------------------------------
    def obtener_markup(self) -> str:
        eventos = self._texto.dump("1.0", "end-1c", tag=True, text=True)
        parrafos = []
        parrafo_actual = {"alineacion": "left", "tramos": []}
        activos = set()

        def alineacion_activa():
            for nombre in activos:
                if nombre.startswith("al::"):
                    return nombre.split("::", 1)[1]
            return "left"

        def formato_activo():
            familia = tamano = None
            negrita = cursiva = False
            url = None
            for nombre in activos:
                if nombre.startswith("fnt::"):
                    _, familia_t, tamano_t, negrita_t, cursiva_t = nombre.split("::")
                    familia, tamano = familia_t, int(tamano_t)
                    negrita, cursiva = negrita_t == "1", cursiva_t == "1"
                elif nombre.startswith("url::"):
                    url = self._enlaces.get(nombre)
            return familia, tamano, negrita, cursiva, url

        for clave, valor, _indice in eventos:
            if clave == "tagon":
                activos.add(valor)
            elif clave == "tagoff":
                activos.discard(valor)
            elif clave == "text":
                partes = valor.split("\n")
                for indice_parte, parte in enumerate(partes):
                    if parte:
                        familia, tamano, negrita, cursiva, url = formato_activo()
                        parrafo_actual["tramos"].append({
                            "texto": parte, "fuente": familia, "tamano": tamano,
                            "negrita": negrita, "cursiva": cursiva, "url": url,
                        })
                        parrafo_actual["alineacion"] = alineacion_activa()
                    if indice_parte < len(partes) - 1:
                        parrafos.append(parrafo_actual)
                        parrafo_actual = {"alineacion": "left", "tramos": []}

        parrafos.append(parrafo_actual)
        return json.dumps({"formato": MARCA_FORMATO, "parrafos": parrafos}, ensure_ascii=False)

    def cargar_markup(self, valor: str):
        estaba_deshabilitada = self._texto.cget("state") == "disabled"
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")
        for nombre in list(self._texto.tag_names()):
            if nombre.startswith(("fnt::", "url::")):
                self._texto.tag_delete(nombre)
        self._fuentes_configuradas.clear()
        self._enlaces.clear()
        self._contador_enlaces = 0

        datos = analizar(valor)
        for indice_parrafo, parrafo in enumerate(datos["parrafos"]):
            if indice_parrafo > 0:
                self._texto.insert("end", "\n")
            inicio_parrafo = self._texto.index("end-1c")
            for tramo in parrafo.get("tramos", []):
                texto_tramo = tramo.get("texto", "")
                if not texto_tramo:
                    continue
                nombre_fuente = self._tag_fuente(
                    tramo.get("fuente"), tramo.get("tamano"),
                    tramo.get("negrita", False), tramo.get("cursiva", False),
                )
                etiquetas = [nombre_fuente]
                href = tramo.get("url")
                if href:
                    etiquetas.append(self._nuevo_tag_url(href))
                self._texto.insert("end", texto_tramo, tuple(etiquetas))

            alineacion = parrafo.get("alineacion", "left")
            if alineacion != "left":
                self._texto.tag_add(f"al::{alineacion}", inicio_parrafo, self._texto.index("end-1c"))

        if estaba_deshabilitada or self._solo_lectura:
            self._texto.configure(state="disabled")
        self._texto.edit_modified(False)
        self.after(10, self._ajustar_altura)
