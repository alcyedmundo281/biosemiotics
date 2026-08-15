---
id: signo-derrame-pleural
tipo: signo
titulo: "Derrame pleural"
titulo_en: "Pleural effusion"
url: "https://www.biosemiotics.net/derrame-pleural-ultrasonido/"
doi: null
version: "2.0"

abstract: >
  Colección líquida entre las pleuras parietal y visceral, habitualmente visible
  como un espacio anecoico o hipoecoico sobre el diafragma. El ultrasonido
  confirma su presencia, extensión, movilidad y complejidad, además de mostrar
  el pulmón atelectásico y guiar un sitio seguro para toracocentesis. La
  ecogenicidad orienta, pero no establece por sí sola la etiología ni distingue
  de forma definitiva transudado de exudado.

sistema: respiratorio
organo: pulmon
nivel: principiante
ventana: base-pulmonar
sonda: [convexa, sectorial]
pregunta_clinica: "¿Hay líquido pleural, cuánto parece haber y existe una ventana segura para intervenir?"
escenario: [urgencias, consulta, hospitalizacion, uci]
descriptores: [derrame-pleural, ultrasonido-pulmonar, pocus, toracocentesis, disnea]
mesh: [Pleural Effusion, Ultrasonography, Thoracentesis, Point-of-Care Systems]

significante: "Espacio anecoico entre la pared torácica y el pulmón, sobre el diafragma."
significado: "Líquido en el espacio pleural."
decision: "Cuantificar. Considerar toracocentesis diagnóstica/terapéutica guiada por ultrasonido."
umbral: >
  No existe un único volumen que obligue a drenar. La decisión depende de
  síntomas, etiología probable, infección, accesibilidad y seguridad.
falsos_positivos:
  - ascitis-subdiafragmatica
  - consolidacion-pulmonar
  - organo-solido
  - engrosamiento-o-masa-pleural
  - derrame-pericardico
  - ventana-mala
se_basa_en: [ecogenicidad, artefacto-refuerzo-posterior, tipos-de-sonda]
contrasta_con: [signo-lineas-b]

autores:
  - nombre: "Alcy Edmundo Torres Guerrero"
    orcid: null
    afiliacion: "Universidad Central del Ecuador"
    credit: [conceptualizacion, redaccion]

medios:
  - tipo: imagen
    id: "wikimedia:Pleural effusion on lung ultrasound"
    descripcion: "Ecografía pulmonar que muestra líquido pleural hipoecoico por encima del diafragma"
    credito: "Gillman L. y Kirkpatrick A. (fotograma adaptado)"
    fuente: "Wikimedia Commons"
    fuente_url: "https://commons.wikimedia.org/wiki/File:Portable-bedside-ultrasound-the-visual-stethoscope-of-the-21st-century-1757-7241-20-18-S7.ogv"
    licencia_img: "CC BY 2.0"
    licencia_url: "https://creativecommons.org/licenses/by/2.0/"
    archivo_local: "assets/img/derrame-pleural.jpg"

refs: [volpicelli2012, soni2015, balik2006, asciak2023, roberts2023, ibitoye2018, teichgraeber2018, rodriguezlima2020]
fecha: 2026-07-17
actualizado: 2026-07-17
licencia: CC-BY-4.0
---

## La pregunta clínica

Un paciente con disnea. Antecedente oncológico, cardíaco o renal. Auscultas la
base y suena distinto —o suena a nada. La pregunta que resuelve el manejo no es
"¿hay líquido?"; es **¿cuánto hay, y vale la pena sacarlo?**

## Por qué el examen físico no basta

Matidez y disminución del murmullo vesicular son signos tardíos y groseros: en
derrames pequeños o loculados no aparecen, y en el paciente obeso o con mala
posición se pierden. La radiografía de tórax portátil, además, subestima los
derrames posteriores. Treinta segundos de ecografía en la base pulmonar dan
información que ninguna de las dos.

## Cómo se obtiene la ventana

Sonda convexa o sectorial, apoyada en la base pulmonar, justo por encima del
diafragma. Lo que buscas primero **no es el líquido**: es el **diafragma**, esa
línea curva brillante que separa el tórax del abdomen. Con el diafragma como
ancla, el resto se ordena solo.

Posición del paciente: idealmente sentado o con el tórax inclinado a 30° si no
tolera sentarse. Esa inclinación importa —no es cosmética— porque las fórmulas
de cuantificación se calibraron con posiciones específicas.

## El signo

**Significante.** Espacio anecoico entre la pared torácica y el pulmón, sobre el
diafragma. Suele acompañarse de refuerzo posterior y, si el derrame es grande,
del "pulmón flotando" en su interior.

**Significado.** Líquido en el espacio pleural.

## Variantes del signo

No todo derrame es anecoico puro. Tres variantes cambian el manejo y hay que
reconocerlas como parte del signo, no como su ausencia:

- **Empiema.** Ecos internos flotantes —el clásico "**plancton pleural**"— y
  a veces septos gruesos. El líquido deja de ser puramente anecoico. La fórmula
  de cuantificación falla y la toracocentesis con aguja fina puede no drenar:
  suele hacer falta tubo de tórax [asciak2023].
- **Hemotórax.** Sedimentación en capas (fase densa por debajo, líquida por
  arriba): el **signo del hematocrito**. Es un derrame verdadero, pero
  heterogéneo, y traduce sangrado activo o reciente.
- **Derrame loculado.** Septos hiperecoicos que dividen el espacio pleural. El
  líquido no fluye libre con los cambios de posición, y la fórmula asume fluido
  libre —así que la estimación se rompe [roberts2023].

Reconocer estas variantes es tan importante como reconocer el signo puro: te
cambia el drenaje, el pronóstico y a veces la especialidad que maneja el caso.

## Cuánto líquido hay

Aquí la ecografía deja de ser diagnóstica y se vuelve cuantitativa. La fórmula
más práctica al pie de la cama, en el paciente supino con ligera elevación del
tronco (el escenario típico de UCI):

**Volumen estimado (mL) ≈ 20 × separación pleural máxima (mm)**

Se mide la separación máxima entre la pleura parietal y el pulmón en una ventana
definida, al final de la espiración, y se multiplica por 20. Fórmula de Balik en
81 pacientes con ventilación mecánica, supinos con el tronco elevado 15°: el
error medio de predicción fue de 158,4 ± 160,6 mL —la desviación es tan grande
como la media, de modo que la fórmula ordena la magnitud pero no fija el
volumen—, y el estudio excluyó empiema, hemotórax y patología diafragmática
[balik2006].

Existen alternativas para otros escenarios. Teichgräber validó contra TC una
fórmula basada en el grosor del creciente en el sexto espacio intercostal
[teichgraeber2018]; Ibitoye comparó cuatro fórmulas contra el volumen drenado y
halló mejor correlación con una variante en posición erecta [ibitoye2018]. Todas
comparten el mismo principio: convertir una distancia en un volumen aproximado.

Ninguna estimación es exacta. Son órdenes de magnitud útiles para decidir si
puncionar y para anticipar cuánto drenaje esperar —no cifras para reportar con
dos decimales [soni2015].

## La bifurcación

Con el signo confirmado y una estimación de volumen en mano, la conducta se
ordena en tres escenarios:

**Líquido simple, pequeño y contexto conocido** → correlacionar con la clínica
y seguir. No toda ecogenicidad anecoica pide aguja.

**Derrame nuevo, unilateral, atípico, sintomático o complejo** → estudio
etiológico y valorar toracocentesis diagnóstica o terapéutica guiada por
ultrasonido [roberts2023].

**Ventana insegura o líquido loculado** → **no puncionar** por una referencia
anatómica fija. Buscar otro sitio con mejor ventana o solicitar apoyo experto
[asciak2023].

## Antes de puncionar

Toracocentesis guiada por ecografía en tiempo real, hecha por intensivistas en
UCI: 1 neumotórax en 81 procedimientos = **1,2 %** de complicaciones mecánicas
[rodriguezlima2020]. Es una tasa baja, y sostiene el argumento de que el
procedimiento no es del radiólogo intervencionista por decreto —es de quien
tiene la sonda al pie de la cama y sabe usarla.

Dos condiciones para que ese 1,2 % sea tu 1,2 %: **guía en tiempo real** (no
marcar en la piel y puncionar a ciegas cinco minutos después), y verificar
**pulmón deslizándose** en el sitio de punción antes de meter la aguja.

## Dónde NO confiar

Un derrame anecoico puede ser transudado o exudado; los ecos y septos sugieren
complejidad pero no reemplazan al análisis del líquido. Además, seis situaciones
imitan al signo sin ser derrame verdadero:

- **Ascitis subdiafragmática.** Un derrame masivo del lado derecho y una ascitis
  se parecen si pierdes de vista el diafragma. Regla: **si no ves el diafragma,
  no llamas al espacio pleural.**
- **Consolidación pulmonar.** Un pulmón consolidado tiene apariencia de tejido
  sólido —"hepatización pulmonar"— con broncograma aéreo. Se distingue del
  derrame por su textura interna y por no cambiar de forma con la respiración.
- **Órgano sólido subdiafragmático.** Hígado o bazo hipoecoicos, sobre todo en
  ventana lateral baja, pueden pasar por derrame si el diafragma no está
  identificado.
- **Engrosamiento o masa pleural.** Una pleura engrosada aparece como banda
  hipoecoica que remeda un derrame delgado; una masa pleural puede simular un
  derrame loculado. Ninguno se mueve con la respiración ni cambia con la postura.
- **Derrame pericárdico.** En ventana subxifoides o paraesternal baja, un
  derrame pericárdico grande puede confundirse con pleural izquierdo. La regla
  anatómica: el pericárdico rodea el corazón; el pleural queda por fuera del
  saco pericárdico.
- **Ventana mala.** Poca ganancia o profundidad excesiva simulan un espacio
  seco donde hay líquido pequeño —o al revés, generan artefactos que se
  confunden con un derrame que no existe.

Si el patrón no calza con la clínica, **la clínica manda**. El signo es una
entrada de información, no un veredicto.

## Practica esto

Esta semana, en cinco pacientes sin derrame conocido, ve a la base pulmonar y
**encuentra el diafragma** en menos de diez segundos. Solo eso. Cuando el
diafragma te salga sin pensar, el derrame —cuando aparezca— será obvio.

## Discusión abierta

En tu servicio, ¿quién hace la toracocentesis y con qué guía? ¿Has usado alguna
de estas dos fórmulas para decidir puncionar, o el volumen todavía se estima "a
ojo"?
