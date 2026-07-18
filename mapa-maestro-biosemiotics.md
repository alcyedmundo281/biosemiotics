# Mapa maestro — biosemiotics

Plano completo del atlas: los dos cursos (cardiopulmonar y emergencias) más las extensiones, convertidos en la estructura del banco. Cada signo ya sabe dónde encaja: su `sistema`, `organo`, `nivel` y en qué oleada se publica.

**Cómo se usa:** cuando escribas un signo nuevo, copia su fila de aquí al front-matter. La taxonomía es fija; publicar en orden de oleada mantiene el mensaje de "puedes empezar hoy".

---

## 1. Taxonomía (los valores fijos del esquema)

### `sistema`
`respiratorio` · `cardiovascular` · `digestivo` · `genitourinario` · `vascular` · `musculoesqueletico` · `endocrino` · `nervioso` · `multiorgano`

### `organo` (por sistema)
- **respiratorio:** pulmon, pleura, diafragma
- **cardiovascular:** corazon, pericardio, aorta, cava
- **digestivo:** vesicula, via-biliar, higado, apendice, pancreas, intestino
- **genitourinario:** riñon, ureter, vejiga, utero, ovario, prostata
- **vascular:** vena-profunda, carotida, arteria-periferica, aorta-abdominal
- **musculoesqueletico:** pared, ganglio
- **endocrino:** tiroides
- **nervioso:** nervio-optico
- **multiorgano:** (protocolos que cruzan sistemas: VExUS, FAST)

### `nivel`
- **principiante** — reconocimiento binario, poca dependencia de operador, decide una conducta simple
- **intermedio** — requiere técnica cuidadosa o integración de varios signos
- **avanzado** — Doppler cuantitativo, cálculo, alta dependencia de operador

### `escenario`
`urgencias` · `consulta` · `hospitalizacion` · `uci` · `preoperatorio`

---

## 2. Estado actual (lo ya publicado)

| signo | sistema | organo | nivel | estado |
|---|---|---|---|---|
| Líneas B | respiratorio | pulmon | principiante | ✅ publicado |
| Perfil A | respiratorio | pulmon | principiante | ⚠ en banco, sin publicar |
| Derrame pleural | respiratorio | pulmon | principiante | ✅ publicado |
| Riñón crónico | genitourinario | riñon | intermedio | ✅ publicado |

---

## 3. OLEADA 1 — los que desintimidan
*Alto impacto clínico, baja dificultad de adquisición. Reconocimiento casi binario. Son la prueba de que "POCUS se puede empezar hoy". Publica estos primero.*

| signo | sistema | organo | nivel | escenario | decisión que cambia |
|---|---|---|---|---|---|
| Derrame pericárdico | cardiovascular | pericardio | principiante | urgencias, uci | ¿hay líquido alrededor del corazón? → vigilar/drenar |
| Eyeball EF (función VI a ojo) | cardiovascular | corazon | principiante | urgencias, uci | ¿el VI se contrae bien o mal? → fluidos vs inotrópicos |
| Globo vesical | genitourinario | vejiga | principiante | urgencias, consulta | ¿retención? → sondar (y explica creatinina alta) |
| Colelitiasis | digestivo | vesicula | principiante | urgencias, consulta | ¿cálculos? → orienta dolor en hipocondrio derecho |
| Litiasis nefroureteral / hidronefrosis | genitourinario | riñon | principiante | urgencias | ¿obstrucción? → causa reversible de fallo renal/dolor |
| Aneurisma aórtico abdominal (AAA) | vascular | aorta-abdominal | principiante | urgencias | ¿aorta > 3 cm? → catástrofe potencial, no demorar |
| Neumotórax (ausencia de sliding) | respiratorio | pleura | principiante | urgencias, uci | ¿pulmón deslizante? → descarta/sugiere neumotórax |
| Trombosis venosa profunda (compresión) | vascular | vena-profunda | principiante | urgencias | ¿vena compresible? → TVP, ancla el TEP |

---

## 4. OLEADA 2 — urgencias que cambian conductas
*Más difíciles o más dramáticos. El mensaje pasa de "es fácil" a "esto salva vidas". Requieren más integración.*

| signo | sistema | organo | nivel | escenario | decisión que cambia |
|---|---|---|---|---|---|
| Taponamiento cardíaco | cardiovascular | pericardio | intermedio | urgencias, uci | derrame + colapso cámaras → drenaje urgente |
| Ventrículo derecho (sobrecarga/TEP) | cardiovascular | corazon | intermedio | urgencias, uci | VD dilatado, septo en D → sospecha TEP |
| Colecistitis aguda | digestivo | vesicula | intermedio | urgencias | pared, Murphy ecográfico → cirugía/antibiótico |
| Coledocolitiasis | digestivo | via-biliar | intermedio | urgencias | vía biliar dilatada → obstrucción, CPRE |
| Apendicitis | digestivo | apendice | intermedio | urgencias | apéndice no compresible > 6 mm → cirugía |
| Embarazo ectópico | genitourinario | utero | intermedio | urgencias | útero vacío + βhCG+ → emergencia |
| Colección/absceso, hernia complicada | musculoesqueletico | pared | intermedio | urgencias | contenido, reductibilidad → cirugía |

### FAST / eFAST — protocolo, no signo único
*FAST es un recorrido de ventanas; cada una es un signo con su propia ficha. El nodo "protocolo FAST" las enlaza. Varias ya existen en otras oleadas — el protocolo las teje, no las duplica.*

| ventana | sistema | organo | nivel | qué busca |
|---|---|---|---|---|
| **Protocolo FAST/eFAST** (nodo integrador) | multiorgano | multiorgano | intermedio | secuencia de trauma; enlaza las ventanas de abajo |
| Cuadrante sup. derecho (Morrison) | multiorgano | higado | principiante | líquido en receso hepatorrenal |
| Cuadrante sup. izquierdo (esplenorrenal) | multiorgano | intestino | principiante | líquido periesplénico |
| Pelvis (Douglas / retrovesical) | multiorgano | vejiga | principiante | líquido pélvico |
| Subxifoides pericárdico | cardiovascular | pericardio | principiante | *= signo Derrame pericárdico (Oleada 1)* |
| eFAST — neumotórax | respiratorio | pleura | principiante | *= signo Neumotórax (Oleada 1)* |
| eFAST — hemotórax | respiratorio | pleura | principiante | líquido supradiafragmático en trauma |

**Modelado:** el nodo "Protocolo FAST" usa `signos: [morrison, esplenorrenal, douglas, derrame-pericardico, neumotorax, hemotorax]`. Así el atlas muestra el protocolo como un caso que recorre signos ya existentes. Enseña la *secuencia*, no repite el contenido.

---

## 5. OLEADA 3 — avanzados y cuantitativos
*Doppler, cálculo, integración fina. Para el lector que ya escanea y quiere profundidad. Aquí el atlas se vuelve referencia, no on-ramp.*

| signo | sistema | organo | nivel | escenario | decisión que cambia |
|---|---|---|---|---|---|
| Disfunción diastólica (E/e') | cardiovascular | corazon | avanzado | consulta, uci | presiones de llenado → manejo de fluidos/IC |
| VTI (integral velocidad-tiempo) | cardiovascular | corazon | avanzado | uci | volumen sistólico, respuesta a fluidos |
| Gasto cardíaco | cardiovascular | corazon | avanzado | uci | estado hemodinámico → vasoactivos |
| FEVI por Simpson biplano | cardiovascular | corazon | avanzado | consulta, uci | método de referencia; trazado de bordes en 2 planos |
| FEVI por métodos lineales (Teichholz, FA) | cardiovascular | corazon | intermedio | consulta | estimación cuantitativa rápida en modo M |
| Protocolo VExUS (congestión venosa) | multiorgano | cava | avanzado | uci | congestión sistémica → descongestión guiada |
| Weaning / disfunción diafragmática | respiratorio | diafragma | avanzado | uci | excursión diafragmática → extubar o no |
| Coartación aórtica | cardiovascular | aorta | avanzado | consulta | flujo, gradiente → derivar |

### El gradiente de la función del VI (mismo significado, tres resoluciones)
*Un ejemplo perfecto de semiótica clínica: el mismo referente —función sistólica del VI— leído con precisión creciente. Modelar los tres como signos vinculados, para que el atlas muestre la escalera del principiante al experto.*

| método | nivel | lectura | vínculo |
|---|---|---|---|
| **Eyeball EF** | principiante | "¿se contrae bien o mal?" | puerta de entrada (Oleada 1) |
| **Lineales (Teichholz / FA)** | intermedio | cálculo en modo M, un plano | `se_relaciona: [eyeball-ef]` |
| **Simpson biplano** | avanzado | trazado en 2 planos, referencia | `se_relaciona: [eyeball-ef]`; contrasta la precisión |

El lector entra por el eyeball y el mismo nodo lo lleva, cuando madura, hasta Simpson. **El significante gana resolución; el significado no cambia.** Esa es la marca del proyecto hecha estructura.

---

## 6. EXTENSIONES — otros territorios
*Fuera de los dos cursos base, pero en tu lista. Se integran cuando el núcleo esté maduro. Cada uno abre un órgano/sistema nuevo.*

| signo | sistema | organo | nivel | notas |
|---|---|---|---|---|
| Vaina del nervio óptico (ONSD) | nervioso | nervio-optico | intermedio | ya esbozado; riesgo térmico retiniano; dolor ocular como puerta |
| Pancreatitis | digestivo | pancreas | intermedio | ventana difícil (gas); apoyo, no descarta |
| Tiroides (nódulos, bocio) | endocrino | tiroides | intermedio | superficial, sonda lineal; TIRADS aparte |
| Carótidas (estenosis, GIM) | vascular | carotida | avanzado | Doppler; cribado vascular |
| Arterial periférico | vascular | arteria-periferica | avanzado | Doppler; isquemia/pulsos |
| Rastreo ganglionar | musculoesqueletico | ganglio | intermedio | benigno vs sospechoso; sonda lineal |
| Colecistitis alitiásica / pólipos | digestivo | vesicula | intermedio | variantes del signo vesical |
| Quiste ovárico | genitourinario | ovario | intermedio | dolor pélvico; distinguir de ectópico |

---

## 7. Conceptos base que faltan (el "por qué")
*Sustentan los signos de arriba. Sin ellos, el grafo tiene nodos huérfanos. Escríbelos en paralelo — son cortos.*

- **Doppler** (color, espectral, pulsado) → sustenta E/e', VTI, VExUS, carótidas, vascular
- **Modo M** → sustenta sliding pulmonar, TAPSE, diafragma
- **Signo del sliding / lung point** → sustenta neumotórax
- **Compresibilidad venosa** → sustenta TVP, VExUS
- **Ventanas cardíacas** (paraesternal, apical, subcostal) → sustenta todo lo cardíaco
- **Cuantificación y sus límites** → concepto transversal: toda fórmula es poblacional

---

## 8. Orden de trabajo recomendado

1. **Ahora:** ampliar la taxonomía del esquema (sistema/organo) en la skill y en `esquema.md` con los valores de la sección 1.
2. **Completar** los abstracts y URLs de lo que ya existe (4 signos + conceptos).
3. **Oleada 1**, un signo por semana: cada uno con NotebookLM → refs.py verificado → Ghost → banco.
4. **Conceptos base** intercalados cuando un signo los necesite (Doppler antes de la Oleada 3).
5. **Oleada 2**, luego **Oleada 3**, luego **Extensiones**.

### La regla que no cambia
Cada cifra, verificada contra PubMed antes de publicar. Cada signo, con su sección de límites ("dónde NO confiar"). El orden por oleada mantiene vivo el mensaje: *empezar es más fácil de lo que te dijeron.*

### Conteo
- Publicados: **3** (líneas B, derrame pleural, riñón crónico)
- En banco sin publicar: **1** (perfil A)
- Por escribir: **~38 signos/protocolos + ~6 conceptos base**
- Total proyectado del atlas maduro: **~48 entidades**

Nota: FAST añade pocas fichas nuevas (Morrison, esplenorrenal, Douglas, hemotórax) porque reutiliza pericardio y neumotórax. El gradiente de FEVI añade 2 (lineales, Simpson) sobre el eyeball ya contado.

A un signo por semana, el núcleo (oleadas 1-2, incluido FAST) está completo en ~4-5 meses. Ritmo sostenible para un clínico en ejercicio.
