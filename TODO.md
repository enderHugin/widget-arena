# Lista de pendientes

Orden propuesto. `[ ]` pendiente · `[x]` hecho (con el pack).

## Bugs
- [x] 1. (Pack 171) **Notas: respetar la alineación a la izquierda.** Si el texto está alineado a la izquierda debe obedecer; solo se centra automáticamente en vertical (ejemplo: «personales» sale centrado aunque está alineado a la izquierda).
- [x] 2. (Pack 172) **La corona se mueve con Ctrl+rueda (hue).** Revisar si pasa con otras acciones de rueda (tamaño, giro, zoom…) y arreglar la causa común.
- [x] 2b. (Pack 173) **Zona sensible más allá del widget con marco.** La zona de clic se limita al contorno exterior del marco (sin sombra) y se corrige el pintado de la zona con capa web + marco.

## Funciones
- [ ] 3. **Ajuste al mover widgets** (atajos de teclado o por defecto en la configuración): a otros widgets, a una rejilla configurable de líneas × columnas, a los límites de la pantalla.

## Diseño (acordar antes de tocar)
- [ ] 4. **Qué viaja al copiar/pegar forma de papel, marco o widget** (rotación, hue, dimensiones actuales…): qué se copia, qué se conserva del destino y cómo elegirlo. Caso típico: pegar un marco generado por el programa, modificado como imagen en el origen, y que el destino ajuste tamaños/hue y se pierda lo que se quería conservar.
- [ ] 5. **Capas/aspecto y exportar un widget «tal cual»** sin pasar por un menú titulado «Aspecto». Valorar unificar capas y aspecto. Afecta a los puntos 4 y 6.
- [ ] 6. **Grupos/familias de widgets** con subordinación («transparentes», «bordes redondeados», «reloj y calendarios modernos»…): navegables visualmente en el navegador de widgets y en un nuevo elemento del menú contextual de la bandeja para crear widgets; exportar packs por grupo (hoy solo «los de mi perfil» o individuales); los widgets conservan el flag de pertenencia al grupo (autor: X Smith).

## Pendientes del asistente (al final; no bloquean lo anterior)
- [ ] 7a. Pedir las líneas de registro de Linux `Ctrl+Alt+rueda: evento=… fisicas=…` (rotación fina).
- [ ] 7b. Probar los packs 167–170 con QtWebEngine real y en Windows:
  - si `grab()` del visor devuelve transparencia (Pack 169);
  - páginas casi transparentes con botones (Pack 169);
  - paso del clic al widget de debajo en Linux y macOS;
  - `indexedDB`, `sessionStorage` y eventos `storage` de las páginas locales (Packs 168/170);
  - línea de registro del Pack 170 «El sistema ha colocado el widget en…» (cable desajustado en la VM; el usuario prefiere que el widget pueda salirse de la pantalla);
  - rotación de la capa web con el marco (Ctrl+Alt+Shift): viable pero no barata; aparcada.

## Otros temas del usuario
- «Necesito varias cosas»: el usuario las dirá al terminar esta lista.
