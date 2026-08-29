from controller.contenido_controller import ContenidoController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController


def test_curso_nuevo_no_tiene_matriculados(curso):
    ic = InscripcionController()
    assert ic.listar_aprendices_matriculados(curso.id_curso) == []


def test_aprendiz_disponible_antes_de_matricular(curso, aprendiz):
    ic = InscripcionController()
    disponibles = ic.listar_aprendices_disponibles(curso.id_curso)
    assert any(u.id_usuario == aprendiz.id_usuario for u in disponibles)


def test_matricular_aprendiz(curso, aprendiz):
    ic = InscripcionController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)

    matriculados = ic.listar_aprendices_matriculados(curso.id_curso)
    assert any(u.id_usuario == aprendiz.id_usuario for u in matriculados)

    cursos_del_aprendiz = ic.listar_cursos_matriculados(aprendiz.id_usuario)
    assert any(c.id_curso == curso.id_curso for c in cursos_del_aprendiz)

    disponibles = ic.listar_aprendices_disponibles(curso.id_curso)
    assert not any(u.id_usuario == aprendiz.id_usuario for u in disponibles)


def test_desmatricular_aprendiz(curso, aprendiz):
    ic = InscripcionController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    ic.desmatricular(aprendiz.id_usuario, curso.id_curso)

    cursos_del_aprendiz = ic.listar_cursos_matriculados(aprendiz.id_usuario)
    assert cursos_del_aprendiz == []


def test_aprendiz_no_matriculado_no_ve_el_curso(curso, aprendiz):
    """Un curso activo NO debe aparecer para un aprendiz que no fue matriculado en él."""
    ic = InscripcionController()
    assert curso.id_curso not in [c.id_curso for c in ic.listar_cursos_matriculados(aprendiz.id_usuario)]


def test_progreso_inicia_en_cero_al_matricular(curso, aprendiz):
    ic = InscripcionController()
    pc = ProgresoController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    assert pc.obtener_progreso(aprendiz.id_usuario, curso.id_curso) is None


def test_marcar_contenido_visto_actualiza_progreso(curso, aprendiz):
    ic = InscripcionController()
    ctrl = ContenidoController()
    pc = ProgresoController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    c1 = ctrl.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    c2 = ctrl.crear_contenido_texto(curso.id_curso, "Dos", "Texto con longitud suficiente para pasar.")

    assert pc.ya_visto(aprendiz.id_usuario, c1) is False

    progreso = pc.registrar_contenido_visto(aprendiz.id_usuario, c1)
    assert progreso.porcentaje_avance == 50.0
    assert progreso.estado == "EN_PROGRESO"
    assert pc.ya_visto(aprendiz.id_usuario, c1) is True

    progreso = pc.registrar_contenido_visto(aprendiz.id_usuario, c2)
    assert progreso.porcentaje_avance == 100.0
    assert progreso.estado == "COMPLETADO"


def test_desmarcar_contenido_visto_revierte_progreso(curso, aprendiz):
    ic = InscripcionController()
    ctrl = ContenidoController()
    pc = ProgresoController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    c1 = ctrl.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    c2 = ctrl.crear_contenido_texto(curso.id_curso, "Dos", "Texto con longitud suficiente para pasar.")

    pc.registrar_contenido_visto(aprendiz.id_usuario, c1)
    pc.registrar_contenido_visto(aprendiz.id_usuario, c2)

    progreso = pc.desregistrar_contenido_visto(aprendiz.id_usuario, c1)
    assert progreso.porcentaje_avance == 50.0
    assert progreso.estado == "EN_PROGRESO"
    assert pc.ya_visto(aprendiz.id_usuario, c1) is False
    assert pc.ya_visto(aprendiz.id_usuario, c2) is True


def test_historial_progreso_es_acumulado_no_decreciente(curso, aprendiz):
    ic = InscripcionController()
    ctrl = ContenidoController()
    pc = ProgresoController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    contenido = ctrl.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)

    serie = pc.historial_progreso_aprendiz(aprendiz.id_usuario)
    assert len(serie) >= 1
    valores = [valor for _fecha, valor in serie]
    assert valores == sorted(valores)
    assert all(0 <= v <= 100 for v in valores)
