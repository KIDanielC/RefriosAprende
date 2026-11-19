"""Prueba de humo para utils/poblar_carga.py y utils/medir_tiempos_respuesta.py: no mide el
rendimiento real (eso lo pide el comité sobre un equipo del taller, con los volúmenes
mediano/grande), pero confirma que ambos scripts corren de punta a punta sin romperse,
sobre el volumen "pequeño" y una sola repetición por pantalla."""
import importlib
import sqlite3

import database.connection as connection_module


def test_poblar_carga_pequeno_genera_los_datos_esperados(tmp_path, monkeypatch):
    import utils.poblar_carga as modulo_carga

    ruta_bd = tmp_path / "bd_carga_pequena.db"
    resumen = modulo_carga.poblar("pequeno", str(ruta_bd))

    assert resumen["resultados"] == 20
    conexion = sqlite3.connect(str(ruta_bd))
    try:
        assert conexion.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 11  # 10 aprendices + 1 admin
        assert conexion.execute("SELECT COUNT(*) FROM cursos").fetchone()[0] == 4
        assert conexion.execute("SELECT COUNT(*) FROM resultados").fetchone()[0] == 20
    finally:
        conexion.close()
        connection_module.ConexionBD._instancia = None


def test_poblar_carga_rechaza_un_volumen_desconocido(tmp_path):
    import utils.poblar_carga as modulo_carga

    try:
        modulo_carga.poblar("inexistente", str(tmp_path / "bd.db"))
        assert False, "se esperaba ValueError"
    except ValueError:
        pass


def test_medir_tiempos_respuesta_produce_un_reporte(tmp_path):
    import utils.poblar_carga as modulo_carga
    import utils.medir_tiempos_respuesta as modulo_medicion

    ruta_bd = tmp_path / "bd_carga_pequena.db"
    resumen = modulo_carga.poblar("pequeno", str(ruta_bd))
    connection_module.ConexionBD._instancia = None

    ruta_salida = tmp_path / "tiempos.md"
    modulo_medicion.medir(str(ruta_bd), resumen["usuario_admin"], str(ruta_salida), repeticiones=1)

    contenido = ruta_salida.read_text(encoding="utf-8")
    assert "Mediana (ms)" in contenido
    assert "Usuarios" in contenido
    assert "Reportes" in contenido

    connection_module.ConexionBD._instancia = None
