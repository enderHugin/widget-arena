# Widget Arena

**Notas y widgets en tu escritorio, muy usables y configurables, pensados para el uso diario.**
Conecta las notas con cables, jerarquízalas en padres e hijos y pliega o despliega grupos enteros para ordenar la vista.
Funciona en Windows, macOS y Linux, con instalación de un clic.

*Desktop notes and widgets, highly usable and configurable, built for daily use. Link notes with cables, organise them as parents and children, and collapse or expand whole groups. Windows, macOS and Linux, one-click install.*

## Qué puedes hacer

- **Notas y widgets flotantes** sobre el escritorio: texto, imágenes y páginas web, cada uno con sus capas, fuente, color, giro y tamaño.
- **Conectar**: enlaza una nota con otra y los dos widgets quedan unidos por un cable, que cuelga como una cuerda con física y se balancea al moverlos.
- **Jerarquizar**: padres, hijos, nietos… Los hijos pueden seguir al padre cuando lo arrastras, y puedes mover una rama entera.
- **Plegar y desplegar**: oculta los hijos de una nota (o de todas) para ver solo lo que importa, y recupéralos cuando quieras.
- **Perfiles**: guarda conjuntos completos de widgets y cambia entre ellos al instante con el teclado.
- **Packs de estilos**: comparte o estrena estilos y tableros en un solo archivo `.wapack`; exporta lo que ya tienes.
- **Configurable a fondo**: cables (grosor, opacidad, degradado, cuerda, calidad de dibujo), estilos de nota, templates, atajos de teclado y gestos del icono de bandeja.
- **Rápido y ligero**: la calidad de dibujo de los cables se adapta sola al ordenador.
- **Tus datos son tuyos**: todo se guarda en archivos JSON en tu carpeta de usuario, con copias de seguridad.

## Instalar (un clic)

Entra en la página del proyecto y pulsa el botón: detecta tu sistema y descarga el instalador que toca.
No hace falta tener Python ni ser administrador: el instalador prepara su propio Python y las librerías,
instala el programa **solo para tu usuario**, crea los accesos directos con su icono y lo abre.

| Sistema | Qué haces |
|---|---|
| **Windows** 10/11 (64 bits) | Abre `install-windows.cmd`. Si SmartScreen avisa: *Más información → Ejecutar de todas formas*. |
| **macOS** 12+ | Abre `install-macos.zip` y haz doble clic en `Widget Arena.command` (si avisa: clic derecho → *Abrir*). |
| **Linux** (glibc) | `curl -fsSL <URL de la página>/dl/install-linux.sh \| bash` |

La primera vez descarga unos cientos de MB (Qt). Volver a ejecutar el instalador **actualiza** el programa y conserva tus notas.

**Desinstalar:** en Windows, *Configuración → Aplicaciones → Widget Arena*. En Linux/macOS, `bash ~/.local/share/WidgetArena/uninstall.sh`
(macOS: `~/Library/Application Support/WidgetArena/uninstall.sh`). Te pregunta si quieres borrar también tus datos.

### Por qué el sistema avisa
Los instaladores no están firmados con un certificado de pago, así que Windows y macOS avisan ante cualquier archivo descargado que no conocen.
Todo el código está en este repositorio (`installers/`) para que puedas leerlo antes de ejecutarlo.

## Primer arranque

La primera vez que se abre aparece el perfil **Bienvenida**: doce notas enlazadas por cables que sirven de tutorial (mover y enlazar con **Ctrl** / **Alt** + arrastrar,
crear y clonar hijas, gestos y ayuda con **F1**, cambiar el tono con **Ctrl + rueda**, mover una rama entera, plegar y desplegar hijos, perfiles con **Ctrl + 1…0** y el icono de la bandeja).
Además queda guardado un perfil de ejemplo de uso diario, «Ejemplo - semana», para que veas cómo se organiza un tablero real; cámbialo con **Ctrl + 2** (y vuelve con **Ctrl + 1**)
o desde el menú del icono de bandeja → *Perfiles*. Puedes borrarlos cuando quieras: no vuelven a aparecer.

## Actualizaciones

*Icono de bandeja → Buscar actualizaciones...* compara tu versión con la publicada en esta página (`dl/update.json`: número de pack, huellas sha256 y novedades).
Si hay una más nueva, la descarga, comprueba que coincide con la huella y que es Python válido, **guarda una copia de la tuya** (carpeta `backups_programa/`) y reinicia el programa.
Tus notas, perfiles y ajustes no se tocan, y *Volver a la versión anterior* restaura la copia. Nunca baja de versión: si tu copia es más nueva que la publicada, no hace nada.

Al abrir el programa pregunta, como cualquier aplicación, si hay una versión nueva («¿Descargarla e instalarla ahora?»). Marca *No mostrar más este mensaje* si prefieres actualizar a mano;
se vuelve a activar en la ventana de actualizaciones. Es una conexión más a esta página; `WA_OFFLINE=1` la desactiva. En una instalación como ejecutable no se actualiza sola: baja el instalador nuevo.

## Traer los datos de otra versión

Si usabas una versión anterior (o otro equipo), no hace falta copiar nada a mano: **Ajustes → Importar y exportar → Importar datos de otra instalación...**
Elige la carpeta `widget_arena_data` de la versión anterior (suele estar junto al programa), la carpeta que la contiene, o una copia completa `.zip`, y marca lo que quieras traer:
widgets (sustituyendo, añadiendo a los actuales o como perfil nuevo), perfiles, templates, imágenes y marcos, ajustes, atajos de teclado y la conexión con Telegram.

- Antes de tocar nada se guarda una copia completa de lo que tenías.
- Nunca se pisa un archivo que ya exista con otro contenido: el importado entra con otro nombre («... (importado)»).
- Las rutas de las imágenes se ajustan solas, también las absolutas de otro equipo o de Windows.
- Una copia completa `.zip` solo lleva los `.json`; para traer también las imágenes usa la carpeta.
- Si cargas una copia vieja (un `.json`) y alguna nota se queda sin su base o su imagen, el programa avisa de cuáles faltan; *Importar y exportar → Buscar las imágenes que faltan (en otra carpeta)...* las recupera de la carpeta `widget_arena_data` de la versión anterior.

## Fuentes

Las notas de ejemplo usan **Segoe Print**, una letra de Windows que no se puede redistribuir. Fuera de Windows (o si no la tienes) se sustituye sola por una fuente libre
parecida. Widget Arena trae tres, con licencia SIL Open Font License (están en `defaults/fonts/`, con su licencia): **Kalam** (la más parecida, redonda y ancha),
**Patrick Hand** (clara y compacta) y **Caveat** (estrecha y caligráfica).

- La primera vez que abres el programa te lo pregunta en una ventana con muestras: cada opción enseña una nota escrita con esa fuente, y eliges la que quieres como **fuente predeterminada** (la de las notas nuevas y la que sustituye a una que falta).
  Puedes cambiarla cuando quieras en *icono de bandeja → Ajustes → Apariencia → Fuente predeterminada...*.
- Si falta alguna de las tres, el programa la descarga sola, en segundo plano, de esta misma página (`dl/fonts/`) y comprueba su huella sha256. Junto con la comprobación de versiones, son las únicas conexiones que hace por su cuenta;
  sin red no pasa nada y lo reintenta pasadas unas horas. Para desactivarla, define la variable de entorno `WA_OFFLINE=1`.
- Al **exportar un pack** te pregunta por las fuentes que usa: las del sistema no se pueden incluir, las libres se marcan solas y las demás solo se incluyen si confirmas que tienes derecho.

## Packs de estilos

Un **pack** (`.wapack`, un zip) reúne estilos de notas y conjuntos de widgets ya colocados, con las imágenes que usan, para compartir o estrenar.
Abre *icono de bandeja → Packs de estilos...* (o arrastra un `.wapack` a la ventana *Guardar y cargar*): ves sus estilos con vista previa y los añades a tus
templates y perfiles. Las notas base no guardan imagen: se vuelven a dibujar y se pueden seguir editando. También puedes **exportar lo que ya tienes**
(*Exportar mis estilos y widgets...*), y tus notas, estilos y perfiles de siempre se leen sin cambios.

Con el primer arranque se instala un pack de ejemplo, **Notas de colores** (8 colores y dos tableros). Descárgalo también desde la página: `dl/notas-de-colores.wapack`.
El formato está descrito en [docs/FORMATO-WAPACK.md](docs/FORMATO-WAPACK.md).

## Gestos y atajos más útiles

| Gesto | Qué hace |
|---|---|
| Clic derecho en una nota | Menú del widget: capas, aspecto, relaciones, clonar, eliminar |
| Arrastrar | Mover el widget (los hijos con posición ligada lo siguen) |
| **Ctrl** + arrastrar sobre otra nota | Enlazar: pasa a ser **hija** de la nota donde sueltas |
| **Alt** + arrastrar sobre otra nota | Enlazar: pasa a ser **padre** de la nota donde sueltas |
| **Ctrl + Alt + Win** + arrastrar | Mover el widget con todos sus descendientes |
| **Ctrl + Alt + Mayús** + arrastrar | Crear un hijo bajo el cursor |
| Doble clic | Ocultar el widget (pide confirmación) |
| **Ctrl + 1…0** | Cargar el perfil número N |
| **Ctrl + Alt + B** | Navegador de todos tus widgets |
| **F1** | Guía de gestos y atajos completa |

Mantén **Ctrl**, **Alt**, **Mayús** o **Win** sobre una nota y aparece un recuadro con lo que hace cada gesto.
Los atajos se pueden cambiar en *icono de bandeja → Ajustes → Atajos de teclado*.

## Ejecutar sin instalar (para desarrollo)

```bash
python widget_arena.py        # Python 3.12 o superior
```

La primera vez comprueba que están `numpy` y `PySide6` y ofrece instalarlos. `herramientas.py` (también por doble clic) instala, desinstala,
compila un ejecutable o deja el programa en modo portable.

## Cómo está montado

- `widget_arena.py`: el programa (un solo archivo).
- `herramientas.py`: instalar / desinstalar / compilar / librerías de cualquier `.py` de la carpeta.
- `defaults/`: lo que se copia en el primer arranque (notas de bienvenida, perfil de ejemplo, estilo de nota y el pack de ejemplo en `defaults/packs/`).
- `docs/FORMATO-WAPACK.md`: especificación del formato de los packs.
- `installers/`: `install-windows.cmd` (con PowerShell dentro) e `install-unix.sh` (Linux y macOS). Descargan `uv`, un Python 3.12 propio, y llaman a `herramientas.py install`.
- `site/` y `tools/build_site.sh`: la página con el botón único y el montaje de lo que se publica.
- `.github/workflows/pages.yml`: publica la página en GitHub Pages en cada cambio; calcula las URLs solo.

### Activar la página (una sola vez)
En el repositorio: **Settings → Pages → Build and deployment → Source: GitHub Actions**. Después, cada `push` a `main` la publica.

## Apoyar el proyecto

Es gratis y sin anuncios. Si te resulta útil, puedes invitarme a un café:

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Inv%C3%ADtame%20a%20un%20caf%C3%A9-ff5e5b?logo=ko-fi&logoColor=white&style=for-the-badge)](https://ko-fi.com/jaimeluisolguinmesina)

## Si algo no funciona: los registros

Si el acceso del menú no abre nada o el instalador falla, hay archivos de registro que dicen por qué. Si el programa no llega a abrirse, además sale una ventana con el motivo.

| Qué | Windows | Linux | macOS |
|---|---|---|---|
| Instalación | `%LOCALAPPDATA%\WidgetArena\logs\instalacion.log` | `~/.local/share/WidgetArena/logs/instalacion.log` | `~/Library/Application Support/WidgetArena/logs/instalacion.log` |
| Arranque (lo que pasa al pulsar el icono) | `%LOCALAPPDATA%\Programs\WidgetArena\arranque.log` | `~/.local/share/WidgetArena/app/arranque.log` | `~/Applications/WidgetArena/arranque.log` |
| El programa en marcha | `%APPDATA%\WidgetArena\data\logs\` | `~/.local/share/WidgetArena/data/logs/` | `~/Library/Application Support/WidgetArena/data/logs/` |

Si abres una incidencia, adjunta `instalacion.log` y `arranque.log`.

## Licencia

MIT. Ver [LICENSE](LICENSE).
