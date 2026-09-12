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
  `config/settings.py`). En arranques posteriores esa copia ya existe y **no se vuelve a
  pisar** — así nunca se borran datos reales del usuario al abrir la app de nuevo.

Desinstalar la app (o incluso borrarla de `Program Files` a mano) **no borra**
`%LOCALAPPDATA%\RefriosAprende\`: si se reinstala después, los datos siguen ahí.

## Paso 1 — Compilar con PyInstaller

Con el entorno virtual activado, desde la raíz de `RefriosAprende/`:

```
py -m pip install -r requirements-dev.txt
py -m PyInstaller packaging/refrios_aprende.spec
```

Resultado: `dist/RefriosAprende/RefriosAprende.exe` (+ sus dependencias en la misma
carpeta). Se puede probar directamente haciendo doble clic en ese `.exe`, sin instalar
nada — es útil para verificar que arrancó bien antes de generar el instalador.

**Base de datos precargada (opcional):** si al ejecutar `PyInstaller` existe el archivo
`database/refrios.db`, el `.spec` lo incluye automáticamente como "semilla de fábrica" —
la primera persona que abra la app instalada arrancará con esos datos. Para publicar una
versión en blanco (sin cursos ni usuarios de ejemplo), renombrar o mover ese archivo antes
de compilar.

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

## Verificación antes de entregar un instalador

1. `py -m pytest -q` sobre el código fuente (no sobre el `.exe`) — sigue siendo la primera
   línea de defensa.
2. Ejecutar `dist/RefriosAprende/RefriosAprende.exe` directamente (sin instalar) en una
   sesión limpia (borrar antes `%LOCALAPPDATA%\RefriosAprende` si existe de una prueba
   anterior) y confirmar que el login carga, con íconos/imágenes visibles.
3. Instalar con el `.exe` generado por Inno Setup en una cuenta de usuario normal (no
   administrador) y repetir la prueba de arranque — confirma que de verdad no hace falta
   ser administrador para usar la app día a día.
4. Desinstalar y confirmar que `%LOCALAPPDATA%\RefriosAprende` sigue existiendo (los datos
   no se pierden).
