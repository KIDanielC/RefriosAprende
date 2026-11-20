"""Pruebas de la arquitectura extendida de cursos: prerrequisitos entre cursos,
aprendizaje secuencial (contenido bloqueado) y certificado de finalización."""
import pytest

from controller.certificado_controller import CursoNoCompletadoError, CertificadoController
from controller.contenido_controller import ContenidoController
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.inscripcion_controller import PrerrequisitosIncompletosError, InscripcionController
from controller.progreso_controller import ProgresoController


def _publicar(cc, curso, admin):
    return cc.actualizar_curso(
        curso.id_curso, curso.nombre_curso, curso.descripcion, admin.id_usuario, "ACTIVO", usuario_actor=admin,
    )


# ---------------------------------------------------------------------
# Prerrequisitos entre cursos
# ---------------------------------------------------------------------
def test_matricular_sin_prerrequisito_completado_falla(curso, aprendiz, admin):
    cc = CursoController()
    ic = InscripcionController()

    curso_basico = _publicar(cc, cc.crear_curso("Curso Básico", "Fundamentos", admin.id_usuario, usuario_actor=admin), admin)
    cc.guardar_prerrequisitos(curso.id_curso, [curso_basico.id_curso], usuario_actor=admin)

    with pytest.raises(PrerrequisitosIncompletosError):
        ic.matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)


def test_matricular_con_prerrequisito_completado_funciona(curso, aprendiz, admin):
    cc = CursoController()
    ic = InscripcionController()
    pc = ProgresoController()
    contenido_controlador = ContenidoController()

    curso_basico = _publicar(cc, cc.crear_curso("Curso Básico", "Fundamentos", admin.id_usuario, usuario_actor=admin), admin)
    contenido = contenido_controlador.crear_contenido_texto(
        curso_basico.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación.",
        usuario_actor=admin,
    )
    ic.matricular(aprendiz.id_usuario, curso_basico.id_curso, usuario_actor=admin)
    progreso = pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)
    assert progreso.estado == "COMPLETADO"  # sin evaluación final, ver todo el contenido ya completa el curso

    cc.guardar_prerrequisitos(curso.id_curso, [curso_basico.id_curso], usuario_actor=admin)
    ic.matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)  # no debe lanzar
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
        aprendizaje_secuencial=True, usuario_actor=admin,
    )
    contenido_1 = contenido_controlador.crear_contenido_texto(
        curso_secuencial.id_curso, "Primero", "Texto con longitud suficiente para pasar la validación.",
        usuario_actor=admin,
    )
    contenido_2 = contenido_controlador.crear_contenido_texto(
        curso_secuencial.id_curso, "Segundo", "Texto con longitud suficiente para pasar la validación.",
        usuario_actor=admin,
    )

    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_1, curso_secuencial) is False
    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_2, curso_secuencial) is True

    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido_1)
    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_2, curso_secuencial) is False


def test_contenido_no_se_bloquea_si_curso_no_es_secuencial(curso, aprendiz, admin):
    pc = ProgresoController()
    contenido_controlador = ContenidoController()
    contenido_1 = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Primero", "Texto con longitud suficiente para pasar la validación.", usuario_actor=admin,
    )
    contenido_2 = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Segundo", "Texto con longitud suficiente para pasar la validación.", usuario_actor=admin,
    )
    assert pc.contenido_bloqueado(aprendiz.id_usuario, contenido_2, curso) is False


# ---------------------------------------------------------------------
# Certificado de finalización
# ---------------------------------------------------------------------
def test_certificado_falla_si_curso_no_completado(curso, aprendiz):
    certificado_controlador = CertificadoController()
    with pytest.raises(CursoNoCompletadoError):
        certificado_controlador.obtener_datos_certificado(aprendiz, curso)


def test_certificado_se_genera_cuando_el_curso_esta_completado(curso, aprendiz, admin):
    pc = ProgresoController()
    contenido_controlador = ContenidoController()
    certificado_controlador = CertificadoController()

    contenido = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación.",
        usuario_actor=admin,
    )
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)

    datos = certificado_controlador.obtener_datos_certificado(aprendiz, curso)
    assert datos["nombre_aprendiz"] == aprendiz.nombre_completo
    assert datos["nombre_curso"] == curso.nombre_curso
    assert datos["nota_obtenida"] is None  # este curso no tiene evaluación final


def test_exportar_certificado_falla_si_curso_no_completado(curso, aprendiz, tmp_path):
    certificado_controlador = CertificadoController()
    with pytest.raises(CursoNoCompletadoError):
        certificado_controlador.exportar_certificado(aprendiz, curso, str(tmp_path / "certificado.pdf"))
    assert not (tmp_path / "certificado.pdf").exists()


def test_exportar_certificado_crea_un_pdf_valido(curso, aprendiz, admin, tmp_path):
    pc = ProgresoController()
    contenido_controlador = ContenidoController()
    certificado_controlador = CertificadoController()

    contenido = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación.",
        usuario_actor=admin,
    )
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)

    ruta_destino = tmp_path / "certificado.pdf"
    ruta_devuelta = certificado_controlador.exportar_certificado(aprendiz, curso, str(ruta_destino))

    assert ruta_devuelta == str(ruta_destino)
    assert ruta_destino.is_file()
    with open(ruta_destino, "rb") as archivo:
        assert archivo.read(4) == b"%PDF"


def test_dibujar_certificado_funciona_sin_duracion_ni_nota_ni_competencias():
    certificado_controlador = CertificadoController()
    datos = {
        "nombre_aprendiz": "Aprendiz de Prueba",
        "documento": "1000000002",
        "nombre_curso": "Curso de Prueba",
        "nombre_instructor": "Admin de Prueba",
        "nombre_emisor": "Refrios Aprende",
        "duracion_horas": None,
        "nota_obtenida": None,
        "tipo_participacion": "Participación completa de los contenidos del curso (sin evaluación obligatoria).",
        "competencias": None,
        "fecha_finalizacion": "01/01/2026",
        "fecha_emision": "01/01/2026",
        "codigo_validacion": "AAAA-BBBB-CCCC-DDDD",
    }
    imagen = certificado_controlador._dibujar_certificado(datos)
    assert imagen.size == (1754, 1240)


def test_dibujar_certificado_funciona_con_duracion_nota_y_competencias():
    certificado_controlador = CertificadoController()
    datos = {
        "nombre_aprendiz": "Aprendiz de Prueba",
        "documento": "1000000002",
        "nombre_curso": "Curso de Prueba",
        "nombre_instructor": "Admin de Prueba",
        "nombre_emisor": "Refrios Aprende",
        "duracion_horas": 20,
        "nota_obtenida": 4.5,
        "tipo_participacion": "Finalización mediante evaluación final aprobada (nota 4.5 / 5.0).",
        "competencias": "Diagnóstico de fallas eléctricas y mecánicas en unidades condensadoras.",
        "fecha_finalizacion": "01/01/2026",
        "fecha_emision": "02/01/2026",
        "codigo_validacion": "AAAA-BBBB-CCCC-DDDD",
    }
    imagen = certificado_controlador._dibujar_certificado(datos)
    assert imagen.size == (1754, 1240)
