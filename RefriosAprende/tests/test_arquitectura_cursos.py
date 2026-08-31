"""Pruebas de las mejoras arquitectónicas de Sprint 4: prerrequisitos entre cursos,
aprendizaje secuencial (contenido bloqueado) y certificado de finalización."""
import pytest

from controller.certificado_controller import CertificadoController, CursoNoCompletadoError
from controller.contenido_controller import ContenidoController
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.inscripcion_controller import InscripcionController, PrerrequisitosIncompletosError
from controller.progreso_controller import ProgresoController


def _publicar(cc, curso, admin):
    return cc.actualizar_curso(curso.id_curso, curso.nombre_curso, curso.descripcion, admin.id_usuario, "ACTIVO")


# ---------------------------------------------------------------------
# Prerrequisitos entre cursos
# ---------------------------------------------------------------------
def test_matricular_sin_prerrequisito_completado_falla(curso, aprendiz, admin):
    cc = CursoController()
    ic = InscripcionController()

    curso_basico = _publicar(cc, cc.crear_curso("Curso Básico", "Fundamentos", admin.id_usuario), admin)
    cc.guardar_prerrequisitos(curso.id_curso, [curso_basico.id_curso])

    with pytest.raises(PrerrequisitosIncompletosError):
        ic.matricular(aprendiz.id_usuario, curso.id_curso)


def test_matricular_con_prerrequisito_completado_funciona(curso, aprendiz, admin):
    cc = CursoController()
    ic = InscripcionController()
    pc = ProgresoController()
    contenido_controlador = ContenidoController()

    curso_basico = _publicar(cc, cc.crear_curso("Curso Básico", "Fundamentos", admin.id_usuario), admin)
    contenido = contenido_controlador.crear_contenido_texto(
        curso_basico.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación."
    )
    ic.matricular(aprendiz.id_usuario, curso_basico.id_curso)
    progreso = pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)
    assert progreso.estado == "COMPLETADO"  # sin evaluación final, ver todo el contenido ya completa el curso

    cc.guardar_prerrequisitos(curso.id_curso, [curso_basico.id_curso])
    ic.matricular(aprendiz.id_usuario, curso.id_curso)  # no debe lanzar
    assert curso.id_curso in [c.id_curso for c in ic.listar_cursos_matriculados(aprendiz.id_usuario)]


def test_prerrequisitos_pendientes_vacio_sin_prerrequisitos(curso, aprendiz):
    ic = InscripcionController()
    assert ic.prerrequisitos_pendientes(aprendiz.id_usuario, curso.id_curso) == []


# ---------------------------------------------------------------------
# Aprendizaje secuencial (contenido bloqueado)
# ---------------------------------------------------------------------
def test_contenido_bloqueado_hasta_completar_el_anterior(curso, aprendiz, admin):
    cc = CursoController()
    pc = ProgresoController()
    contenido_controlador = ContenidoController()

    curso_secuencial = cc.actualizar_curso(
        curso.id_curso, curso.nombre_curso, curso.descripcion, admin.id_usuario, "ACTIVO",
        aprendizaje_secuencial=True,
    )
    contenido_1 = contenido_controlador.crear_contenido_texto(
        curso_secuencial.id_curso, "Primero", "Texto con longitud suficiente para pasar la validación."
    )
    contenido_2 = contenido_controlador.crear_contenido_texto(
        curso_secuencial.id_curso, "Segundo", "Texto con longitud suficiente para pasar la validación."
    )

    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_1, curso_secuencial) is False
    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_2, curso_secuencial) is True

    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido_1)
    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_2, curso_secuencial) is False


def test_contenido_no_se_bloquea_si_curso_no_es_secuencial(curso, aprendiz):
    pc = ProgresoController()
    contenido_controlador = ContenidoController()
    contenido_1 = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Primero", "Texto con longitud suficiente para pasar la validación."
    )
    contenido_2 = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Segundo", "Texto con longitud suficiente para pasar la validación."
    )
    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_2, curso) is False


# ---------------------------------------------------------------------
# Certificado de finalización
# ---------------------------------------------------------------------
def test_certificado_falla_si_curso_no_completado(curso, aprendiz):
    certificado_controlador = CertificadoController()
    with pytest.raises(CursoNoCompletadoError):
        certificado_controlador.obtener_datos_certificado(aprendiz, curso)


def test_certificado_se_genera_cuando_el_curso_esta_completado(curso, aprendiz):
    pc = ProgresoController()
    contenido_controlador = ContenidoController()
    certificado_controlador = CertificadoController()

    contenido = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación."
    )
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)

    datos = certificado_controlador.obtener_datos_certificado(aprendiz, curso)
    assert datos["nombre_aprendiz"] == aprendiz.nombre_completo
    assert datos["nombre_curso"] == curso.nombre_curso
    assert datos["nota_obtenida"] is None  # este curso no tiene evaluación final
