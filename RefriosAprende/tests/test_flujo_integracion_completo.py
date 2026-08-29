"""Prueba de integración de punta a punta: reproduce el recorrido completo de un aprendiz
por un curso, y verifica que todos los módulos (matrícula, contenidos, progreso, evaluación,
reportes, dashboard) queden consistentes entre sí al final."""
from controller.contenido_controller import ContenidoController
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.reporte_controller import ReporteController


def test_flujo_completo_aprendiz_aprueba_el_curso(admin, aprendiz):
    curso_controlador = CursoController()
    contenido_controlador = ContenidoController()
    inscripcion_controlador = InscripcionController()
    progreso_controlador = ProgresoController()
    evaluacion_controlador = EvaluacionController()
    reporte_controlador = ReporteController()

    # 1. El administrador crea un curso con dos contenidos y una evaluación final.
    curso = curso_controlador.crear_curso("Refrigerantes R134a", "Curso integral", admin.id_usuario)
    contenido_1 = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Propiedades del refrigerante", "Texto con longitud suficiente para pasar la validación."
    )
    contenido_2 = contenido_controlador.crear_contenido_texto(
        curso.id_curso, "Presiones de operación", "Texto con longitud suficiente para pasar la validación."
    )
    evaluacion = evaluacion_controlador.crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.5, 2)
    pregunta = evaluacion_controlador.crear_pregunta(
        evaluacion.id_evaluacion, "¿Cuál es la presión de baja típica?",
        [("Entre 25 y 45 PSI", True), ("Entre 100 y 150 PSI", False)],
    )

    # 2. Antes de matricular, el aprendiz no debe ver el curso.
    assert curso.id_curso not in [c.id_curso for c in inscripcion_controlador.listar_cursos_matriculados(aprendiz.id_usuario)]

    # 3. El administrador matricula al aprendiz.
    inscripcion_controlador.matricular(aprendiz.id_usuario, curso.id_curso)
    assert curso.id_curso in [c.id_curso for c in inscripcion_controlador.listar_cursos_matriculados(aprendiz.id_usuario)]

    # 4. El aprendiz aún no ha marcado nada como visto: progreso 0.
    assert progreso_controlador.obtener_progreso(aprendiz.id_usuario, curso.id_curso) is None

    # 5. El aprendiz marca "Ya lo vi" en el primer contenido.
    progreso = progreso_controlador.registrar_contenido_visto(aprendiz.id_usuario, contenido_1)
    assert progreso.porcentaje_avance == 50.0
    assert progreso.estado == "EN_PROGRESO"

    # 6. El aprendiz marca el segundo contenido.
    progreso = progreso_controlador.registrar_contenido_visto(aprendiz.id_usuario, contenido_2)
    assert progreso.porcentaje_avance == 100.0
    # Vio todo el contenido, pero aún no aprueba la evaluación final -> no está completado del todo.
    assert progreso.estado == "EN_PROGRESO"

    # 7. El aprendiz presenta y aprueba la evaluación final.
    id_opcion_correcta = pregunta.opcion_correcta().id_opcion
    resultado = evaluacion_controlador.presentar_evaluacion(
        aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: id_opcion_correcta}
    )
    assert resultado.aprobado is True

    # 8. Ahora sí: contenido visto al 100% + evaluación aprobada -> curso COMPLETADO.
    progreso_final = progreso_controlador.obtener_progreso(aprendiz.id_usuario, curso.id_curso)
    assert progreso_final.porcentaje_avance == 100.0
    assert progreso_final.estado == "COMPLETADO"

    # 9. El reporte administrativo debe reflejar exactamente este resultado.
    fila_reporte = next(
        f for f in reporte_controlador.detalle_por_curso() if f["nombre_curso"] == curso.nombre_curso
    )
    assert fila_reporte["aprendices_inscritos"] == 1
    assert fila_reporte["progreso_promedio"] == 100.0
    assert fila_reporte["evaluaciones_presentadas"] == 1
    assert fila_reporte["porcentaje_aprobacion"] == 100.0

    # 10. El historial acumulado de progreso del aprendiz llega hasta 100%.
    serie = progreso_controlador.historial_progreso_aprendiz(aprendiz.id_usuario)
    assert serie[-1][1] == 100.0
