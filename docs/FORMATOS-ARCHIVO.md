# Archivos `.waset`, `.wawidget` y `.wapaper`

Tres tipos de archivo para llevar tu trabajo de un equipo a otro o compartirlo. Los tres son un `.zip` con la misma estructura (los packs `.wapack` son otro formato, en [FORMATO-WAPACK.md](FORMATO-WAPACK.md)).

| Extensión | Qué lleva | Qué hace al cargarlo |
|---|---|---|
| `.waset` | Widgets con su jerarquía y cables: un árbol, o todos los del set activo; opcionalmente la configuración y los atajos | Agregarlos, guardarlos como un set nuevo o reemplazar el set activo |
| `.wawidget` | Un widget guardado (aspecto y contenido) | Se añade a tus widgets guardados, o sustituye el aspecto de un widget |
| `.wapaper` | Una forma de papel (forma, colores, borde, sombra), sin texto ni posición | Se añade a tus formas de papel, o se aplica a un widget conservando su texto |

## Contenido del zip

```
wa.json       {"format": "widget-arena-file", "format_version": 1, "kind": "set" | "widget" | "paper", "app_pack": N, "created": "...", "images": N}
data.json     lo mismo que llevaba el .json de siempre (ver abajo)
images/...    imágenes de capa
sticky/...    imágenes de notas
frames/...    marcos
```

- Se reconocen por el contenido (`wa.json`), no por la extensión: renombrar un `.waset` no lo rompe.
- `data.json` de un `.waset` es `{id_de_widget: estado, ..., "__config__": {...}}`; `__config__` puede llevar `arbol` (qué árbol es), `settings` y `hotkeys`. De un `.wawidget` o un `.wapaper`, es el *template* del widget.
- Las imágenes están en el zip con su ruta portable (`images/x.png`, `sticky/x.png`, `frames/x.png`); las capas de `data.json` apuntan a `widget_arena_data/<carpeta>/<nombre>`. Al cargar, se copian a la carpeta de datos **sin pisar nada**: lo idéntico se salta y una imagen distinta con el mismo nombre entra como «nombre (importado).png».
- **Las formas de papel no se guardan como bitmap**: su imagen se redibuja desde sus parámetros (`base_note`).
- Los `.json` de versiones anteriores (con las imágenes en base64) se siguen leyendo, y se pueden escribir eligiendo ese tipo al guardar.
- Nunca incluye datos de Telegram.
