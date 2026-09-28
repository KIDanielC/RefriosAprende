"""Acceso a datos para la tabla tiempo_uso_curso."""
from database.connection import ConexionBD


class TiempoUsoCursoDAO:
    def __init__(self):
        self._conexion = ConexionBD()

    def crear(self, id_usuario: int, id_curso: int) -> int:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            "INSERT INTO tiempo_uso_curso (id_usuario, id_curso) VALUES (?, ?)",
            (id_usuario, id_curso),
        )
        self._conexion.confirmar()
        return cursor.lastrowid

    def actualizar_duracion(self, id_registro: int, duracion_segundos: int) -> None:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            UPDATE tiempo_uso_curso
            SET duracion_segundos = ?, fecha_fin = datetime('now', 'localtime')
            WHERE id_registro = ?
            """,
            (duracion_segundos, id_registro),
        )
        self._conexion.confirmar()

    def horas_por_usuario_y_curso(self, id_usuario: int, id_curso: int) -> float:
        cursor = self._conexion.obtener_cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(duracion_segundos), 0) AS total_segundos
            FROM tiempo_uso_curso
            WHERE id_usuario = ? AND id_curso = ?
            """,
            (id_usuario, id_curso),
        )
        return cursor.fetchone()["total_segundos"] / 3600.0
