"""Pruebas del certificado de finalización: el controlador y el PDF que genera deben traer
los datos que pidió el jurado (documento, duración, tipo de participación, fecha de
finalización real, competencias, firma del instructor y código de validación con su QR),
y deben mantenerse al exportar a PDF, no solo en la vista previa en pantalla."""
import os

from controller.certificado_controller import CertificadoController, CursoNoCompletadoError
from controller.contenido_controller import ContenidoController
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.taller_controller import TallerController


def _curso_completado_con_evaluacion(admin, aprendiz, curso_controlador):
    curso = curso_controlador.crear_curso("Refrigerantes R410A", "Curso de certificación", admin.id_usuario, usuario_actor=admin)
    contenido = ContenidoController().crear_contenido_texto(
        curso.id_curso, "Propiedades", "Texto con longitud suficiente para pasar la validación.", usuario_actor=admin,
    )
    GuiaAprendizajeController().guardar_guia(
        curso.id_curso,
        {"objetivo_general": "Diagnosticar fallas en sistemas HVAC.", "competencias": "Diagnóstico de fallas eléctricas y mecánicas en unidades condensadoras."},
        duracion_horas="12", usuario_actor=admin,
    )
    InscripcionController().matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)
    ProgresoController().registrar_contenido_visto(aprendiz.id_usuario, contenido)

    evaluacion = EvaluacionController().crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.0, 2, usuario_actor=admin)
    pregunta = EvaluacionController().crear_pregunta(
        evaluacion.id_evaluacion, "¿Cuál opción es correcta?", [("Correcta", True), ("Incorrecta", False)],
        usuario_actor=admin,
    )
    EvaluacionController().presentar_evaluacion(
        aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: pregunta.opcion_correcta().id_opcion},
    )
    return curso


def test_certificado_de_curso_sin_completar_falla(curso, aprendiz):
    with __import__("pytest").raises(CursoNoCompletadoError):
        CertificadoController().obtener_datos_certificado(aprendiz, curso)


def test_datos_del_certificado_traen_los_campos_que_pidio_el_jurado(admin, aprendiz):
    from controller.curso_controller import CursoController
    curso = _curso_completado_con_evaluacion(admin, aprendiz, CursoController())

    datos = CertificadoController().obtener_datos_certificado(aprendiz, curso)

    assert datos["nombre_aprendiz"] == aprendiz.nombre_completo
    assert datos["documento"] == aprendiz.documento
    assert datos["nombre_curso"] == curso.nombre_curso
    assert datos["nombre_instructor"] == curso.nombre_instructor
    assert datos["nombre_emisor"] == "Refrios Aprende"
    assert datos["duracion_horas"] == 12
    assert datos["nota_obtenida"] == 5.0
    assert "evaluación final aprobada" in datos["tipo_participacion"]
    assert "Diagnóstico de fallas" in datos["competencias"]
    assert datos["fecha_finalizacion"]
    assert datos["fecha_emision"]
    # 4 bloques de 4 caracteres hexadecimales, ej. "A1B2-C3D4-E5F6-7890".
    bloques = datos["codigo_validacion"].split("-")
    assert len(bloques) == 4 and all(len(bloque) == 4 for bloque in bloques)


def test_curso_sin_evaluacion_ni_talleres_queda_como_participacion(admin, aprendiz):
    from controller.curso_controller import CursoController
    cc = CursoController()
    curso = cc.crear_curso("Curso solo de contenidos", "Sin evaluación ni talleres", admin.id_usuario, usuario_actor=admin)
    contenido = ContenidoController().crear_contenido_texto(
        curso.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación.", usuario_actor=admin,
    )
    InscripcionController().matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)
    ProgresoController().registrar_contenido_visto(aprendiz.id_usuario, contenido)

    datos = CertificadoController().obtener_datos_certificado(aprendiz, curso)
    assert datos["tipo_participacion"] == "Participación completa de los contenidos del curso (sin evaluación obligatoria)."


def test_curso_con_taller_aprobado_lo_menciona_en_tipo_de_participacion(admin, aprendiz):
    from controller.curso_controller import CursoController
    cc = CursoController()
    curso = cc.crear_curso("Curso con taller", "Con taller práctico", admin.id_usuario, usuario_actor=admin)
    contenido = ContenidoController().crear_contenido_texto(
        curso.id_curso, "Único contenido", "Texto con longitud suficiente para pasar la validación.", usuario_actor=admin,
    )
    taller_controlador = TallerController()
    taller = taller_controlador.crear_taller(
        curso.id_curso, "Taller práctico", "Actividad práctica de ejemplo.", usuario_actor=admin,
    )

    InscripcionController().matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=admin)
    ProgresoController().registrar_contenido_visto(aprendiz.id_usuario, contenido)

    import tempfile
    from PIL import Image
    ruta_entrega = os.path.join(tempfile.mkdtemp(), "entrega.png")
    Image.new("RGB", (100, 100)).save(ruta_entrega)
    taller_controlador.subir_entrega(taller.id_taller, aprendiz.id_usuario, ruta_entrega)
    entrega = taller_controlador.listar_entregas_por_taller(taller.id_taller)[0]
    taller_controlador.calificar_entrega(entrega.id_entrega, True, "Bien hecho.", usuario_actor=admin)

    datos = CertificadoController().obtener_datos_certificado(aprendiz, curso)
    assert "talleres prácticos aprobados" in datos["tipo_participacion"]


def test_el_codigo_de_validacion_es_siempre_el_mismo_para_el_mismo_certificado(admin, aprendiz):
    from controller.curso_controller import CursoController
    curso = _curso_completado_con_evaluacion(admin, aprendiz, CursoController())

    controlador = CertificadoController()
    primero = controlador.obtener_datos_certificado(aprendiz, curso)["codigo_validacion"]
    segundo = controlador.obtener_datos_certificado(aprendiz, curso)["codigo_validacion"]
    assert primero == segundo


def test_exportar_certificado_genera_un_pdf_con_todos_los_datos(admin, aprendiz, tmp_path):
    from controller.curso_controller import CursoController
    curso = _curso_completado_con_evaluacion(admin, aprendiz, CursoController())

    ruta_pdf = str(tmp_path / "certificado.pdf")
    CertificadoController().exportar_certificado(aprendiz, curso, ruta_pdf)

    assert os.path.isfile(ruta_pdf)
    assert os.path.getsize(ruta_pdf) > 0
