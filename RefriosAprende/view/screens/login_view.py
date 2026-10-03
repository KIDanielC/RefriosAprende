"""Vista de inicio de sesión. No contiene lógica de negocio."""
import math
import os

import customtkinter as ctk
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.settings import (
    APP_NAME,
    IMAGES_DIR,
    COLOR_ACENTO_GLOW,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_BORDE_SUTIL,
    COLOR_ERROR,
    COLOR_FONDO_APP,
    COLOR_FONDO_TARJETA,
    COLOR_NAV_BORDE,
    COLOR_NAV_TEXTO,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    FONT_FAMILY,
    GROSOR_BORDE_SUTIL,
    RADIO_BOTON,
    RADIO_TARJETA,
    VENTANA_ALTO,
    VENTANA_ANCHO,
)
from controller.autenticacion_controller import (
    CredencialesInvalidasError,
    AutenticacionController,
    UsuarioInactivoError,
)

_DIR_FUENTES_WINDOWS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def _hex_a_rgb(color_hex: str) -> tuple:
    color_hex = color_hex.lstrip("#")
    return tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))


def _cargar_fuente(nombre_archivo: str, tamano: int) -> ImageFont.FreeTypeFont:
    """Carga Century Gothic desde las fuentes de Windows para dibujarla directamente sobre
    la ilustración (Tkinter no permite mezclar texto con transparencia real sobre una imagen
    de fondo: solo pintando el texto como píxeles de la propia imagen se logra que se vea
    "parte del fondo" y no una caja de color encima). Si la fuente no está instalada, cae a
    la fuente por defecto de Pillow en vez de fallar."""
    try:
        return ImageFont.truetype(os.path.join(_DIR_FUENTES_WINDOWS, nombre_archivo), tamano)
    except OSError:
        return ImageFont.load_default()


def _envolver_texto(texto: str, fuente: ImageFont.FreeTypeFont, ancho_maximo: int) -> list:
    palabras = texto.split()
    lineas = []
    actual = ""
    for palabra in palabras:
        candidata = f"{actual} {palabra}".strip()
        if not actual or fuente.getlength(candidata) <= ancho_maximo:
            actual = candidata
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


class LoginView(ctk.CTk):
    """Ventana de autenticación. Una sola ilustración de fondo cubre toda la ventana; el texto
    de marca se dibuja directamente sobre esa imagen (con Pillow, no como widgets encima), para
    que quede realmente integrado con la foto en vez de sobre un recuadro de color sólido. Solo
    la tarjeta del formulario (a la derecha) es una tarjeta de verdad, como es normal en un
    formulario. No contiene lógica de negocio."""

    _PAD_DERECHO = 56
    _PAD_INFERIOR = 44
    _ANCHO_TEXTO = 420
    _LADO_INSIGNIA = 52

    def __init__(self, al_iniciar_sesion):
        super().__init__()
        self._al_iniciar_sesion = al_iniciar_sesion
        self._controlador = AutenticacionController()

        self.title(APP_NAME)
        self.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}")
        self.minsize(1000, 640)
        self.configure(fg_color=COLOR_FONDO_APP)

        self._ilustracion_original = self._cargar_ilustracion_original()
        self._imagen_fondo = None
        self._ultimo_tamano_fondo = None
        self._tarea_redimensionar_fondo = None

        self._fuente_insignia = _cargar_fuente("GOTHICB.TTF", 20)
        self._fuente_titulo = _cargar_fuente("GOTHICB.TTF", 30)
        self._fuente_texto = _cargar_fuente("GOTHIC.TTF", 14)
        self._fuente_estadistica_valor = _cargar_fuente("GOTHICB.TTF", 20)
        self._fuente_estadistica_etiqueta = _cargar_fuente("GOTHIC.TTF", 11)

        self._construir_fondo()
        self._construir_panel_formulario()

        self.bind("<Configure>", self._al_redimensionar_ventana)

    # -- Fondo: una sola ilustración detrás de toda la ventana, con el texto de marca ------
    # dibujado directamente sobre ella (no como widgets superpuestos).
    def _cargar_ilustracion_original(self) -> Image.Image | None:
        ruta = os.path.join(IMAGES_DIR, "ilustracion_login.jpg")
        if not os.path.isfile(ruta):
            return None
        with Image.open(ruta) as archivo_imagen:
            return archivo_imagen.convert("RGB").copy()

    @staticmethod
    def _recortar_a_cubrir(imagen: Image.Image, ancho: int, alto: int) -> Image.Image:
        """Recorta al centro y redimensiona para cubrir exactamente (ancho x alto),
        sin deformar la imagen ni dejar franjas vacías (equivalente a CSS background-size: cover)."""
        proporcion_objetivo = ancho / alto
        proporcion_imagen = imagen.width / imagen.height
        if proporcion_imagen > proporcion_objetivo:
            nuevo_ancho = round(imagen.height * proporcion_objetivo)
            x0 = (imagen.width - nuevo_ancho) // 2
            recorte = imagen.crop((x0, 0, x0 + nuevo_ancho, imagen.height))
        else:
            nuevo_alto = round(imagen.width / proporcion_objetivo)
            y0 = (imagen.height - nuevo_alto) // 2
            recorte = imagen.crop((0, y0, imagen.width, y0 + nuevo_alto))
        return recorte.resize((ancho, alto), Image.LANCZOS)

    @staticmethod
    def _oscurecer(imagen: Image.Image) -> Image.Image:
        """Viñeta suave y radial anclada en la esquina inferior derecha (donde va el texto
        de marca): se desvanece de forma continua hacia arriba y hacia la izquierda, sin
        bordes duros de rectángulo, para que el texto que se dibuja encima siga leyéndose sin
        tapar la foto con una caja de color plano."""
        ancho, alto = imagen.size
        lejania_derecha = 1 - np.linspace(0, 1, ancho)
        cercania_abajo = 1 - np.linspace(0, 1, alto)
        uu, cc = np.meshgrid(lejania_derecha, cercania_abajo)
        radio = np.sqrt((uu / 0.55) ** 2 + (cc / 0.95) ** 2)
        factor = np.clip(1 - radio, 0, 1) ** 1.3
        alpha = (factor * 145).astype("uint8")

        mascara = Image.fromarray(alpha, mode="L")
        capa = Image.new("RGBA", (ancho, alto), (8, 11, 15, 255))
        capa.putalpha(mascara)
        return Image.alpha_composite(imagen.convert("RGBA"), capa).convert("RGB")

    def _dibujar_texto_marca(self, imagen: Image.Image) -> Image.Image:
        """Dibuja la insignia, el titular, la descripción y las estadísticas como píxeles
        reales de la imagen (con Pillow): así quedan integradas con la foto de fondo, en vez
        de sobre un widget con su propio color de relleno."""
        draw = ImageDraw.Draw(imagen)
        ancho_imagen, alto_imagen = imagen.size

        lineas_titulo = ["Educación técnica", "certificada en refrigeración."]
        lineas_texto = _envolver_texto(
            "Cursos, evaluaciones y simulaciones de diagnóstico para formar al equipo técnico "
            "de Refrios — con seguimiento de avance en tiempo real.",
            self._fuente_texto, self._ANCHO_TEXTO,
        )
        estadisticas = (("18", "Cursos activos"), ("92%", "Aprobación"), ("236", "Aprendices"))

        alto_linea_titulo = round(self._fuente_titulo.size * 1.3)
        alto_linea_texto = round(self._fuente_texto.size * 1.55)
        alto_valor_estadistica = round(self._fuente_estadistica_valor.size * 1.3)
        alto_etiqueta_estadistica = round(self._fuente_estadistica_etiqueta.size * 1.3)

        gap_tras_insignia = 20
        gap_tras_titulo = 12
        gap_tras_texto = 22
        gap_tras_separador = 18
        gap_valor_etiqueta = 4

        alto_total = (
            self._LADO_INSIGNIA + gap_tras_insignia
            + alto_linea_titulo * len(lineas_titulo) + gap_tras_titulo
            + alto_linea_texto * len(lineas_texto) + gap_tras_texto
            + 1 + gap_tras_separador
            + alto_valor_estadistica + gap_valor_etiqueta + alto_etiqueta_estadistica
        )
        y = max(24, alto_imagen - self._PAD_INFERIOR - alto_total)
        x = ancho_imagen - self._PAD_DERECHO - self._ANCHO_TEXTO

        # Insignia: copo de nieve (identidad de Refrios Aprende: refrigeración + formación),
        # dibujado con líneas en vez de un glifo de fuente (no todas las fuentes traen "❄").
        color_acento = _hex_a_rgb(COLOR_ACENTO_PRIMARIO)
        draw.rounded_rectangle(
            (x, y, x + self._LADO_INSIGNIA, y + self._LADO_INSIGNIA), radius=RADIO_BOTON, fill=color_acento,
        )
        cx, cy = x + self._LADO_INSIGNIA / 2, y + self._LADO_INSIGNIA / 2
        radio_copo = self._LADO_INSIGNIA * 0.32
        for angulo_grados in (90, 210, 330):
            ang = math.radians(angulo_grados)
            dx, dy = math.cos(ang) * radio_copo, math.sin(ang) * radio_copo
            draw.line((cx - dx, cy - dy, cx + dx, cy + dy), fill=(255, 255, 255), width=4)
            for punta_signo in (-1, 1):
                px, py = cx + punta_signo * dx, cy + punta_signo * dy
                largo_rama = radio_copo * 0.4
                for delta in (28, -28):
                    ang_rama = ang + math.radians(delta)
                    draw.line(
                        (px, py, px - punta_signo * largo_rama * math.cos(ang_rama), py - punta_signo * largo_rama * math.sin(ang_rama)),
                        fill=(255, 255, 255), width=3,
                    )
        y += self._LADO_INSIGNIA + gap_tras_insignia

        # Todo el texto lleva un contorno oscuro (como un subtítulo de video): así se sigue
        # leyendo sin importar qué haya detrás en la foto (ropa clara, guantes, metal brillante…),
        # en vez de depender solo del degradado para el contraste.
        color_contorno = (10, 14, 19)

        # Titular
        color_titulo = _hex_a_rgb(COLOR_NAV_TEXTO)
        for linea in lineas_titulo:
            draw.text((x, y), linea, font=self._fuente_titulo, fill=color_titulo, stroke_width=2, stroke_fill=color_contorno)
            y += alto_linea_titulo
        y += gap_tras_titulo

        # Descripción (blanco, no gris, para que no se pierda sobre zonas claras de la foto)
        color_descripcion = _hex_a_rgb(COLOR_NAV_TEXTO)
        for linea in lineas_texto:
            draw.text((x, y), linea, font=self._fuente_texto, fill=color_descripcion, stroke_width=1, stroke_fill=color_contorno)
            y += alto_linea_texto
        y += gap_tras_texto

        # Separador
        draw.line((x, y, x + self._ANCHO_TEXTO, y), fill=_hex_a_rgb(COLOR_NAV_BORDE), width=1)
        y += 1 + gap_tras_separador

        # Estadísticas
        color_glow = _hex_a_rgb(COLOR_ACENTO_GLOW)
        x_columna = x
        for valor, etiqueta in estadisticas:
            draw.text(
                (x_columna, y), valor, font=self._fuente_estadistica_valor, fill=color_glow,
                stroke_width=2, stroke_fill=color_contorno,
            )
            draw.text(
                (x_columna, y + alto_valor_estadistica + gap_valor_etiqueta), etiqueta,
                font=self._fuente_estadistica_etiqueta, fill=color_descripcion,
                stroke_width=1, stroke_fill=color_contorno,
            )
            ancho_columna = max(
                self._fuente_estadistica_valor.getlength(valor),
                self._fuente_estadistica_etiqueta.getlength(etiqueta),
            )
            x_columna += ancho_columna + 34

        return imagen

    def _construir_fondo(self):
        self._etiqueta_fondo = ctk.CTkLabel(self, text="", fg_color=COLOR_FONDO_APP)
        self._etiqueta_fondo.place(x=0, y=0, relwidth=1, relheight=1)

    def _actualizar_fondo(self):
        ancho = self.winfo_width()
        alto = self.winfo_height()
        if ancho < 10 or alto < 10 or self._ilustracion_original is None:
            return
        if self._ultimo_tamano_fondo == (ancho, alto):
            return
        self._ultimo_tamano_fondo = (ancho, alto)

        cubierta = self._recortar_a_cubrir(self._ilustracion_original, ancho, alto)
        cubierta = self._oscurecer(cubierta)
        cubierta = self._dibujar_texto_marca(cubierta)
        self._imagen_fondo = ctk.CTkImage(light_image=cubierta, dark_image=cubierta, size=(ancho, alto))
        self._etiqueta_fondo.configure(image=self._imagen_fondo)

    def _al_redimensionar_ventana(self, evento):
        if evento.widget is not self:
            return
        if self._tarea_redimensionar_fondo is not None:
            self.after_cancel(self._tarea_redimensionar_fondo)
        self._tarea_redimensionar_fondo = self.after(60, self._actualizar_fondo)

    # -- Tarjeta de login: flota sobre el fondo, del lado izquierdo -------------------------
    def _construir_panel_formulario(self):
        tarjeta = ctk.CTkFrame(
            self,
            fg_color=COLOR_FONDO_TARJETA,
            corner_radius=RADIO_TARJETA + 4,
            width=440,
            border_width=GROSOR_BORDE_SUTIL,
            border_color=COLOR_BORDE_SUTIL,
        )
        tarjeta.place(relx=0.23, rely=0.5, anchor="center")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text="Bienvenido de nuevo", font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXTO_PRIMARIO
        ).grid(row=0, column=0, padx=44, pady=(40, 8), sticky="w")
        ctk.CTkLabel(
            tarjeta,
            text=" Ingresa tus credenciales para continuar tu formación.",
            font=(FONT_FAMILY, 13.5),
            text_color=COLOR_TEXTO_SECUNDARIO,
            wraplength=350,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, padx=44, pady=(0, 28), sticky="w")

        self._campo_usuario = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Usuario",
            width=350,
            height=48,
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL,
            border_width=GROSOR_BORDE_SUTIL,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 15),
        )
        self._campo_usuario.grid(row=2, column=0, padx=44, pady=10)

        self._campo_contrasena = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Contraseña",
            show="•",
            width=350,
            height=48,
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_FONDO_APP,
            border_color=COLOR_BORDE_SUTIL,
            border_width=GROSOR_BORDE_SUTIL,
            text_color=COLOR_TEXTO_PRIMARIO,
            font=(FONT_FAMILY, 15),
        )
        self._campo_contrasena.grid(row=3, column=0, padx=44, pady=10)
        self._campo_contrasena.bind("<Return>", lambda evento: self._manejar_inicio_sesion())

        self._etiqueta_error = ctk.CTkLabel(
            tarjeta, text="", font=(FONT_FAMILY, 13), text_color=COLOR_ERROR, wraplength=350
        )
        self._etiqueta_error.grid(row=4, column=0, padx=44, pady=(6, 0))

        self._boton_ingresar = ctk.CTkButton(
            tarjeta,
            text="Iniciar sesión",
            width=350,
            height=50,
            corner_radius=RADIO_BOTON,
            fg_color=COLOR_ACENTO_PRIMARIO,
            hover_color=COLOR_ACENTO_SECUNDARIO,
            text_color="#FFFFFF",
            font=(FONT_FAMILY, 16, "bold"),
            command=self._manejar_inicio_sesion,
        )
        self._boton_ingresar.grid(row=5, column=0, padx=44, pady=(24, 14))

        ctk.CTkLabel(
            tarjeta,
            text="¿Olvidaste tu contraseña? Contacta a un administrador.",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=6, column=0, padx=44, pady=(0, 32))

    # ------------------------------------------------------------------
    def _manejar_inicio_sesion(self):
        usuario = self._campo_usuario.get()
        contrasena = self._campo_contrasena.get()

        try:
            entidad_usuario = self._controlador.iniciar_sesion(usuario, contrasena)
        except (CredencialesInvalidasError, UsuarioInactivoError) as error:
            self._etiqueta_error.configure(text=str(error))
            return

        self._etiqueta_error.configure(text="")
        self.destroy()
        self._al_iniciar_sesion(entidad_usuario)
