"""Pruebas de las piezas de packaging/generar_ficha_entrega.py que no dependen de tener
dist/ ni el instalador ya compilados (eso se valida a mano, como pide el comité, corriendo
el script completo sobre un build real antes de entregar)."""
import hashlib
import importlib.util
import os

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cargar_generar_ficha_entrega():
    ruta_script = os.path.join(_RAIZ_PROYECTO, "packaging", "generar_ficha_entrega.py")
    spec = importlib.util.spec_from_file_location("generar_ficha_entrega_script", ruta_script)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_sha256_de_coincide_con_hashlib(tmp_path):
    modulo = _cargar_generar_ficha_entrega()
    ruta_archivo = tmp_path / "archivo_de_prueba.bin"
    ruta_archivo.write_bytes(b"contenido de prueba para la huella")

    esperado = hashlib.sha256(ruta_archivo.read_bytes()).hexdigest()
    assert modulo._sha256_de(str(ruta_archivo)) == esperado


def test_verificar_arbol_limpio_lanza_si_git_status_no_esta_vacio(monkeypatch):
    modulo = _cargar_generar_ficha_entrega()
    monkeypatch.setattr(modulo, "_ejecutar", lambda comando, cwd: " M algun_archivo_versionado.py")

    try:
        modulo._verificar_arbol_limpio()
        assert False, "se esperaba EntregaInvalidaError"
    except modulo.EntregaInvalidaError:
        pass


def test_verificar_arbol_limpio_no_lanza_si_git_status_esta_vacio(monkeypatch):
    modulo = _cargar_generar_ficha_entrega()
    monkeypatch.setattr(modulo, "_ejecutar", lambda comando, cwd: "")
    modulo._verificar_arbol_limpio()  # no lanza
