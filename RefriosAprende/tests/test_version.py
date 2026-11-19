"""El manual técnico señalaba que APP_VERSION (config/settings.py) y MyAppVersion
(packaging/instalador.iss) podían quedar desincronizadas, porque nada las comparaba."""
import pathlib
import re

from config.settings import APP_VERSION

_RUTA_INSTALADOR_ISS = pathlib.Path(__file__).resolve().parent.parent / "packaging" / "instalador.iss"


def test_version_app_coincide_con_version_instalador():
    contenido = _RUTA_INSTALADOR_ISS.read_text(encoding="utf-8")
    coincidencia = re.search(r'#define MyAppVersion "([^"]+)"', contenido)
    assert coincidencia is not None, "No se encontró MyAppVersion en instalador.iss"
    assert coincidencia.group(1) == APP_VERSION
