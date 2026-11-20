"""El comité señaló que, fuera de la calificación de talleres (ver test_autorizacion_calificar.py),
no se había revisado si las demás operaciones administrativas de verdad exigen un rol de
administrador, o si solo estaban ocultas en la vista. Esta ronda agrega la misma verificación
de rol a cursos, contenidos, evaluaciones, guía, simulaciones, talleres, validación, matrícula
y usuarios, y aquí se confirma que un aprendiz (o nadie autenticado) no puede ejecutarlas."""
import pytest

from controller.contenido_controller import ContenidoController
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.guia_aprendizaje_controller import GuiaAprendizajeController
from controller.inscripcion_controller import InscripcionController
from controller.simulacion_controller import SimulacionController
from controller.taller_controller import TallerController
from controller.usuario_controller import UsuarioController
from controller.validacion_controller import ValidacionController
from utils.autorizacion import AccesoNoAutorizadoError


# -- Cursos -----------------------------------------------------------------------------------
def test_crear_curso_sin_actor_falla(admin):
    with pytest.raises(AccesoNoAutorizadoError):
        CursoController().crear_curso("Curso cualquiera", "Descripción", admin.id_usuario)


def test_crear_curso_con_aprendiz_como_actor_falla(aprendiz, admin):
    with pytest.raises(AccesoNoAutorizadoError):
        CursoController().crear_curso("Curso cualquiera", "Descripción", admin.id_usuario, usuario_actor=aprendiz)


# -- Contenidos ---------------------------------------------------------------------------------
def test_crear_contenido_texto_sin_actor_falla(curso):
    with pytest.raises(AccesoNoAutorizadoError):
        ContenidoController().crear_contenido_texto(
            curso.id_curso, "Titulo valido", "Texto con longitud suficiente para pasar."
        )


def test_crear_contenido_texto_con_aprendiz_como_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        ContenidoController().crear_contenido_texto(
            curso.id_curso, "Titulo valido", "Texto con longitud suficiente para pasar.", usuario_actor=aprendiz,
        )


# -- Evaluación final ---------------------------------------------------------------------------
def test_crear_evaluacion_final_sin_actor_falla(curso):
    with pytest.raises(AccesoNoAutorizadoError):
        EvaluacionController().crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.0, 2)


def test_crear_evaluacion_final_con_aprendiz_como_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        EvaluacionController().crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.0, 2, usuario_actor=aprendiz)


# -- Guía de aprendizaje ------------------------------------------------------------------------
def test_guardar_guia_sin_actor_falla(curso):
    with pytest.raises(AccesoNoAutorizadoError):
        GuiaAprendizajeController().guardar_guia(
            curso.id_curso, {"objetivo_general": "Objetivo general con longitud suficiente"}, ""
        )


def test_guardar_guia_con_aprendiz_como_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        GuiaAprendizajeController().guardar_guia(
            curso.id_curso, {"objetivo_general": "Objetivo general con longitud suficiente"}, "", usuario_actor=aprendiz,
        )


# -- Simulaciones -------------------------------------------------------------------------------
def test_crear_caso_simulacion_sin_actor_falla(curso):
    with pytest.raises(AccesoNoAutorizadoError):
        SimulacionController().crear_caso(
            curso.id_curso, "Caso", "Escenario clínico detallado de al menos 15 caracteres.", "Diagnóstico"
        )


def test_crear_caso_simulacion_con_aprendiz_como_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        SimulacionController().crear_caso(
            curso.id_curso, "Caso", "Escenario clínico detallado de al menos 15 caracteres.", "Diagnóstico",
            usuario_actor=aprendiz,
        )


# -- Talleres -------------------------------------------------------------------------------------
def test_crear_taller_sin_actor_falla(curso):
    with pytest.raises(AccesoNoAutorizadoError):
        TallerController().crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.")


def test_crear_taller_con_aprendiz_como_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        TallerController().crear_taller(
            curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=aprendiz,
        )


# -- Preguntas de validación de contenido --------------------------------------------------------
def test_crear_pregunta_validacion_sin_actor_falla(curso, admin):
    contenido = ContenidoController().crear_contenido_texto(
        curso.id_curso, "Contenido con preguntas", "Texto con longitud suficiente para pasar.", usuario_actor=admin,
    )
    with pytest.raises(AccesoNoAutorizadoError):
        ValidacionController().crear_pregunta(contenido, "¿Pregunta válida?", [("A", True), ("B", False)])


def test_crear_pregunta_validacion_con_aprendiz_como_actor_falla(curso, admin, aprendiz):
    contenido = ContenidoController().crear_contenido_texto(
        curso.id_curso, "Contenido con preguntas", "Texto con longitud suficiente para pasar.", usuario_actor=admin,
    )
    with pytest.raises(AccesoNoAutorizadoError):
        ValidacionController().crear_pregunta(
            contenido, "¿Pregunta válida?", [("A", True), ("B", False)], usuario_actor=aprendiz,
        )


# -- Matrícula --------------------------------------------------------------------------------
def test_matricular_sin_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        InscripcionController().matricular(aprendiz.id_usuario, curso.id_curso)


def test_matricular_con_aprendiz_como_actor_falla(curso, aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        InscripcionController().matricular(aprendiz.id_usuario, curso.id_curso, usuario_actor=aprendiz)


# -- Usuarios: eliminar (estrictamente administrador) ----------------------------------------
def test_eliminar_usuario_sin_actor_falla(aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        UsuarioController().eliminar_usuario(aprendiz.id_usuario)


def test_eliminar_usuario_con_aprendiz_como_actor_falla(aprendiz):
    with pytest.raises(AccesoNoAutorizadoError):
        UsuarioController().eliminar_usuario(aprendiz.id_usuario, usuario_actor=aprendiz)


# -- Usuarios: reglas duales (uno mismo o administrador) -------------------------------------
def test_actualizar_usuario_uno_mismo_no_necesita_ser_administrador(aprendiz):
    """Cualquier usuario puede editar su propio perfil sin ser administrador."""
    uc = UsuarioController()
    actualizado = uc.actualizar_usuario(
        aprendiz.id_usuario, "Nombre Actualizado", aprendiz.documento, aprendiz.correo, aprendiz.id_rol,
        activo=True, usuario_actor=aprendiz,
    )
    assert actualizado.nombre_completo == "Nombre Actualizado"


def test_actualizar_usuario_de_otro_sin_ser_administrador_falla(aprendiz, admin):
    """Un aprendiz no puede editar el perfil de otro usuario."""
    with pytest.raises(AccesoNoAutorizadoError):
        UsuarioController().actualizar_usuario(
            admin.id_usuario, admin.nombre_completo, admin.documento, admin.correo, admin.id_rol,
            activo=True, usuario_actor=aprendiz,
        )


def test_cambiar_contrasena_propia_no_necesita_ser_administrador(aprendiz):
    """Cambiar la propia contraseña no exige ser administrador (caso de Configuración)."""
    UsuarioController().cambiar_contrasena(aprendiz.id_usuario, "ClaveNueva2", usuario_actor=aprendiz)  # no debe lanzar


def test_cambiar_contrasena_de_otro_sin_ser_administrador_falla(aprendiz, admin):
    with pytest.raises(AccesoNoAutorizadoError):
        UsuarioController().cambiar_contrasena(admin.id_usuario, "ClaveNueva2", usuario_actor=aprendiz)


# -- Usuarios: crear_usuario (bootstrap del primer administrador) ----------------------------
def test_crear_usuario_sin_ningun_administrador_no_necesita_actor(id_rol_admin):
    """La ventana de 'crear el primer administrador' no tiene ningún usuario logueado todavía:
    debe seguir funcionando sin exigir un actor, mientras no exista ya un administrador activo."""
    uc = UsuarioController()
    assert uc.existe_administrador_activo() is False
    creado = uc.crear_usuario(
        "Primer Administrador", "1000000900", "primero@refrios.local", "primero.refrios", "ClaveInicial1", id_rol_admin,
    )
    assert creado.id_usuario is not None


def test_crear_usuario_con_un_administrador_ya_existente_exige_actor(admin, id_rol_aprendiz):
    """Una vez que ya existe un administrador, crear a cualquier otro usuario exige serlo."""
    with pytest.raises(AccesoNoAutorizadoError):
        UsuarioController().crear_usuario(
            "Otro Usuario", "1000000901", "otro@refrios.local", "otro.refrios", "ClaveInicial1", id_rol_aprendiz,
        )
