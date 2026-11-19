"""El comité señaló que dashboard_view.py, evaluaciones_screen.py y curso_aprendiz_screen.py
consultaban ResultadoDAO directamente, en contra de la arquitectura MVC descrita en la
monografía (la vista solo debe hablar con el controlador). Esta prueba falla si alguna vista
vuelve a importar un DAO."""
import pathlib
import re

_DIR_VISTAS = pathlib.Path(__file__).resolve().parent.parent / "view"
_PATRON_IMPORT_DAO = re.compile(r"^\s*(?:from|import)\s+model\.dao", re.MULTILINE)


def test_ninguna_vista_importa_un_dao():
    archivos_con_import_dao = []
    for archivo in _DIR_VISTAS.rglob("*.py"):
        codigo_fuente = archivo.read_text(encoding="utf-8")
        if _PATRON_IMPORT_DAO.search(codigo_fuente):
            archivos_con_import_dao.append(str(archivo.relative_to(_DIR_VISTAS)))

    assert archivos_con_import_dao == [], (
        f"Estas vistas importan un DAO directamente (deben pasar por un controlador): {archivos_con_import_dao}"
    )


def test_evaluacion_controller_expone_aprobo_evaluacion(curso, aprendiz):
    from controller.evaluacion_controller import EvaluacionController

    controlador = EvaluacionController()
    evaluacion = controlador.crear_evaluacion_final(curso.id_curso, "Evaluación final", 3.0, 2)
    assert controlador.aprobo_evaluacion(aprendiz.id_usuario, evaluacion.id_evaluacion) is False
