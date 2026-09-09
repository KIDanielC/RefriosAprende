"""Acceso a datos para la tabla resultados."""
import sqlite3

from database.connection import ConexionBD
from model.entities.resultado import Resultado

_SELECT_BASE = """
    SELECT id_resultado, id_usuario, id_evaluacion, nota_obtenida, aprobado, fecha_intento
    FROM resultados
"""


class ResultadoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> Resultado:
        return Resultado(
            id_resultado=fila["id_resultado"],
            id_usuario=fila["id_usuario"],
            id_evaluacion=fila["id_evaluacion"],
            nota_obtenida=fila["nota_obtenida"],
            aprobado=fila["aprobado"],
            fecha_intento=fila["fecha_intento"],
        )

    def listar_por_usuario_y_evaluacion(self, id_usuario: int, id_evaluacion: int) -> list[Resultado]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            f"{_SELECT_BASE} WHERE id_usuario = ? AND id_evaluacion = ? ORDER BY fecha_intento",
            (id_usuario, id_evaluacion),
        )
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def listar_por_evaluacion(self, id_evaluacion: int) -> list[Resultado]:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(f"{_SELECT_BASE} WHERE id_evaluacion = ? ORDER BY fecha_intento", (id_evaluacion,))
        return [self._fila_a_entidad(fila) for fila in cursor.fetchall()]

    def listar_detalle_por_evaluacion(self, id_evaluacion: int) -> list[tuple[str, float, bool, str]]:
        """Cada intento con el nombre del aprendiz (para que el administrador vea notas e
        intentos sin tener que cruzar usuarios y resultados a mano)."""
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            SELECT u.nombre_completo, r.nota_obtenida, r.aprobado, r.fecha_intento
            FROM resultados r
            JOIN usuarios u ON u.id_usuario = r.id_usuario
            WHERE r.id_evaluacion = ?
            ORDER BY u.nombre_completo, r.fecha_intento
            """,
            (id_evaluacion,),
        )
        return [
            (fila["nombre_completo"], fila["nota_obtenida"], bool(fila["aprobado"]), fila["fecha_intento"])
            for fila in cursor.fetchall()
        ]

    def existe_aprobado(self, id_usuario: int, id_evaluacion: int) -> bool:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT 1 FROM resultados WHERE id_usuario = ? AND id_evaluacion = ? AND aprobado = 1 LIMIT 1",
            (id_usuario, id_evaluacion),
        )
        return cursor.fetchone() is not None

    def crear(self, id_usuario: int, id_evaluacion: int, nota_obtenida: float, aprobado: bool) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT INTO resultados (id_usuario, id_evaluacion, nota_obtenida, aprobado) VALUES (?, ?, ?, ?)",
            (id_usuario, id_evaluacion, nota_obtenida, int(aprobado)),
        )
        self._conexion.confirmar()
        return cursor.lastrowid
