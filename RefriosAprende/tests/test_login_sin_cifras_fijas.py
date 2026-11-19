"""El comité señaló que la pantalla de acceso mostraba cifras fijas ('18 Cursos activos',
'92% Aprobación', '236 Aprendices') que podían confundirse con resultados reales del taller.
Esta prueba falla si alguien las vuelve a escribir en el código de la pantalla de acceso."""
import pathlib

_RUTA_LOGIN_VIEW = pathlib.Path(__file__).resolve().parent.parent / "view" / "screens" / "login_view.py"
_CADENAS_PROHIBIDAS = ("Cursos activos", "Aprobación", "Aprendices", "92%", "236")


def test_login_view_no_tiene_cifras_fijas():
    codigo_fuente = _RUTA_LOGIN_VIEW.read_text(encoding="utf-8")
    encontradas = [cadena for cadena in _CADENAS_PROHIBIDAS if cadena in codigo_fuente]
    assert encontradas == [], f"Reaparecieron cifras/etiquetas fijas en login_view.py: {encontradas}"
