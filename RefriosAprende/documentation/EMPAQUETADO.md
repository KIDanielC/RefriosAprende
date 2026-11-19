# Empaquetado: instalador de Windows

Procedimiento para generar un instalador `.exe` de "Refrios Aprende" que se pueda entregar
y ejecutar en un computador con Windows que no tenga Python instalado.

## Resumen de la estrategia

1. **PyInstaller** empaqueta la app (`main.py` + dependencias + Python embebido) en una
   carpeta autocontenida (`dist/RefriosAprende/`), modo `--onedir` (más rápido de abrir y
   más fácil de depurar que `--onefile`).
2. **Inno Setup** envuelve esa carpeta en un instalador `.exe` de verdad: crea acceso
   directo en el menú inicio, opcionalmente en el escritorio, y un desinstalador.

## Dónde vive cada cosa cuando la app ya está instalada

El instalador deja el `.exe` en `Program Files`, una carpeta donde un usuario normal (sin
permisos de administrador) **no puede escribir**. Por eso, desde `config/settings.py`, la
app distingue dos carpetas cuando corre empaquetada (`sys.frozen`):

- **Carpeta de solo lectura** (dentro de la instalación): el `schema.sql` original, los
  íconos/imágenes de fábrica y, si se incluyó, una base de datos precargada de fábrica.
- **Carpeta de datos del usuario** (`%LOCALAPPDATA%\RefriosAprende\`): donde vive la base
  de datos real (`refrios.db`) con la que trabaja la app y los contenidos (PDF/imágenes)
  que suban los instructores. Se crea automáticamente en el primer arranque, copiando ahí
  el contenido de la carpeta de solo lectura (ver `_preparar_datos_usuario()` en
  `config/settings.py`). Los recursos propios de la app (íconos, imágenes, `schema.sql`) se
  reemplazan en **cada** arranque, para que una reinstalación con una versión nueva se vea
  reflejada de inmediato; `refrios.db` y los contenidos/fotos/entregas, en cambio, solo se
  copian la primera vez y nunca se vuelven a pisar — así no se pierden datos reales del
  usuario al actualizar la app.

Desinstalar la app (o incluso borrarla de `Program Files` a mano) **no borra**
`%LOCALAPPDATA%\RefriosAprende\`: si se reinstala después, los datos siguen ahí.

## Paso 1 — Compilar con PyInstaller

Con el entorno virtual activado, desde la raíz de `RefriosAprende/`:

```
py -m pip install -r requirements-dev.txt
py -m utils.crear_semilla
py -m PyInstaller packaging/refrios_aprende.spec
```

Resultado: `dist/RefriosAprende/RefriosAprende.exe` (+ sus dependencias en la misma
carpeta). Se puede probar directamente haciendo doble clic en ese `.exe`, sin instalar
nada — es útil para verificar que arrancó bien antes de generar el instalador.

**Base de datos semilla (obligatoria):** el `.spec` siempre empaqueta
`packaging/semilla/refrios.db` (generada con `utils.crear_semilla`, incluida en el
repositorio) y falla si no existe. Esa semilla solo trae el esquema y los roles fijos del
sistema — nunca usuarios, cursos ni resultados de ejemplo. La primera persona que abra la
app instalada ve la ventana de creación del primer administrador, no un login con una
cuenta ya hecha. El `.spec` nunca toma `database/refrios.db` (la base real de desarrollo):
volver a correr `utils.crear_semilla` después de cualquier cambio en `database/schema.sql`
para que la semilla empaquetada no quede desactualizada.

Después de compilar, verificar que el paquete no arrastra datos reales:

```
py packaging/verificar_paquete.py dist\RefriosAprende\_internal
```

## Paso 2 — Generar el instalador con Inno Setup

Requiere tener instalado [Inno Setup](https://jrsoftware.org/isinfo.php) (gratuito). Una
vez instalado (deja disponible el compilador `iscc`):

```
iscc packaging/instalador.iss
```

Resultado: `packaging/salida/RefriosAprende-Setup-<version>.exe` — este es el archivo que
se entrega al usuario final. Al ejecutarlo: instala en `Program Files`, crea el acceso
directo en el menú inicio (y en el escritorio si se marca esa opción), y dentro deja un
desinstalador estándar de Windows (aparece en "Agregar o quitar programas").

## Actualizar la versión

`APP_VERSION` en `config/settings.py` y `MyAppVersion` en `packaging/instalador.iss` se
mantienen sincronizados a mano — al subir de versión, actualizar ambos.
`tests/test_version.py` falla si alguna vez quedan desincronizados.

## Verificación antes de entregar un instalador

1. `py -m pytest -q` sobre el código fuente (no sobre el `.exe`) — sigue siendo la primera
   línea de defensa.
2. `py packaging/verificar_paquete.py dist\RefriosAprende\_internal` — confirma que el
   paquete compilado no trae usuarios, cursos ni resultados de ejemplo.
3. Ejecutar `dist/RefriosAprende/RefriosAprende.exe` directamente (sin instalar) en una
   sesión limpia (borrar antes `%LOCALAPPDATA%\RefriosAprende` si existe de una prueba
   anterior) y confirmar que aparece la ventana de primer administrador, se crea la cuenta
   y se puede iniciar sesión con ella.
4. Instalar con el `.exe` generado por Inno Setup en una cuenta de usuario normal (no
   administrador) y repetir la prueba de arranque — confirma que de verdad no hace falta
   ser administrador para usar la app día a día. Repetir `verificar_paquete.py` sobre la
   carpeta ya instalada (`%ProgramFiles%\RefriosAprende\_internal` o donde se haya elegido
   instalar).
5. Desinstalar y confirmar que `%LOCALAPPDATA%\RefriosAprende` sigue existiendo (los datos
   no se pierden).
6. `py packaging/generar_ficha_entrega.py` — deja una ficha en Markdown con la versión, el
   commit, las huellas SHA-256 del instalador y del paquete portable, y el resumen de la
   suite de pruebas. Exige que el árbol de git no tenga cambios sin confirmar.
