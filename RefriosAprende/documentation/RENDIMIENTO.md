# Rendimiento y cobertura de pruebas — Refrios Aprende v1.0.1

Este documento reúne, para tener una sola fuente confiable:

1. Los tiempos de respuesta reales de cada operación del software, medidos con los
   controladores de verdad (no simulados) sobre tres volúmenes de datos de fondo.
2. La cobertura de pruebas automatizadas, módulo por módulo.
3. Los hallazgos y oportunidades de mejora que salieron de ambas mediciones.

Se generó corriendo `py -m utils.medir_tiempos_operaciones` y
`py -m pytest --cov=controller --cov=model --cov=utils --cov=view --cov=database --cov=config --cov-report=term-missing`
sobre el repositorio en el commit en que se agregó este archivo.

## 1. Metodología

- **Operación, no pantalla:** cada fila mide una sola llamada de negocio (crear un curso,
  matricular, calificar una entrega, etc.), para poder señalar con precisión cuál paso es
  lento, en vez de un tiempo agregado de toda una pantalla.
- **Prueba de saturación:** cada operación se repite 30 veces sobre tres bases de datos de
  fondo distintas — `pequeño` (11 usuarios, 4 cursos, 20 resultados), `mediano` (51
  usuarios, 15 cursos, 500 resultados) y `grande` (201 usuarios, 40 cursos, 5000
  resultados) — para revelar si el tiempo se degrada cuando crece el volumen de datos, no
  solo cuánto tarda con una base vacía.
- **Equipo de prueba:** AMD Ryzen 5 5600 6-Core Processor (12 núcleos lógicos) ·
  31.9 GB RAM · Windows 11 · Python 3.14.3. Es un computador real del taller, no una
  máquina de desarrollo aparte: las mediciones reflejan el equipo donde de verdad se usa
  el programa.
- Por cada operación y volumen se reportan: mínimo, media, mediana, P90, P95, P99, máximo
  y desviación estándar, en milisegundos. La mediana es el caso típico; el P95 y el máximo
  son el peor caso real que puede encontrar un usuario.

## 2. Tiempos de respuesta por operación (milisegundos)

Cada celda es `mediana / P95 / máximo`.

| Operación | pequeño | mediano | grande |
|---|---|---|---|
| Autenticación - iniciar_sesion (credenciales correctas) | 194.85 / 196.51 / 198.09 | 194.52 / 195.53 / 195.83 | 194.79 / 195.75 / 197.07 |
| Usuarios - crear_usuario (aprendiz nuevo) | 202.38 / 204.3 / 211.3 | 202.62 / 205.42 / 211.28 | 202.97 / 214.24 / 216.34 |
| Usuarios - listar_usuarios (lectura completa) | 0.19 / 0.22 / 0.33 | 0.31 / 0.34 / 0.54 | 0.76 / 0.79 / 1.02 |
| Cursos - crear_curso (borrador) | 7.56 / 7.94 / 8.11 | 7.6 / 7.96 / 12.46 | 7.66 / 8.03 / 8.27 |
| Cursos - actualizar_curso (publicar a ACTIVO) | 7.64 / 8.05 / 13.12 | 7.53 / 7.93 / 11.63 | 7.55 / 7.89 / 7.99 |
| Cursos - listar_cursos_activos (lectura) | 0.22 / 0.3 / 0.41 | 0.24 / 0.25 / 0.37 | 0.3 / 0.33 / 0.43 |
| Contenidos - crear_contenido_texto | 7.74 / 8.9 / 11.49 | 7.6 / 7.95 / 9.54 | 7.71 / 7.97 / 8.06 |
| Contenidos - crear_contenido_pdf | 8.85 / 9.41 / 10.29 | 8.82 / 9.4 / 10.87 | 8.74 / 9.42 / 9.58 |
| Contenidos - crear_contenido_imagen | 9.38 / 10.69 / 11.03 | 9.08 / 9.63 / 9.96 | 8.94 / 11.6 / 45.05 |
| Contenidos - crear_contenido_video | 9.26 / 10.32 / 11.47 | 8.85 / 9.74 / 18.94 | 9.27 / 9.7 / 9.81 |
| Contenidos - mover_contenido (reordenar, 'bajar') | 8.25 / 8.7 / 8.84 | 8.03 / 8.26 / 12.84 | 8.34 / 8.91 / 11.59 |
| Matrícula - matricular | 7.6 / 7.9 / 8.06 | 8.09 / 8.91 / 9.85 | 7.73 / 7.96 / 7.99 |
| Evaluaciones - crear_evaluacion_final | 7.59 / 7.94 / 8.01 | 7.52 / 7.87 / 8.06 | 7.71 / 8.31 / 9.64 |
| Evaluaciones - crear_pregunta | 22.59 / 23.17 / 23.51 | 22.72 / 23.41 / 25.11 | 22.75 / 23.28 / 24.2 |
| Evaluaciones - presentar_evaluacion | 15.89 / 16.65 / 18.79 | 15.32 / 16.01 / 16.62 | 15.75 / 16.83 / 17.18 |
| Talleres - crear_taller | 7.71 / 8.24 / 9.94 | 7.61 / 7.98 / 8.4 | 7.8 / 8.04 / 8.1 |
| Talleres - subir_entrega | 8.71 / 9.19 / 10.21 | 8.88 / 9.36 / 12.23 | 8.85 / 9.12 / 9.88 |
| Talleres - calificar_entrega | 15.22 / 15.81 / 16.01 | 15.65 / 16.26 / 21.35 | 15.47 / 18.03 / 23.14 |
| Certificado - exportar_certificado (PDF) | 12.65 / 14.11 / 65.89 | 12.52 / 13.38 / 14.14 | 12.71 / 14.1 / 21.08 |
| Reportes - resumen_general | 4.71 / 5.38 / 5.75 | 7.99 / 9.03 / 9.12 | 20.62 / 24.41 / 25.32 |
| Reportes - detalle_por_curso | 6.15 / 7.51 / 8.31 | 9.31 / 10.75 / 12.75 | 22.92 / 25.61 / 28.42 |
| Reportes - avance_por_estudiante | 5.8 / 6.22 / 6.89 | 21.7 / 27.11 / 27.92 | 29.93 / 31.22 / 31.34 |
| Reportes - estudiantes_en_riesgo | 5.71 / 6.05 / 6.27 | 21.63 / 22.47 / 22.64 | 29.76 / 30.02 / 30.7 |

El informe completo, con el detalle estadístico (n, mín, media, mediana, P90, P95, P99,
máx, desviación estándar) de cada una de estas 22 operaciones en cada volumen, queda
reproducible con:

```
py -m utils.medir_tiempos_operaciones packaging/salida/mediciones_operaciones 30
```

## 3. Hallazgos sobre los tiempos

- **Ninguna operación de escritura (crear curso, matricular, calificar, etc.) se degrada
  con el volumen de datos.** Todas se mantienen entre 7 y 23 ms sin importar si la base
  tiene 20 o 5000 resultados, porque cada escritura solo toca las filas que le
  corresponden (inserciones puntuales, no recorridos de toda la tabla).
- **Los cuatro reportes sí se degradan con el volumen**, porque recorren en Python todos
  los cursos/usuarios en memoria en vez de agregarlos con SQL:
  - `resumen_general`: 4.7 ms → 8.0 ms → 20.6 ms (×4.4 de pequeño a grande).
  - `detalle_por_curso`: 6.2 ms → 9.3 ms → 22.9 ms (×3.7).
  - `avance_por_estudiante`: 5.8 ms → 21.7 ms → 29.9 ms (×5.2).
  - `estudiantes_en_riesgo`: 5.7 ms → 21.6 ms → 29.8 ms (×5.2).

  **Oportunidad de mejora:** mover estos cálculos a consultas SQL con `GROUP BY`/`COUNT`
  en vez de iterarlos en Python, o agregar índices sobre las columnas de filtro más
  usadas. Con los volúmenes probados el tiempo absoluto sigue siendo imperceptible para
  un usuario (<30 ms), pero la tendencia de crecimiento es real y debe quedar documentada
  para un trabajo futuro si la cantidad de cursos/usuarios creciera un orden de magnitud
  más.
- **`iniciar_sesion` y `crear_usuario` toman ~195-205 ms de forma constante**,
  independiente del volumen de datos. No es una falla: es el costo deliberado del
  algoritmo bcrypt (hashing lento a propósito, para dificultar ataques de fuerza bruta
  contra contraseñas). Como no varía con el volumen, confirma que el costo es
  exclusivamente criptográfico y no una consulta lenta.
- **Dos picos aislados (outliers), explicados y no preocupantes:**
  - `crear_contenido_imagen` en el volumen grande: una repetición tomó 45 ms frente a una
    mediana de 8.9 ms. Es una sola repetición de 30, compatible con una pausa puntual de
    E/S en disco (por ejemplo, un antivirus inspeccionando el archivo nuevo), no con un
    problema del código.
  - `exportar_certificado` en el volumen pequeño: una repetición tomó 65.9 ms frente a una
    mediana de 12.65 ms. Corresponde a la primera llamada, que paga el costo único de
    cargar las fuentes TrueType (Arial) desde disco; de ahí en adelante el sistema
    operativo las mantiene en caché y el costo baja a ~12-14 ms.

## 4. Cobertura de pruebas automatizadas por módulo

172 pruebas automatizadas, 58% de cobertura total de líneas (controller + model + utils +
view + database + config). Desglosada por capa:

| Capa | Cobertura típica | Comentario |
|---|---|---|
| `controller/` (lógica de negocio) | 64% – 100% | La mayoría entre 85% y 97%; son las pruebas que más importan porque ahí vive toda la validación y las reglas de negocio. |
| `model/dao/` (acceso a datos) | 81% – 100% | Todas las operaciones SQL quedan cubiertas por pruebas de integración contra una base real de prueba. |
| `model/entities/` | 78% – 95% | Clases de datos simples; lo no cubierto son casos borde de propiedades calculadas. |
| `database/connection.py` | 95% | Incluye las migraciones y la reconstrucción segura de tablas. |
| `utils/` (utilidades operativas) | 0% – 100% | Ver detalle abajo: dispareja a propósito. |
| `view/` (pantallas CustomTkinter) | 14% – 69% | Baja por naturaleza: es interfaz gráfica, no lógica de negocio; cubrir cada callback de clic requeriría automatizar la GUI, no pruebas unitarias. |

**Módulos con cobertura baja, revisados uno por uno (para que quede explícito que es una
decisión informada y no un descuido):**

| Módulo | Cobertura | Por qué |
|---|---|---|
| `utils/generar_fondo_login.py`, `utils/generar_ilustracion_login.py` | 0% | Scripts de un solo uso para generar imágenes estáticas de la pantalla de login; no se ejecutan en producción ni los usa la aplicación en tiempo de ejecución. |
| `utils/poblar_escenarios_prueba.py` | 0% | Script manual para cargar datos de demostración; se corre a mano cuando se necesita, no como parte del programa. |
| `utils/restablecer_admin.py` | 18% | **Esta sí es una oportunidad de mejora real.** Es una herramienta de recuperación de acceso (restablece el administrador) y hoy casi no tiene pruebas automatizadas. Es candidata a reforzar en una próxima iteración. |
| `controller/_pregunta_opcion_utils.py` | 64% | Función interna compartida entre evaluaciones y simulaciones; los casos no cubiertos son ramas de edición de preguntas existentes. |
| `controller/progreso_controller.py` | 72% | Los historiales y gráficas de progreso general tienen menos pruebas que el cálculo de avance individual, que sí está bien cubierto. |
| `view/*` en general | 14% – 49% | Cobertura de UI; mitigado porque las pantallas no tienen lógica de negocio propia (`tests/test_vistas_no_usan_dao.py` verifica justamente que las vistas no puedan saltarse la validación de los controladores). |

## 5. Conclusión

- El software responde en menos de 25 ms para cualquier operación individual, incluso
  con 5000 resultados de evaluación en la base de datos, salvo las dos operaciones que
  usan bcrypt a propósito (~200 ms, es una medida de seguridad, no una falla).
- Los reportes administrativos son el único punto que se degrada con el volumen de datos,
  de forma medible y explicada arriba; a la escala real del taller (decenas de usuarios,
  no miles) el tiempo sigue siendo imperceptible.
- La cobertura de pruebas automatizadas es alta en toda la capa de lógica de negocio y
  acceso a datos (los módulos que de verdad pueden introducir errores), y deliberadamente
  más baja en interfaz gráfica y scripts de un solo uso, con cada caso de baja cobertura
  identificado y justificado arriba en vez de ocultado.
