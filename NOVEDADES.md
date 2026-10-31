## Pack 122 · 2026-10-31
- **Doble clic en el icono de la bandeja**: sin tecla, mostrar u ocultar todos los widgets; **Mayús**, widget nuevo (el predeterminado); **Ctrl**, set anterior; **Alt**, set siguiente. Mayús ya se lee en los gestos del icono (nuevos *Mayús + clic* y *Mayús + doble clic* en *Atajos de teclado → Gestos*). Solo cambian los valores por defecto: lo que ya hubieras asignado se respeta; Ctrl + doble clic (plegar todo) y Alt + doble clic (mostrar / ocultar) dejan de estar asignados salvo que los vuelvas a poner.
- **Rotación de sets editable**: *Sets de widgets → Elegir los sets de la rotación...* (o *Atajos de teclado → Gestos*) permite marcar y ordenar los sets por los que se mueven Ctrl / Alt + doble clic, *Set siguiente / anterior* y Ctrl + Mayús + ↑ / ↓. Sin lista rotan todos por orden alfabético. En el menú *Sets de widgets* los de la rotación llevan ↻.
- **Al pasar el ratón por el icono de la bandeja**: versión y número de pack, y número (ranura) y nombre del set activo.
- **Página de descarga**: muestra la versión y el pack actuales (y en el pie).
- **Notas de bienvenida**: «Sets de widgets» habla de widgets, «Mover una rama» aclara que incluye a las hijas de posición independiente y «Icono de la bandeja» cuenta los gestos nuevos (solo en instalaciones nuevas).

## Pack 121 · 2026-10-31
- **Un solo vocabulario en todos los menús y ventanas**: lo que antes se llamaba *template* / *estilo* / *perfil* ahora es **widget guardado** (un widget ya diseñado, con su texto), **forma de papel** (la nota base: forma, color, esquinas) y **set de widgets** (un conjunto de widgets colocados). *Packs de estilos* pasa a *Packs de widgets*; *Añadir* → *Agregar*, *Borrar* → *Eliminar*, y las etiquetas de los menús van en minúscula tras la primera palabra. Tus atajos de teclado y los gestos del icono de bandeja se migran solos a los nombres nuevos.
- **Menú del widget**: *Copiar / Pegar árbol (json)* y *Exportar árbol a un archivo...* salen de *Clonar* y pasan a la raíz, en una sección de gestión de widgets entre *Clonar* y *Eliminar*, junto con *Usar como predeterminado*. *Widget guardado* y *Forma de papel* conservan cada uno su propio copiar / pegar. Se quitan del menú del widget *Ocultar todos*, *Mostrar todos* y *Nuevo widget...* (siguen en el icono de la bandeja).
- **Icono de bandeja**: *Sets de widgets* incluye ahora *Eliminar todos los widgets del set activo...* y mantiene *Importar y exportar*; *Packs de widgets* queda dentro de *Guardar y cargar*; *Nueva nota & forma de papel...*.
- **Tamaño de las notas**: pegar una forma de papel o un widget guardado, o editar la forma de papel, ya no agranda el widget a su tamaño nominal: conserva el que tenía (las notas de bienvenida, más pequeñas, se mantenían pequeñas hasta el primer cambio y entonces saltaban).
- **Arreglos**: textos con caracteres corruptos (por ejemplo «Deshacer último cambio») corregidos.

## Pack 120 · 2026-10-31
- **Copiar, pegar y exportar un árbol de widgets**: clic derecho sobre un widget → *Clonar* → *Copiar árbol (json)* deja en el portapapeles el widget y todos sus descendientes como JSON (sin imágenes). *Pegar árbol (json)* lo añade al perfil activo con ids nuevos y la jerarquía intacta (también en *Importar y exportar → Pegar árbol copiado*). *Exportar árbol a un archivo...* guarda un `.json` que lleva dentro las imágenes que usan las notas; se importa en otro perfil o equipo con *Agregar widgets desde un archivo* o *Cargar un archivo*, sin pisar imágenes que ya existan.
- **Arreglo**: una imagen que Qt no podía leer abortaba la creación de la nota (`QPixmap.supportedImageFormats` no existe); ahora se usa `QImageReader`.

## Pack 119 · 2026-10-30
- **Imágenes que faltan al cargar una copia vieja**: un `.json` no lleva las imágenes de las notas, así que si faltan la nota enseñaba un cartel de error en lugar de su base. Ahora, al restaurar una copia, el programa avisa de cuáles faltan y *Importar y exportar → Buscar las imágenes que faltan (en otra carpeta)...* las recupera de la carpeta `widget_arena_data` de la versión anterior. Las notas base que el programa dibuja se rehacen solas.

## Pack 118 · 2026-10-30
- **Importar datos de otra instalación**: *Ajustes → Importar y exportar → Importar datos de otra instalación...*. Trae widgets, perfiles, templates, imágenes, ajustes, atajos y Telegram desde la carpeta `widget_arena_data` de una versión anterior (o desde un .zip). Guarda antes una copia de lo actual y no pisa nada.

## Pack 117 · 2026-10-30
- **Acerca de**: nuevo botón «Página del proyecto» que abre https://enderhugin.github.io/widget-arena/.

## Pack 116 · 2026-10-30
- **Linux**: corregida la detección de librerías del sistema. Ya no pide instalar `libXcomposite`, `libXdamage` o `libXrandr` cuando están instaladas (se comparaban mayúsculas con minúsculas), y también encuentra `ldconfig` en Debian aunque `/sbin` no esté en el PATH.
- **Notas de la instalación**: las notas de bienvenida y de ejemplo ya no nacen con «Siempre encima»: se quedan en el escritorio como una nota normal y se pueden activar en el menú de cada una. Solo afecta a instalaciones nuevas.

## Pack 115 · 2026-10-30
- **Elegir la fuente, con muestras**: la primera vez que abres el programa sale una ventana con una nota de ejemplo escrita con cada fuente (Kalam, Patrick Hand, Caveat, Inter u otra de tu equipo). El instalador ya no pregunta en la terminal.

## Pack 114 · 2026-10-30
- **Actualizaciones**: icono de bandeja → *Buscar actualizaciones...*. Al abrir el programa avisa si hay una versión nueva (puedes marcar «no mostrar más» y actualizar a mano). Guarda una copia de la versión anterior y permite volver a ella.

## Pack 113 · 2026-10-30
- **Fuentes**: Kalam, Patrick Hand y Caveat (libres) se descargan solas; sustituyen a Segoe Print cuando falta. *Ajustes → Apariencia → Fuente predeterminada...*.
- Al exportar un pack se pregunta por las fuentes (libres, del sistema, personal o para compartir).

## Pack 112 · 2026-10-29
- **Packs de estilos** (`.wapack`): importar, exportar y catálogo, con pack de ejemplo.
