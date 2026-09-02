---
id: signo-sobrecarga-vd
tipo: signo
titulo: "Ventrículo derecho dilatado (sobrecarga aguda de presión)"
titulo_en: "Right ventricular overload (pulmonary embolism)"
url: "https://www.biosemiotics.net/sobrecarga-del-ventriculo-derecho-tep/"
doi: null
version: "1.1"

abstract: >
  Ventrículo derecho dilatado, tabique interventricular aplanado hacia el
  ventrículo izquierdo (signo de la D) y TAPSE reducido en el paciente con
  disnea aguda o inestabilidad. Señala sobrecarga de presión del VD,
  típicamente por tromboembolia pulmonar que obstruye el lecho vascular
  pulmonar. Con clínica compatible, acelera la anticoagulación empírica y, si
  hay inestabilidad, la activación para trombólisis o embolectomía. Su
  ausencia no descarta una tromboembolia pulmonar submasiva sin repercusión
  hemodinámica.

sistema: cardiovascular
organo: corazon
nivel: intermedio
ventana: paraesternal-apical-subcostal
sonda: [sectorial]
pregunta_clinica: "¿Este paciente con disnea o inestabilidad tiene signos de sobrecarga aguda del ventrículo derecho que sugieran tromboembolia pulmonar?"
escenario: [urgencias, hospitalizacion, uci]
descriptores: [sobrecarga-vd, tromboembolia-pulmonar, dilatacion-vd, septo-d, mcconnell, focus]
mesh: [Pulmonary Embolism, "Ventricular Dysfunction, Right", Echocardiography, Point-of-Care Systems]

significante: "Ventrículo derecho dilatado (su diámetro se acerca o supera al del ventrículo izquierdo), tabique interventricular aplanado o desplazado hacia el ventrículo izquierdo en sístole (signo de la D), TAPSE reducido y, en algunos casos, acinesia de la pared libre media del VD con el ápex conservado (signo de McConnell)."
significado: "El ventrículo derecho, de pared delgada y diseñado para bajas presiones, se dilata y falla agudamente ante un aumento súbito de la resistencia vascular pulmonar —típicamente una tromboembolia pulmonar que obstruye una porción significativa del lecho vascular."
decision: "Con clínica compatible (disnea aguda, hipoxemia, taquicardia, factores de riesgo trombótico), estos hallazgos aceleran la anticoagulación empírica y, si hay inestabilidad hemodinámica, la activación para trombólisis o embolectomía; la ausencia de sobrecarga del VD no descarta una tromboembolia pulmonar submasiva sin repercusión hemodinámica."
umbral: >
  No hay un hallazgo aislado suficiente. Para el conjunto de signos de
  sobrecarga derecha ("right heart strain") en el diagnóstico de tromboembolia
  pulmonar, la sensibilidad reportada es 53 % (IC95% 45–61 %) y la
  especificidad 83 % (IC95% 74–90 %): útil para orientar la sospecha y
  adelantar conductas, insuficiente para descartar por su cuenta. La guía ESC
  de tromboembolia pulmonar señala la relación de diámetros VD:VI ≥ 1 y el
  TAPSE < 16 mm como hallazgos de disfunción del VD con valor pronóstico en
  el paciente ya diagnosticado —no es un criterio combinado obligatorio:
  cualquiera de los dos, en el contexto correcto, ya aporta información de
  severidad, no un umbral de tamizaje aislado.
falsos_positivos:
  - "Cor pulmonale crónico (EPOC, hipertensión pulmonar crónica, cardiopatía congénita): dilata el VD de forma crónica; pared libre gruesa (>5 mm) y aurícula derecha mayor que la izquierda orientan a cronicidad, no a un evento agudo"
  - "Signo de McConnell descrito también en infarto del ventrículo derecho: no es exclusivo de tromboembolia pulmonar"
  - "Ventana subóptima o corte oblicuo del ápex que simula una relación VD:VI aumentada sin serlo"
  - "TAPSE reducido por disfunción del ventrículo izquierdo que arrastra secundariamente al derecho"
  - "Ausencia de todos estos hallazgos no descarta tromboembolia pulmonar submasiva o de bajo riesgo hemodinámico"
se_basa_en: [ventanas-cardiacas, modo-m, ecogenicidad, tipos-de-sonda]
contrasta_con: [signo-taponamiento-cardiaco]

autores:
  - nombre: "Alcy Edmundo Torres Guerrero"
    orcid: null
    afiliacion: "Universidad Central del Ecuador"
    credit: [conceptualizacion, redaccion]

medios:
  - tipo: imagen
    id: "wikimedia:McConnell-Sign-in-a-Patient-with-Massive-Acute-Pulmonary-Embolism-201097.f1.ogv"
    descripcion: "Fotograma de ecocardiografía apical de cuatro cámaras que muestra el signo de McConnell en una embolia pulmonar masiva antes de la trombólisis"
    credito: "Shafiq Q, Assaly R y Kanjwal Y (fotograma derivado del video original)"
    fuente: "Wikimedia Commons"
    fuente_url: "https://commons.wikimedia.org/wiki/File:McConnell-Sign-in-a-Patient-with-Massive-Acute-Pulmonary-Embolism-201097.f1.ogv"
    licencia_img: "CC BY 3.0"
    licencia_url: "https://creativecommons.org/licenses/by/3.0/"
    archivo_local: "assets/img/sobrecarga-vd.jpg"
    original_local: "assets/media/sobrecarga-vd-mcconnell.ogv"
    adaptacion: "Fotograma fijo de la previsualización de Wikimedia Commons, 500 × 340 px"
    referencia: "shafiq2011"

refs: [via2014, fields2017, mandoli2021, konstantinides2019, sanz2019, shafiq2011]
fecha: 2026-08-07
actualizado: 2026-08-07
licencia: CC-BY-4.0
---

## La pregunta clínica

Un paciente con disnea súbita, dolor torácico pleurítico, taquicardia o
hipotensión inexplicada, con factores de riesgo trombótico —cirugía reciente,
inmovilización, cáncer, embarazo, anticonceptivos—. La pregunta no es "¿tiene
tromboembolia pulmonar?" —eso lo confirma la angio-TC o la gammagrafía—, sino
**¿hay signos de sobrecarga aguda del ventrículo derecho que cambien el manejo
mientras se organiza la confirmación?**

## Por qué el examen físico no basta

Taquicardia y taquipnea son inespecíficas. El score de Wells y el dímero D
orientan la probabilidad pretest, pero un paciente inestable no siempre tiene
tiempo para esperar la angio-TC. El ultrasonido cardíaco a la cabecera no
reemplaza la confirmación por imagen; puede acelerar la anticoagulación
empírica o la activación del equipo de tromboembolia masiva en minutos.

## Cómo se obtiene la ventana

Usa sonda sectorial. La vista apical de cuatro cámaras y la subcostal son las
más rentables para comparar el tamaño del VD contra el VI lado a lado. Agrega
la paraesternal de eje corto a nivel de los músculos papilares para ver el
tabique interventricular en corte transversal —ahí se aprecia mejor el signo
de la D—. Si quieres estimar el TAPSE, coloca el cursor de modo M sobre el
anillo tricuspídeo, en la pared libre del VD.

Antes de comparar tamaños, confirma que estás viendo el ventrículo derecho de
verdad: búscale la banda moderadora, esa estructura muscular que cruza la
cavidad cerca del ápex y es exclusiva del VD. Te confirma el corte antes de
que saques conclusiones sobre proporciones.

## El signo

**Significante.** Ventrículo derecho dilatado —su diámetro se acerca o supera
al del ventrículo izquierdo en la vista apical o subcostal, cuando lo normal
es que el VD sea claramente menor—; tabique interventricular aplanado o
desplazado hacia el ventrículo izquierdo en sístole, dándole al corte
transversal del VI forma de D en vez de círculo; TAPSE reducido; y, en algunos
casos, acinesia de la pared libre media del VD con el ápex contrayéndose
normalmente (signo de McConnell).

**Significado.** El ventrículo derecho —de pared delgada, diseñado para bajas
presiones— se dilata y falla agudamente ante un aumento súbito de la
resistencia vascular pulmonar. La causa más frecuente en el paciente agudo es
una tromboembolia pulmonar que obstruye una porción significativa del lecho
vascular pulmonar.

## La bifurcación

**Sin dilatación del VD, tabique normal y TAPSE conservado** → no excluye
tromboembolia pulmonar, pero hace menos probable que sea masiva o submasiva de
alto riesgo; sigue la ruta diagnóstica estándar según la probabilidad clínica.

**VD dilatado con tabique en D o TAPSE reducido, en un paciente inestable o
con probabilidad clínica alta/intermedia de tromboembolia pulmonar (Wells,
Ginebra)** → sospecha fuerte de sobrecarga aguda: si el paciente está
inestable, activa al equipo para trombólisis o embolectomía sin esperar la
confirmación por imagen si no la tolera. Si está estable, estos hallazgos
apoyan iniciar anticoagulación empírica mientras se confirma —solo cuando la
probabilidad pretest ya era alta o intermedia, sin contraindicación y sin
riesgo de sangrado prohibitivo, nunca solo por el hallazgo ecográfico en un
paciente de baja probabilidad: la especificidad del conjunto es 83 %, y cor
pulmonale crónico, infarto de VD u otra causa de disfunción del VD quedan sin
descartar por la ecografía sola.

Y a la inversa: un VD normal en un paciente que se sigue deteriorando no
cierra la pregunta. Un émbolo puede no generar poscarga suficiente para
deformar la arquitectura cardíaca, sobre todo en el paciente todavía
compensado; un examen normal no excluye la enfermedad.

## Dónde NO confiar

- **Cor pulmonale crónico:** EPOC, hipertensión pulmonar crónica o
  cardiopatía congénita dilatan el VD de forma crónica; una pared libre
  gruesa (>5 mm) y una aurícula derecha mayor que la izquierda orientan a
  cronicidad, no a un evento agudo.
- **El signo de la D distingue presión de volumen, y la fase del ciclo
  importa:** si el tabique se aplana en sístole y diástole, la sobrecarga es
  de presión (típico de TEP aguda). Si solo se aplana en diástole y el
  ventrículo izquierdo recupera su forma circular en sístole, la sobrecarga
  es de volumen —insuficiencia tricuspídea, sobrecarga de fluidos— y el
  cuadro es otro.
- **Signo de McConnell en infarto de VD:** descrito también fuera de la
  tromboembolia pulmonar; no es exclusivo.
- **Ventana subóptima o corte oblicuo del ápex:** puede simular una relación
  VD:VI aumentada que no es real.
- **TAPSE reducido por disfunción del ventrículo izquierdo:** el VD puede
  fallar secundariamente sin que exista sobrecarga de presión aguda.
- **Ausencia de todo lo anterior no descarta tromboembolia pulmonar:** una
  embolia submasiva o de bajo riesgo hemodinámico puede no dejar huella
  ecográfica en el VD.

## Practica esto

Empieza por las proporciones normales. En pacientes sin sospecha, obtén la
apical de cuatro cámaras y confirma que el VD es claramente menor que el VI,
con forma triangular y su banda moderadora cerca del ápex. Después ve a
paraesternal eje corto y observa cómo el VI mantiene su forma circular
durante todo el ciclo cardíaco. Esa circunferencia intacta es el fondo contra
el cual reconoces una D.

En cada vista apical que hagas después, compara de un vistazo el tamaño del
VD contra el VI antes de seguir. Acostúmbrate a nombrar en voz alta si el
tabique se ve curvo hacia el VD (normal —la mayor presión del VI lo empuja
hacia el lado de menor presión) o aplanado/curvo hacia el VI (signo de la D
—la presión del VD ya alcanza o supera a la del VI).

## Discusión abierta

¿Cuánto tarda tu servicio en confirmar una tromboembolia pulmonar con imagen?
¿Has usado el ultrasonido a la cabecera para adelantar la anticoagulación
mientras esperabas?
