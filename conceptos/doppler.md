---
id: doppler
tipo: concepto
titulo: "Doppler: el color no mide, el ángulo decide"
url: ""

abstract: >
  El Doppler detecta movimiento midiendo el cambio de frecuencia del eco que
  vuelve. Lo que informa no es la velocidad real sino su componente hacia la
  sonda, así que el ángulo de insonación gobierna todo: a 90° el flujo real se
  vuelve invisible, y por encima de 60° el error de medición crece de forma
  exponencial. El color responde "¿hay flujo y hacia dónde?"; cuantificar exige
  espectral, ángulo corregido y saber leer el aliasing.

dominio: fisica
nivel: intermedio
capitulo: 2
orden: 4
tags: [doppler, color, espectral, pulsado, angulo, aliasing, seguridad]
relacionado_con: [propagacion-sonido, frecuencia-profundidad, ecogenicidad, tipos-de-sonda]
prerequisito_de: [signo-coledocolitiasis, signo-absceso-partes-blandas, signo-hernia-complicada]

autores:
  - nombre: "Alcy Edmundo Torres Guerrero"
    orcid: "0000-0002-9742-375X"
    afiliacion: "Universidad Central del Ecuador"
    credit: [conceptualizacion, redaccion, supervision]

refs: [boote2003, elwertowski2014, vandenhof2018, hangiandreou2003]
fecha: 2026-08-15
actualizado: 2026-08-15
licencia: CC-BY-NC-4.0
---

## Qué mide realmente el Doppler

Cuando el haz choca contra algo que se mueve, el eco vuelve con una **frecuencia
distinta** de la que salió. Si el objeto se acerca, la frecuencia sube; si se
aleja, baja. Esa diferencia entre la frecuencia emitida y la recibida es el
**desplazamiento Doppler**, y es lo único que el equipo mide de verdad.

Todo lo demás —los colores, la curva espectral, los números en centímetros por
segundo— son interpretaciones que el aparato construye a partir de ese
desplazamiento. Conviene tenerlo presente, porque explica de golpe casi todos
los errores del método: **si el desplazamiento se mide mal, todo lo derivado
está mal, y la pantalla no avisa.**

## El ángulo lo gobierna todo

Aquí está el concepto que hay que entender antes de tocar el botón de color.

El equipo no percibe la velocidad del glóbulo rojo: percibe **su componente en
la dirección del haz**. Es la misma razón por la que un tren que cruza delante
de ti no te cambia el tono de la bocina, y sí lo hace cuando viene hacia ti.

Las consecuencias son tres, y las tres son clínicas:

- **A 90°, un flujo real puede verse como ausencia de flujo.** No hay componente
  hacia la sonda, no hay desplazamiento, no hay color. La vena está permeable y
  tu pantalla dice que no pasa nada.
- **Cuanto más paralelo al flujo, mejor la señal.** Por eso en vascular se
  angula el haz o se usa el ajuste de dirección del cursor en vez de mirar de
  frente.
- **Para cuantificar, el ángulo debe corregirse y mantenerse bajo.** El estándar
  vascular exige explorar con un ángulo de insonación de 60°, porque por encima
  de ese valor **el error de medición aumenta de forma exponencial**.

De ahí el título de esta ficha. El color contesta una pregunta binaria —¿hay
flujo, y hacia dónde va?—. Los números exigen mucho más cuidado, y en el primer
contacto la mayoría de las veces no hacen falta.

## Los tres modos que vas a usar

**Doppler color.** Superpone color sobre la imagen en escala de grises dentro de
una caja que tú colocas. Por convención, el color indica dirección respecto a la
sonda —no "arteria roja, vena azul"—. Responde: ¿hay flujo aquí?

**Doppler espectral (pulsado).** Toma una muestra en un punto que eliges y
dibuja velocidad contra tiempo. Es el modo que permite cuantificar, y también el
que exige corregir el ángulo. Es el que usarás en la Oleada 3 para E/e', VTI o
gasto cardíaco.

**Doppler de potencia.** Muestra la cantidad de movimiento sin decir la
dirección. Es más sensible a flujos lentos y menos dependiente del ángulo, pero
renuncia a la información direccional. Útil para "¿hay algo de perfusión?" en
una pared inflamada.

Para lo que este atlas necesita hoy —descartar que una estructura tubular sea un
vaso, comprobar que una colección no tenga flujo dentro, separar el colédoco de
la arteria hepática— **el color basta y sobra**.

## Aliasing: cuando el equipo se queda corto

El Doppler pulsado toma muestras a intervalos. Como toda medición muestreada,
tiene un límite: si el desplazamiento excede la mitad de la frecuencia con que
se muestrea, el equipo ya no puede representar la velocidad y **la envuelve** —la
dibuja al revés—.

En la pantalla se ve como un flujo que "se sale por arriba y reaparece por
abajo" en el espectro, o como un mosaico de colores en medio de un vaso donde el
flujo en realidad va en una sola dirección.

No es una patología: es el equipo diciendo que se le acabó el rango. Se corrige
subiendo la escala de velocidad, bajando la frecuencia, o moviendo la línea de
base. Confundir aliasing con turbulencia real es el error más frecuente de quien
empieza a usar color.

## Dónde NO confiar

- **Ausencia de color no es ausencia de flujo.** Ángulo de 90°, escala
  demasiado alta, ganancia de color baja o filtro de pared agresivo apagan un
  flujo real. Antes de decir "no hay flujo", cambia el ángulo y baja la escala.
- **Presencia de color no siempre es flujo.** El movimiento del paciente, la
  respiración o la transmisión de un latido vecino pintan color donde no hay
  vaso. La ganancia de color demasiado alta llena de ruido la caja.
- **No cuantifiques con un ángulo que no corregiste.** Por encima de 60° el
  error crece exponencialmente, y el número que aparece en pantalla no lleva
  ninguna advertencia.
- **El color es más lento que el modo B.** Activar la caja baja la tasa de
  cuadros; en estructuras que se mueven rápido eso degrada la imagen que estabas
  usando para orientarte. Ábrela pequeña y ciérrala cuando termines.
- **El Doppler deposita más energía que el modo B, y eso importa.** La guía
  obstétrica canadiense señala explícitamente que el mayor depósito de energía
  preocupa de forma particular en los estudios Doppler —pulsado, color y
  potencia—, y recomienda mantener la exposición tan baja como sea
  razonablemente posible, limitando el tiempo sobre estructuras críticas. Esto
  se aplica al embarazo temprano, al ojo y al paciente febril. **No dejes el
  color encendido "por si acaso".**
- **El aliasing imita turbulencia.** Sube la escala antes de diagnosticar un
  flujo desordenado.

## Practica esto

Empieza por hacer desaparecer un flujo que sabes que existe. Coloca el color
sobre una arteria superficial —radial, braquial, carótida— y ve girando la sonda
hasta ponerte perpendicular al vaso. Mira cómo el color se apaga con el vaso
intacto delante de ti. Esa imagen, provocada a propósito una vez, vale más que
cualquier explicación del coseno.

Después juega con la escala. En el mismo vaso, bájala hasta que aparezca el
mosaico del aliasing y vuelve a subirla hasta que se limpie. Aprende a
reconocer ese mosaico como "escala equivocada" y no como "turbulencia".

Y termina con el gesto que vas a usar de verdad en la clínica: sobre una
colección de partes blandas o sobre el hilio hepático, enciende el color **dos
segundos**, comprueba si hay flujo dentro y apágalo. Ese es el uso honesto del
Doppler en el primer contacto: una pregunta binaria, respondida rápido y con la
energía apagada enseguida.
