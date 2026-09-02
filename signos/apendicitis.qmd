---
id: signo-apendicitis
tipo: signo
titulo: "Apendicitis: el apéndice que no se aplasta"
titulo_en: "Appendicitis: the appendix that will not compress"
url: "https://www.biosemiotics.net/apendicitis-el-apendice-que-no-se-aplasta/"
doi: null
version: "1.0"

abstract: >
  Una estructura tubular ciega en fosa ilíaca derecha que no se aplasta bajo la
  sonda, mide más de 6 mm y duele exactamente donde se comprime, es un apéndice
  inflamado. El hallazgo positivo acelera la vía quirúrgica. Pero en la mayoría
  de las exploraciones el apéndice no se ve, y no verlo no lo descarta: en
  población general de urgencias el rendimiento es modesto, y el umbral de 6 mm
  es consenso, no evidencia.

sistema: digestivo
organo: apendice
nivel: intermedio
ventana: fosa-iliaca-derecha-compresion-graduada
sonda: [lineal, convexa]
pregunta_clinica: "¿Puedo ver un apéndice inflamado en el punto donde este paciente duele?"
escenario: [urgencias]
descriptores: [apendicitis, apendice, compresion-graduada, fosa-iliaca-derecha, abdomen-agudo, pocus]
mesh: [Appendicitis, Appendix, Ultrasonography, Point-of-Care Systems]

significante: "Estructura tubular de extremo ciego en fosa ilíaca derecha, que no se colapsa al comprimir con la sonda, con diámetro externo mayor de 6 mm, pared en capas (signo de la diana en corte transversal) y dolor máximo justo sobre ella. Como acompañantes: apendicolito con sombra, líquido periapendicular y grasa vecina hiperecogénica."
significado: "Obstrucción de la luz apendicular con distensión e inflamación de la pared. La estructura no se aplasta porque está a presión, no porque el operador no apriete."
decision: "Un apéndice inflamado bien visto en el punto de dolor, con clínica compatible, es argumento para llamar a cirugía sin más imagen. Un estudio en el que NO viste el apéndice no es un estudio negativo: dilo así, y decide con clínica, laboratorio y —si la sospecha se mantiene— tomografía. Nunca des de alta apoyándote en un apéndice que no encontraste."
umbral: >
  El corte habitual es diámetro externo mayor de 6 mm con apéndice no
  compresible, pero conviene saber de dónde sale: es consenso, no un valor
  derivado de datos. En una serie pediátrica de 398 apéndices efectivamente
  visualizados, el punto de corte con mayor área bajo la curva ROC fue 7,0 mm;
  la mediana del diámetro fue 9,4 mm en los operados y 5,5 mm en los no
  operados. Mover el corte de 6 a 7 mm cambia el balance —menos cirugías
  innecesarias a cambio de más casos perdidos—, y esa es una decisión clínica,
  no una medición.
falsos_positivos:
  - "Asa intestinal llena de gas o heces que no se deja comprimir: la falta de compresibilidad no basta, hace falta el extremo ciego"
  - "Íleon terminal engrosado y adenopatías mesentéricas: en la serie original de 170 pacientes con sospecha de apendicitis, 14 tenían ese patrón y NINGUNO tenía apendicitis —ocho de nueve cultivos fueron positivos para Yersinia—"
  - "Apéndice normal en la zona gris de 5 a 7 mm, sobre todo si no hay dolor focal ni cambios en la grasa vecina"
  - "Apéndice engrosado por otra causa: enfermedad de Crohn, tiflitis, tumor apendicular"
  - "Compresión insuficiente por dolor, defensa u obesidad, leída como incompresibilidad"
  - "Uréter, vasos ilíacos u otra estructura tubular tomada por apéndice: sin Doppler y sin demostrar el extremo ciego, el error es fácil"
  - "Patología anexial en mujeres, que ocupa el mismo cuadrante y la misma clínica"
  - "El error inverso y más peligroso: apéndice perforado que se descomprime. Al vaciarse puede medir menos y volverse compresible, justo cuando el paciente está peor"
se_basa_en: [ecogenicidad, tipos-de-sonda, frecuencia-profundidad, knobology-profundidad]
contrasta_con: []

autores:
  - nombre: "Alcy Edmundo Torres Guerrero"
    orcid: "0000-0002-9742-375X"
    afiliacion: "Universidad Central del Ecuador"
    credit: [conceptualizacion, redaccion, supervision]

medios:
  - tipo: imagen
    destacada: true
    id: "wikimedia:Appendicitis_ultrasound.png"
    descripcion: "Ecografía de apendicitis aguda con apéndice aumentado de calibre y no compresible"
    credito: "Borbély Márton"
    fuente: "Wikimedia Commons"
    fuente_url: "https://commons.wikimedia.org/wiki/File:Appendicitis_ultrasound.png"
    licencia_img: "CC BY-SA 4.0"
    licencia_url: "https://creativecommons.org/licenses/by-sa/4.0/"
    archivo_local: "assets/img/apendicitis-aguda.png"

refs: [puylaert1986, puylaert1986b, prendergast2014, arruzza2022, becker2022, harel2022, held2018, mangona2017, rud2019, bom2021]
fecha: 2026-08-15
actualizado: 2026-08-15
licencia: CC-BY-4.0
---

## La pregunta clínica

Dolor que empezó periumbilical y migró a la fosa ilíaca derecha. Náusea,
febrícula, leucocitosis. La pregunta parece simple —**¿es apendicitis?**— pero
la que el ultrasonido puede responder es más estrecha y conviene enunciarla con
precisión: **¿puedo ver un apéndice inflamado en el punto donde este paciente
duele?**

La diferencia entre esas dos preguntas es el artículo entero. Porque este es el
primer signo del atlas donde **el resultado más frecuente no es "sí" ni "no",
sino "no lo vi"** —y donde confundir "no lo vi" con "no lo tiene" manda a casa
a alguien que se va a perforar.

## Por qué el examen físico no basta

El examen físico en apendicitis no es malo: la migración del dolor, el rebote y
la defensa en fosa ilíaca derecha siguen siendo la columna del diagnóstico, y
ningún ultrasonido los reemplaza. El problema es el rango intermedio —el
paciente que duele pero no tanto, la mujer joven en quien el ovario compite por
el mismo cuadrante, el anciano con clínica sorda, el niño que no localiza—.

Ahí el ultrasonido aporta algo que la mano no puede: **ver el órgano**. Y en
este signo, a diferencia de los anteriores, la sonda no solo mira: también
empuja. La compresión graduada es una maniobra, no una vista.

## Cómo se obtiene la ventana

Esta es la parte que hay que aprender con las manos, y la que el video enseña
peor. La técnica que describió Puylaert en 1986 sigue siendo la misma.

**Sonda lineal** de alta frecuencia en el paciente delgado —el apéndice es
superficial— y **convexa** si el panículo o el gas te ganan.

**Empieza donde duele.** Pídele al paciente que señale con un dedo el punto de
máximo dolor y pon ahí la sonda. Es la mejor pista anatómica disponible.

**Comprime de a poco.** "Graduada" quiere decir exactamente eso: presión
progresiva y sostenida, no un empujón. El objetivo es desplazar el gas
intestinal y acercar el transductor al retroperitoneo sin provocar defensa. Si
aprietas de golpe, el paciente se contrae y pierdes la ventana que estabas
construyendo.

**Ubica los referentes:** el músculo psoas y los vasos ilíacos por debajo, el
ciego por dentro. El apéndice nace de la base del ciego. Recórrelo en
transversal y en longitudinal, y **demuestra el extremo ciego** —es lo que lo
separa de un asa de intestino.

**Si no lo encuentras, mueve al paciente.** El decúbito lateral izquierdo
desplaza asas y a veces revela un apéndice retrocecal. Y si aun así no aparece,
mira alrededor: líquido libre, grasa hiperecogénica, adenopatías, íleon
engrosado. Esos hallazgos secundarios son la información que te llevas cuando
el órgano no se dejó ver.

## El signo

**Significante.** Un tubo de extremo ciego, que no se aplasta cuando comprimes,
de más de 6 mm de diámetro externo, con la pared en capas —en corte transversal
da la imagen de diana— y con el dolor máximo del paciente justo encima. Con
frecuencia acompañan: un apendicolito que deja sombra, una lámina de líquido a
su alrededor y la grasa vecina brillante e inmóvil.

**Significado.** La luz del apéndice se obstruyó, la secreción no sale, la
presión sube y la pared se inflama. **No se aplasta porque está a presión**, no
porque tú no estés apretando lo suficiente. Esa es la traducción exacta del
signo: incompresibilidad es tensión intraluminal.

Y conviene decir lo que este signo tiene de honesto: cuando se ve, se ve bien.
En la serie original de compresión graduada, el apéndice inflamado se visualizó
en 25 de 28 pacientes con apendicitis confirmada (89 %), y en los 32 pacientes
sin apendicitis no se visualizó ningún apéndice. El problema nunca fue el
apéndice enfermo bien visto. El problema es todo lo demás.

## La bifurcación

**Apéndice visualizado, no compresible, mayor de 6 mm, con dolor focal encima**
→ llama a cirugía. Con clínica compatible, esto no necesita tomografía para
avanzar.

**Apéndice visualizado, compresible, menor de 6 mm, sin dolor focal ni cambios
en la grasa** → apéndice normal. Es el único escenario en que el ultrasonido
realmente descarta, y solo si de verdad viste el órgano completo hasta la punta.

**Apéndice NO visualizado** → este es el desenlace más frecuente y el que hay
que saber manejar. En una serie de 543 niños evaluados por sospecha de
apendicitis, **el apéndice no se vio en 398 (73 %)**. De esos, 370 no tenían
apendicitis: el valor predictivo negativo de la no visualización fue 93 %, y
subió a 97 % cuando además los leucocitos estaban por debajo de 10 000. Es
decir: no verlo inclina la balanza, sobre todo con laboratorio tranquilo —pero
uno de cada diez a quince sí lo tiene. En otra serie de 470 apéndices no
visualizados, 47 (10 %) resultaron apendicitis. **No verlo no es descartarlo.**
Si la clínica sigue apuntando ahí, la tomografía es la que cierra: en la
revisión Cochrane de 64 estudios y 10 280 participantes rindió sensibilidad de
0,95 y especificidad de 0,94.

**Apéndice no visualizado pero con signos secundarios** (líquido, grasa
inflamada, adenopatías) → sube la sospecha, pero con menos fuerza de la que uno
querría: la presencia de al menos un signo secundario rindió sensibilidad de
38,3 % y especificidad de 80 %, con valor predictivo positivo de solo 17,3 %.
Sirven más para tranquilizar cuando faltan que para confirmar cuando están.

## Dónde NO confiar

- **El umbral de 6 mm es un acuerdo, no un dato.** Es el criterio más objetivo y
  más aceptado, pero carece de un respaldo empírico que lo fije en ese número.
  Cuando se buscó el corte óptimo en 398 apéndices visualizados de una población
  pediátrica, el mejor punto por curva ROC fue 7,0 mm. Entre 5 y 7 mm estás en
  una zona gris donde el número no decide: deciden el dolor focal, la grasa y la
  clínica.
- **El rendimiento en urgencias generales es modesto, y hay que decirlo.** En un
  estudio prospectivo multicéntrico de 256 pacientes adultos, con prevalencia de
  28,1 %, el POCUS hecho por médicos de urgencias con experiencia variable tuvo
  sensibilidad de 0,85 pero **especificidad de 0,63**, con razón de
  verosimilitud positiva de apenas 2,29. Los propios autores concluyen que no
  alcanza para funcionar como prueba definitiva en población no seleccionada.
  Un LR+ de 2,29 mueve poco la probabilidad: no es el argumento que crees que
  es.
- **Los números buenos vienen de contextos buenos.** En un hospital pediátrico
  dedicado, la ecografía rindió sensibilidad de 94,0 % y especificidad de 93,7 %
  en turno diurno, y 92,0 % y 91,2 % en turno nocturno. Y el metaanálisis de
  adultos da 0,821 y 0,859 para ultrasonido frente a 0,972 y 0,956 para
  tomografía. Ese es el techo del método, no tu resultado esperable la primera
  semana.
- **Cuidado con los metaanálisis que descartan los estudios equívocos.** Ese
  mismo metaanálisis encontró que los trabajos que excluyeron los hallazgos
  indeterminados reportaron valores significativamente mayores que el resto
  (p < 0,0001). Traducido: parte de la buena fama del ultrasonido en apendicitis
  se construyó borrando del cálculo exactamente los casos que más te van a pasar
  a ti.
- **No visualizado ≠ negativo.** Escríbelo así en la historia clínica. "No se
  visualizó el apéndice; no hay líquido libre ni cambios en la grasa" es
  información. "Ecografía negativa para apendicitis" cuando nunca viste el
  órgano es una frase que puede matar a alguien.
- **El apéndice perforado engaña al descomprimirse.** Al vaciarse puede medir
  menos y volverse compresible justo cuando el paciente está peor. Si la clínica
  empeora y tu imagen mejora, cree en la clínica.
- **Distinguir complicada de no complicada excede al ultrasonido.** Una revisión
  sistemática que buscaba separar apendicitis complicada de no complicada
  encontró solo dos estudios de ultrasonido, insuficientes para estimar su
  rendimiento; ni siquiera la tomografía lo resuelve bien (sensibilidad 78 %,
  especificidad 91 %). No pretendas graduar la gravedad con la sonda.
- **La adenitis mesentérica ocupa el mismo lugar.** Ganglios mesentéricos
  aumentados con íleon terminal engrosado, sin apéndice visible, apuntan a
  adenitis e ileítis terminal, no a apendicitis. Esa distinción, descrita en la
  misma serie que popularizó la técnica, evita apendicectomías innecesarias.

## Practica esto

No empieces por el paciente con sospecha. Empieza por la técnica, en pacientes
sin dolor abdominal: localiza el psoas y los vasos ilíacos en fosa ilíaca
derecha y practica **la compresión graduada** —presión lenta, sostenida,
observando cómo el gas se desplaza y la profundidad útil aumenta—. Cuenta hasta
cinco mientras aprietas. Ese ritmo es la técnica.

Después, en pacientes con sospecha, hazlo en este orden y en voz alta: primero
que el paciente señale el punto con un dedo; después la sonda ahí; después los
referentes; después el apéndice. Y al terminar, di siempre una de tres frases,
nunca otra: *"lo vi y está inflamado"*, *"lo vi completo y está normal"*, o
*"no lo vi"*. Prohíbete la cuarta —"parece normal"— porque no significa nada.

Lleva la cuenta de cuántas veces dices la tercera. Si tu tasa de "no lo vi" se
parece al 73 % de la literatura, estás normal. Ese número no es tu fracaso: es
la línea de base de este signo.

## Discusión abierta

¿Qué haces en tu servicio con el paciente cuya ecografía no mostró el apéndice
pero cuya clínica no cede: observación, tomografía o consulta quirúrgica
directa? ¿Y cómo lo escribes en la historia?
