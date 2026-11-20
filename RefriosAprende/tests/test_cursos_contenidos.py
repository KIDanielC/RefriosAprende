import os

import pytest
from PIL import Image

from config.settings import BASE_DIR
from controller.contenido_controller import (
    TIPO_IMAGEN,
    TIPO_PDF,
    TIPO_TEXTO,
    TIPO_VIDEO,
    ContenidoController,
    DatosContenidoInvalidosError,
)
from controller.curso_controller import DatosCursoInvalidosError, CursoController


def test_crear_curso_valido(admin):
    cc = CursoController()
    creado = cc.crear_curso("Curso Nuevo", "Descripción", admin.id_usuario, usuario_actor=admin)
    assert creado.es_borrador()  # los cursos nuevos nacen como borrador, no publicados aun
    assert creado.nombre_instructor == admin.nombre_completo


def test_crear_curso_nombre_corto_falla(admin):
    cc = CursoController()
    with pytest.raises(DatosCursoInvalidosError):
        cc.crear_curso("ab", "Descripción", admin.id_usuario, usuario_actor=admin)


def test_crear_curso_instructor_invalido(admin):
    cc = CursoController()
    with pytest.raises(DatosCursoInvalidosError):
        cc.crear_curso("Curso Valido", "Descripción", id_instructor=99999, usuario_actor=admin)


def test_publicar_curso_lo_activa(admin):
    cc = CursoController()
    creado = cc.crear_curso("Curso Nuevo", "Descripción", admin.id_usuario, usuario_actor=admin)
    publicado = cc.actualizar_curso(
        creado.id_curso, creado.nombre_curso, creado.descripcion, admin.id_usuario, "ACTIVO", usuario_actor=admin,
    )
    assert publicado.esta_activo()
    assert creado.id_curso in [c.id_curso for c in cc.listar_cursos_activos()]


def test_curso_con_categoria_nueva_la_crea_automaticamente(admin):
    cc = CursoController()
    creado = cc.crear_curso(
        "Curso Nuevo", "Descripción", admin.id_usuario, nombre_categoria="Compresores", usuario_actor=admin,
    )
    assert creado.nombre_categoria == "Compresores"
    assert any(c.nombre_categoria == "Compresores" for c in cc.listar_categorias())


def test_desactivar_curso_lo_saca_de_activos(curso, admin):
    cc = CursoController()
    cc.actualizar_curso(curso.id_curso, curso.nombre_curso, curso.descripcion, admin.id_usuario, "INACTIVO", usuario_actor=admin)
    assert curso.id_curso not in [c.id_curso for c in cc.listar_cursos_activos()]
    assert curso.id_curso in [c.id_curso for c in cc.listar_cursos()]


def test_crear_contenido_texto(curso, admin):
    ctrl = ContenidoController()
    contenido = ctrl.crear_contenido_texto(
        curso.id_curso, "Titulo valido", "Texto con longitud suficiente para pasar.", usuario_actor=admin,
    )
    assert contenido.tipo_contenido == TIPO_TEXTO
    assert contenido.ruta_archivo is None
    assert contenido.orden == 1


def test_crear_contenido_texto_muy_corto_falla(curso, admin):
    ctrl = ContenidoController()
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_texto(curso.id_curso, "Titulo valido", "corto", usuario_actor=admin)


def test_orden_de_contenidos_es_secuencial(curso, admin):
    ctrl = ContenidoController()
    c1 = ctrl.crear_contenido_texto(curso.id_curso, "Primero", "Texto con longitud suficiente para pasar.", usuario_actor=admin)
    c2 = ctrl.crear_contenido_texto(curso.id_curso, "Segundo", "Texto con longitud suficiente para pasar.", usuario_actor=admin)
    assert c1.orden == 1
    assert c2.orden == 2


def test_crear_contenido_pdf(curso, admin, tmp_path):
    ctrl = ContenidoController()
    ruta_pdf = tmp_path / "manual.pdf"
    ruta_pdf.write_bytes(b"%PDF-1.4\n%%EOF")

    contenido = ctrl.crear_contenido_pdf(curso.id_curso, "Manual tecnico", "Descripcion", str(ruta_pdf), usuario_actor=admin)
    assert contenido.tipo_contenido == TIPO_PDF
    ruta_copiada = os.path.join(BASE_DIR, contenido.ruta_archivo)
    assert os.path.isfile(ruta_copiada)

    ctrl.eliminar_contenido(contenido.id_contenido, usuario_actor=admin)
    assert not os.path.isfile(ruta_copiada)


def test_crear_contenido_pdf_archivo_inexistente_falla(curso, admin):
    ctrl = ContenidoController()
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_pdf(curso.id_curso, "Titulo valido", "desc", "no_existe.pdf", usuario_actor=admin)


def test_crear_contenido_imagen(curso, admin, tmp_path):
    ctrl = ContenidoController()
    ruta_imagen = tmp_path / "diagrama.png"
    Image.new("RGB", (400, 200), color=(10, 20, 30)).save(ruta_imagen)

    contenido = ctrl.crear_contenido_imagen(curso.id_curso, "Diagrama", "Descripcion", str(ruta_imagen), usuario_actor=admin)
    assert contenido.tipo_contenido == TIPO_IMAGEN
    ruta_copiada = os.path.join(BASE_DIR, contenido.ruta_archivo)
    assert os.path.isfile(ruta_copiada)

    ctrl.eliminar_contenido(contenido.id_contenido, usuario_actor=admin)
    assert not os.path.isfile(ruta_copiada)


def test_crear_contenido_imagen_extension_invalida_falla(curso, admin, tmp_path):
    ctrl = ContenidoController()
    ruta_txt = tmp_path / "no_es_imagen.txt"
    ruta_txt.write_text("hola")
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_imagen(curso.id_curso, "Titulo valido", "desc", str(ruta_txt), usuario_actor=admin)


def test_crear_contenido_video(curso, admin, tmp_path):
    ctrl = ContenidoController()
    ruta_video = tmp_path / "procedimiento.mp4"
    ruta_video.write_bytes(b"contenido de prueba de un video")

    contenido = ctrl.crear_contenido_video(
        curso.id_curso, "Procedimiento de carga", "Descripcion", str(ruta_video), usuario_actor=admin,
    )
    assert contenido.tipo_contenido == TIPO_VIDEO
    ruta_copiada = os.path.join(BASE_DIR, contenido.ruta_archivo)
    assert os.path.isfile(ruta_copiada)

    ctrl.eliminar_contenido(contenido.id_contenido, usuario_actor=admin)
    assert not os.path.isfile(ruta_copiada)


def test_crear_contenido_video_extension_invalida_falla(curso, admin, tmp_path):
    ctrl = ContenidoController()
    ruta_txt = tmp_path / "no_es_video.txt"
    ruta_txt.write_text("hola")
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_video(curso.id_curso, "Titulo valido", "desc", str(ruta_txt), usuario_actor=admin)


def test_crear_contenido_video_archivo_inexistente_falla(curso, admin):
    ctrl = ContenidoController()
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_video(curso.id_curso, "Titulo valido", "desc", "no_existe.mp4", usuario_actor=admin)


def test_crear_contenido_video_demasiado_grande_falla(curso, admin, tmp_path, monkeypatch):
    import controller.contenido_controller as contenido_controller_module
    monkeypatch.setattr(contenido_controller_module, "_TAMANO_MAXIMO_VIDEO_BYTES", 10)

    ctrl = ContenidoController()
    ruta_video = tmp_path / "demasiado_grande.mp4"
    ruta_video.write_bytes(b"este archivo pesa mas de 10 bytes")
    with pytest.raises(DatosContenidoInvalidosError):
        ctrl.crear_contenido_video(curso.id_curso, "Titulo valido", "desc", str(ruta_video), usuario_actor=admin)


def test_eliminar_curso_elimina_contenidos_en_cascada(curso, admin):
    cc = CursoController()
    ctrl = ContenidoController()
    ctrl.crear_contenido_texto(curso.id_curso, "Contenido", "Texto con longitud suficiente para pasar.", usuario_actor=admin)

    cc.eliminar_curso(curso.id_curso, usuario_actor=admin)

    assert ctrl.listar_por_curso(curso.id_curso) == []
