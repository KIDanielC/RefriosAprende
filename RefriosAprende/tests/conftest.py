"""Fixtures compartidas: cada prueba corre contra una base de datos SQLite nueva y aislada
(un archivo temporal distinto por prueba), nunca contra refrios.db real."""
import pytest

import database.connection as connection_module
from controller.curso_controller import CursoController
from controller.usuario_controller import UsuarioController
from model.dao.rol_dao import RolDAO


@pytest.fixture(autouse=True)
def base_datos_de_prueba(tmp_path, monkeypatch):
    """Apunta ConexionBD a un archivo temporal y resetea el singleton para que cada
    prueba arranque con un esquema limpio (schema.sql se re-aplica desde cero)."""
    ruta_bd_prueba = tmp_path / "prueba.db"
    monkeypatch.setattr(connection_module, "DATABASE_PATH", str(ruta_bd_prueba))
    connection_module.ConexionBD._instancia = None
    yield
    connection_module.ConexionBD._instancia = None


@pytest.fixture
def id_rol_admin():
    return RolDAO().obtener_por_nombre("ADMINISTRADOR").id_rol


@pytest.fixture
def id_rol_aprendiz():
    return RolDAO().obtener_por_nombre("APRENDIZ").id_rol


@pytest.fixture
def admin(id_rol_admin):
    uc = UsuarioController()
    return uc.crear_usuario(
        "Admin de Prueba", "1000000001", "admin.prueba@refrios.local", "admin.prueba", "clave123", id_rol_admin
    )


@pytest.fixture
def aprendiz(id_rol_aprendiz):
    uc = UsuarioController()
    return uc.crear_usuario(
        "Aprendiz de Prueba", "1000000002", "aprendiz.prueba@refrios.local", "aprendiz.prueba", "clave123",
        id_rol_aprendiz,
    )


@pytest.fixture
def curso(admin):
    """Curso ya publicado (ACTIVO): los cursos nacen en BORRADOR, así que la mayoría de
    pruebas —que asumen un curso visible/matriculable— lo publican de inmediato aquí."""
    cc = CursoController()
    curso_creado = cc.crear_curso("Curso de Prueba", "Descripción del curso de prueba", admin.id_usuario)
    return cc.actualizar_curso(
        curso_creado.id_curso, curso_creado.nombre_curso, curso_creado.descripcion,
        admin.id_usuario, "ACTIVO",
    )
