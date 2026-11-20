"""RF-04 y CU-05 prometían reordenar contenidos, pero cada contenido nuevo solo recibía el
siguiente número de orden y nunca cambiaba. Se agrega ContenidoController.mover_contenido."""
import pytest

from controller.contenido_controller import ContenidoController, DatosContenidoInvalidosError
from controller.curso_controller import CursoController
from controller.progreso_controller import ProgresoController


def _crear_tres_contenidos(curso, admin):
    cc = ContenidoController()
    uno = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.", usuario_actor=admin)
    dos = cc.crear_contenido_texto(curso.id_curso, "Dos", "Texto con longitud suficiente para pasar.", usuario_actor=admin)
    tres = cc.crear_contenido_texto(curso.id_curso, "Tres", "Texto con longitud suficiente para pasar.", usuario_actor=admin)
    return cc, uno, dos, tres


def test_subir_contenido_intercambia_el_orden(curso, admin):
    cc, uno, dos, tres = _crear_tres_contenidos(curso, admin)
    assert [c.orden for c in (uno, dos, tres)] == [1, 2, 3]

    cc.mover_contenido(dos.id_contenido, "subir", usuario_actor=admin)

    contenidos = cc.listar_por_curso(curso.id_curso)
    assert [c.titulo for c in contenidos] == ["Dos", "Uno", "Tres"]


def test_bajar_contenido_intercambia_el_orden(curso, admin):
    cc, uno, dos, tres = _crear_tres_contenidos(curso, admin)

    cc.mover_contenido(dos.id_contenido, "bajar", usuario_actor=admin)

    contenidos = cc.listar_por_curso(curso.id_curso)
    assert [c.titulo for c in contenidos] == ["Uno", "Tres", "Dos"]


def test_el_primero_no_sube(curso, admin):
    cc, uno, dos, tres = _crear_tres_contenidos(curso, admin)

    cc.mover_contenido(uno.id_contenido, "subir", usuario_actor=admin)

    contenidos = cc.listar_por_curso(curso.id_curso)
    assert [c.titulo for c in contenidos] == ["Uno", "Dos", "Tres"]


def test_el_ultimo_no_baja(curso, admin):
    cc, uno, dos, tres = _crear_tres_contenidos(curso, admin)

    cc.mover_contenido(tres.id_contenido, "bajar", usuario_actor=admin)

    contenidos = cc.listar_por_curso(curso.id_curso)
    assert [c.titulo for c in contenidos] == ["Uno", "Dos", "Tres"]


def test_el_orden_persiste_tras_recargar(curso, admin):
    cc, uno, dos, tres = _crear_tres_contenidos(curso, admin)
    cc.mover_contenido(uno.id_contenido, "bajar", usuario_actor=admin)

    # Simula "recargar": pide los contenidos de nuevo desde cero, no desde un valor en memoria.
    otro_controlador = ContenidoController()
    contenidos = otro_controlador.listar_por_curso(curso.id_curso)
    assert [c.titulo for c in contenidos] == ["Dos", "Uno", "Tres"]


def test_mover_direccion_invalida_falla(curso, admin):
    cc, uno, dos, tres = _crear_tres_contenidos(curso, admin)
    with pytest.raises(DatosContenidoInvalidosError):
        cc.mover_contenido(uno.id_contenido, "lateral", usuario_actor=admin)


def test_el_bloqueo_secuencial_respeta_el_nuevo_orden(curso, aprendiz, admin):
    curso_controlador = CursoController()
    curso_secuencial = curso_controlador.actualizar_curso(
        curso.id_curso, curso.nombre_curso, curso.descripcion, admin.id_usuario, "ACTIVO",
        aprendizaje_secuencial=True, usuario_actor=admin,
    )
    cc, uno, dos, tres = _crear_tres_contenidos(curso_secuencial, admin)
    pc = ProgresoController()

    # Antes de reordenar: "Dos" (orden 2) está bloqueado porque "Uno" (orden 1) no se ha visto.
    assert pc.contenido_bloqueado(aprendiz.id_usuario, dos, curso_secuencial) is True

    # Se sube "Tres" al principio: ahora el orden es Tres, Uno, Dos.
    cc.mover_contenido(tres.id_contenido, "subir", usuario_actor=admin)
    cc.mover_contenido(tres.id_contenido, "subir", usuario_actor=admin)
    contenidos = cc.listar_por_curso(curso_secuencial.id_curso)
    assert [c.titulo for c in contenidos] == ["Tres", "Uno", "Dos"]

    tres_actualizado, uno_actualizado, dos_actualizado = contenidos
    # "Tres" ahora es el primero: ya no está bloqueado por nada.
    assert pc.contenido_bloqueado(aprendiz.id_usuario, tres_actualizado, curso_secuencial) is False
    # "Uno" ahora depende de haber visto "Tres" (el nuevo primero), no al revés.
    assert pc.contenido_bloqueado(aprendiz.id_usuario, uno_actualizado, curso_secuencial) is True

    pc.registrar_contenido_visto(aprendiz.id_usuario, tres_actualizado)
    assert pc.contenido_bloqueado(aprendiz.id_usuario, uno_actualizado, curso_secuencial) is False
