# Lista de pendientes

Orden propuesto. `[ ]` pendiente · `[x]` hecho (con el pack).

## Bugs
- [x] 1. (Pack 171) **Notas: respetar la alineación a la izquierda.** Si el texto está alineado a la izquierda debe obedecer; solo se centra automáticamente en vertical (ejemplo: «personales» sale centrado aunque está alineado a la izquierda).
- [x] 2. (Pack 172) **La corona se mueve con Ctrl+rueda (hue).** Revisar si pasa con otras acciones de rueda (tamaño, giro, zoom…) y arreglar la causa común.
- [x] 2b. (Pack 173) **Zona sensible más allá del widget con marco.** La zona de clic se limita al contorno exterior del marco (sin sombra) y se corrige el pintado de la zona con capa web + marco.

## Funciones
- [x] 3. (Pack 185) **Ajuste al mover widgets** (atajos de teclado o por defecto en la configuración): a otros widgets, a una rejilla configurable de líneas × columnas, a los límites de la pantalla.

## Diseño (acordar antes de tocar)
- [ ] 4. **Qué viaja al copiar/pegar forma de papel, marco o widget** (rotación, hue, dimensiones actuales…): qué se copia, qué se conserva del destino y cómo elegirlo. Caso típico: pegar un marco generado por el programa, modificado como imagen en el origen, y que el destino ajuste tamaños/hue y se pierda lo que se quería conservar.
- [x] 5. (Pack 176) **Capas/aspecto unificados:** el menú del widget se reparte por función (Widget / Contenido / Forma y borde / Color y efectos / Posición y tamaño / Corona); exportar el widget «tal cual» está en *Widget ▸ Exportar widget a un archivo…*. Queda decidir el punto 4 (qué viaja al copiar/pegar forma de papel, marco y widget).
- [x] 5b. (Pack 175) **Concepto «modelo»:** pasa a «widget»; la biblioteca es «Mis widgets»; «Guardar widget», «Sustituir widget». Queda el menú del widget por función (Pack 176, opción B: Widget / Contenido / Forma y borde / Color y efectos / Posición y tamaño / Corona), que cierra también el punto 5.
- [ ] 6. **Grupos/familias de widgets** con subordinación («transparentes», «bordes redondeados», «reloj y calendarios modernos»…): navegables visualmente en el navegador de widgets y en un nuevo elemento del menú contextual de la bandeja para crear widgets; exportar packs por grupo (hoy solo «los de mi perfil» o individuales); los widgets conservan el flag de pertenencia al grupo (autor: X Smith).
  - Pack 174 (hecho): autor + familias (varias a la vez) en cada modelo, filtro/agrupación en Modelos y Navegador, submenú de bandeja, exportar familia, nombre de autor. **Falta:** registro/verificación de autores y de quién puede añadir a una familia (concursos), carpetas de familias en el modo usuario, ordenar/ver familias en más sitios.

## Nuevo (propuesto por ti, a diseñar)
- [ ] 8. **Crear y transformar widgets desde una interfaz («constructor»)**: hoy crear uno de cero es una odisea (elegir capa, navegar por el disco…). Y en una nota (capa 1 = texto) no se puede poner un marco generado en la capa 1 («Marco» sale desactivado). Idea: ventana con vista previa en vivo y pasos (fondo, marco, contenido, forma) que sirva para crear uno nuevo y para cambiar uno existente.

## Nuevos (2026-11-11)
- [x] 9. (Pack 183) **Bug (vídeo): rastro del texto anterior en modo edición** de una nota. Probable causa: entrar en edición no desactiva el «brillo por hover».
- [x] 10. (Pack 183) **Bug (vídeo): «Editar forma de papel» cambia los colores** del widget.
- [x] 11. (Pack 184) **Hotkeys para TODAS las opciones de los menús contextuales**, incluidas las de edición de texto, que hoy no tienen (alineación/justificado, color, fuente…).
- [x] 12. (Pack 184) **Edición de texto: rotar entre fuentes elegidas por el usuario** (lista personal de fuentes favoritas). **Bug:** con Ctrl+Mayús+rueda la lista de fuentes a veces no sale completa (solo una parte).
- [x] 13. (Pack 186; queda el blur a través de transparencias → punto 14) **Flechas entre widgets** (nueva capa de dependencias, aparte de los cables): relaciones entre ramas de árboles que en principio no dependían entre sí; sin los problemas de recursión y bucles infinitos de la idea anterior. Con su propia edición de apariencia y **toda la familia de opciones de los cables, pero propia** (colores, grosor, opacidad, degradado…).
- [x] 14. (Pack 187) **Desenfoque (blur) de lo que se ve a través de widgets transparentes:** hoy los cables, widgets y (futuras) flechas que no entran ni salen directamente de ese widget se ven nítidos a través de la transparencia; deben verse con blur **editable**. Para (1) flechas, (2) widgets y (3) cables.

## Pendientes del asistente (al final; no bloquean lo anterior)
- [ ] 7a. Pedir las líneas de registro de Linux `Ctrl+Alt+rueda: evento=… fisicas=…` (rotación fina).
- [ ] 7b. Probar los packs 167–170 con QtWebEngine real y en Windows:
  - si `grab()` del visor devuelve transparencia (Pack 169);
  - páginas casi transparentes con botones (Pack 169);
  - paso del clic al widget de debajo en Linux y macOS;
  - `indexedDB`, `sessionStorage` y eventos `storage` de las páginas locales (Packs 168/170);
  - línea de registro del Pack 170 «El sistema ha colocado el widget en…» (cable desajustado en la VM; el usuario prefiere que el widget pueda salirse de la pantalla);
  - rotación de la capa web con el marco (Ctrl+Alt+Shift): viable pero no barata; aparcada.

## Opciones ocultas
- [x] Pack 182: casilla del vigilante de actualizaciones, oculta; se muestra con Mayús+Ctrl+Win+Alt+F12 en la ventana *Actualizaciones*.

## Página web (GitHub Pages)
- [x] Contador de descargas (GoatCounter, sitio `enderhugin`), por sistema, con enlace a las estadísticas (país, sistema, procedencia); autor/versión/licencia del pack de ejemplo (`dl/packs.json`).
- [ ] En GoatCounter (Settings → Site): activar «Allow adding visitor counts on your website» (si no, la página no enseña cifras) y «Allow public view» (para el enlace a las estadísticas).
- [ ] Comentarios con Telegram: crear un canal público con grupo de debate enlazado, publicar un mensaje y poner `canal/número` en `SITE.telegram` de `site/index.html`.

## Otros temas del usuario
- «Necesito varias cosas»: el usuario las dirá al terminar esta lista.
