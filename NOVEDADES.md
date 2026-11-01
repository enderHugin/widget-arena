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
