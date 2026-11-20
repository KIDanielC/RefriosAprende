import os

import pytest

import controller.taller_controller as taller_controller_module
from controller.contenido_controller import ContenidoController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.taller_controller import DatosTallerInvalidosError, TallerController


@pytest.fixture
def carpeta_entregas(tmp_path, monkeypatch):
    """Aísla dónde se guardan los archivos de entregas de taller durante la prueba (nunca en resources/ real)."""
    monkeypatch.setattr(taller_controller_module, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(taller_controller_module, "ENTREGAS_DIR", str(tmp_path / "resources" / "entregas"))
    return tmp_path


def _crear_archivo_de_prueba(tmp_path, nombre="entrega.png") -> str:
    ruta = tmp_path / nombre
    ruta.write_bytes(b"contenido de prueba")
    return str(ruta)


# -- CRUD de talleres (instructor) -------------------------------------------------------
def test_crear_taller(curso, admin):
    tc = TallerController()
    taller = tc.crear_taller(
        curso.id_curso, "Cambio de compresor", "Desmonta y cambia el compresor siguiendo el procedimiento visto en clase.",
        usuario_actor=admin,
    )
    assert taller.titulo == "Cambio de compresor"
    talleres = tc.listar_por_curso(curso.id_curso)
    assert len(talleres) == 1
    assert talleres[0].id_taller == taller.id_taller


def test_un_curso_puede_tener_varios_talleres(curso, admin):
    tc = TallerController()
    tc.crear_taller(curso.id_curso, "Taller uno", "Descripción suficientemente larga del taller uno.", usuario_actor=admin)
    tc.crear_taller(curso.id_curso, "Taller dos", "Descripción suficientemente larga del taller dos.", usuario_actor=admin)
    assert len(tc.listar_por_curso(curso.id_curso)) == 2


def test_crear_taller_titulo_muy_corto_falla(curso, admin):
    tc = TallerController()
    with pytest.raises(DatosTallerInvalidosError):
        tc.crear_taller(curso.id_curso, "Ta", "Descripción suficientemente larga del taller.", usuario_actor=admin)


def test_crear_taller_descripcion_muy_corta_falla(curso, admin):
    tc = TallerController()
    with pytest.raises(DatosTallerInvalidosError):
        tc.crear_taller(curso.id_curso, "Taller válido", "corta", usuario_actor=admin)


def test_actualizar_taller(curso, admin):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller original", "Descripción suficientemente larga del taller original.", usuario_actor=admin)
    actualizado = tc.actualizar_taller(
        taller.id_taller, "Taller actualizado", "Nueva descripción suficientemente larga.", usuario_actor=admin,
    )
    assert actualizado.titulo == "Taller actualizado"


def test_eliminar_taller(curso, admin):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    tc.eliminar_taller(taller.id_taller, usuario_actor=admin)
    assert tc.listar_por_curso(curso.id_curso) == []


# -- Entrega del aprendiz ------------------------------------------------------------------
def test_subir_entrega_valida(curso, aprendiz, admin, carpeta_entregas):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)

    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas))

    assert entrega.estado == "PENDIENTE"
    assert entrega.ruta_archivo.endswith(".png")
    assert os.path.isfile(os.path.join(str(carpeta_entregas), entrega.ruta_archivo))


def test_subir_entrega_rechaza_extension_no_permitida(curso, aprendiz, admin, carpeta_entregas):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    ruta_invalida = _crear_archivo_de_prueba(carpeta_entregas, nombre="entrega.txt")

    with pytest.raises(DatosTallerInvalidosError):
        tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, ruta_invalida)


def test_subir_entrega_rechaza_archivo_inexistente(curso, aprendiz, admin, carpeta_entregas):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)

    with pytest.raises(DatosTallerInvalidosError):
        tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, str(carpeta_entregas / "no_existe.pdf"))


def test_subir_entrega_reemplaza_y_borra_la_anterior(curso, aprendiz, admin, carpeta_entregas):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)

    primera = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas, "primera.png"))
    ruta_primera_absoluta = os.path.join(str(carpeta_entregas), primera.ruta_archivo)
    assert os.path.isfile(ruta_primera_absoluta)

    segunda = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas, "segunda.png"))

    assert segunda.ruta_archivo != primera.ruta_archivo
    assert not os.path.isfile(ruta_primera_absoluta)
    assert os.path.isfile(os.path.join(str(carpeta_entregas), segunda.ruta_archivo))


# -- Calificación del instructor ------------------------------------------------------------
def test_calificar_entrega_aprobada(curso, aprendiz, admin, carpeta_entregas):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas))

    calificada = tc.calificar_entrega(entrega.id_entrega, aprobado=True, comentario="Excelente trabajo", usuario_actor=admin)

    assert calificada.estado == "APROBADO"
    assert calificada.comentario_instructor == "Excelente trabajo"


def test_calificar_entrega_rechazada_permite_volver_a_subir(curso, aprendiz, admin, carpeta_entregas):
    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas, "v1.png"))
    tc.calificar_entrega(entrega.id_entrega, aprobado=False, comentario="Falta el paso 3", usuario_actor=admin)

    rechazada = tc.obtener_entrega(taller.id_taller, aprendiz.id_usuario)
    assert rechazada.estado == "RECHAZADO"
    assert rechazada.comentario_instructor == "Falta el paso 3"

    reenviada = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas, "v2.png"))
    assert reenviada.estado == "PENDIENTE"
    assert reenviada.comentario_instructor is None


# -- Requisito de finalización del curso ----------------------------------------------------
def test_curso_no_se_completa_hasta_aprobar_todos_los_talleres(curso, aprendiz, admin, carpeta_entregas):
    ic = InscripcionController()
    cc = ContenidoController()
    tc = TallerController()
    pc = ProgresoController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)
    contenido = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.", usuario_actor=admin)
    taller = tc.crear_taller(
        curso.id_curso, "Taller final", "Diagnostica una fuga real y documenta el procedimiento seguido.",
        usuario_actor=admin,
    )

    progreso = pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)
    assert progreso.estado == "EN_PROGRESO"  # vio todo el contenido, pero el taller aun no esta aprobado

    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(carpeta_entregas))
    assert pc.obtener_progreso(aprendiz.id_usuario, curso.id_curso).estado == "EN_PROGRESO"  # entrega pendiente

    tc.calificar_entrega(entrega.id_entrega, aprobado=True, comentario="Aprobado", usuario_actor=admin)

    assert pc.obtener_progreso(aprendiz.id_usuario, curso.id_curso).estado == "COMPLETADO"


def test_curso_sin_talleres_se_completa_igual_que_antes(curso, aprendiz, admin):
    """Un curso sin talleres no debe verse afectado por el nuevo requisito."""
    ic = InscripcionController()
    cc = ContenidoController()
    pc = ProgresoController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)
    contenido = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.", usuario_actor=admin)

    progreso = pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)
    assert progreso.estado == "COMPLETADO"
