"""El manual técnico y el de usuario describen un procedimiento de respaldo y restauración
que nunca se había probado de verdad sobre datos reales: usuarios, un curso, una nota de
evaluación y una entrega de taller con su archivo adjunto."""
import os
import shutil
import sqlite3

import controller.taller_controller as taller_controller_module
import database.connection as connection_module
from controller.contenido_controller import ContenidoController
from controller.evaluacion_controller import EvaluacionController
from controller.inscripcion_controller import InscripcionController
from controller.taller_controller import TallerController
from utils.respaldo import crear_respaldo, leer_metadata_respaldo, restaurar_respaldo


def test_respaldo_y_restauracion_conservan_los_datos_reales(tmp_path, monkeypatch, admin, aprendiz, curso):
    carpeta_datos = tmp_path / "datos_app"
    ruta_bd = carpeta_datos / "database" / "refrios.db"
    ruta_entregas = carpeta_datos / "resources" / "entregas"

    # Traslada la base de datos (ya con admin/aprendiz/curso de las fixtures) a la
    # estructura real de carpetas (database/ + resources/...) y apunta ahí los controladores
    # que tocan archivos, en vez de a la carpeta real del proyecto.
    os.makedirs(os.path.dirname(ruta_bd), exist_ok=True)
    shutil.copyfile(connection_module.DATABASE_PATH, ruta_bd)
    connection_module.ConexionBD._instancia = None
    monkeypatch.setattr(connection_module, "DATABASE_PATH", str(ruta_bd))
    monkeypatch.setattr(taller_controller_module, "BASE_DIR", str(carpeta_datos))
    monkeypatch.setattr(taller_controller_module, "ENTREGAS_DIR", str(ruta_entregas))

    InscripcionController().matricular(aprendiz.id_usuario, curso.id_curso)
    ContenidoController().crear_contenido_texto(curso.id_curso, "Introducción", "Texto de ejemplo.")

    evaluacion_controlador = EvaluacionController()
    evaluacion = evaluacion_controlador.crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.0, 1)
    pregunta = evaluacion_controlador.crear_pregunta(
        evaluacion.id_evaluacion, "¿Cuál opción es correcta?", [("Correcta", True), ("Incorrecta", False)]
    )
    resultado = evaluacion_controlador.presentar_evaluacion(
        aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: pregunta.opcion_correcta().id_opcion},
    )
    assert resultado.aprobado is True

    taller_controlador = TallerController()
    taller = taller_controlador.crear_taller(curso.id_curso, "Taller de prueba", "Descripción suficientemente larga.")
    archivo_adjunto = tmp_path / "entrega_original.png"
    archivo_adjunto.write_bytes(b"contenido real de una entrega de taller")
    taller_controlador.subir_entrega(taller.id_taller, aprendiz.id_usuario, str(archivo_adjunto))

    ruta_zip = tmp_path / "respaldo.zip"
    crear_respaldo(str(carpeta_datos), str(ruta_zip))

    metadata = leer_metadata_respaldo(str(ruta_zip))
    assert metadata["version_app"]
    assert metadata["fecha"]

    # "La borra": se pierde la carpeta de datos por completo (reinstalación fallida, disco
    # dañado, error humano...). Hay que cerrar la conexión (no solo olvidar la instancia):
    # en Windows, SQLite mantiene el archivo abierto y shutil.rmtree no podría borrarlo.
    connection_module.ConexionBD().cerrar()
    shutil.rmtree(carpeta_datos)
    assert not carpeta_datos.exists()

    restaurar_respaldo(str(ruta_zip), str(carpeta_datos))

    conexion = sqlite3.connect(str(ruta_bd))
    try:
        nombres_usuarios = {
            fila[0] for fila in conexion.execute("SELECT nombre_completo FROM usuarios").fetchall()
        }
        assert admin.nombre_completo in nombres_usuarios
        assert aprendiz.nombre_completo in nombres_usuarios

        nombre_curso_restaurado = conexion.execute(
            "SELECT nombre_curso FROM cursos WHERE id_curso = ?", (curso.id_curso,)
        ).fetchone()[0]
        assert nombre_curso_restaurado == curso.nombre_curso

        nota_restaurada = conexion.execute(
            "SELECT nota_obtenida FROM resultados WHERE id_usuario = ? AND id_evaluacion = ?",
            (aprendiz.id_usuario, evaluacion.id_evaluacion),
        ).fetchone()
        assert nota_restaurada is not None

        entrega_restaurada = conexion.execute(
            "SELECT ruta_archivo FROM entregas_taller WHERE id_taller = ? AND id_usuario = ?",
            (taller.id_taller, aprendiz.id_usuario),
        ).fetchone()
        assert entrega_restaurada is not None
    finally:
        conexion.close()

    archivos_restaurados = os.listdir(ruta_entregas)
    assert len(archivos_restaurados) == 1
    ruta_entrega_restaurada = ruta_entregas / archivos_restaurados[0]
    assert ruta_entrega_restaurada.read_bytes() == b"contenido real de una entrega de taller"

    connection_module.ConexionBD._instancia = None
