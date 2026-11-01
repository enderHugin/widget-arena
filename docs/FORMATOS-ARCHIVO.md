# Archivos `.waset`, `.wawidget`, `.wapaper` y `.waframe`

Cuatro tipos de archivo para llevar tu trabajo de un equipo a otro o compartirlo. Todos son un `.zip` con la misma estructura (los packs `.wapack` son otro formato, en [FORMATO-WAPACK.md](FORMATO-WAPACK.md)).

| Extensión | Qué lleva | Qué hace al cargarlo |
|---|---|---|
| `.waset` | Widgets con su jerarquía y cables: un árbol, o todos los del set activo; opcionalmente la configuración y los atajos | Agregarlos, guardarlos como un set nuevo o reemplazar el set activo |
| `.wawidget` | Un widget guardado (aspecto y contenido) | Se añade a tus widgets guardados, o sustituye el aspecto de un widget |
| `.wapaper` | Una forma de papel (forma, colores, borde, sombra), sin texto ni posición | Se añade a tus formas de papel, o se aplica a un widget conservando su texto |
| `.waframe` | Un marco: sus parámetros (grosor de cada lado, color o degradado, bisel, textura, sombras, forma) y una miniatura `preview.png` | Se guarda en *Mis marcos* (carpeta `marcos/` de los datos); desde el editor de marcos o el menú *Aspecto → Marco* del widget se pone en un widget conservando su tamaño |

## Contenido del zip

```
wa.json       {"format": "widget-arena-file", "format_version": 1, "kind": "set" | "widget" | "paper" | "frame", "app_pack": N, "created": "...", "images": N}
data.json     lo mismo que llevaba el .json de siempre (ver abajo)
images/...    imágenes de capa
sticky/...    imágenes de notas
frames/...    marcos
```

- Se reconocen por el contenido (`wa.json`), no por la extensión: renombrar un `.waset` no lo rompe.
- `data.json` de un `.waset` es `{id_de_widget: estado, ..., "__config__": {...}}`; `__config__` puede llevar `arbol` (qué árbol es), `settings` y `hotkeys`. De un `.wawidget` o un `.wapaper`, es el *template* del widget. De un `.waframe` es `{"name": "...", "frame_shape": {parámetros}}`: sin imágenes de marco, que se dibujan al ponerlo. El editor de marcos también lee y escribe un `.json` con `{"frame_shape": {...}}` (el que copia *Copiar marco*).
- Las imágenes están en el zip con su ruta portable (`images/x.png`, `sticky/x.png`, `frames/x.png`); las capas de `data.json` apuntan a `widget_arena_data/<carpeta>/<nombre>`. Al cargar, se copian a la carpeta de datos **sin pisar nada**: lo idéntico se salta y una imagen distinta con el mismo nombre entra como «nombre (importado).png».
- **Las formas de papel no se guardan como bitmap**: su imagen se redibuja desde sus parámetros (`base_note`).
- Los `.json` de versiones anteriores (con las imágenes en base64) se siguen leyendo, y se pueden escribir eligiendo ese tipo al guardar.
- Nunca incluye datos de Telegram.
