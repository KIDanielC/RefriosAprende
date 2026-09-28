from datetime import datetime, timedelta

from controller.contenido_controller import ContenidoController
from controller.curso_controller import CursoController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.reporte_controller import (
    ReporteController,
    SEMAFORO_AMARILLO,
    SEMAFORO_ROJO,
    SEMAFORO_VERDE,
    UMBRAL_DIAS_RIESGO,
)
from controller.tiempo_uso_controller import TiempoUsoController
from database.connection import ConexionBD


def _backdatear_matricula(id_usuario, id_curso, dias):
    conexion = ConexionBD()
    cursor = conexion.obtener_cursor()
    fecha = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE inscripciones SET fecha_inscripcion = ? WHERE id_usuario = ? AND id_curso = ?",
        (fecha, id_usuario, id_curso),
    )
    conexion.confirmar()


# -- Tiempo de uso real ---------------------------------------------------------------------
def test_tiempo_uso_sin_registros_es_cero(curso, aprendiz):
    tc = TiempoUsoController()
    assert tc.horas_acumuladas(aprendiz.id_usuario, curso.id_curso) == 0.0


def test_tiempo_uso_se_acumula_en_horas(curso, aprendiz):
    tc = TiempoUsoController()
    id_registro = tc.iniciar_sesion_curso(aprendiz.id_usuario, curso.id_curso)
    tc.actualizar_sesion_curso(id_registro, 3600)
    assert tc.horas_acumuladas(aprendiz.id_usuario, curso.id_curso) == 1.0


def test_tiempo_uso_de_varias_visitas_se_suma(curso, aprendiz):
    tc = TiempoUsoController()
    primera = tc.iniciar_sesion_curso(aprendiz.id_usuario, curso.id_curso)
    tc.actualizar_sesion_curso(primera, 1800)
    segunda = tc.iniciar_sesion_curso(aprendiz.id_usuario, curso.id_curso)
    tc.actualizar_sesion_curso(segunda, 1800)
    assert tc.horas_acumuladas(aprendiz.id_usuario, curso.id_curso) == 1.0


# -- Riesgo por poco avance en mucho tiempo -------------------------------------------------
def test_recien_matriculado_no_esta_en_riesgo(curso, aprendiz):
    ic = InscripcionController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)

    rc = ReporteController()
    fila = next(
        f for f in rc.avance_por_estudiante(curso.id_instructor) if f["nombre_estudiante"] == aprendiz.nombre_completo
    )
    assert fila["en_riesgo"] is False
    assert fila["semaforo"] != SEMAFORO_ROJO


def test_estudiante_en_riesgo_por_poco_avance_y_mucho_tiempo_matriculado(curso, aprendiz):
    ic = InscripcionController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    _backdatear_matricula(aprendiz.id_usuario, curso.id_curso, UMBRAL_DIAS_RIESGO + 5)

    rc = ReporteController()
    en_riesgo = rc.estudiantes_en_riesgo(curso.id_instructor)
    assert any(f["nombre_estudiante"] == aprendiz.nombre_completo for f in en_riesgo)


def test_estudiante_no_en_riesgo_si_ya_completo_el_curso(curso, aprendiz):
    ic = InscripcionController()
    cc = ContenidoController()
    pc = ProgresoController()

    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    _backdatear_matricula(aprendiz.id_usuario, curso.id_curso, UMBRAL_DIAS_RIESGO + 5)
    contenido = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)

    rc = ReporteController()
    en_riesgo = rc.estudiantes_en_riesgo(curso.id_instructor)
    assert not any(f["nombre_estudiante"] == aprendiz.nombre_completo for f in en_riesgo)


def test_estudiantes_en_riesgo_no_incluye_otros_instructores(curso, aprendiz):
    """El panel de riesgo de un instructor no debe mostrar estudiantes de cursos ajenos."""
    rc = ReporteController()
    otro_id_instructor = curso.id_instructor + 999
    assert rc.estudiantes_en_riesgo(otro_id_instructor) == []


# -- Semáforo de seguimiento (avance + horas de uso vs. duración estimada) ------------------
def test_semaforo_amarillo_por_pocas_horas_de_uso_frente_a_lo_estimado(curso, aprendiz):
    ic = InscripcionController()
    cc = ContenidoController()
    pc = ProgresoController()
    gc = GuiaAprendizajeController()

    gc.guardar_guia(curso.id_curso, {"objetivo_general": "Objetivo general con longitud suficiente"}, "10")
    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    c1 = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    cc.crear_contenido_texto(curso.id_curso, "Dos", "Texto con longitud suficiente para pasar.")
    pc.registrar_contenido_visto(aprendiz.id_usuario, c1)  # 50%, EN_PROGRESO, sin horas de uso registradas

    rc = ReporteController()
    fila = next(
        f for f in rc.avance_por_estudiante(curso.id_instructor) if f["nombre_estudiante"] == aprendiz.nombre_completo
    )
    assert fila["en_riesgo"] is False
    assert fila["semaforo"] == SEMAFORO_AMARILLO


def test_semaforo_verde_cuando_las_horas_de_uso_alcanzan_lo_estimado(curso, aprendiz):
    ic = InscripcionController()
    cc = ContenidoController()
    pc = ProgresoController()
    gc = GuiaAprendizajeController()
    tc = TiempoUsoController()

    gc.guardar_guia(curso.id_curso, {"objetivo_general": "Objetivo general con longitud suficiente"}, "1")
    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    c1 = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    cc.crear_contenido_texto(curso.id_curso, "Dos", "Texto con longitud suficiente para pasar.")
    pc.registrar_contenido_visto(aprendiz.id_usuario, c1)

    id_registro = tc.iniciar_sesion_curso(aprendiz.id_usuario, curso.id_curso)
    tc.actualizar_sesion_curso(id_registro, 3600)  # 1 hora, iguala la duración estimada

    rc = ReporteController()
    fila = next(
        f for f in rc.avance_por_estudiante(curso.id_instructor) if f["nombre_estudiante"] == aprendiz.nombre_completo
    )
    assert fila["semaforo"] == SEMAFORO_VERDE


def test_semaforo_verde_cuando_el_curso_esta_completado_sin_importar_las_horas(curso, aprendiz):
    ic = InscripcionController()
    cc = ContenidoController()
    pc = ProgresoController()
    gc = GuiaAprendizajeController()

    gc.guardar_guia(curso.id_curso, {"objetivo_general": "Objetivo general con longitud suficiente"}, "100")
    ic.matricular(aprendiz.id_usuario, curso.id_curso)
    contenido = cc.crear_contenido_texto(curso.id_curso, "Uno", "Texto con longitud suficiente para pasar.")
    pc.registrar_contenido_visto(aprendiz.id_usuario, contenido)  # unico contenido -> COMPLETADO

    rc = ReporteController()
    fila = next(
        f for f in rc.avance_por_estudiante(curso.id_instructor) if f["nombre_estudiante"] == aprendiz.nombre_completo
    )
    assert fila["semaforo"] == SEMAFORO_VERDE


def test_avance_por_estudiante_filtra_por_instructor(curso, aprendiz):
    """Solo debe incluir cursos donde el usuario figura como instructor."""
    ic = InscripcionController()
    ic.matricular(aprendiz.id_usuario, curso.id_curso)

    rc = ReporteController()
    otro_id_instructor = curso.id_instructor + 999
    assert rc.avance_por_estudiante(otro_id_instructor) == []
    assert len(rc.avance_por_estudiante(curso.id_instructor)) == 1


def test_listar_cursos_por_instructor(curso):
    cc = CursoController()
    cursos = cc.listar_cursos_por_instructor(curso.id_instructor)
    assert any(c.id_curso == curso.id_curso for c in cursos)
