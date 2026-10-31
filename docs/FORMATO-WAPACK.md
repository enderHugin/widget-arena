# Formato `.wapack` (packs de widgets de Widget Arena)

Un pack es un archivo **`.wapack`**: un `.zip` normal (se puede abrir con cualquier programa de zip) con estilos de notas,
conjuntos de widgets colocados y las imágenes que usan. Sirve para compartir, vender o estrenar aspectos sin pasar archivos sueltos.

*English: a `.wapack` is a plain zip holding note styles (templates), ready-made widget sets and the images they use. The app reads it in place; only what you use is copied.*

## Cómo se usa

- **Instalar:** arrastra el `.wapack` a la ventana *Guardar y cargar* o a *Packs de widgets* (menú del icono → *Guardar y cargar* → *Packs de widgets...*), o usa *Cargar un archivo*.
  Se copia a la carpeta `packs/` de tus datos. No se extrae nada.
- **Usar un estilo:** *Packs de widgets* → elige uno o varios → *Agregar a mis widgets guardados* o *Crear una nota con este widget guardado*.
  Solo se copian las imágenes que ese estilo necesita, y lo que queda son archivos normales: no dependen del pack.
- **Usar un set:** *Agregar a mis sets* o *Abrir el set ahora*. Nunca pisa uno tuyo con el mismo nombre.
- **Quitar un pack:** borra el archivo; lo que ya agregaste a tus widgets guardados y sets sigue funcionando.
- **Crear el tuyo:** *Packs de widgets* → *Exportar mis widgets y sets...*. Eliges qué entra y las imágenes se meten solas.

## Estructura

```
mi-pack.wapack  (zip)
  pack.json            manifiesto (obligatorio)
  cover.png            portada (opcional)
  LICENSE.txt          texto de la licencia (opcional)
  styles/<id>.json     un template por archivo
  previews/<id>.png    vista previa de cada estilo (opcional, pero recomendable)
  sets/<id>.json       un perfil (conjunto de widgets con sus enlaces) por archivo
  assets/<hash>.png    imágenes propias (png, jpg, gif, webp, bmp); el nombre es el hash de su contenido
  fonts/*.ttf|otf      fuentes (opcional; solo si su licencia permite redistribuirlas)
```

Todas las rutas del zip usan `/`, son relativas y no contienen `..`. Las que no cumplen esto se ignoran.

## `pack.json`

```json
{
  "format": "widget-arena-pack",
  "format_version": 1,
  "min_reader": 1,
  "render_v": 1,
  "id": "notas-de-colores",
  "name": "Notas de colores",
  "author": "Widget Arena",
  "version": "1.0.0",
  "license": "CC0 (dominio público)",
  "description": "Ocho colores de nota doblada y dos tableros de ejemplo.",
  "created": "2026-10-29T16:57:00",
  "styles": [ { "file": "styles/menta.json", "name": "Menta", "preview": "previews/menta.png" } ],
  "sets":   [ { "file": "sets/bienvenida.json", "name": "Bienvenida", "notes": 10 } ],
  "fonts":  [ { "file": "fonts/Mi.ttf", "family": "Mi Fuente", "license": "OFL" } ],
  "fonts_used": ["Segoe Print"],
  "fonts_scope": "personal",
  "font_fallbacks": { "Segoe Print": ["Kalam", "Patrick Hand", "Caveat"] }
}
```

| Campo | Para qué |
|---|---|
| `format` | Debe ser `widget-arena-pack`. |
| `format_version` / `min_reader` | Versión del formato y versión mínima de lector que lo entiende. Un programa que no llega a `min_reader` se niega a abrirlo y lo dice. |
| `render_v` | Versión del dibujado de las notas base con la que se hizo el pack (ver abajo). |
| `id` | Nombre corto único (`a-z`, `0-9`, `-`). Dos packs con el mismo `id` son el mismo pack (se ofrece sustituir). |
| `version` | Números separados por puntos; se compara numéricamente. |
| `styles`, `sets` | Listas de lo que hay dentro. Si faltan, se descubren por las carpetas `styles/` y `sets/`. |
| `fonts_used` | Informativo: familias de letra que usan los estilos. Si el equipo no las tiene, se avisa. |
| `fonts_scope` | Solo si hay `fonts`: `personal` (copia para los equipos de su autor) o `share` (el autor declaró que puede redistribuirlas). |
| `fonts[].license` | Informativo: licencia reconocida en la propia fuente (`OFL`, `Apache 2.0`...) o vacío. |
| `font_fallbacks` | Informativo: familias sustitutas sugeridas para las fuentes propietarias. El programa usa las suyas (ver más abajo). |

Los campos desconocidos se ignoran, así que se pueden añadir más sin romper nada.

## Estilos (`styles/*.json`)

Es un template normal del programa, con dos diferencias para que viaje bien:

1. **Capa 2 generada.** Si la imagen de la nota la dibuja el programa (notas base: curl, sombra, degradado...), la capa lleva `"source": "generated"` y `"content": ""`,
   y el template conserva `base_note` con todos los parámetros. Al usarla, la imagen se **vuelve a dibujar** (queda idéntica) y la nota sigue siendo
   editable con *Editar forma*. El pack no guarda ningún bitmap de ella.
2. **Imágenes propias.** Cualquier otra imagen se guarda en `assets/` con el hash de su contenido y se cita como `"content": "asset:<hash>.<ext>"`.
   Nunca hay rutas del equipo de origen (ni barras de Windows). Las direcciones web (`https://...`) se dejan como están.

Los efectos (`image_effects`: tono, saturación...), el giro, la geometría y los colores son parámetros de capa y viajan en el JSON sin más.
`base_hue_src`, si existe, vale lo mismo que `content` (el programa lo sustituye por la ruta final).

`render_v` dentro de `base_note` es la versión del dibujado; al instalar el estilo se quita. Si algún día cambia el dibujado, el programa lo sabrá por este número.

## Perfiles (`sets/*.json`)

Mismo formato que un perfil del programa: `{ "widget_1": { "template_data": {...}, "parent_id": "...", "collapsed": false, ... }, ... }`.
Se conservan los enlaces padre/hijo, el plegado y los ajustes de jerarquía (`hierarchy_settings*`). Se pasan por la misma normalización de imágenes que los estilos.
Los datos personales (por ejemplo, la configuración de Telegram) no se exportan nunca: solo salen las notas.

## Límites y seguridad

- Un pack se **lee en el sitio**: no se extrae a ninguna carpeta. No se ejecuta nada de su contenido.
- Se rechazan los nombres con `..`, rutas absolutas o letras de unidad; más de 4000 archivos; más de 600 MB descomprimido; JSON de más de 8 MB; imágenes de más de 40 MB.
- Un `.zip` cualquiera (por ejemplo, una copia de seguridad del programa) no es un pack: hace falta `pack.json` con `format` correcto.

## Licencia y fuentes

El programa es MIT, pero **lo que contiene un pack es de quien lo crea**: ponle la licencia que quieras en `license` y en `LICENSE.txt`.
Las letras (fuentes) suelen tener licencias propias: incluye solo las que permitan redistribución (por ejemplo, las de Google Fonts) o no las incluyas y decláralas en
`fonts_used`. Las de Windows (como Segoe Print) **no** se pueden redistribuir.

Al exportar, el programa pregunta por las fuentes que usan los estilos y perfiles elegidos: las libres de la aplicación (Kalam, Patrick Hand y Caveat, licencia
OFL) no hace falta incluirlas porque se descargan solas; las del sistema (Windows, macOS) no se pueden incluir; las demás se incluyen solo si las marcas y
confirmas que puedes hacerlo, y el pack anota si son de uso personal o para compartir. Lo que figura en el pack es una declaración de su autor, no una garantía legal.

**Si falta una fuente.** Cuando el equipo no tiene la fuente pedida por un widget, Qt usa la primera disponible de esta lista: la *fuente predeterminada* que haya
elegido el usuario, luego Kalam, Patrick Hand, Caveat y las manuscritas de macOS (Bradley Hand, Noteworthy, Marker Felt). Solo se sustituyen familias conocidas
(Segoe Print, Ink Free, Comic Sans MS, Bradley Hand, etc.); si la fuente existe en el equipo, se usa ella siempre.

## Compatibilidad

- Un estilo o un perfil que sale de un pack es un archivo normal: lo abre cualquier versión del programa. Lo que añade este formato (`origin`, `source`) se ignora donde no se conoce.
- Los datos que ya tenías no se tocan. Las rutas guardadas por versiones antiguas (con `\` de Windows, relativas a `widget_arena_data`, o solo el nombre del archivo) siguen funcionando y al exportar se normalizan.
- Si falta la imagen de una nota base (por ejemplo, porque borraste la carpeta `sticky/`), se vuelve a dibujar al cargar.
