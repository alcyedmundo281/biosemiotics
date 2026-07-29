---
id: signo-neumotorax
tipo: signo
titulo: "Neumotórax en POCUS: la ausencia de sliding no basta"
titulo_en: "Pneumothorax in POCUS: absent lung sliding is not enough"
url: ""
doi: null
version: "1.0"

abstract: >
  La ausencia de sliding pleural, líneas B y pulso pulmonar crea un patrón
  compatible con neumotórax; encontrar un lung point lo confirma con alta
  especificidad. POCUS permite una evaluación rápida al lado de la camilla,
  pero ninguna ausencia aislada basta. Apnea, ventilación selectiva,
  adherencias, pleurodesis, fibrosis y bullas pueden imitarlo, y un lung point
  puede faltar cuando el neumotórax es extenso.

sistema: respiratorio
organo: pleura
nivel: principiante
ventana: intercostal-anterior-lateral
sonda: [lineal, convexa, sectorial]
pregunta_clinica: "¿Hay aire pleural separando ambas pleuras en este punto?"
escenario: [urgencias, uci]
descriptores: [neumotorax, sliding, lung-point, pleura, efast, pocus]
mesh: [Pneumothorax, Pleura, Ultrasonography, Point-of-Care Systems]

significante: "Línea pleural sin sliding, sin líneas B y sin pulso pulmonar; el lung point muestra la transición hacia pleura en contacto."
significado: "Aire en el espacio pleural que separa la pleura visceral de la parietal en la zona examinada."
decision: "Integra el patrón con estabilidad y mecanismo; en un paciente inestable compatible, activa tratamiento urgente sin retrasarlo por intentar documentar todos los signos."
umbral: >
  No usa un conteo. La presencia de sliding o de líneas B excluye neumotórax en
  el punto examinado. La ausencia de sliding aislada no confirma el diagnóstico;
  el lung point aporta confirmación cuando puede encontrarse.
falsos_positivos:
  - "Apnea o ventilación muy superficial"
  - "Intubación endobronquial o ventilación selectiva"
  - "Adherencias pleurales, pleurodesis o fibrosis"
  - "Contusión pulmonar, síndrome de dificultad respiratoria o consolidación extensa"
  - "Bullas enfisematosas e interfaces anatómicas que imitan lung point"
  - "Sonda sobre una costilla o línea pleural mal identificada"
se_basa_en: [sliding-lung-point, modo-m, artefacto-reverberacion, tipos-de-sonda]
contrasta_con: [signo-perfil-a]

autores:
  - nombre: "Alcy Edmundo Torres Guerrero"
    orcid: "0000-0002-9742-375X"
    afiliacion: "Universidad Central del Ecuador"
    credit: [conceptualizacion, redaccion, supervision]

medios:
  - tipo: imagen
    id: "wikimedia:PENDIENTE"
    descripcion: "Modo M con patrón de orilla normal y patrón estratosfera"

refs: [lichtenstein2000, staub2018, skulec2021, volpicelli2012]
fecha: 2026-07-29
actualizado: 2026-07-29
licencia: CC-BY-NC-4.0
---

## La pregunta clínica

En trauma, disnea brusca, deterioro ventilatorio o shock, pregunta:
**¿hay aire pleural separando las dos pleuras en esta región?**

La respuesta se construye con movimiento y artefactos. No se obtiene con una
imagen fija ni con un único signo negativo.

## Cómo se obtiene la ventana

En decúbito supino, comienza en el tórax anterior, donde el aire pleural tiende a
acumularse. Coloca una sonda lineal entre dos costillas; una convexa o sectorial
también sirve si la profundidad o el contexto lo exige.

Identifica dos sombras costales y, entre ellas, la línea pleural. Observa en modo
B antes de activar modo M. Explora varios espacios desde anterior hacia lateral
y compara con el lado opuesto.

## El signo

**Significante.** La línea pleural no se desliza. No aparecen líneas B ni pulso
pulmonar. Persisten líneas A. En modo M, el patrón granular bajo la pleura se
reemplaza por líneas horizontales: estratosfera o código de barras.

**Significado.** Ese conjunto indica que, en ese punto, la pleura visceral no
está transmitiendo movimiento a la pared. El neumotórax es una causa importante,
pero la ausencia de sliding por sí sola no revela cuál.

El **lung point** es la transición respiratoria entre el patrón sin contacto y
una zona donde reaparece sliding o artefactos pleurales. Cuando se identifica
correctamente, confirma neumotórax; puede no existir en uno muy extenso.

## La bifurcación

**Sliding o líneas B presentes** → no hay neumotórax en ese punto.

**Sliding ausente, pero pulso pulmonar presente** → las pleuras están en
contacto; busca otra causa de inmovilidad.

**Sliding, líneas B y pulso ausentes, con lung point** → neumotórax confirmado.

**Paciente inestable con cuadro compatible** → la ecografía acelera, no retrasa.
No prolongues el examen intentando encontrar un lung point si la conducta
salvadora ya está indicada.

## Dónde NO confiar

- **Ausencia de sliding no equivale a neumotórax.** Apnea, ventilación selectiva,
  adherencias, fibrosis y pleurodesis también la producen.
- **Sliding presente es local.** Descarta aire pleural donde miraste, no en todo
  el hemitórax.
- **Un lung point ausente no descarta.** En neumotórax completo puede no haber
  transición accesible.
- **Bullas e interfaces pueden imitar el punto.** Confirma el patrón respiratorio
  y el conjunto de signos.
- **Modo M no corrige una mala ventana.** Si la línea pasa por costilla, el código
  de barras es técnico.
- **No esperes una imagen perfecta en inestabilidad.** La clínica y la necesidad
  de intervención urgente mandan.

## Evidencia

1. Lichtenstein D, et al. The “lung point”: an ultrasound sign specific to
   pneumothorax. *Intensive Care Med.* 2000.
2. Staub LJ, et al. Chest ultrasonography for the emergency diagnosis of
   traumatic pneumothorax and haemothorax: a systematic review and meta-analysis.
   *Injury.* 2018.
3. Skulec R, et al. Lung Point Sign in Ultrasound Diagnostics of Pneumothorax:
   Imitations and Variants. *Emerg Med Int.* 2021.
4. Volpicelli G, et al. International evidence-based recommendations for
   point-of-care lung ultrasound. *Intensive Care Med.* 2012.

## Practica esto

En cinco tórax sin sospecha de neumotórax, localiza pleura en varios espacios.
Di en voz alta: “sliding presente, líneas B sí/no, pulso pulmonar sí/no”. Después
documenta el patrón de orilla en modo M. La seguridad empieza reconociendo la
normalidad.

## Discusión abierta

¿Qué causa de sliding ausente te preocupa más confundir con neumotórax y qué
segundo signo usas para salir del error?
