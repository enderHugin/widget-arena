## Pack 208 · 2026-11-14
- **Más fluidez al arrastrar grupos, sin tocar la calidad de imagen:**
  - **Las flechas del grupo se desplazan con él sin repintarse.** Si todas las flechas que se ven se han movido lo mismo (van entre widgets del grupo que arrastras), su ventana se desplaza con el grupo. Si alguna va a un widget que se queda quieto, se repintan como siempre. Arrastrando un grupo de 22 widgets con 6 flechas, la ventana de las flechas pasa de repintarse en cada paso (62 veces) a 4 (solo mientras aparecen).
  - **Windows: todas las ventanas del grupo se mueven en una sola operación del sistema.** Ya no van unas por detrás de otras, como se veía en el vídeo. Al empezar el arrastre se comprueba que las coordenadas de Qt y las del sistema cuadran en esa pantalla. Si no cuadran, o si el grupo pasa a otra pantalla, se mueven de una en una como antes. Si algo falla, se apaga solo para el resto de la sesión.
  - **Los widgets ocultos que siguen al grupo (ramas plegadas) no se mueven en cada paso:** van a su sitio al soltar.
  - Medido aquí, arrastrando 22 widgets (CPU por fotograma):
    - con 6 flechas: de 14,1 a 9,6 ms;
    - con 6 flechas y un widget transparente: de 42,2 a 13,9 ms.
- **Arreglo: la silueta del papel cambiaba 1-2 px de alto o de ancho según la posición del widget.** Python redondea los ,5 al número par. Al arrastrar, las flechas y el borde de los cables temblaban un píxel. Ahora la silueta es siempre la misma, solo desplazada.
- **`rendimiento.log`: resumen de cada arrastre lento.** Anota cuántos pasos por segundo se consiguen, cuánto cuesta mover las ventanas, cuánto los cables, cuánto tarda lo demás entre paso y paso (pintar, enviar a la pantalla) y si se usó el movimiento conjunto de Windows.

## Pack 207 · 2026-11-14
- **Arrastrar grupos de widgets va mucho más fluido, en todos los sistemas.** En el vídeo, al mover un árbol entero con sus cables, la imagen se actualizaba unas 6-7 veces por segundo. Cambios:
  - **Si se mueve el grupo entero, los cables se desplazan con él sin repintarse.** Pasa cuando todos los cables que se ven van entre widgets que se mueven juntos, como al arrastrar la raíz con sus descendientes. Entonces el dibujo no cambia, solo se desplaza: la ventana de los cables (y la corona) se mueve con el grupo, van pegados y no cuesta nada.
    - Solo se repinta para que las cuerdas con física se balanceen, a su ritmo y sin pasar de un cuarto del tiempo.
    - Si hace falta cubrir otra zona o pantalla, o si los cables pasan bajo un widget transparente que no se mueve con ellos, se repintan como siempre.
  - **El arrastre se aplica a un ritmo que el equipo aguanta.** Los movimientos del ratón que llegan más deprisa de lo que da tiempo a mover el grupo se juntan en uno: se aplica el último, con un hueco según lo que cuesta (entre 7 y 33 ms). El programa ya no se satura con ratones muy rápidos. Al soltar siempre se aplica la última posición.
  - **La silueta del papel y su región se calculan una vez.** Antes se calculaban por cada cable y en cada fotograma, con un json de por medio. Al mover un widget no se recalculan.
  - **Un cable solo se difumina a través de un widget transparente si de verdad pasa por debajo.** Antes bastaba con que el widget estuviera a menos de 300 px.
  - **Sin widgets transparentes a la vista no se calcula ningún velo.**
  - Medido aquí, arrastrando un grupo de 22 widgets con sus cables (CPU por fotograma):
    - sin transparentes: de 13,5 a 8 ms;
    - con uno transparente en el grupo: de 27,6 a 12,4 ms;
    - con flechas: de 22,1 a 11,7 ms.
- `rendimiento.log` anota también «arrastre (mover el grupo y sus cables)».

## Pack 206 · 2026-11-12
- **Rendimiento del difuminado** (lo que se ve a través de un widget transparente):
  - **El refresco periódico ya no captura cada medio segundo.** Por si lo de debajo cambia solo (un reloj, una web), cada widget difuminado se volvía a capturar y a difuminar por turnos, aunque nada hubiera cambiado, y cada vez se repasaban todos los widgets. Ahora:
    - si la captura sale igual que la anterior, no se difumina de nuevo y la siguiente se deja para cada vez más tarde (0,5 s, 1, 2… hasta 1 minuto); si cambia, vuelve a mirarse a menudo;
    - nunca con el ratón en uso ni justo después de mover algo;
    - según lo que tarde en tu equipo (como mucho ~2 % del tiempo);
    - y solo se repasa ese widget, no todos.
    - Con 33 widgets transparentes y nada que hacer, el sondeo pasa de ~9 ms a ~0,2 ms.
  - **Al mover un widget por encima de otros, cada uno de los de debajo repinta solo la franja que cambia**, no la ventana entera: en la prueba, como mucho el 3 % de su superficie. En Windows, cada repintado de una ventana transparente obliga a recomponerla entera, así que esto es lo que más se notaba al arrastrar.
  - **Cables y flechas vistos a través de widgets transparentes:** se dibujan y se difuminan una sola vez para todos los widgets por los que pasan (antes, una vez por cada uno), y el difuminado se hace a la cuarta parte de resolución, que se ve igual. Un cable que pasa bajo 6 widgets transparentes, arrastrando: de ~16 a ~9 ms por fotograma, y el difuminado en sí cuesta menos de la mitad que antes.
  - **El orden de las ventanas** (en Windows hay que recorrer todas las ventanas del sistema para saberlo) se lee una vez por repaso, no dos, y se recuerda hasta que algún widget sube, aparece o desaparece.
  - **Mover un widget ya no obliga a capturar y difuminar otra vez lo que tiene debajo:** solo cuando cambia su contenido.
  - Para capturar ya no se oculta y se vuelve a mostrar el velo, que repintaba la ventana entera.
- **`rendimiento.log` más detallado:** separa «difuminado: captura», «difuminado: orden Z» y «difuminado: cables y flechas vistos a través».

## Pack 205 · 2026-11-12
- **Sombra para las flechas** (nueva pestaña **«Sombra»** en la apariencia general, en la de cada tipo y en «Retocar solo esta flecha…»): intensidad (0 = sin sombra, lo predeterminado), color, desplazamiento a la derecha y hacia abajo (también negativos) y borde difuso. Se ve en vivo mientras la ajustas.
  - Es barata, como el resplandor: la misma forma de la flecha (trazo, punta y cola), oscura y desplazada, con el borde suavizado en franjas y dibujada a media resolución. No hay difuminados. Una flecha que no cambia reutiliza su sombra.
  - Va siempre **detrás**: nunca oscurece el trazo y se ve a través del resplandor. Sus piezas no se suman entre sí, así que no se le ve el esqueleto.
- **Al pasar el ratón por un widget se ven también las flechas encadenadas**, como los cables de dependencias. Se ajusta en la pestaña **«Visibilidad»** de la apariencia general:
  - **«Mostrar también las flechas encadenadas»:** *hacia delante y hacia atrás* (lo predeterminado), *solo hacia delante* (las que siguen: de B a C, de C a D…), *solo hacia atrás* (las que llevan hasta él: de A a B, de Z a A…) o *no* (solo las del propio widget, como antes).
  - **Cada recorrido va en un solo sentido**, como los cables, que muestran los descendientes y la línea de antepasados pero no los hermanos. Si hay A→B→C y también X→C, con el cursor en B no se ve X→C: X llega a C por un lado, no sigue la cadena de B. Con el cursor en X sí se ven X→C, C→D…
  - **«Cuántos pasos de la cadena»** (0 = toda) y **«Cada paso más lejos se ve a este % del anterior»** (80 % por defecto; como poco, a la cuarta parte). Las flechas del propio widget se ven siempre en los dos sentidos.
  - **«Encadenar también al arrastrar»** (activado): al mover un widget se ve su cadena entera.
  - Los bucles no la cuelgan (cada widget se recorre una vez por sentido) y no pasa por widgets ocultos. Una red de 40 widgets y unas 80 flechas se calcula en unos 4 ms por fotograma.
- **Clonar repite las flechas, con ids nuevos.**
  - **Con sus descendientes:** las flechas entre widgets del árbol van entre sus clones. Las que unían el árbol con widgets de fuera se repiten entre el clon y ese mismo widget, igual que el clon conserva el padre del original.
  - **Un solo widget:** sus flechas de salida y de llegada se repiten en el clon.
  - Clonar y sus flechas son un solo paso de deshacer.
- **Arreglo: las flechas se perdían al abrir un set desde su archivo.** Pasaba también con los sets que se precargan para cambiar rápido. Al abrirlo, sus widgets se renombran, pero las flechas seguían apuntando a los nombres viejos y dejaban de verse. Ahora se reapuntan. Lo mismo al **pegar un árbol** (json) o al **agregar widgets desde un archivo**: las flechas internas van entre los widgets nuevos y las que van a un widget que ya está aquí se conservan.
  - **Las que ya se habían perdido se recuperan** al arrancar y al abrir cada set, cuando se sabe sin duda a qué widget apuntaban.
- Las flechas semitransparentes se componen en píxeles enteros: ya no se reescalan medio píxel y quedan un poco más nítidas.

## Pack 204 · 2026-11-12
- **Arreglo: las flechas no respetaban la separación del widget.** Calculaban dónde salir y dónde llegar sobre el rectángulo de la ventana del widget, que incluye la sombra y los márgenes transparentes y, si el widget está girado o tiene esquinas redondeadas, también las esquinas vacías. Con la separación a 0, la flecha se quedaba a 14–24 px del papel, y más si el widget estaba girado. Ahora salen y llegan al **borde real del papel** (su silueta, la misma con la que se recortan los cables), también girado o con esquinas redondeadas. La separación se mide desde ahí: con 0 tocan el borde, con 12 quedan a 12 px, y con valores negativos se meten dentro. Igual en la flecha provisional del gesto de arrastre.
- La opción pasa a llamarse **«Separación del borde del papel (negativo = se mete dentro)»** y su rango se amplía de −20…60 a **−60…120 px**.

## Pack 203 · 2026-11-12
- **Norma general: mientras editas, cada cambio se ve en el momento**, sobre lo de verdad y no solo en la vista previa del diálogo. **Cancelar o cerrar sin aceptar lo deja todo como estaba**, y lo que estás editando se ve aunque normalmente esté oculto. Queda escrita en `TODO.md` («Normas») para todo lo que se haga a partir de ahora. Se ha repasado cada diálogo que cambia el aspecto, y faltaba en estos:
  - **Apariencia de las flechas.** La general, la de cada flecha («Retocar solo esta flecha…») y la de cada tipo: las flechas cambian a la vez que tocas cualquier control. Mientras editas se ven completas, aunque estén en modo «al pasar el ratón»: al editar la general se ven todas, al retocar una se ve esa, y en el navegador de tipos se ven todas.
  - **Navegador de tipos de flecha.** Al editar el aspecto de un tipo, sus flechas, y solo las suyas, cambian en el momento. Lo aceptado en el aspecto de un tipo se sigue viendo mientras el navegador está abierto. Si cancelas el navegador, todo queda como estaba.
  - **Selectores de color** (en los diálogos de flechas): el color se ve en las flechas mientras lo eliges. Si cancelas el selector, vuelve el anterior.
  - **«Girar un ángulo personalizado…»**: antes pedía un número a ciegas. Ahora tiene barra y casilla, y el widget gira mientras eliges el ángulo. Cancelar lo devuelve a su ángulo.
  - **«Fuente predeterminada…»**: las notas cambian de fuente al marcar una opción. Si cierras sin aceptar, vuelve la de antes, y no se guarda nada hasta aceptar.
  - **«Color base de varias imágenes…»**: las imágenes marcadas cambian mientras eliges el color. Si cancelas el selector, quedan como estaban.
- Ya lo hacían, y siguen igual: forma de papel, marco, corona, cables, resaltado al pasar el ratón, efectos de imagen y enderezar.

## Pack 202 · 2026-11-12
- **Lo que de verdad congelaba el programa (según el `rendimiento.log` del usuario): los widgets web.** Cada widget web (relojes en HTML, páginas) hacía una foto de su página **cada 2 segundos** para saber qué zona agarra el ratón (pack 169). En Windows esa foto, más su reescalado con suavizado por la escala de pantalla y el análisis, tardaba **400–560 ms**, y mientras tanto el programa se quedaba congelado: 111 de los 118 segundos de bloqueos registrados con el pack 201. Al arrastrar widgets, con o sin flechas, se notaba como tirones constantes. Ahora:
  - **Nunca mientras usas el ratón** (arrastrar, hacer clic, cambiar de tamaño) **ni justo después de mover algo** (1,5 s): se deja para luego.
  - **Si la página no cambia, se mira cada vez menos:** 2 s, 4, 8, 16, 32… hasta 1 minuto. Si cambia lo que dibuja o se recarga, vuelve a 2 s.
  - **Si mirar sale caro en tu equipo, se espacia en proporción:** como mucho ~2 % del tiempo. Una foto de 500 ms no se repite hasta pasados 25 s.
  - El reescalado de la foto es el rápido: para saber qué zona agarra no hace falta suavizado.
- **Flechas:** el temporizador ya no repite el cálculo que acaba de hacer un movimiento. Antes, durante un arrastre, eran hasta 85 cálculos por segundo; ahora unos 60. Además, para el difuminado solo se miran los widgets transparentes cerca de las flechas, no todos.
- **`rendimiento.log` más útil:**
  - apunta también la **carga sostenida**, es decir, muchos pasos medianos seguidos que ocupan más del 35 % del tiempo aunque ninguno pase de 25 ms, con cuántas veces por segundo ocurre cada cosa;
  - mide **cuánto tarda en tu equipo mirar cada página web** («web: mirar la página»).

## Pack 201 · 2026-11-11
- **La ventana de las flechas, como la de los cables.** Era la causa de la saturación al mover widgets con flechas: las flechas se pintaban en una ventana transparente **del tamaño de toda la pantalla**, y en Windows cada actualización de una ventana así obliga al sistema a recomponer esa superficie entera. Los cables siempre han usado una ventana ajustada a su zona, y por eso iban fluidos. Ahora las flechas también:
  - la ventana solo ocupa la zona de las flechas visibles, con margen;
  - solo cambia de tamaño cuando se le quedan cortas o le sobra mucho, no en cada píxel de un arrastre (en la prueba, ningún cambio de tamaño en 40 movimientos);
  - cuando las flechas se van lejos, la ventana se va con ellas y deja libre el sitio de antes.
- **Como mucho ~60 repintados por segundo.** Desde el pack 198 las flechas se recalculaban en cada movimiento del ratón, y un ratón que informa a 500–1000 Hz disparaba cientos de actualizaciones por segundo. Ahora siguen al widget sin retraso, pero a un ritmo de pantalla.
- **Zona de cada flecha ajustada a lo que ocupa de verdad.** Se había quedado calculada para el halo difuminado del pack 197, que llegaba mucho más lejos: era 2–3 veces más grande de lo necesario. Comprobado con estilos extremos (puntas grandes, curvas fuertes, resplandor amplio, etiquetas) que no queda nada fuera.
- **`rendimiento.log` mide ahora también el envío a la pantalla** («flechas (pintado y pantalla)»), que es lo que de verdad cuesta en Windows. Si algo pasa de 25 ms, queda apuntado con cifras del propio equipo.

## Pack 200 · 2026-11-11
- **El verdadero culpable de la lentitud al mover widgets: el difuminado de lo que se ve a través de los widgets transparentes (pack 187), no las flechas.** Cada movimiento de un widget recapturaba y volvía a difuminar *todos* los widgets que tenían otro transparente encima, y comparaba todos con todos recalculando la forma de cada papel. Además, con el difuminado activo, todo se repetía cada medio segundo aunque no se moviera nada. Medido arrastrando un widget con una flecha gorda con resplandor:

  | Widgets transparentes | Antes | Ahora |
  |---|---|---|
  | 20 | ~36 ms por fotograma | ~4,6 ms |
  | 60 | ~810 ms por fotograma | ~6,6 ms |

  Antes, con 60 widgets, casi un segundo por fotograma.
- Cómo se hace ahora (se ve exactamente igual):
  - El contenido de cada widget se difumina entero **una sola vez**, y de nuevo solo si cambia lo que muestra, su tamaño o el radio. Al arrastrar otro widget por encima solo cambia qué zona se ve difuminada: durante un arrastre no se captura ni se difumina nada.
  - Al mover widgets **solo se revisan los que están, o estaban, debajo o encima de ellos**, no todos.
  - Lo caro de cada widget (forma del papel, si es transparente) se calcula una vez por repaso. Si un papel es transparente se guarda junto con su contenido.
  - El contenido que cambia solo (relojes, webs) se refresca **por turnos**, un widget cada medio segundo, y nunca durante un arrastre.
  - La capa de flechas tampoco recalcula todas las regiones transparentes ni se repinta entera cuando se mueve un widget transparente: solo las flechas que tiene cerca.
- **Si algo sigue yendo lento, queda apuntado:** cuando el cálculo o el pintado de las flechas, o el difuminado, pasan de 25 ms, se escribe una línea en `rendimiento.log` (carpeta de registros, como mucho una cada 5 s). Dice qué parte tardó cuánto, con cuántos widgets, transparentes y flechas. Con esa línea se sabe exactamente qué falla.

## Pack 199 · 2026-11-11
- **Flechas gordas con resplandor sin bajada de fps.** El pack 198 seguía siendo pesado con flechas gruesas y resplandor amplio, sobre todo con la pantalla escalada (125–150 %, lo habitual en Windows): una flecha gorda en diagonal costaba unos 55 ms por fotograma, y ahora unos 7. En arrastres normales con flechas gordas, de 4–14 ms a 1,3–3,8 ms.
- **Resplandor como el de los cables:** dos trazos más anchos y muy transparentes alrededor del trazo, la punta y la cola, sin difuminados ni imágenes intermedias. Sigue el grosor variable y el degradado. «Intensidad» y «Alcance» funcionan igual (el alcance es lo que sobresale a cada lado).
- **Sin esqueleto, sin imagen intermedia:** en la ventana de flechas, cada pieza (halo, trazo, punta, cola) lleva su propia transparencia y se pinta reemplazando lo que hay debajo, así que donde se solapan no se acumula opacidad. Solo cuando una flecha se cruza con otra ya pintada se compone aparte, para no borrarla.
- Las vistas previas y las miniaturas (diálogos de aspecto y de tipos, menús) se pintan como antes.

## Pack 198 · 2026-11-11
- **Flechas sin bajada de fps (mismo aspecto).** Medido en un arrastre con una flecha, en milisegundos por fotograma:

  | Flecha | Antes | Ahora |
  |---|---|---|
  | Normal | 1,2 | 0,5–1 |
  | Con resplandor | 9–10 | 1,5–2,5 |
  | Afilada con resplandor | 31–39 | 3–4 |
  | Afilada con resplandor y puntos | 46–55 | 3–4 |

  A 60 fps hay 16 ms por fotograma, así que antes no daba tiempo.
- Qué cambia por dentro (nada visible):
  - **Sin operaciones de unir figuras.** Trazo, punta, cola y halo se unían en una sola figura en cada fotograma, y era lo que más costaba (13–22 ms con resplandor y grosor variable). Desde el pack 197 la flecha se pinta opaca en su imagen y se le aplica la opacidad una vez, así que las piezas se pintan tal cual.
  - **Grosor variable:** se dibuja en tramos cortos con su grosor, que Qt pinta de forma nativa, en vez de construir el contorno punto a punto.
  - **La ventana de flechas solo repinta la zona que cambia.** Antes se borraba y se repintaba la pantalla entera en cada fotograma; ahora es menos del 2 % de una pantalla de 2560×1440. En Windows esto importa mucho, porque esa ventana transparente se envía al compositor en cada actualización.
  - Esa ventana **ya no se sube al frente en cada fotograma**: solo al mostrarse, cuando se activa un widget o, como mucho, cada 2 s.
  - **Al mover un widget, sus flechas se recalculan en ese mismo momento.** Antes esperaban a un temporizador de 40 ms y por eso iban por detrás del widget al arrastrarlo.
  - Sin flechas, el temporizador no calcula nada.
- Comprobado que se ven igual: comparadas píxel a píxel con las del pack 197 en nueve estilos (resplandor, afiladas, puntos, rayas, degradado, punta abierta, transparencia, extremos planos), solo hay diferencias de suavizado de bordes.

## Pack 197 · 2026-11-11
- **Flechas semitransparentes sin «esqueleto».** Al hacerse transparentes (al pasar el ratón, en los fundidos o con poca opacidad), se veía el trazo por dentro del resplandor, y la punta y el trazo por encima del halo, porque cada pieza se transparentaba por separado. Ahora la flecha entera (resplandor, trazo, punta, cola y etiqueta) se pinta opaca en una imagen aparte y se le aplica la transparencia una sola vez: se ve como una sola pieza, con la misma opacidad en todas partes.
- **Resplandor nuevo: halo suave alrededor de toda la flecha.** Antes era una banda de bordes duros que solo seguía el trazo y terminaba bajo la punta. Ahora envuelve la figura completa (punta y cola incluidas) y se difumina hacia fuera, con el color de la flecha y su degradado. «Intensidad» y «Alcance» siguen funcionando igual.
- Rendimiento: la imagen de cada flecha se guarda en caché (hasta 40), así que en los fundidos, donde solo cambia la opacidad, no se recalcula nada. Las flechas opacas y sin resplandor se pintan directamente, como antes. Funciona a resolución completa en pantallas con escala (HiDPI), y las flechas desmesuradas se pintan sin imagen intermedia para no gastar memoria.

## Pack 196 · 2026-11-11
- **Las flechas se ven igual que los cables.** Antes dependían de los eventos de «entrar/salir» del widget y de cualquier movimiento de su ventana, y eso podía dejarlas encendidas (en Windows llegan movimientos sueltos, y un «salir» que no llega deja el widget como si siguiera con el ratón encima). Ahora usan el mismo mecanismo que los cables. Se sondea la **posición real del cursor**: cuando reposa sobre uno de sus widgets (origen o destino), sus flechas aparecen **tenues** tras una breve espera. **Mientras arrastras** uno de sus widgets (o su padre, que lo mueve) se ven a **opacidad plena**, siguen así un momento al soltarlo y luego se desvanecen. Mover un widget por programa ya no las enciende.
- **Todo editable**, como en los cables: en *Ajustes ▸ Apariencia ▸ Flechas (apariencia y visibilidad)…*, pestaña nueva **«Visibilidad»**:
  - opacidad al pasar el ratón (**35 %** por defecto, como los cables; se multiplica por la de cada flecha);
  - espera con el cursor encima (80 ms);
  - opacidad mientras se arrastra (100 %) y cuánto dura al soltar (600 ms);
  - fundido de entrada (150 ms) y de salida (220 ms).
  Son ajustes generales: los tipos y los retoques de cada flecha no los cambian.
- Si seguías con «Siempre visibles» guardado, pasa una vez al modo de los cables; si después lo vuelves a elegir, se respeta.
- **Color de cada flecha según sus widgets, directo en el menú:** *Aspecto de las flechas ▸ (la flecha)* tiene ahora **Color: el de su tipo / el del widget de origen / el del widget de destino / degradado del origen al destino** (marcado el actual). Usa el mismo color que los cables, y si el widget cambia de color, la flecha lo sigue. Antes solo se podía desde «Retocar solo esta flecha…».
- **Arreglo:** el resplandor no seguía el color de la flecha. Usaba solo el primer color, así que con degradado (por ejemplo, del origen al destino) el final de la flecha brillaba del color equivocado. Ahora el resplandor lleva el mismo degradado que el trazo.

## Pack 195 · 2026-11-11
- **Arrastrar al revés borra la flecha.** Con el gesto de flechas (Alt + Mayús + arrastrar), si arrastras en sentido contrario a una flecha que ya existe (de su destino a su origen), al soltar se **borra** esa flecha. Antes de soltar, la flecha provisional se pone roja, a rayas y con la etiqueta «✕ borrar». Repetir el arrastre en el mismo sentido con otro tipo cambia el tipo de la flecha, sin duplicarla.
- **La rueda elige el tipo de flecha mientras la creas.** Durante el arrastre (antes de soltar), cada paso de la rueda pasa al tipo siguiente o al anterior. La flecha provisional ya se dibuja con ese tipo y un aviso dice cuál es («Flecha: Rayas (3/7)»). Funciona con el cursor sobre cualquier widget, y también cuando con Alt pulsado el sistema manda la rueda como horizontal; las ruedas finas o de panel táctil acumulan hasta completar un paso. El siguiente arrastre empieza con el último tipo usado.
- **Tipos de flecha.** Un tipo es un aspecto con nombre que se suma a la apariencia general: **apariencia general → tipo → retoques de esa flecha**. Si cambias un tipo, cambian todas las flechas de ese tipo. Vienen siete de ejemplo: Afilada, Rayas, Puntos, Doble punta, Como un cable, Resaltada y Recta y fina (esta última fuera de la rueda). La rueda recorre «Apariencia general» y los tipos marcados, en el orden de la lista.
- **Navegador y editor de tipos:** *Ajustes ▸ Apariencia ▸ Flechas: tipos (navegador y editor)…*, o desde el menú del widget en *Aspecto de las flechas*. Muestra la lista con miniaturas y una vista grande. Permite renombrar, marcar o quitar de la rueda, editar el aspecto, crear, duplicar, borrar, subir y bajar (el orden es el de la rueda), y añadir los de ejemplo que falten. Al borrar un tipo en uso pide confirmación, y sus flechas conservan el aspecto aunque se quedan sin tipo.
- **Menú del widget ▸ Aspecto de las flechas:** cada flecha es ahora un submenú con su **tipo** («Apariencia general (sin tipo)» o cualquiera de los tipos, con miniatura y marcado el actual) y **«Retocar solo esta flecha…»** (los retoques van encima de su tipo; «Quitar los retoques» la deja como su tipo). La lista *Flechas de este widget…* muestra el tipo de cada flecha. Invertir una flecha conserva su tipo y sus retoques.
- La ayuda de gestos (recuadro y F1) explica la rueda y el arrastre inverso.

## Pack 194 · 2026-11-11
- **Flechas: solo se ven al pasar el ratón o al mover.** Nuevo comportamiento predeterminado: las flechas de un widget aparecen cuando pasas el ratón por él (por su origen o por su destino) y mientras lo mueves (arrastrándolo, o porque se mueve con su padre). Al salir el ratón o dejar de moverlo siguen visibles un momento (0,9 s) y se desvanecen suavemente (0,45 s). Al arrancar la aplicación los widgets se colocan en su sitio, pero eso no cuenta como moverlos, así que no aparecen todas de golpe.
- Se elige en *Ajustes ▸ Apariencia ▸ Flechas (apariencia y visibilidad)…* ▸ «Mostrar las flechas»: **Al pasar el ratón por uno de sus widgets o al moverlo** (la primera opción y la predeterminada), *Siempre visibles* u *Ocultas*.
- Si tenías guardado «Siempre visibles» (era lo que venía por defecto), pasa una sola vez al nuevo modo; si después vuelves a elegir «Siempre visibles», se respeta.
- La flecha provisional del gesto de arrastre (Alt + Mayús) se ve siempre, sea cual sea el modo.

## Pack 193 · 2026-11-11
- **Menú del widget: el aspecto de las flechas, separado de Relaciones.** *Relaciones* (mismo nombre: las flechas también son relaciones) queda para la estructura: crear hijo, enlazar, y en *Flechas* crear, poner etiqueta, invertir el sentido, borrar y la lista *Flechas de este widget…*. La apariencia sale de ahí a un submenú nuevo, **«Aspecto de las flechas»**, en la zona de aspecto del menú (justo después de *Corona*): una entrada por cada flecha del widget (→ las que salen, ← las que llegan, con su etiqueta) que abre la apariencia de esa flecha, y **«Todas las flechas (aspecto general)…»**. Solo aparece si el widget tiene flechas.
- Si tenías un atajo o una tecla de menú en *Relaciones ▸ Flechas ▸ Apariencia de todas las flechas…*, pasa solo a la nueva ruta.

## Pack 192 · 2026-11-11
- **Flechas con grosor distinto al salir y al llegar.** En la apariencia de las flechas (la general y la de cada flecha), pestaña *Opacidad y grosor*: **«Grosor al salir del origen»** y **«Grosor al llegar al destino»**, en % del grosor que ya toca por la longitud (100 % = como antes). Así se hacen flechas que empiezan finas y acaban gruesas, o al revés; funciona también con rayas, puntos y resplandor. La punta (y la cola) crecen con el grosor del extremo para no quedar más estrechas que el trazo.
- **Colores tomados de los widgets, como los cables.** Pestaña *Color*: el color de salida y el segundo color (el de la punta, con degradado) pueden ser **el color elegido**, **el del widget de origen** o **el del widget de destino** (con el mismo tono más vivo que usan los cables). Origen → destino con degradado reproduce el aspecto de los cables. Si cambia el color de un widget, sus flechas lo siguen. La vista previa del diálogo muestra un origen amarillo y un destino azul para verlo.
- **Arreglo:** con flechas semitransparentes se veía una zona más opaca donde el trazo se junta con la punta o la cola. Ahora trazo, punta y cola se pintan como una sola figura.

## Pack 191 · 2026-11-11
- **Corrección de sitio:** *Flechas: gesto de arrastre…* no es apariencia (decide qué teclas crean flechas al arrastrar), así que sale de Apariencia y queda en **Ajustes**, junto a *Tipo de hijo al crear con el ratón…* e *Imán y cuadrícula al mover…*. En **Ajustes ▸ Apariencia** queda solo *Flechas (apariencia y visibilidad)…*, junto a *Cables*, y ahora, igual que Cables, también se ve en modo usuario.

## Pack 190 · 2026-11-11
- **Flechas: sus opciones, en Apariencia.** *Flechas (apariencia y visibilidad)…* y *Flechas: gesto de arrastre…* pasan de colgar sueltas en Ajustes a **Ajustes ▸ Apariencia**, junto a los cables.
- **Apariencia de CADA flecha, desde el menú del widget.** En *Relaciones ▸ Flechas*, bajo «Cada flecha», aparece una entrada por cada flecha que sale del widget (→) o le llega (←), con su etiqueta si la tiene; cada una tiene su submenú: **Apariencia de esta flecha…** (color, grosor, punta, trazo… solo para esa flecha; el botón «Usar la apariencia general» la devuelve al aspecto común), **Etiqueta…**, **Invertir el sentido** y **Borrar esta flecha**. Lo mismo sigue disponible, con lista y botones, en *Flechas de este widget…*.
- El editor de atajos no lista flechas concretas (cambian de un widget a otro).

## Pack 189 · 2026-11-11
- **Flechas con el ratón: tecla(s) + arrastrar.** Mantén **Alt + Mayús**, pulsa sobre el widget de origen, **arrastra hasta otro widget y suelta**: se crea la flecha de uno a otro. Mientras arrastras se ve una **flecha provisional** (rayada, siguiendo al cursor; al pasar sobre un widget se dibuja ya como quedará). Soltar en el vacío, sobre el mismo widget o sobre uno al que ya llega una flecha de ese origen no crea nada (en el último caso avisa). El widget de origen no se mueve.
- **Configurable:** *Ajustes ▸ «Flechas: gesto de arrastre…»* (bandeja): activar o desactivar el gesto y elegir las teclas (Ctrl, Alt, Mayús, Win/Cmd en cualquier combinación). Las combinaciones que ya hacen otra cosa con el ratón (Ctrl = hijo, Alt = padre, Mayús = mover/alinear, Ctrl+Mayús = cuadrícula, Ctrl+Alt…, etc.) se rechazan y el diálogo dice qué hacen. La ayuda de gestos (el recuadro junto al cursor y la guía F1) muestra el gesto con la combinación elegida.
- Antes de este pack, Alt + Mayús + arrastrar se comportaba igual que Mayús solo (mover el widget y alinear); ahora crea una flecha. Mayús solo sigue igual. Si tu Windows cambia el idioma del teclado con Alt + Mayús, elige otra combinación (por ejemplo Mayús + Win) en el diálogo.
- El menú del widget sigue valiendo (*Relaciones ▸ Flechas…*) y también sus atajos de teclado.

## Pack 188 · 2026-11-11
- **Arreglo: «Editar marco ▸ Tamaño exterior» movía el widget.** Al cambiar el ancho o el alto del marco (con la vista en vivo y al aceptar), la ventana se corría hacia arriba y a la izquierda el doble de lo debido, y solo **la primera vez** (por eso parecía intermitente: cuando la ventana coincidía con la posición guardada). Causa: el marco ya crece desde su centro y la capa 2 sigue a su hueco, pero la compensación que se añadió para el tamaño del papel (Pack 147) leía ese reajuste como si hubieras pedido tú un «Mover X/Y» y movía la ventana otra vez. Ahora esa compensación no se aplica cuando el cambio lo hace el propio marco: **el centro del marco no se mueve** al cambiar su tamaño (en vivo, al aceptar, tras arrastrar el widget y al cancelar).
- Ojo: como con el papel, el marco crece **desde su centro**, así que sus bordes se mueven la mitad del cambio hacia cada lado; lo que ya no pasa es que el conjunto se desplace.

## Pack 187 · 2026-11-11
- **Desenfoque de lo que se ve a través de un widget transparente.** Antes, lo que quedaba debajo de un widget con fondo translúcido (otros widgets, cables, flechas) se veía nítido. Ahora se ve **difuminado**, como un cristal esmerilado, con un radio **editable**: *Cables ▸ pestaña «Transparencias» ▸ «Difuminado de lo que se ve a través de un widget transparente»* (0-30 px, **5 px por defecto**; 0 = como antes, sin desenfoque).
- Qué se difumina, y qué no: (1) **widgets** que están debajo de uno translúcido, salvo su padre y sus hijos directos (la relación inmediata se sigue viendo nítida); (2) **cables** que pasan bajo el widget y no salen ni llegan a él (solo bajo los widgets que están por encima del cable); (3) **flechas** que cruzan por debajo y no empiezan ni acaban en ese widget (una flecha que llega a él se ve nítida). Fuera de la zona del widget transparente todo queda igual.
- **Web (demo de capas):** «prueba el botón» solo funcionaba con las capas separadas; con el marco (capa 1) encima de la web (capa 2) la capa 1 se comía los clics. Ahora el marco los deja pasar y el botón de la web responde también con las capas juntas; los botones de la capa 1 de una nota siguen funcionando.
- Límites: no se puede difuminar el escritorio ni otras aplicaciones que haya detrás (haría falta el acrílico del sistema operativo, que no es igual en Windows, macOS y Linux); el cálculo se rehace al mover o cambiar widgets, así que con muchos widgets translúcidos superpuestos y radios grandes puede notarse algo más de carga.

## Pack 186 · 2026-11-11
- **Flechas entre widgets.** Una capa de dependencias aparte de los cables: los cables siguen siendo la jerarquía padre/hijo; las flechas relacionan **cualquier par de widgets**, también de ramas de árboles distintas, sin cambiar quién es hijo de quién. Se crean desde el menú del widget: **Relaciones ▸ Flechas ▸ «Nueva flecha: elegir el destino con el ratón»** (clic en el widget de destino; Esc cancela) o **«Nueva flecha hacia…»** (lista). Van del widget de origen al de destino; pueden ir y volver (A→B y B→A se pintan cada una por su lado) y formar ciclos (A→B→C→A) sin ningún problema: **una flecha solo se dibuja entre sus dos extremos, nunca se recorre como árbol**, así que no hay recursión ni bucles. Se guardan dentro del widget de origen (viajan con los sets, las copias de seguridad y el deshacer) y se borran solas cuando se elimina uno de sus extremos.
- **Apariencia propia** (la misma familia de opciones que los cables, pero independiente, con vista previa): color y **degradado** hasta un segundo color; **opacidad y grosor según la longitud** (corta/larga, con los límites que quieras); **curvatura** (negativa = hacia el otro lado) y cuánta conserva una flecha larga; separación del borde; **punta** (triángulo, abierta, rombo, círculo, ninguna) y **cola**; trazo (continuo, rayas, puntos, raya y punto) y extremos; **resplandor**; y **etiqueta** con texto, color, fondo y opacidad. Hay una apariencia **general** (*Ajustes ▸ Flechas: apariencia y visibilidad…*, con «siempre visibles / solo al pasar el ratón / ocultas») y cada flecha puede tener la **suya** (*Flechas de este widget… ▸ Apariencia…*; «Usar la apariencia general» la quita).
- *Flechas de este widget…* lista las que salen y las que llegan: cambiar apariencia, etiqueta, **invertir el sentido** o borrar; también «Quitar todas las flechas de este widget». Las opciones están en el editor de atajos como el resto del menú.
- Qué hacen y qué no: las flechas salen del borde visible de un widget y llegan al borde del otro (sobre la recta entre sus centros); si dos widgets se tocan o se solapan no se pinta. Se ven por encima de los widgets mientras trabajas con ellos (y sobre todo si alguno está «siempre encima»); con otra aplicación delante quedan detrás, como los widgets. Aún **no** hacen: desenfoque al verse a través de widgets transparentes (es el siguiente punto de la lista) ni la cuerda con física de los cables.

## Pack 185 · 2026-11-11
- **Imán y cuadrícula al mover widgets.** Al arrastrar un widget: **Mayús** lo **alinea** con los bordes y los centros de los demás widgets visibles y con los de la pantalla (se «pega» a menos de 10 px, también borde con borde para dejarlos juntos); **Ctrl + Mayús** lo ajusta a una **cuadrícula** de la pantalla (12 columnas × 8 filas por defecto; se pega el borde del widget que quede más cerca de una línea). Mientras arrastras se ven las **líneas guía** (rosa = la que ha imantado; azul tenue = la cuadrícula). Los hijos con posición ligada siguen al widget, y la posición ajustada es la que se guarda. Se puede combinar con lo de siempre (Mayús ya servía para mover todo el widget aunque haya una capa seleccionada).
- **Ajustes ▸ «Imán y cuadrícula al mover…»** (bandeja): qué hace sin pulsar teclas (*nada* por defecto / *alinear siempre* / *cuadrícula siempre*), distancia de alineación, **columnas y filas** de la cuadrícula, alinear con la pantalla y/o con los widgets, y mostrar o no las guías. La ayuda de gestos lo menciona en Mayús y Ctrl+Mayús.
- Límites a tener en cuenta: la pantalla es la que está bajo el cursor y se usa su área útil (sin barra de tareas); lo que se ve del widget es su máscara (sin los márgenes transparentes).

## Pack 184 · 2026-11-11
- **Atajos de teclado para TODAS las opciones del menú del editor de texto.** En *Atajos de teclado…* hay un grupo nuevo, **Comandos ▸ Edición de texto**, con: negrita, cursiva, subrayado, tachado, **alinear a la izquierda / centrar / alinear a la derecha / justificar**, enlace, **cambiar fuente, tamaño y color**, aumentar/reducir tamaño, fuente siguiente/anterior (todas o favoritas), y deshacer, rehacer, cortar, copiar, pegar, eliminar y seleccionar todo (estas últimas, además de las teclas de siempre). Solo actúan mientras escribes en un widget; no pueden ser globales. Por defecto: Ctrl+B/I/U, Ctrl+Mayús+X, Ctrl+K y, nuevas, **Ctrl+L / E / R / J** (izquierda / centro / derecha / justificado). El menú del editor muestra ahora la tecla de cada opción y refleja tus cambios. Una letra suelta (sin Ctrl/Alt) no se admite como atajo: es texto.
- **Cambiar fuente, tamaño y color sin selección** ahora vale: se aplican a todo el texto (antes la opción estaba desactivada).
- **Fuentes favoritas.** Menú del editor ▸ **Mis fuentes favoritas…** (o su atajo): eliges de las instaladas, las ordenas y listo. **Mayús + rueda** rota solo por tus favoritas (si no has elegido ninguna, por todas); **Ctrl + Mayús + rueda** recorre **todas** las instaladas (antes Ctrl+Mayús cambiaba el tamaño, igual que Ctrl; el tamaño sigue siendo Ctrl + rueda). Un aviso junto al cursor dice la fuente y su posición (p. ej. «Carlito (3/181)»).
- **Arreglo: la lista de fuentes con la rueda a veces «no abarcaba todo».** Se seguía la pista de la fuente leyéndola del cursor, que no siempre devolvía la última puesta y hacía oscilar la rueda entre unas pocas; ahora el recorrido lleva su propio índice (y ya no se lee la familia con la llamada que cierra el programa con algunos formatos). En la prueba recorre las 181 fuentes sin saltarse ninguna.
- **Arreglo en el menú del widget:** «Recorte de la capa ▸ Esquinas redondeadas (10 %)» y «(25 %)» compartían el mismo nombre de atajo; la segunda es ahora «Esquinas redondeadas medias (25 %)». Se ha comprobado que no queda ninguna otra opción repetida en el menú del widget ni en el de la bandeja.

## Pack 183 · 2026-11-11
- **Arreglo: sin rastro del texto anterior al editar una nota.** Al pasar el ratón por un widget se pinta el «brillo por hover» (una captura del widget); al entrar en edición esa captura se quedaba encima y se veía el texto viejo detrás del que escribías. Ahora, mientras editas el texto, el brillo de ese widget se apaga y no vuelve a encenderse hasta terminar (Intro/clic fuera/Esc); entonces se restablece si el ratón sigue encima.
- **Arreglo: «Editar forma de papel» ya no cambia los colores al abrirse.** Antes la vista previa en vivo se aplicaba sobre la nota real nada más abrir el editor, y las notas antiguas (sin parámetros de forma guardados) arrancaban con los *ajustes globales* de la última forma creada. Ahora: la nota real no se toca hasta que cambias algo; y una nota antigua arranca con el color y el tamaño de **su propia imagen**.

## Pack 182 · 2026-11-08
- **Vigilante de actualizaciones (opción avanzada oculta).** Una casilla en la ventana *Actualizaciones*, invisible de serie, que activa «actualizar automáticamente en cuanto se detecte una versión nueva»: mientras el programa está abierto mira cada 10 minutos (y al abrirse) y, si hay una versión nueva publicada, la instala **sin preguntar y sin avisos previos** (la copia de seguridad se hace igualmente) y se reinicia; al volver a abrir avisa «Actualizado automáticamente al pack N». El valor se guarda; si está activada la casilla se ve, y si se desactiva vuelve a ocultarse.
- No reinicia en mitad de un arrastre ni con un cuadro de diálogo o un menú abierto (espera hasta 2 minutos). Sigue sin tocar un archivo con cambios propios y sin repetir la misma versión si algo falla.

## Pack 181 · 2026-11-07
- **Soltar un archivo sobre un widget cambia su estilo.** Arrastra un `.wawidget`, `.wapaper` o `.waframe` (o un `.json` de widget o de marco) **encima del widget destino**: el propio widget lee el archivo, sin importarlo antes, y adopta ese estilo. Con `.wawidget` y `.wapaper` funciona como *Sustituir widget* (conserva su texto y su sitio, según el ajuste «conservar el contenido»); con `.waframe` le pone el marco con su tamaño actual. Avisa de lo que ha hecho y se deshace con Ctrl+Alt+Z. No añade nada a *Mis widgets*. Los archivos que no sirven (imágenes, `.waset`, `.wapack`) no se aceptan al arrastrar. En widgets con página web, la página ya no se queda el archivo soltado.
- **Arreglo: soltar un `.wawidget` en la ventana del Navegador de widgets fallaba** si el cursor caía sobre un campo de texto (nombre, autor, familias, atajos…; el campo se quedaba el arrastre y no lo entendía). Ahora se importa suelto donde se suelte (también en la galería *Mis widgets*, *Packs de widgets* y *Guardar y cargar*).

## Pack 180 · 2026-11-07
- **«Actualizar automáticamente al iniciar»** en *Ajustes* de la bandeja (casilla, desactivada por defecto; también en la ventana *Actualizaciones*). Si la marcas, al abrir el programa (unos segundos después) se instala sola la versión nueva publicada, con copia de seguridad (puedes volver desde *Actualizaciones*), y se reinicia; al volver a abrir avisa «Actualizado automáticamente al pack N». Sin la casilla, todo sigue como antes (pregunta antes de instalar).
- Solo instala versiones **nuevas** (si tu archivo tiene cambios propios sin publicar no lo toca) y **una vez por versión publicada**: si algo falla o la versión sigue pareciendo nueva, no insiste en bucle; avisa del motivo.

## Pack 179 · 2026-11-07
- **«Iniciar con el sistema»** en *Ajustes* de la bandeja (casilla): Widget Arena se abre solo al iniciar sesión en el equipo. Windows: entrada en el registro del usuario (*Run*, sin consola); macOS: un *LaunchAgent* en `~/Library/LaunchAgents`; Linux: un `.desktop` en `~/.config/autostart`. La casilla refleja lo que hay realmente en el sistema; desmarcarla lo quita. Si no se puede (permisos), avisa.

## Pack 178 · 2026-11-07
- **Tu autor y tu familia «predeterminados», a un clic.** En el Navegador de widgets, pestaña *Widget elegido*: junto a **Autor** hay una casilla **[x] predeterminado** (ese es tu nombre de autor) y junto a **Familias** otra, **[x] predeterminada** (esas familias se ponen solas). Si la marcas, los widgets **nuevos** y los que **guardes en Mis widgets** llevan esa familia y tu firma, siempre que no traigan familia propia; los de otros autores no se tocan. Desmarcarla la quita. Si editas el campo mientras está marcada, la predeterminada se mantiene al día.
- **Tu nombre también en *Ajustes* de la bandeja:** «Mi nombre de autor…» (y sigue en *Mis widgets ▸ Gestionar*).

## Pack 177 · 2026-11-07
- **Autor y familias del widget elegido, en el Navegador de widgets.** En la pestaña *Widget elegido*, dentro del recuadro «Widget», hay ahora los campos **Autor** y **Familias** (varias, separadas por comas) y un botón **Añadir ▾** con las familias que ya existen. Se guardan al salir del campo o pulsar Intro, y el filtro «Familia: X» del Navegador se actualiza solo. Si pones familias y no autor, se firma con tu nombre de autor. (Antes solo se podía por el menú del widget, *Widget ▸ Familias y autor…*.)

## Pack 176 · 2026-11-07
- **Menú del widget por función.** Desaparecen «Capas» y «Aspecto»; ahora hay: **Widget** (guardar widget, exportar widget a un archivo, copiar y pegar widget, sustituir widget, familias y autor), **Contenido** (tipo de capa, texto, zoom de la web, estirar imagen), **Forma y borde** (forma de papel, marco, recorte de la capa 2), **Color y efectos** (efectos de imagen y tono, por capa), **Posición y tamaño** (por capa: seleccionar, posición, girar, inclinar, tamaño; y girar el widget entero) y **Corona**. Cuando hay dos capas, cada función tiene una entrada por capa.
- **Tus atajos y teclas de menú se migran solos** a su nuevo sitio (también los de versiones anteriores). Las opciones hacen exactamente lo mismo que antes.
- En el Navegador de widgets, el recuadro «Contenido (capas)» pasa a «Editar», con un botón por función.
- Ya no queda la palabra «modelo» en ningún menú; README y documentos de formatos actualizados.

## Pack 175 · 2026-11-07
- **«Modelo» pasa a llamarse «widget» en todos los textos de la aplicación.** La biblioteca se llama ahora **«Mis widgets»** (como ya existen «Mis marcos» y «Mis formas de papel»): pestaña del Navegador, ventana, botones, avisos, ayudas, packs, importar y exportar. Donde se cambiaba un widget por otro, la acción es **«Sustituir widget»** (botón «Sustituir "nombre"» y aviso «Sustituyendo…»).
- Los atajos y teclas de menú que ya tenías asignados se migran solos (por ejemplo, «Exportar todos mis modelos a un archivo…» de la bandeja pasa a «…mis widgets…»). Tus archivos y packs no cambian: siguen siendo los mismos.
- En el menú del widget, el submenú «Modelo» (dentro de «Aspecto») conserva aún su nombre; se reorganiza entero en el Pack 176 (menú por función).

## Pack 174 · 2026-11-07
- **Familias de modelos y widgets (primera parte).** Cada modelo puede llevar un **autor** y una o varias **familias** («Relojes modernos», «Transparentes»…): un modelo puede estar en varias a la vez. Se guardan en un bloque propio del modelo (`wa_meta`: `author` y `groups`), pensado para ampliarse (registro de autores, concursos…). Los widgets creados desde un modelo llevan esa marca, y también la conservan al clonarlos o guardarlos como modelo.
- **Dónde se ve y se edita:** en *Modelos*, campos «Autor» y «Familias» (separadas por comas), un filtro por familia («Todas», «Sin familia», cada familia) y la casilla «Agrupar por familia» (un modelo que está en varias sale en cada una; las familias se indican bajo su nombre). En *Navegador de widgets*, una entrada «Familia: X» en el filtro por cada familia de los widgets que hay, y las familias y el autor en el aviso de cada widget. En el menú del widget, *Modelo ▸ Familias y autor de este widget…*.
- **Bandeja:** nuevo submenú «Nuevo widget de una familia» (familia ▸ modelos, con miniatura, y «Exportar esta familia…»).
- **Exportar una familia** a un pack (*Modelos ▸ Gestionar ▸ Exportar una familia…*): el pack se llama como la familia y lo firma tu nombre de autor.
- **Mi nombre de autor** (*Modelos ▸ Gestionar ▸ Mi nombre de autor…*): por ahora es solo un texto (por defecto, el usuario del sistema). Si un modelo tiene familias y no autor, se firma con él.

## Pack 173 · 2026-11-06
- **La zona sensible de un widget con marco es el contorno exterior del marco.** Antes se calculaba por transparencia de la imagen, así que la sombra del marco (y su difuminado) contaba como zona de clic. Ahora, con un marco generado, la zona sale de su silueta exacta (sin sombra), y el hueco interior sigue agarrando. Si el marco está girado o es una imagen propia, se sigue usando la imagen como hasta ahora.
- **Arreglo al pintar la zona de agarre:** cuando había una capa web y un marco a la vez, el recorte de la segunda capa no se aplicaba y el marco rellenaba todo su rectángulo (de ahí el espacio transparente sensible que seguía apareciendo). Ahora cada capa se pinta con su recorte aislado.
- **Diagnóstico:** Mayús + clic derecho en un widget añade «Mostrar zona sensible (3 s)», que dibuja en rojo la zona que realmente responde al ratón.

## Pack 172 · 2026-11-06
- **La corona ya no se mueve al cambiar el tono (Ctrl+rueda).** El borde superior del papel, su inclinación y su zona visible (de donde salen la posición de la corona, el anclaje de los cables y el rectángulo del papel) se medían sobre la imagen *ya con efectos*, buscando píxeles opacos y con brillo; al cambiar el tono (o la saturación, el brillo…) cambiaba el brillo de los píxeles y, con él, lo que se detectaba como papel (en papeles oscuros con un filo claro, el filo cambiaba de sitio). Ahora se mide sobre la imagen original de la capa 2, sin efectos, que no cambia con la rueda. Sin imagen original (capas que no son imagen) se usa la que se muestra, como antes.
- Esto vale también para el resto de lo que usa esa medida (cables de la nota, zona del papel para las teclas globales) con tono, saturación, brillo y contraste.

## Pack 171 · 2026-11-06
- **Notas: el texto alineado a la izquierda se respeta.** En una nota el texto sin alineación propia se centra; pero Qt, al guardar el texto del editor, *no escribe* la alineación cuando es a la izquierda (es la de por defecto), así que un párrafo que habías alineado a la izquierda volvía a dibujarse centrado al terminar de editar. Ahora, al guardar, la alineación izquierda se escribe de forma explícita (`align="left"`), y el texto solo se centra automáticamente en vertical.
- Las notas que ya tenías guardadas con un párrafo «perdido» en el centro no se pueden recuperar solas (no se sabe si estaba a la izquierda o sin alineación): hay que volver a alinearlas una vez.

## Pack 170 · 2026-11-06
- **El estado de las páginas locales ya no depende del «origen» que da el visor.** En el Pack 168 el aviso de cambios (color, modo…) llegaba por la consola de la página y solo se aceptaba si venía de un archivo local; un script que el programa inyecta no siempre figura así, y el estado podía quedarse sin guardar. Ahora el aviso lleva una clave propia de cada widget (que una página de internet no conoce) y se acepta venga de donde venga; además, cada 2,5 s la aplicación pregunta a la página por su estado como red de seguridad.
- Comprobado con clones: cada widget (y cada clon) tiene su propio almacenamiento, el clon parte de una copia del estado del original y desde ahí son independientes. Antes, todas las páginas locales compartían el mismo `localStorage` del navegador interno.
- **Diagnóstico:** si el sistema coloca un widget en un sitio distinto del que se le pidió al arrastrarlo (por ejemplo, limitándolo a la pantalla en una máquina virtual), queda anotado en el registro con las dos posiciones.

## Pack 169 · 2026-11-06
- **Un widget web agarra solo por lo que su página dibuja.** Con widgets web con marco, el visor ocupa un rectángulo que puede ser mayor que lo que se ve, y ese espacio transparente seguía agarrando el ratón (al arrastrar la esquina de otro widget se movía el reloj). Ahora la zona que agarra se calcula con una foto de lo que la página dibuja: el contorno visible y todo lo que encierra (aunque dentro sea casi transparente), cruzado con el recorte del visor si lo hay.
- La foto se vuelve a mirar al cargar la página y cada 2 s; solo si lo dibujado cambió se recalcula (por ejemplo, si aparece un panel). Si el visor no da una foto fiable (en blanco, sin página), se usa el rectángulo entero como antes, así que ningún widget se queda sin zona. En el registro (nivel depuración) queda anotada la zona calculada.
- En Windows, lo que queda fuera deja pasar el clic al widget de debajo (Pack 167); en otros sistemas la zona se calcula igual pero el paso del clic no cambia.

## Pack 168 · 2026-11-06
- **Las páginas locales recuerdan su estado dentro del widget.** Una página HTML guardada en tu equipo (como `calendario_led.html`, que guarda el color y el modo día/mes con `localStorage`) no conservaba esos datos de forma fiable: Chromium no mantiene bien el almacenamiento de las páginas `file://` y además lo comparte entre todas las páginas locales. Ahora cada widget lleva su propio `localStorage` y sus cookies, guardados dentro del propio widget (capa 2, `web_state`): se restauran antes de que cargue la página, cada cambio se guarda al momento (sin llenar el historial de deshacer) y un widget no ve lo de otro.
- Si la página se recarga por dentro, vuelve con lo último guardado. El estado de las páginas locales sigue viajando al exportar (Pack 163). Las páginas de internet no cambian.

## Pack 167 · 2026-11-06
- **Se deshace el recorte de la ventana del Pack 166** (quitaba las sutilezas de los widgets translúcidos: el cuerpo casi transparente y el bloque del texto se veían distintos). La ventana vuelve a dibujarse entera.
- **La zona que agarra el widget toma el borde como referencia:** es zona del widget todo lo que encierra su contorno visible (aunque dentro sea casi transparente), no los halos tenues de fuera ni las esquinas cortadas o redondeadas. En Windows, cuando el ratón está fuera de esa zona el sistema pasa el clic al widget (o ventana) de debajo; en otros sistemas no cambia nada.

## Pack 166 · 2026-11-06
- **Cada widget agarra solo por lo que se ve.** La máscara que decide qué parte de la ventana recibe el ratón se rellenaba mal (`fill(Qt.transparent)` en un bitmap deja todos los bits puestos), así que en la práctica cada widget agarraba su rectángulo entero, y un vecino por encima te robaba el arrastre aunque su parte fuese transparente. Ahora la máscara es la forma real.
- Los halos tenues (sombras, bordes difusos de menos de un tercio de opacidad) no cuentan como zona que agarra; una imagen translucida entera sí. Un texto agarra por todo su bloque, no solo por las letras. Una capa web recortada agarra por su forma, no por su rectángulo. El editor de texto y las insignias (plegar, campana, corona) siempre agarran.

## Pack 165 · 2026-11-06
- **Puente de red para páginas locales.** Una página HTML guardada en tu equipo (como el mando de la TV) puede pedir a Widget Arena que haga una petición GET por ella: escribe en su consola `__WA_HTTP_GET__<dirección>`, la aplicación hace la petición y le contesta llamando a `window.__waNet({url, ok, status, error})`. Así funciona aunque el visor web bloquee las peticiones de la página. Solo vale para páginas locales (nunca para páginas de internet), solo `http`/`https`, con un máximo de 20 peticiones cada 5 segundos.
- Las páginas locales encuentran `window.__waApp` definido cuando están dentro de Widget Arena, para poder elegir el puente por sí solas.
- Nuevo `mando_tv.html`: opción de envío «Puente (Widget Arena)», elegida por defecto dentro del widget (también para configuraciones guardadas de versiones anteriores, sin perder los códigos), y el aviso dice si la TV contestó, no contestó o no se pudo llegar a ella.

## Pack 164 · 2026-11-06
- **Las páginas locales pueden hablar con la red.** El visor web bloqueaba por defecto que una página guardada en tu equipo (un mando, un panel) hiciera peticiones a direcciones de red, como el mando de la TV hacia `http://tv_switch.local/...`. Ahora está permitido.
- **La consola de la página queda en el registro.** Lo que la página cuenta en su consola (bloqueos, errores de red, avisos de seguridad) se anota en el registro de la aplicación, y también si una página no termina de cargar. Así se puede ver por qué una página local no consigue hacer algo.

## Pack 163 · 2026-11-03
- **Los widgets web viajan con su página.** Al exportar un modelo (`.wawidget`), un árbol o todos los widgets (`.waset`), la página HTML de una capa web va dentro del archivo junto con los archivos que usa por ruta relativa (imágenes, `.css`, `.js`, tipografías, sonidos...), por ejemplo el cristal del reloj LED. Al importar se dejan en `html/<nombre>/` sin pisar nada: lo idéntico se reutiliza y lo distinto entra en otra carpeta `(2)`. Antes de traer páginas nuevas el programa avisa de que son código que se ejecuta en tu equipo y pide confirmación; si dices que no, el widget entra sin ellas. En `.json` y al copiar al portapapeles no se empaquetan.
- **El estado de la página viaja con el widget.** Se guarda lo que la página tiene en `localStorage` y en las cookies (el color del reloj, por ejemplo) y se restaura al importar, justo antes de que cargue la página y una sola vez: lo que cambies después no se pisa. Las cookies marcadas HttpOnly no se pueden leer y no viajan.
- **Casilla «No incluir información personal»** al exportar widgets con página web (marcada por defecto). Marcada: de las páginas de internet no se guarda nada (cookies, sesiones, datos del sitio); el estado de las páginas locales, como el reloj, sí va. Desmarcada: se incluye también el de las páginas de internet (pueden llevar sesiones iniciadas: no compartas ese archivo). Si no hay ningún widget web, no pregunta.

## Pack 162 · 2026-11-03
- **Borrar widgets desde los navegadores.** En la galería simple *Añadir un widget* hay un botón **Borrar** (también la tecla Supr y clic derecho → *Borrar este widget...*): quita de la lista el widget elegido, con confirmación; los que ya tienes en pantalla no cambian, y el predeterminado no se borra (se explica por qué). En el navegador completo, la pestaña *Modelos* tiene ahora el botón **Eliminar** a la vista (y Supr en la lista), y el árbol de widgets tiene el botón **Eliminar...** (y Supr) para quitar de la pantalla el widget elegido, siempre con confirmación.
- **Arrastrar `.wawidget` a *Añadir un widget*.** Soltando uno o varios archivos en la galería simple se añaden a la lista (con otro nombre si ya existe uno igual), el último queda elegido con su miniatura y solo hay que pulsar *Añadir*. Un archivo que no es un widget se rechaza con un aviso.
- **Configuración inicial nueva** (`defaults/config.json`): cables, cuerda, corona, jerarquía, forma de papel y marco por defecto de las instalaciones nuevas. Se aplica una sola vez, en el primer arranque, y no pisa nada que ya exista.

## Pack 161 · 2026-11-03
- **El zoom de una capa web se conserva.** Ctrl+rueda sobre la web (o *Capas → Capa 2 → Contenido → Acercar / Alejar / Zoom al 100 %*) cambia el zoom y el widget lo recuerda: al reabrir el programa, recargar la página o cambiar de set se queda como lo dejaste. Va del 25 % al 500 %; con una capa seleccionada (Ctrl+Alt+clic), Ctrl+rueda sigue siendo su tamaño, y Ctrl+Alt / Ctrl+Mayús+rueda no se tocan. Sale un aviso breve con el porcentaje.
- **Menú Aspecto, en gris lo que no aplica.** *Marco* aparece en gris en los widgets cuya capa 1 es texto (las notas), y *Forma de papel* en gris en los widgets cuya capa 1 no es texto (imagen o marco). Con el cursor encima explica por qué. En el editor de atajos y teclas siguen apareciendo los dos activos para poder asignarles tecla.

## Pack 160 · 2026-11-03
- **El texto de las notas se centra solo.** Sin pulsar Intro ni recolocar la capa 1: el texto queda centrado en horizontal y en vertical dentro de su recuadro, tanto al escribir como al dibujarse. Los párrafos con alineación propia (izquierda, derecha, justificado) la conservan y solo se centran en vertical. Está activado por defecto en los widgets tipo nota; en los demás, apagado. Se cambia por capa en *Capas → Capa N → Contenido → Centrar el texto automáticamente*.
- **Reducir el texto para que quepa.** Nueva opción *Reducir el texto para que quepa* en el mismo submenú: si el texto no cabe en su recuadro, todas las tipografías (también las de tamaño propio) se reducen por igual, hasta un 25 %, hasta que encaje. Activada por defecto en notas. Se aplica al terminar de escribir; mientras se escribe, el texto se ve a su tamaño.
- Los enlaces del texto se siguen detectando donde está dibujado el texto, con el centrado y la reducción.
- **El reloj LED ya no enseña barras de desplazamiento.** El recorte de la web forzaba `overflow:auto` en el cuerpo de la página, y una página que ocupa justo el visor (como el reloj) acababa con las dos barras. Ahora se respeta el `overflow:hidden` de la página; las páginas largas siguen desplazándose.

## Pack 159 · 2026-11-03
- **Pico doblado y esquina levantada con tu diseño por defecto.** Al elegir «Doblez» o «Esquina levantada» en una esquina del editor de notas, la esquina toma ahora el diseño que enviaste (forma, curvas, punta y luces), tanto en el editor como en las miniaturas del selector de esquina y en las muestras («Post-it con doblez», «Esquina levantada», «Doblez + levantadas»). El diseño está dibujado para la esquina superior izquierda (doblez) y la inferior derecha (levantada); en las otras esquinas sale reflejado, con las luces espejadas. Las notas ya guardadas no cambian.
- **Arrastrar y soltar en el navegador de widgets.** Puedes soltar archivos `.wawidget` (también `.wapaper` y `.json` de modelo) sobre la ventana del navegador de widgets: se importan como modelos nuevos (con otro nombre si ya existe uno igual), el navegador pasa a la pestaña «Modelos» y deja seleccionado el último. Otros archivos propios (`.waset`, `.waframe`, `.wapack`, copias `.zip`…) siguen su carga de siempre.
- **Dos marcos nuevos en la lista de predefinidos:** «Neón cian» y «Neón lima» (borde negro translúcido con filo de color y sombra interior).

## Pack 158 · 2026-11-03
- **El marco, por encima de la web: su sombra interior y su filo se ven sobre cualquier página.** Qt pinta el visor web por encima del marco, así que lo que el marco dibuja sobre el hueco no se veía. Ahora, además de recortar la web por el hueco, la imagen del marco se superpone *dentro de la propia página* (una capa fija, transparente a los clics y por encima de todo el contenido), así que vale con cualquier web: el reloj, una página de internet o tu propio `.html`. Los clics, el desplazamiento y la selección de la página no cambian. Solo se hace con los marcos del programa; con otra imagen como capa 1 se sigue recortando por su silueta. Límite: una web con una política de seguridad muy estricta (que prohíba imágenes `data:`) puede no mostrar la capa, igual que ya pasaba con el recorte.

## Pack 157 · 2026-11-03
- **Arreglo: en un widget web con marco, el marco recorta la web (ya no queda «debajo»).** El visor web de Qt se pinta como una ventana propia por encima del marco, así que la página tapaba el aro en las esquinas redondeadas del hueco y bajo los bordes. Ahora la web se recorta por el **hueco exacto** del marco (rectangular con esquinas redondeadas, u ovalado), y el aro se ve siempre completo. Si la capa 1 es una imagen cualquiera (no un marco del programa) o está girada, se sigue recortando por su silueta. Límite: lo que el marco dibuja sobre el contenido (la sombra interior) no puede pintarse sobre la web.

## Pack 156 · 2026-11-03
- **Arreglo: con el editor de marcos abierto, la web ya no desaparece según la luz del bisel.** La vista en vivo del editor dibuja una imagen temporal del marco y el recorte por la silueta no la reconocía como marco: seguía usando la transparencia de la imagen (por eso, con *Luz del bisel* por debajo de cierto valor, el aro seguía contando como «vacío» y la web se recortaba entera). Ahora la vista en vivo usa también la silueta exacta. Además, un widget web con marco que se acaba de crear (o al arrancar el programa) se recorta por la silueta desde el principio, no solo tras editarlo.
- **El Reloj LED viene con marco** (capa 1 imagen, un marco de cristal verdoso; la página se ve por el hueco). A quien ya tenía el modelo del Pack 154 sin marco y sin tocar, se le pone el marco una sola vez; si lo habías cambiado o borrado, no se toca.
- **Se acabó la nota «fea» de textos superpuestos.** Cuando no existía el modelo predeterminado (`default.json`), el programa creaba una nota de emergencia con «Post-it» en la capa 2 y «Clic derecho para opciones / Doble clic para ocultar» encima, y además la guardaba como predeterminada: de ahí que reapareciera una y otra vez (al actualizar, con *Nuevo widget predeterminado*, en el primer arranque…). Ahora el predeterminado de fábrica es la nota normal que trae el programa (*Nota doblada*, sin texto) y, si hace falta la de emergencia, no lleva texto debajo. Si tu `default.json` era justo la nota antigua, se sustituye por la normal (una sola vez, dejando un aviso en el registro); si lo habías personalizado, no se toca.
- **Dónde están los registros:** nuevo *Abrir la carpeta de registros* en la bandeja (modo creativo). En Windows es `%APPDATA%\WidgetArena\data\logs` (`widget_arena_app_debug.log`, `rendimiento.log` y `widget_arena_crash.log`).

## Pack 155 · 2026-11-03
- **Arreglo: un marco translúcido ya no deja la web invisible.** Con un marco como *Cristal esmerilado* (aro casi transparente) sobre una web o una imagen, el recorte por la silueta del marco se calculaba a partir de la transparencia de la imagen, no veía «sólido» el aro y recortaba la capa 2 hasta dejarla vacía: se veía solo el marco, con un destello de la página al redibujar. Ahora la silueta de un marco dibujado por el programa se calcula exacta desde sus parámetros (su contorno exterior, rectangular, redondeado u ovalado), sea cual sea su transparencia. Si la capa 1 está girada se sigue usando la imagen, como antes. Vale también para imágenes recortadas por un marco translúcido.

## Pack 154 · 2026-11-02
- **El reloj LED, como widget HTML.** Viene entre tus modelos como *Reloj LED* (también para quien ya usaba el programa; si lo borras no vuelve). Es una página HTML con su reflejo de cristal, de fondo negro y con clic transparente: pulsas el reloj y cambia de color, y el color se recuerda aunque cierres y abras el programa. En modo creativo, *Nuevo widget HTML desde un archivo…* (bandeja) copia cualquier `.html` a `widget_arena_data/html/` y lo abre como widget. Límite: los sets, modelos y packs exportados todavía no llevan la página HTML dentro; y una página con imágenes propias necesita esas imágenes en la misma carpeta `html/`.
- **Arreglo: recortar una web ahora funciona.** El recorte (esquinas redondeadas, elipse o la silueta de un marco) se hace dentro de la propia página con una máscara CSS, así que vale igual en Windows, macOS y Linux. La página se desplaza dentro del recorte y el fondo de la web no asoma por las esquinas.
- **El editor de marcos, al nivel del de papeles.**
  - Vista previa con zoom (rueda), mover (arrastrar), doble clic = vista completa, bloquear el zoom y **fondo cambiable** (gris, color o escritorio), compartido con la vista previa de los papeles.
  - La vista previa **ya no miente**: por el hueco se ve la imagen real de la capa 2 del widget, recortada como quedará (*Contenido del hueco*: paisaje de ejemplo, imagen de este widget o sin contenido), y respeta *Ajustar la imagen o la página al hueco*.
  - **Ajustar a su contenido**: un marco nuevo nace con el tamaño de la imagen o la página de la capa 2 más sus bordes, y el botón *Ajustar el marco al contenido* lo recalcula cuando cambias los grosores.
  - **Crear y guardar:** el botón pasa a *Crear marco* y, como al crear un papel, hay una casilla *Guardar también en Mis marcos:* con su nombre.
  - **Copiar y pegar un marco desde el menú del widget** (*Aspecto → Marco*): *Copiar este marco (json)* y *Pegar un marco copiado (json)*. Se pega el aspecto; el tamaño se queda (o se ajusta al contenido si el widget aún no tenía marco). «Generar marco» pasa a llamarse *Crear un marco…*.
- **«Widget guardado» pasa a llamarse «modelo».** Se revisó cada texto del programa: pestaña *Modelos*, *Crear desde un modelo*, submenú *Aspecto → Modelo* con *Cambiar el modelo de este widget…* y *Guardar este widget como modelo…*, *Exportar todos mis modelos a un archivo…*, packs con «modelos y sets». Los mensajes de copiar, pegar y exportar un widget ya no dicen «widget guardado» (dicen «widget»), porque ahí no se guarda ningún modelo. Los archivos `.wawidget` y las carpetas no cambian, y los atajos que tuvieras con los nombres de antes se traducen solos.
- **Si falta un modelo, se avisa** en vez de crear en silencio la nota por defecto: aparece «No encuentro el modelo …: uso el predeterminado» (una vez por modelo y sesión) y queda en el registro.

## Pack 153 · 2026-11-02
- **El modo usuario ahora es de verdad sencillo.** La bandeja pasa de 15 opciones a 10: *Añadir un widget…*, *Mis widgets* (con la casilla de mostrar u ocultar de cada uno), *Cambiar de set* (con *Guardar el set actual…* al final), *Ocultar o Mostrar todos los widgets*, *Deshacer*, *Rehacer*, *Ayuda*, *Buscar actualizaciones…*, *Modo creativo* y *Salir*. El menú de un widget pasa de 9 a 6: *Renombrar…*, *Ocultar*, *Siempre encima*, *Cambiar aspecto…*, *Duplicar* y *Eliminar este widget…*. El modo creativo sigue con todo, igual que antes.
- **Una sola galería para añadir.** *Añadir un widget…* abre una ventana con miniaturas grandes de tus widgets guardados: eliges uno y pulsas *Añadir* (o doble clic). *Cambiar aspecto…* de un widget abre la misma galería y le pone el aspecto elegido (el contenido de la nota no cambia).
- **Las notas nuevas ya no nacen «siempre encima».** Si no hay otros widgets, la primera nota se crea en la banda normal (en los dos modos). Con otros widgets, la nueva sigue la banda de la mayoría para que los cables no queden por encima de unas notas y por debajo de otras.

## Pack 152 · 2026-11-02
- **Grados cíclicos: 0° = 360° en todos los controles de grados** (dirección del degradado, rotaciones, ángulos de marcos y máscaras, grados de los formularios…). Al arrastrar sobre el control, al girar la rueda, con las flechas o al escribir un valor, pasar del tope da la vuelta automáticamente en una dirección y en la otra (359° → 0° → 1°…, y 0° → 359° hacia abajo) en vez de detenerse. Los deslizadores de matiz (hue) son deslizadores y no pueden dar la vuelta: siguen con sus topes.
- **«Previsualizar como en la realidad (giro y matiz)»** en el editor de forma de papel. La muestra del editor sale girada como la nota real (una nota girada 90° enseña el brillo del cristal donde de verdad caerá) y con el matiz y demás efectos de color que tenga la nota; el texto no se tiñe, igual que en la nota real. La casilla se recuerda para todas las vistas previas futuras, de esta y otras notas. Si la nota no está girada ni tiene el matiz cambiado, la casilla queda desactivada (conserva su estado). Funciona al editar la forma de una nota, al editar un widget guardado y al generar la forma de un widget; no cambia el giro ni el matiz de la nota real. Los widgets guardados ya guardaban giro y matiz de sus capas; las formas de papel guardadas siguen sin llevar giro (es solo un modo de ver la muestra).

## Pack 151 · 2026-11-02
- **Arreglo: un widget guardado ya no enseña «ERROR: ¡Archivo no encontrado!».** Si la imagen de la forma de papel de un widget guardado no estaba en la carpeta de datos, la vista previa y las miniaturas del navegador pintaban un texto rojo de error. Ahora la forma de papel se vuelve a dibujar desde sus parámetros, como ya hacía el widget real al cargarlo; si un widget guardado no tiene de dónde redibujarla, se ve un hueco discreto de «imagen no encontrada», nunca el texto de error.
- **Los widgets guardados llevan un texto estándar, no el de tu nota.** Al guardar un widget (*Guardar este widget…*, *Guardar un widget de la pantalla*, *Guardar forma de papel…*, *Guardar este aspecto*, o la casilla de guardar al crear una forma de papel) el texto de la nota se cambia por un *lorem ipsum* con el mismo formato (fuente, tamaño, color, alineación). Lo mismo al exportar un widget a un archivo, así que lo que compartes no lleva tu texto. *Copiar este widget (json)* sigue llevando el texto, porque es para pegarlo con su contenido.
- **Miniatura en cada elemento de *Mis formas de papel*** (y también en *Mis marcos*). Se dibujan una a una sin hacer esperar a la ventana y se recuerdan para la próxima vez.
- **Exportar todos mis widgets guardados a un archivo:** un solo `.wapack` con todos (con las imágenes que usan; la imagen de las formas de papel se vuelve a dibujar). Está en *Gestionar* del navegador de widgets guardados, en *Importar y exportar* de la bandeja y en el Centro de guardar y cargar; se abre con *Cargar un archivo* o en *Packs de widgets*.

## Pack 150 · 2026-11-01
- **Color del texto de un botón.** En *Editar este botón/enlace…* hay un nuevo campo *Color del texto*: eliges un color o lo dejas en *Automático* (el oscuro de siempre). Se guarda en el propio enlace (`tc=`), así que los botones ya creados no cambian y la rueda del ratón (tamaño y fuente) y el cambio de color del papel lo respetan.
- **Marcos translúcidos con dos bordes.** El editor de marcos tiene opacidad en los dos colores del relleno y una pestaña nueva, *Bordes*: un **borde exterior** (el canto de fuera del marco) y un **borde interior** (el canto del hueco), cada uno con su grosor, color, opacidad, segundo color, dirección y balance del degradado, independientes entre sí. Hay un punto de partida nuevo, *Cristal esmerilado*. Los marcos de antes se dibujan igual.
- **Submenú *Widget guardado* con nombres que dicen sobre qué actúan:** *Guardar este widget…* (lo añade a tus widgets guardados), *Exportar este widget a un archivo…* (un `.wawidget`), *Copiar este widget (json)* y *Pegar un widget copiado (json)*. Los atajos que ya tuvieras con los nombres de antes se traducen solos.

## Pack 149 · 2026-11-01
- **Arreglo (modo usuario): «Elegir los sets de la rotación…» vuelve a verse** en *Sets de widgets*. Los gestos Ctrl / Alt + doble clic en el icono recorren esa rotación en los dos modos, y la entrada se había ocultado por error.

## Pack 148 · 2026-11-01
- **Arreglo: al ir a escribir en un widget girado se recortaban sus lados.** Al editar el texto el papel se endereza para verlo en horizontal, pero la ventana conservaba el tamaño del widget girado: un 280×60 girado 90° quedaba en una ventana estrecha y desaparecían sus lados derecho e izquierdo. Ahora la ventana se ajusta al papel enderezado y al recuadro de edición (el centro del papel no se mueve) y al terminar vuelve a su tamaño y a su sitio.
- **Diagnóstico:** cada widget nuevo deja en el registro quién lo ha pedido (`origen: …`), para localizar notas que aparecen sin haberlas pedido.

## Pack 147 · 2026-11-01
- **Arreglo: el color de los cables, de la corona y de los botones sale del color dominante del papel.** Antes se leía de un solo píxel del centro: si ahí caía el texto o un hueco transparente, salía negro, gris o un tono por defecto que no se parecía al widget (y había que ir a la corona y elegir «Dominante»). Ahora es la misma cuenta que «Dominante», así que cables y corona coinciden con lo que se ve.
- **Arreglo: cambiar el ancho o el alto del papel ya no desplaza el widget.** Pasaba al editar el tamaño desde la configuración, con Ctrl+rueda o con «Editar geometría», sobre todo con la nota girada: la capa crecía desde su esquina y el centro del papel corría la mitad del cambio. Ahora el papel crece desde su centro. Mover X/Y sigue moviéndolo lo que se pida.
- **Los hijos quedan siempre por debajo de su padre.** Tocar o editar un hijo ya no lo deja encima del padre (ni el nieto sobre el hijo). Hay un ajuste para quitar la regla: en el diálogo de cables, sección *Apilamiento de los widgets → Un hijo respecto a su padre*.
- **Al editar el texto de un widget ya no se oscurece lo que queda bajo el recuadro de edición** (era el atenuado de «Un widget bajo otro transparente», que dejaba una mancha oscura).

## Pack 146 · 2026-11-01
- **Arreglo: la nota saltaba de sitio al cambiar el color (u otro ajuste) en «Editar forma de papel» con «Ver los cambios en la nota real».** Cada cambio recolocaba la capa de papel en la esquina (0, 0) de la ventana, y el programa volvía a ajustar la ventana al contenido: la nota se corría hacia arriba y a la izquierda, y más cuanto más girada estaba (en una nota sin giro, unos 5 px; en una girada 30°, decenas). Ahora el papel nuevo se centra donde estaba el anterior: cambiar el color no la mueve; si cambia el tamaño, crece o se encoge por el centro. Lo mismo al aceptar y al cancelar el cuadro.

## Pack 145 · 2026-11-01
- **Modo usuario y modo creativo.** Un interruptor, **Modo creativo**, en el menú del icono de la bandeja. En **modo usuario** los menús se reducen a lo esencial: en la bandeja desaparecen *Nueva nota & forma de papel*, *Nuevo con un aspecto en uso* y la consola, y *Ajustes* queda en apariencia básica, atajos e importar/exportar; *Sets de widgets* conserva guardar, siguiente, anterior, ranuras y la lista de sets. En el menú de un widget desaparecen *Capas*, *Formas de papel*, *Marco*, *Corona*, copiar/pegar/exportar/mover árbol y *Usar como predeterminado*; se mantienen renombrar, temporizador, ocultar, siempre encima, *Widget guardado*, *Girar widget*, **Relaciones completas**, clonar y eliminar. El **modo creativo** es todo lo de antes.
- **Se pregunta una sola vez** al arrancar (también en lo ya instalado): «Solo usar widgets» o «Crear y personalizar». Cerrar la pregunta equivale a modo creativo. Hasta que se conteste, el programa se comporta como siempre.
- Los gestos de ratón con teclas siguen igual en los dos modos. El modo es del programa, no de cada set: cambiar de set no lo cambia, y no se restaura desde copias.
- El editor de atajos de teclado sigue viendo todas las acciones en cualquier modo.

## Pack 144 · 2026-11-01
- **Arreglo: Ctrl+Alt+Mayús+rueda no giraba en Linux (VirtualBox).** La ayuda de gestos lee las teclas pulsadas de verdad, pero el giro leía las que trae el evento de la rueda, y en ese sistema no coinciden (la ayuda decía «girar 1°» y no pasaba nada). Ahora el giro hace caso también a las teclas realmente pulsadas (Ctrl, Alt y Mayús); con la tecla Win pulsada de verdad sigue sin girar.
- **Diagnóstico:** las primeras 24 vueltas de rueda con Ctrl+Alt dejan una línea en el registro (nivel info, sin activar la depuración) con las teclas del evento, las físicas y el desplazamiento recibido.
- **El atenuado bajo un widget transparente se recalcula enseguida al girar o cambiar de tamaño un widget** (antes quedaba un recuadro oscuro del widget anterior hasta medio segundo después).

## Pack 143 · 2026-11-01
- **Arreglo: el ajuste fino de rotación (Ctrl+Alt+Mayús+rueda) ahora se reconoce también si el sistema no incluye Mayús en el evento de la rueda.** Antes, en ese caso el giro salía de 5° en lugar de 1°. Ahora se mira también la tecla Mayús física. En el registro (nivel depuración) se anota si se ha tomado como fino.
- **La ayuda de gestos (el recuadro junto al cursor) nombra el giro con la rueda:** *Ctrl+Alt* → girar el widget 5°; *Ctrl+Alt+Mayús* → 1° (fino). Solo aparece sin capa seleccionada, que es cuando actúa.

## Pack 142 · 2026-11-01
- **Girar con la rueda: Ctrl+Alt+rueda = 5°; con Mayús (Ctrl+Alt+Mayús+rueda) = 1° (fino).** Cambia lo de los Packs 140-141 (que usaban Ctrl+Alt+Mayús para 5°). El sentido es el inverso: **rueda arriba = antihorario, rueda abajo = horario**. Vale con el widget bajo el cursor y sin ninguna capa seleccionada (con una capa seleccionada, Ctrl+Alt+rueda sigue ajustando esa capa); sobre un botón de texto la rueda sigue siendo la del botón. Está en *Aspecto → Girar widget* con 5° y 1°.

## Pack 141 · 2026-11-01
- **Arreglo: Ctrl+Alt+Mayús+rueda no giraba en algunos equipos.** Con Mayús o Alt, muchos sistemas mandan la vuelta de rueda como desplazamiento *horizontal*; el programa solo miraba el vertical y la ignoraba. Ahora lee cualquiera de los dos. Además deja en el registro (nivel depuración) lo que recibe, para diagnosticar si aun así no gira.

## Pack 140 · 2026-11-01
- **Ctrl+Alt+Mayús+rueda gira el widget de 5 en 5 grados** (rueda arriba, en sentido horario; abajo, antihorario), con el widget bajo el cursor. Gira las dos capas por igual, como el resto de giros. Con un panel táctil se acumulan los movimientos pequeños hasta completar cada paso. También está en *Aspecto → Girar widget*.

## Pack 139 · 2026-11-01
- **Arreglo: un widget que no es transparente ya no se vuelve transparente bajo otro que sí lo es.** El atenuado de los Packs 136-137 rebajaba la opacidad de *cualquier* widget bajo un cristal; con eso asomaban el escritorio (iconos, nombres de carpetas) y los widgets de abajo a través de un papel opaco que los tapaba. Ahora **solo se atenúa un papel transparente** (el que cubre menos de la mitad): los demás, aunque no sean opacos al 100 %, siguen tapando lo que tienen detrás, como una sola capa, y manda el orden por clic y jerarquía (un grupo corta al otro). Desaparece la lógica que ocultaba lo de debajo (Pack 137), que ya no hace falta.
- El ajuste *Cables → Transparencias → Un widget bajo otro transparente* pasa a describir exactamente eso.

## Pack 138 · 2026-11-01
- **Un widget y sus descendientes se apilan como un bloque.** Al pasar al frente un widget (al hacerle clic), pasan con él sus hijos, nietos y demás descendientes, manteniendo su orden entre ellos. Dos hermanos son dos grupos: hacer clic en *Préstamos* sube *Préstamos* y todo lo suyo (*Miguel*...) sobre *Pagos* y todo lo suyo, y hacer clic en *Pagos* hace lo contrario. Funciona igual en Windows, macOS y Linux (usa solo las funciones de ventana de Qt). Se puede desactivar en *Cables → Transparencias → Apilamiento de los widgets*.
- **El atenuado bajo un widget transparente usa ese orden**, así que lo que un widget opaco tapa sigue tapado (como una sola capa) también bajo el cristal; el pico de una nota tapada por otra no asoma.
- En **Windows** el programa lee además el orden real de las ventanas, en lugar de deducirlo de los clics. En macOS y Linux el orden se sigue aprendiendo de las activaciones y de las veces que el programa sube un widget; el bloque lo mantiene coherente.

## Pack 137 · 2026-11-01
- **Archivos `.waframe`: un marco en un archivo**, como las formas de papel en `.wapaper`. Lleva solo los parámetros del marco (el marco se dibuja de nuevo al ponerlo) y una miniatura. Se crean con *Exportar...* del editor de marcos o con *Aspecto → Marco → Exportar este marco (.waframe)...* del widget; se abren con *Cargar un archivo*, arrastrándolos a la ventana «Guardar y cargar», con *Importar...* del editor o con *Poner un marco desde un archivo...*. También se puede guardar como `.json`.
- **Mis marcos**: biblioteca de marcos guardados (carpeta `marcos/` de los datos). En el editor de marcos hay una fila *Mis marcos* con la lista y los botones *Guardar aquí...*, *Exportar...*, *Importar...* y *Borrar*; al elegir uno se aplica conservando el tamaño actual. En el menú del widget, *Aspecto → Marco → Mis marcos* lo pone directamente en el widget (ajustando la capa 2 al hueco) y *Guardar este marco en Mis marcos...* lo añade.
- Cargar un `.waframe` (o importarlo) lo guarda en Mis marcos; si ya había uno igual, no lo duplica.
- **Arreglo: el atenuado bajo un widget transparente y el recorte de los cables seguían un rectángulo**, no el papel. Con una esquina doblada se oscurecía (y se ocultaba el cable) también en el hueco que el papel no tiene, y se pasaba un par de píxeles del borde. Ahora siguen la **silueta real del papel** (esquinas dobladas o levantadas incluidas) y coinciden con lo que se ve a ±2 px. Las notas que no son formas de papel del programa conservan el rectángulo.
- **(Sustituido en el Pack 139)** Arreglo de z-index con el atenuado: ocultaba lo que quedaba bajo un widget opaco velado; el Pack 139 lo resuelve de raíz: los widgets opacos no se atenúan.
- **Web, README y `docs/FORMATOS-ARCHIVO.md`:** nombran los marcos entre lo que se puede guardar y compartir.

## Pack 136 · 2026-11-01
- **Arreglo: el cable se seguía viendo a través de un widget muy transparente y se cortaba bajo el borde inferior.** El «cuerpo» de una nota para los cables se deducía de los píxeles de su imagen: con un papel casi invisible no contaba su interior y sí el halo de la sombra, que es mayor por abajo. Ahora es el **papel real** de la nota (con su giro), calculado por sus medidas. El cable sale justo del borde, arriba y abajo, y no se ve dentro del papel.
- **Lo que queda bajo un widget transparente se atenúa**, para distinguir cuál está encima: la parte de un widget que queda bajo el papel translúcido de otro se ve mucho más tenue. El porcentaje es configurable en *Cables → Transparencias → Un widget bajo otro transparente* (por defecto 40 %; 100 % lo desactiva). Se pinta dentro de cada widget, así que funciona igual en Windows, macOS y Linux.
- La pestaña *Widgets* de los ajustes de cables pasa a llamarse **Transparencias**.
- El orden de apilamiento se aprende de los clics y de las veces que el programa sube un widget, porque Qt no dice qué ventana está encima de cuál. Si otra vía las reordena (otro programa, por ejemplo), puede equivocarse hasta que haces clic en el widget. En una capa 2 web el atenuado no se aplica.
- **Web:** el texto de compartir dice ahora que los archivos se abren arrastrándolos a la ventana «Guardar y cargar» (menú del icono de la bandeja).

## Pack 135 · 2026-11-01
- **Estudio rápido del equipo** (opcional): dibuja cables de prueba en cada nivel de calidad, mide la pantalla, el procesador, la animación de las cuerdas y el difuminado, y recomienda la **calidad de dibujo**, los **fotogramas por segundo** de las cuerdas y un **tope de difuminado**. Dura unos 3 segundos, no toca tus widgets y no cambia nada hasta que aceptes con *Aplicar la recomendación*.
- **Cuándo sale:** una sola vez tras instalar el programa (si dices *Ahora no*, no vuelve a salir solo) y siempre que quieras desde *Cables → Punteados y rendimiento*, con el botón *Medir este equipo y recomendar la calidad...* junto a las opciones de rendimiento. Desde ahí rellena los controles, así que *Cancelar* los deja como estaban. El último estudio se ve junto al botón.
- El resultado se guarda solo en este equipo (`rendimiento.json`): no va en las copias de seguridad ni en los sets. Una instalación existente que se actualiza no recibe el aviso.

## Pack 134 · 2026-10-31
- **El cable nace del borde del widget**, no del centro: ya no se ve a través de un papel translúcido. Es lo normal desde ahora (en *Cables → Transparencias*, «Opacidad del cable dentro de esos widgets», 0 %).
- **Efecto cristal:** con una opacidad intermedia el cable se ve dentro del widget como a través de un cristal, y «Difuminado» lo desenfoca. Funciona igual en Windows, macOS y Linux (se dibuja dentro de la propia aplicación, sin efectos del sistema).
- **Recorte de la capa 2** para cualquier imagen o página web (menú del widget → *Capas* → *Capa 2* → *Recorte de la capa*): esquinas redondeadas, elipse o silueta de la capa 1. Con la silueta, lo que sobra de la imagen queda bajo el marco o fuera de él, sin ajustar medidas al milímetro. En una página web el recorte depende de lo que permita cada plataforma.
- **Marcos ovalados y redondeados:** el editor de marcos tiene una lista *Forma* (rectángulo o elipse), con bisel de luz continua; nuevos puntos de partida «Redondeado» y «Óvalo dorado». Al ajustar la capa 2 a un marco, se recorta sola por su silueta.
- Los marcos rectangulares y los widgets anteriores se dibujan igual que antes. Una capa 2 de un widget existente no se recorta hasta que lo eliges.
- **Web y README:** mencionan los cables desde el borde, el recorte y los marcos ovalados.

## Pack 133 · 2026-10-31
- **Editor de marcos con vista en vivo:** los cambios (color, grosor, bisel, sombras, puntos de partida, ajuste de la capa 2...) se ven al momento en el widget real, igual que en el editor de formas de papel. La casilla *Ver los cambios en el widget real mientras edito* los activa o los apaga; al cancelar, el widget vuelve a como estaba, y al aceptar queda exactamente lo que se veía. El editor se abre a un lado del widget para no taparlo.

## Pack 132 · 2026-10-31
- **Forma de papel: transparencia en cada color.** El color de fondo y el segundo color del degradado tienen cada uno su **opacidad** (0-100 %), de modo que el papel puede desvanecerse de opaco a transparente (pestaña *Forma y color → Color y degradado*). El reverso del pico doblado sigue la opacidad del papel.
- **Borde con degradado y opacidad propios** (*Borde y franja adhesiva*): color y opacidad del borde, y «Degradado hasta» con segundo color, su opacidad, la dirección y el balance. La opacidad del borde es independiente de la del papel y deja ver lo que hay detrás del widget (no se mezcla con el color del papel).
- **Borde del doblez** (nueva pestaña *Borde del doblez*): rodea la solapa del pico doblado con grosor, color, degradado, opacidad, dirección y balance propios, aparte del borde del papel. Con grosor 0 queda el filo claro de siempre.
- Todo es opcional y las formas de papel anteriores se dibujan igual que antes (valores por defecto: opaco, sin degradado en el borde, sin borde del doblez).
- **Apoyar el proyecto:** el botón y el texto de *Acerca de*, la web y el README dicen ahora «Apoyar» en lugar de «Invítame a un café».
- **Web:** los textos en primera persona del plural pasan a singular; la galería explica cómo hacerla posible (Ko-fi) y dónde escribirme (Issues de GitHub).
- **Web:** la sección de papeles y marcos explica que puedes usar cualquier imagen (descargada o buscada) como papel de fondo o como marco, y además generarlos con los editores; muestra también marcos; textos de la comunidad reescritos.

## Pack 131 · 2026-10-31
- **Marcos editables**, igual que las formas de papel: menú del widget → *Aspecto* → *Marco* → *Generar marco...* / *Editar este marco...*. El editor deja fijar el tamaño y el grosor de cada lado, el color, el bisel, la textura, las sombras y el filo, con puntos de partida (Madera, Negro, Blanco, Oro, Plata, Rojo laca, Fino negro, Paspartú), vista previa sobre un paisaje y *Copiar marco / Pegar marco* en JSON. El marco es un PNG con el centro transparente en la capa 1 (la imagen o la web de la capa 2 se ajusta al hueco); sus parámetros se guardan en el widget, así que se puede volver a editar, y el PNG viaja con el widget en `.waset`, `.wawidget` y las copias.
- **El efecto resorte también actúa sobre la cuerda** (antes la física de cuerda lo anulaba y solo se veía en la miniatura).
- **Copias de seguridad más completas:** guardan y restauran las fuentes (configuración) y los esquemas de atajos, y la configuración incluye la rotación de sets. Las copias completas **ya no llevan el token ni el chat de Telegram**.
- **Web:** el texto de «formas de papel y marcos propios» refleja que los marcos ya tienen editor.

## Pack 130 · 2026-10-31
- **Valores iniciales de las instalaciones nuevas** (`defaults/config.json`): cables, cuerda, resorte, corona, jerarquía y nota base con los ajustes del autor. Se aplican una sola vez en el primer arranque y no pisan nada existente.
- **Instalador: entornos a medias.** Si una instalación anterior dejó un `.venv` sin `pyvenv.cfg` («No pyvenv.cfg file»), el instalador y `herramientas.py` lo detectan, lo borran y lo rehacen. Las carpetas de Python a medias (sin `Lib\os.py`) también se limpian antes de reintentar.
- **Instalador de Windows más robusto.** Si `uv python install 3.12` falla (antivirus que inspecciona HTTPS, proxy, red lenta), ahora reintenta con los certificados de Windows y con una conexión más paciente, pasa a `uv` el proxy del sistema y, como último recurso, baja Python con PowerShell y lo descomprime con `tar`. Si aun así no puede, el aviso incluye los últimos mensajes de `uv` en vez de solo el código de error.
- **Web:** los papeles con doblez usan tu diseño y el texto y los cables se colocan sobre el papel (no sobre su sombra); los marcos de ejemplo son PNG con hueco transparente.
- **Archivos propios, comprimidos y con sus imágenes**: `.waset` (widgets: un árbol, todos los del set activo; con o sin configuración), `.wawidget` (un widget guardado) y `.wapaper` (una forma de papel). Son un `.zip` con `wa.json` (qué es), `data.json` (lo mismo que llevaba el `.json` de antes) y las imágenes en `images/`, `sticky/` y `frames/`; ya no hay imágenes en base64 dentro de un `.json`. Las formas de papel siguen sin guardarse como bitmap: se redibujan. Se reconocen por su contenido, no por la extensión. *Exportar árbol a un archivo...*, *Exportar todos los widgets a un archivo...*, *Exportar el widget guardado...* (menú del widget y navegador) y *Exportar...* del editor de formas de papel los crean; *Cargar un archivo*, *Agregar / Reemplazar widgets desde un archivo*, *Cambiar por otro widget guardado desde un archivo*, el navegador de widgets guardados y arrastrar y soltar los leen. Los `.json` de antes se siguen leyendo, y también se pueden escribir eligiendo ese tipo en el cuadro de guardar.
- **Forma de papel**: nuevas entradas *Exportar forma de papel a un archivo...* y *Aplicar forma de papel desde un archivo...* (menú del widget → Aspecto → Forma de papel). La aplicación conserva el texto y la posición del widget.
- **Cambiar por otro widget guardado desde un archivo** traía las imágenes del archivo sin copiarlas (con los `.json` de la versión 126 se quedaban dentro del estado); ahora se traen a la carpeta de datos.
- **Página del proyecto renovada** (la de descarga): la portada es un tablero que se puede tocar (widgets que se arrastran, cuerdas que cuelgan y se balancean, dos sets que cambian con un botón), y enseña lo que hace de verdad: notas, imágenes con marco, mini-navegador y botones, las dos capas de cada widget (nota: texto y botones sobre su fondo; marco: marco sobre imagen o página web), jerarquías opcionales con contraer/expandir ramas, formas de papel dibujadas por el propio programa, y los formatos de archivo. Sigue siendo bilingüe y respeta *reducir movimiento*. Incluye un apartado «Galería de escritorios: en preparación» (todavía sin subida de archivos).
- **Los ajustes son de cada set y ya no «se pegan» de un set a otro.** Antes, un set que no traía un ajuste (grosor de cable, peso de la cuerda, tonos...) se quedaba con el del set anterior. Ahora usa el valor inicial: el de `defaults/config.json` si existe y, si no, el de fábrica. Al restaurar el set activo desde una copia pasa lo mismo.

## Pack 129 · 2026-10-31
- **Las copias de seguridad guardan y restauran los ajustes**: cables (grosor, peso, curvatura, opacidad...), jerarquía, tonos y menús, además de los atajos de teclado. *Restaurar copia de seguridad* tiene una casilla nueva, *Configuración y atajos*, que dice cuántos ajustes cambiarían y guarda antes una copia de la configuración actual. Restaurar el set activo recupera también los ajustes de cables que tenía ese set. Una copia que cambia solo un atajo ya cuenta como cambio.
- **Valores iniciales de las instalaciones nuevas** (`defaults/config.json`): ajustes y atajos que se aplican una sola vez, en el primer arranque, sin pisar nada que ya exista. Se genera desde tu propia configuración: *Guardar y cargar → Configuración y atajos → Guardar mi configuración como la de las instalaciones nuevas...*; el archivo se deja en la carpeta `defaults/`. No incluye el set actual, las ranuras, las pistas de gestos ni nada de Telegram.

## Pack 128 · 2026-10-31
- **Mover árbol a otro set...** es ahora una tabla con columnas tituladas: **Ctrl +** (la tecla que carga el set: su ranura o, si no tiene, su puesto alfabético), **Alt +** (solo si tiene ranura), **Set**, **Memoria** (● ya está en memoria, cambio instantáneo) y **Rotación** (↻ n = su puesto en la rotación de Ctrl / Alt + doble clic; ↻ sin número si no hay lista elegida y rotan todos). Doble clic en una fila para aceptar.
- **Guardar y cargar** rehecho para que se entienda dónde está cada cosa: las opciones de cada sección se agrupan por verbo (*Guardar*, *Cargar*, *Llevar a otro equipo*, *Recuperar*, *Meter en la aplicación*, *Carpeta*...) y cada una lleva al lado una explicación de qué hace, en qué formato queda y dónde (por ejemplo, un set es un `.json` en la carpeta de sets, solo en este equipo; las copias completas son un `.zip`; los packs, un `.wapack`). *Mis sets* incluye ahora *Exportar los widgets del set activo...* (archivo `.json` con las imágenes dentro), que antes solo estaba en *Archivos*.
- *Guardar el set activo...* pregunta ahora «Nombre del set (se guarda como un set en la carpeta de sets; si ya existe, se actualiza)».

## Pack 127 · 2026-10-31
- **Mover árbol a otro set...** muestra ahora cada set con su tecla: `[1]` … `[9]`, `[0]` es el set que cargan **Ctrl + N / Alt + N** (su ranura o, si no tiene, el puesto que ocupa en la lista alfabética cuando esa tecla está libre). Van primero los que tienen tecla, por orden de tecla; `●` marca los que están en memoria (cambio instantáneo) y una leyenda lo explica.
- **Arreglo en *Editar forma de papel***: si mientras el editor estaba abierto movías el widget (o algo hacía que la ventana guardara), el estado podía quedarse con la imagen de la vista previa. Ahora, con el editor abierto, la ventana solo guarda su posición, y la vista previa tampoco entra en el historial de deshacer de la nota.

## Pack 126 · 2026-10-31
- **Las imágenes viajan con lo que copias.** *Copiar árbol (json)*, *Copiar widget guardado* y *Copiar forma de papel* dejan en el portapapeles el mismo JSON de siempre, con una marca que apunta a un `.zip` temporal con los bitmaps que usan (marcos, fotos, imágenes de capa). Al pegar se traen a la carpeta de datos sin pisar nada (lo igual se salta; una imagen distinta con el mismo nombre entra como «... (importado)» y la nota pegada apunta a ella). Si el `.zip` ya no existe (otro equipo, limpieza del sistema) se pega igualmente y el programa avisa de las imágenes que faltan. También en *Copiar JSON* del navegador de widgets guardados.
- **Las imágenes viajan con lo que guardas en un archivo.** *Exportar el widget guardado...* (menú del widget y navegador de widgets guardados) y *Exportar todos los widgets a un archivo...* llevan ahora las imágenes dentro del `.json` (como ya hacía *Exportar árbol*). Al cargarlo con *Cargar un archivo*, *Agregar widgets desde un archivo* o *Importar* en el navegador, las imágenes se dejan en su sitio sin pisar nada. Guardar un widget guardado que traiga imágenes incrustadas también las extrae.
- **La forma de papel no se guarda como bitmap**: su imagen se redibuja desde sus parámetros al cargar el widget, así que ni el portapapeles, ni los archivos, ni las copias completas la llevan. Corrige el pack 125, cuyas copias completas sí la incluían.

## Pack 125 · 2026-10-31
- **Las copias completas ya llevan las imágenes.** El `.zip` de `backups/full` solo guardaba los `.json`, así que al restaurarlo en otro equipo (o tras perder la carpeta de datos) faltaban los marcos, las imágenes de capa y las notas base. Ahora cada copia completa incluye, dentro de `sticky/`, `images/` y `frames/`, todas las imágenes que usan el set activo, todos los sets (en disco y en memoria) y los widgets guardados. Una copia nueva se hace también cuando solo cambia una imagen. Las imágenes que viven fuera de la carpeta de datos (rutas absolutas) o pesan más de 120 MB no pueden incluirse: el aviso de *Copia completa ahora* y el registro lo dicen.
- **Restaurar copia**: nueva casilla *Imágenes de la copia que faltan (N de M)*. Al restaurar el set activo, un set o los widgets guardados, sus imágenes se traen solas. No se pisa nada: lo que ya está igual se salta y una imagen distinta con el mismo nombre entra como «... (importado)», con las rutas del set ajustadas. Las copias anteriores a este pack no llevan imágenes (la ventana lo indica). Importar datos desde una copia `.zip` también trae las imágenes.

## Pack 124 · 2026-10-31
- **Editar forma de papel: la vista en vivo ya no enseña imágenes viejas.** Las imágenes de los widgets se guardan en una caché cuya clave incluía la fecha del archivo, pero esa fecha no se leía cuando el programa no se ejecutaba desde la carpeta de datos; entonces una imagen nueva con el mismo nombre recibía la antigua. La vista en vivo reutilizaba los nombres `vivo_1.png`, `vivo_2.png`... en cada ejecución, así que el widget enseñaba formas que no eran las actuales y los cambios de dimensiones no se veían bien. Ahora la clave usa el archivo real (ruta, fecha y tamaño) y cada imagen de la vista en vivo lleva un nombre único.
- **Editar forma de papel**: al abrir el editor, el widget ya no cambia de tamaño (las notas de bienvenida, al 78 %, saltaban al tamaño normal). Y si mientras el editor está abierto algo guarda el estado (por ejemplo, un cambio de set con un atajo global), se guarda la forma original, no la vista previa.

## Pack 123 · 2026-10-31
- **Mover un árbol de widgets a otro set**: clic derecho sobre un widget → *Mover árbol a otro set...* (en la sección de gestión de widgets, junto a *Copiar / Pegar / Exportar árbol*). Eliges un set de la lista **o *Set nuevo...*** y, si quieres, *Ir a ese set después*. El widget y todos sus descendientes se quitan de este set y pasan al otro con la jerarquía intacta; el set de destino no se pisa (si el nombre del set nuevo ya existe se le añade un número) y, si ya tiene widgets en esas posiciones, el árbol se desplaza un poco para que no quede encima.

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
