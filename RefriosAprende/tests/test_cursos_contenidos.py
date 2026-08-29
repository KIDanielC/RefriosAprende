import os

import pytest
from PIL import Image

from config.settings import BASE_DIR
from controller.contenido_controller import (
    TIPO_IMAGEN,
    TIPO_PDF,
    TIPO_TEXTO,
    ContenidoController,
    DatosContenidoInvalidosError,
)
from controller.curso_controller import CursoController, DatosCursoInvalidosError


def test_crear_curso_valido(admin):
    cc = CursoController()
    creado = cc.crear_curso("Curso Nuevo", "Descripción", admin.id_usuario)
    assert creado.esta_activo()
    assert creado.nombre_instructor == admin.nombre_completo


def test_crear_curso_nombre_corto_falla(admin):
    cc = CursoController()
    with pytest.raises(DatosCursoInvalidosError):
        cc.crear_curso("ab", "Descripción", admin.id_usuario)


def test_crear_curso_instructor_invalido():
    cc = CursoController()
    with pytest.raises(DatosCursoInvalidosError):
        cc.crear_curso("Curso Valido", "Descripción", id_instructor=99999)


def test_desactivar_curso_lo_saca_de_activos(curso, admin):
    cc = CursoController()
    cc.actualizar_curso(curso.id_curso, curso.nombre_curso, curso.descripcion, admin.id_usuario, "INACTIVO")
    assert curso.id_curso not in [c.id_curso for c in cc.listar_cursos_activos()]
    assert curso.id_curso in [c.id_curso for c in cc.listar_cursos()]


def test_crear_contenido_texto(curso):
    ctrl = ContenidoController()
    contenido = ctrl.crear_contenido_texto(curso.id_curso, "Titulo valido", "Texto con longitud suficiente para pasar.")
    assert contenido.tipo_contenido == TIPO_TEXTO
    assert contenido.ruta_archivo is None
    assert contenido.orden == 1


def test_crear_contenido_texto_muy_corto_falla(curso):
    ctrl = ContenidoController()
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_texto(curso.id_curso, "Titulo valido", "corto")


def test_orden_de_contenidos_es_secuencial(curso):
    ctrl = ContenidoController()
    c1 = ctrl.crear_contenido_texto(curso.id_curso, "Primero", "Texto con longitud suficiente para pasar.")
    c2 = ctrl.crear_contenido_texto(curso.id_curso, "Segundo", "Texto con longitud suficiente para pasar.")
    assert c1.orden == 1
    assert c2.orden == 2


def test_crear_contenido_pdf(curso, tmp_path):
    ctrl = ContenidoController()
    ruta_pdf = tmp_path / "manual.pdf"
    ruta_pdf.write_bytes(b"%PDF-1.4\n%%EOF")

    contenido = ctrl.crear_contenido_pdf(curso.id_curso, "Manual tecnico", "Descripcion", str(ruta_pdf))
    assert contenido.tipo_contenido == TIPO_PDF
    ruta_copiada = os.path.join(BASE_DIR, contenido.ruta_archivo)
    assert os.path.isfile(ruta_copiada)

    ctrl.eliminar_contenido(contenido.id_contenido)
    assert not os.path.isfile(ruta_copiada)


def test_crear_contenido_pdf_archivo_inexistente_falla(curso):
    ctrl = ContenidoController()
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_pdf(curso.id_curso, "Titulo valido", "desc", "no_existe.pdf")


def test_crear_contenido_imagen(curso, tmp_path):
    ctrl = ContenidoController()
    ruta_imagen = tmp_path / "diagrama.png"
    Image.new("RGB", (400, 200), color=(10, 20, 30)).save(ruta_imagen)

    contenido = ctrl.crear_contenido_imagen(curso.id_curso, "Diagrama", "Descripcion", str(ruta_imagen))
    assert contenido.tipo_contenido == TIPO_IMAGEN
    ruta_copiada = os.path.join(BASE_DIR, contenido.ruta_archivo)
    assert os.path.isfile(ruta_copiada)

    ctrl.eliminar_contenido(contenido.id_contenido)
    assert not os.path.isfile(ruta_copiada)


def test_crear_contenido_imagen_extension_invalida_falla(curso, tmp_path):
    ctrl = ContenidoController()
    ruta_txt = tmp_path / "no_es_imagen.txt"
    ruta_txt.write_text("hola")
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_imagen(curso.id_curso, "Titulo valido", "desc", str(ruta_txt))


def test_eliminar_curso_elimina_contenidos_en_cascada(curso):
    cc = CursoController()
    ctrl = ContenidoController()
    ctrl.crear_contenido_texto(curso.id_curso, "Contenido", "Texto con longitud suficiente para pasar.")

    cc.eliminar_curso(curso.id_curso)

    assert ctrl.listar_por_curso(curso.id_curso) == []
