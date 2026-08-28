"""Acceso a datos para la tabla contenidos_vistos (seguimiento de lectura)."""
from database.connection import ConexionBD


class ContenidoVistoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def marcar_visto(self, id_usuario: int, id_contenido: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO contenidos_vistos (id_usuario, id_contenido) VALUES (?, ?)",
            (id_usuario, id_contenido),
        )
        self._conexion.confirmar()

    def contar_vistos_de_curso(self, id_usuario: int, id_curso: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM contenidos_vistos cv
            INNER JOIN contenidos c ON c.id_contenido = cv.id_contenido
            WHERE cv.id_usuario = ? AND c.id_curso = ?
            """,
            (id_usuario, id_curso),
        )
        return cursor.fetchone()["total"]

    def fue_visto(self, id_usuario: int, id_contenido: int) -> bool:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "SELECT 1 FROM contenidos_vistos WHERE id_usuario = ? AND id_contenido = ? LIMIT 1",
            (id_usuario, id_contenido),
        )
        return cursor.fetchone() is not None
