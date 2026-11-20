# Guía de verificación manual — correcciones del jurado (Evaluación 1 del CNTG)

Este documento explica, corrección por corrección, qué encontró el jurado, qué se cambió
en el código y **cómo comprobar con la aplicación abierta, sin programar, que el cambio
de verdad funciona** — para que se pueda repetir en cualquier momento, incluyendo delante
del jurado si lo vuelven a pedir.

Cada sección cita el commit real donde quedó el cambio (`git log --oneline` lo muestra;
también puedes pegar el hash en `git show <hash>` para ver el detalle línea por línea).

---

## Parte A — Errores que el jurado encontró en el software

### 1. Actualizar una base de datos antigua perdía información
**Commit:** `02e0cd7`

El jurado encontró que al abrir con la versión nueva una base de datos creada con una
versión vieja del programa, algunas evaluaciones y cursos antiguos perdían sus preguntas,
resultados o contenidos asociados.

**Qué se cambió:** el procedimiento que actualiza bases antiguas ahora respalda el archivo
antes de tocarlo, cuenta todas las tablas antes y después, y si algo no coincide, restaura
el respaldo automáticamente en vez de dejar la base dañada.

**Cómo comprobarlo tú mismo:**
1. Antes de actualizar el programa en un equipo, copia `database/refrios.db` a otra
   carpeta como respaldo manual (por si acaso).
2. En la pantalla de **Reportes**, anota cuántos cursos, usuarios y resultados de
   evaluación muestra el resumen general.
3. Actualiza el programa a la versión nueva y ábrelo con esa misma base de datos.
4. Vuelve a la pantalla de Reportes y compara: los números deben ser idénticos a los del
   paso 2. Si algo no coincide, el programa ya debería haber restaurado el respaldo solo
   (revisa que `database/refrios.db.backup-*` no haya quedado huérfano).

### 2. Contraseñas muy largas rompían el programa
**Commit:** `7af92db`

Una contraseña de más de 72 bytes (73 caracteres normales, o 37 letras con tilde) hacía
que el programa se cayera con un error técnico en vez de avisar con un mensaje normal.

**Cómo comprobarlo tú mismo:**
1. Ve a crear un usuario nuevo (o cambiar tu propia contraseña).
2. Escribe una contraseña exageradamente larga (copia y pega un párrafo de 80-100
   caracteres).
3. Deberías ver un mensaje de validación normal ("la contraseña no puede superar..."),
   nunca una pantalla de error ni que el programa se cierre.

### 3. La pantalla de inicio de sesión mostraba cifras inventadas
**Commit:** `f3e438b`

Se mostraban "18 Cursos activos", "92% Aprobación" y "236 Aprendices" en la pantalla de
login, escritos directamente en el código, sin relación con los datos reales — el jurado
señaló que podían confundirse con resultados reales del taller.

**Cómo comprobarlo tú mismo:**
1. Cierra sesión o abre el programa desde cero.
2. En la pantalla de inicio de sesión, confirma que esas tres cifras ya no aparecen en
   ninguna parte de la pantalla.

### 4. Algunas pantallas se saltaban al controlador y consultaban la base directamente
**Commit:** `1263f9c`

Es un error de arquitectura interna (no se ve a simple vista en la pantalla), así que la
forma de comprobarlo sin leer código es confirmar que el comportamiento sigue correcto:

**Cómo comprobarlo tú mismo:**
1. Como aprendiz, presenta y aprueba la evaluación final de un curso.
2. Confirma que el tablero (dashboard), la pantalla de evaluaciones y la pantalla del
   curso del aprendiz **sigan mostrando correctamente** que esa evaluación ya está
   aprobada (una insignia, un check o el estado correspondiente). Si se ve igual que
   antes, el cambio interno no rompió nada.

### 5. El paquete instalable traía usuarios y cursos reales de fábrica
**Commit:** `c3da0bd`

El jurado encontró 13 usuarios, 8 cursos y 8 resultados ya cargados dentro del instalador
entregado — datos reales de desarrollo, no una base vacía de fábrica.

**Cómo comprobarlo tú mismo:**
1. Instala el programa en un equipo limpio (o en una carpeta nueva) usando el instalador
   de `packaging/salida/`.
2. Al abrir el programa por primera vez, **no debe aparecer ningún curso ni usuario
   precargado** — debe pedir crear el primer administrador (ver punto 6).

### 6. Existía un usuario y contraseña de fábrica (`admin` / `admin123`)
**Commit:** `7063adb`

Cualquiera que leyera el código (o el repositorio público) encontraba la contraseña del
administrador de fábrica.

**Cómo comprobarlo tú mismo:**
1. Instala el programa en un equipo limpio o borra `database/refrios.db` para simular un
   primer arranque.
2. Al abrir el programa, en vez de la pantalla de login debe aparecer una ventana para
   **crear el primer administrador**, pidiendo nombre, documento, correo, usuario y
   contraseña a tu elección.
3. Crea esa cuenta, cierra y vuelve a abrir el programa: ahora sí debe pedir el login
   normal, con la cuenta que tú elegiste (nunca `admin`/`admin123`, que ya no existe en
   ningún archivo del proyecto).

### 7. Se podían subir archivos sin límite de tamaño
**Commit:** `6c7bc74`

Contenidos en PDF/imagen, fotos de perfil y entregas de taller no tenían ningún límite de
tamaño.

**Cómo comprobarlo tú mismo:**
1. Intenta subir como contenido de un curso un PDF o una imagen de más de 20 MB: debe
   rechazarlo con un mensaje claro.
2. Intenta subir una entrega de taller de más de 20 MB: mismo rechazo.
3. Intenta poner una foto de perfil de más de 5 MB: debe rechazarla también.

### 8. Dependencia con vulnerabilidades conocidas (Pillow)
**Commit:** `6c7bc74`

`pip-audit` encontró 42 vulnerabilidades conocidas en la versión de Pillow que usaba el
proyecto.

**Cómo comprobarlo tú mismo (requiere la terminal, pero es un solo comando):**
1. Abre una terminal en la carpeta del proyecto.
2. Corre: `py -m pip_audit`
3. No debe reportar ninguna vulnerabilidad para Pillow (quedó en la versión 13.0.0).

### 9. Sin bloqueo tras varios intentos fallidos de inicio de sesión
**Commit:** `6c7bc74`

Cualquiera podía intentar adivinar una contraseña sin límite de intentos.

**Cómo comprobarlo tú mismo:**
1. En la pantalla de login, escribe un usuario válido con una contraseña incorrecta,
   5 veces seguidas.
2. En el quinto intento (o el sexto), el programa debe avisar que la cuenta quedó
   bloqueada temporalmente (5 minutos), incluso si en el siguiente intento escribes la
   contraseña correcta.
3. Espera los 5 minutos (o revisa que el aviso mencione el tiempo de espera) e intenta de
   nuevo con la contraseña correcta: debe dejarte entrar.

---

## Parte B — Cambios para que el software cumpla lo que ya describían los manuales

### 10. Faltaba un README.md en la raíz del proyecto entregado
**Commit:** `f818f96`

**Cómo comprobarlo tú mismo:** abre el ZIP de entrega y confirma que `README.md` está en
la raíz, con la descripción del proyecto, la versión y los comandos para instalar,
ejecutar y probar.

### 11. Nunca se había medido ni probado el respaldo/restauración de datos
**Commit:** `729d08a`

**Cómo comprobarlo tú mismo (con la terminal):**
1. Con el programa cerrado, corre desde la carpeta del proyecto:
   `py -m utils.respaldo respaldar . C:\ruta\que\quieras\respaldo.zip`
2. Confirma que el archivo `respaldo.zip` se creó.
3. (Opcional, para probar la restauración de verdad) copia la carpeta `database/` y
   `resources/` a otro lugar como respaldo manual extra, bórralas, y luego corre:
   `py -m utils.respaldo restaurar C:\ruta\que\quieras\respaldo.zip .`
4. Abre el programa: todos tus cursos, usuarios y archivos subidos deben seguir ahí.

### 12. No se habían medido tiempos de respuesta ni comportamiento bajo carga
**Commits:** `404785f`, `1305b82`

Esta es la medición detallada por operación que ya quedó en
`documentation/RENDIMIENTO.md` (con los números reales) — ver ese archivo para la tabla
completa.

**Cómo repetirlo tú mismo:** `py -m utils.medir_tiempos_operaciones <carpeta_salida> 30`

### 13. Operaciones sensibles sin control de quién puede ejecutarlas
**Commit:** `6c7bc74`

Calificar una entrega de taller no verificaba que quien lo hiciera fuera administrador.

**Cómo comprobarlo tú mismo:** esta validación protege el flujo interno, no se expone una
opción distinta en la pantalla (un aprendiz nunca ve la pantalla de calificar talleres).
La forma de confirmarlo sin tocar código es correr la prueba automatizada dedicada:
`py -m pytest tests/test_autorizacion_calificar.py -v`

### 14. El certificado de finalización no se podía exportar a PDF
**Commit:** `1f8c946`

**Cómo comprobarlo tú mismo:**
1. Como aprendiz, completa un curso (ve todo el contenido, aprueba la evaluación final y
   los talleres si los tiene).
2. Abre el certificado de ese curso y haz clic en **"Guardar como PDF"**.
3. Elige una carpeta destino y confirma que se genera un archivo `.pdf` real que abre bien
   con cualquier lector de PDF.

### 15. No se podían reordenar los contenidos de un curso
**Commit:** `455b14f`

**Cómo comprobarlo tú mismo:**
1. Como administrador, entra a gestionar los contenidos de un curso con al menos 3
   contenidos.
2. Usa las flechas ▲▼ junto a cada contenido para subir o bajar su posición.
3. Cierra y vuelve a abrir esa pantalla (o el curso): el nuevo orden debe mantenerse.
4. Si el curso tiene "aprendizaje secuencial" activado, confirma que el bloqueo de
   contenidos respeta el nuevo orden (no el orden original).

### 16. El tipo de contenido "Video local" existía en la base de datos pero no se podía usar
**Commit:** `aa00161`

**Cómo comprobarlo tú mismo:**
1. Como administrador, al agregar un contenido a un curso, elige el tipo **"Video"** y
   selecciona un archivo `.mp4`, `.avi` o `.mkv` de tu equipo (máximo 200 MB).
2. Como aprendiz, entra a ese contenido y usa el botón **"Abrir video"**: debe abrirse con
   el reproductor que Windows tenga asociado a esa extensión (no hay reproductor dentro
   del programa, eso fue una decisión de alcance).

### 17. La versión del programa y la ficha de entrega no quedaban documentadas
**Commit:** `6899bd0`, corrección posterior en `5e7312f`

**Cómo comprobarlo tú mismo (con la terminal, después de compilar `dist/` y el
instalador):**
1. Corre: `py packaging/generar_ficha_entrega.py`
2. Debe terminar sin errores y crear
   `packaging/salida/entrega/FICHA_ENTREGA_v1.0.1.md`, con las huellas SHA-256 del
   instalador y del paquete portable, la versión de Python, el resumen de la suite de
   pruebas y la lista de dependencias.

---

## Cómo correr TODAS las pruebas automatizadas de una sola vez

Si en algún momento el jurado quiere ver que absolutamente nada de esto se rompió al
tocar otra cosa, el comando que corre las 172 pruebas automatizadas del proyecto es:

```
py -m pytest -v
```

Y para ver, además, qué porcentaje de cada archivo queda cubierto por esas pruebas:

```
py -m pytest --cov=controller --cov=model --cov=utils --cov=view --cov=database --cov=config --cov-report=term-missing
```

Ambos comandos se corren desde la carpeta `RefriosAprende/`, con el entorno virtual del
proyecto activado.
