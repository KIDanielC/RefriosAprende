"""Formato de texto enriquecido compartido entre la vista (editor/visor) y los controladores
que validan longitud mínima de campos de texto. Sin dependencias de tkinter a propósito: los
controladores no deben importar nada de `view` (ver arquitectura MVC del proyecto).

Un valor guardado es JSON con la marca `MARCA_FORMATO`, o texto plano (datos de antes de esta
funcionalidad, o cualquier valor que no traiga formato) — `analizar()` interpreta ambos casos.
"""
import json

MARCA_FORMATO = "rico_v1"


def _markup_valido(datos) -> bool:
    return isinstance(datos, dict) and datos.get("formato") == MARCA_FORMATO and isinstance(datos.get("parrafos"), list)


def analizar(valor: str) -> dict:
    """Interpreta un valor guardado: JSON con formato, o texto plano (posiblemente antiguo)."""
    if valor:
        try:
            datos = json.loads(valor)
        except (ValueError, TypeError):
            datos = None
        if _markup_valido(datos):
            return datos

    lineas = (valor or "").split("\n")
    return {
        "formato": MARCA_FORMATO,
        "parrafos": [{"alineacion": "left", "tramos": [{"texto": linea}]} for linea in lineas],
    }


def texto_plano_desde_markup(valor: str) -> str:
    """Extrae el texto sin formato de un valor guardado. Se usa para vistas previas cortas
    y para validar longitud mínima sin que el formato (JSON) infle el conteo de caracteres."""
    datos = analizar(valor)
    return "\n".join(
        "".join(tramo.get("texto", "") for tramo in parrafo.get("tramos", []))
        for parrafo in datos["parrafos"]
    )
