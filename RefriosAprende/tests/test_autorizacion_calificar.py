"""El comité pidió revisar que las operaciones sensibles comprueben el rol de quien las
ejecuta, no solo que la vista oculte el botón. Calificar una entrega de taller es la
operación que se protegió en esta ronda (ver utils/autorizacion.py)."""
import pytest

from controller.taller_controller import TallerController
from utils.autorizacion import AccesoNoAutorizadoError


def _crear_archivo_de_prueba(tmp_path, nombre="entrega.png") -> str:
    ruta = tmp_path / nombre
    ruta.write_bytes(b"contenido de prueba")
    return str(ruta)


def test_calificar_entrega_sin_actor_falla(curso, aprendiz, admin, tmp_path, monkeypatch):
    import controller.taller_controller as taller_controller_module
    monkeypatch.setattr(taller_controller_module, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(taller_controller_module, "ENTREGAS_DIR", str(tmp_path / "resources" / "entregas"))

    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(tmp_path))

    with pytest.raises(AccesoNoAutorizadoError):
        tc.calificar_entrega(entrega.id_entrega, aprobado=True, comentario="")


def test_calificar_entrega_con_un_aprendiz_como_actor_falla(curso, aprendiz, admin, tmp_path, monkeypatch):
    import controller.taller_controller as taller_controller_module
    monkeypatch.setattr(taller_controller_module, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(taller_controller_module, "ENTREGAS_DIR", str(tmp_path / "resources" / "entregas"))

    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(tmp_path))

    with pytest.raises(AccesoNoAutorizadoError):
        tc.calificar_entrega(entrega.id_entrega, aprobado=True, comentario="", usuario_actor=aprendiz)


def test_calificar_entrega_con_un_administrador_como_actor_funciona(curso, aprendiz, admin, tmp_path, monkeypatch):
    import controller.taller_controller as taller_controller_module
    monkeypatch.setattr(taller_controller_module, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(taller_controller_module, "ENTREGAS_DIR", str(tmp_path / "resources" / "entregas"))

    tc = TallerController()
    taller = tc.crear_taller(curso.id_curso, "Taller", "Descripción suficientemente larga del taller.", usuario_actor=admin)
    entrega = tc.subir_entrega(taller.id_taller, aprendiz.id_usuario, _crear_archivo_de_prueba(tmp_path))

    calificada = tc.calificar_entrega(entrega.id_entrega, aprobado=True, comentario="", usuario_actor=admin)
    assert calificada.estado == "APROBADO"
