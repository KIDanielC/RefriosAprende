"""El comité encontró 13 usuarios, 8 cursos y 8 resultados dentro de database/refrios.db
empaquetado en dist/RefriosAprende/_internal: la base real de desarrollo, no una semilla.
Estas pruebas cubren utils/crear_semilla.py (genera la semilla limpia) y
packaging/verificar_paquete.py (detecta si un paquete trae datos que no debería traer).

packaging/verificar_paquete.py se carga por ruta de archivo, no con 'import packaging...':
existe una librería de PyPI llamada igual que la carpeta (paquete real de pip/setuptools),
así que un import normal resolvería a esa librería en vez de al script de este proyecto."""
import importlib.util
import os
import sqlite3

from utils.crear_semilla import crear_semilla

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cargar_verificar_paquete():
    ruta_script = os.path.join(_RAIZ_PROYECTO, "packaging", "verificar_paquete.py")
    spec = importlib.util.spec_from_file_location("verificar_paquete_script", ruta_script)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_crear_semilla_genera_bd_solo_con_roles(tmp_path, monkeypatch):
    import utils.crear_semilla as modulo_semilla

    ruta_semilla = tmp_path / "refrios.db"
    monkeypatch.setattr(modulo_semilla, "_RUTA_SEMILLA", str(ruta_semilla))

    crear_semilla()

    assert ruta_semilla.is_file()
    conexion = sqlite3.connect(str(ruta_semilla))
    try:
        assert conexion.execute("SELECT COUNT(*) FROM roles").fetchone()[0] == 2
        assert conexion.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0
        assert conexion.execute("SELECT COUNT(*) FROM cursos").fetchone()[0] == 0
    finally:
        conexion.close()


def _preparar_estructura_de_paquete(tmp_path, ruta_bd_origen) -> str:
    ruta_base = tmp_path / "_internal"
    (ruta_base / "database").mkdir(parents=True)
    (ruta_base / "resources" / "contenidos").mkdir(parents=True)
    (ruta_base / "resources" / "fotos_perfil").mkdir(parents=True)
    (ruta_base / "resources" / "entregas").mkdir(parents=True)
    import shutil
    shutil.copyfile(ruta_bd_origen, ruta_base / "database" / "refrios.db")
    return str(ruta_base)


def test_verificar_paquete_pasa_sobre_una_semilla_limpia(tmp_path, monkeypatch):
    import utils.crear_semilla as modulo_semilla

    ruta_semilla = tmp_path / "semilla_origen.db"
    monkeypatch.setattr(modulo_semilla, "_RUTA_SEMILLA", str(ruta_semilla))
    crear_semilla()

    ruta_paquete = _preparar_estructura_de_paquete(tmp_path, ruta_semilla)
    modulo = _cargar_verificar_paquete()
    modulo.verificar_paquete(ruta_paquete)  # no lanza


def test_verificar_paquete_falla_si_la_bd_tiene_usuarios(tmp_path, monkeypatch):
    import utils.crear_semilla as modulo_semilla

    ruta_semilla = tmp_path / "semilla_con_datos.db"
    monkeypatch.setattr(modulo_semilla, "_RUTA_SEMILLA", str(ruta_semilla))
    crear_semilla()

    conexion = sqlite3.connect(str(ruta_semilla))
    conexion.execute(
        "INSERT INTO usuarios (nombre_completo, documento, correo, usuario, contrasena_hash, id_rol) "
        "VALUES ('Alguien', '123', 'a@a.com', 'alguien', 'hash', 1)"
    )
    conexion.commit()
    conexion.close()

    ruta_paquete = _preparar_estructura_de_paquete(tmp_path, ruta_semilla)
    modulo = _cargar_verificar_paquete()
    try:
        modulo.verificar_paquete(ruta_paquete)
        assert False, "se esperaba PaqueteNoLimpioError"
    except modulo.PaqueteNoLimpioError as error:
        assert "usuarios" in str(error)


def test_verificar_paquete_falla_si_resources_contenidos_no_esta_vacia(tmp_path, monkeypatch):
    import utils.crear_semilla as modulo_semilla

    ruta_semilla = tmp_path / "semilla.db"
    monkeypatch.setattr(modulo_semilla, "_RUTA_SEMILLA", str(ruta_semilla))
    crear_semilla()

    ruta_paquete = _preparar_estructura_de_paquete(tmp_path, ruta_semilla)
    (os.path.join(ruta_paquete, "resources", "contenidos"))
    with open(os.path.join(ruta_paquete, "resources", "contenidos", "archivo_real.pdf"), "w") as archivo:
        archivo.write("contenido de ejemplo")

    modulo = _cargar_verificar_paquete()
    try:
        modulo.verificar_paquete(ruta_paquete)
        assert False, "se esperaba PaqueteNoLimpioError"
    except modulo.PaqueteNoLimpioError as error:
        assert "contenidos" in str(error)


def test_verificar_paquete_falla_si_no_existe_la_bd(tmp_path):
    modulo = _cargar_verificar_paquete()
    try:
        modulo.verificar_paquete(str(tmp_path))
        assert False, "se esperaba PaqueteNoLimpioError"
    except modulo.PaqueteNoLimpioError:
        pass
