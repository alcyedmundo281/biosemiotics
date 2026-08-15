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

El índice vigente contiene **34 entidades**: 14 conceptos, 19 signos y 1 caso.
Quince signos tienen URL pública en Ghost; los otros cuatro están escritos y
validados, esperando publicación.

| signo | sistema | organo | nivel | estado |
|---|---|---|---|---|
| [Líneas B](https://www.biosemiotics.net/lineas-b-ultrasonido-pulmonar/) | respiratorio | pulmon | principiante | ✅ publicado |
| [Perfil A](https://www.biosemiotics.net/perfil-a-leer-el-pulmon-seco-sin-confundirlo-con-neumotorax/) | respiratorio | pulmon | principiante | ✅ publicado |
| [Derrame pleural](https://www.biosemiotics.net/derrame-pleural-ultrasonido/) | respiratorio | pulmon | principiante | ✅ publicado |
| [Riñón crónico](https://www.biosemiotics.net/rinon-cronico-ultrasonido/) | genitourinario | riñon | intermedio | ✅ publicado |
| [Derrame pericárdico](https://www.biosemiotics.net/derrame-pericardico-en-pocus-reconocer-liquido-sin-confundirlo-con-taponamiento/) | cardiovascular | pericardio | principiante | ✅ publicado |
| [Eyeball EF](https://www.biosemiotics.net/funcion-sistolica-del-vi-a-ojo-clasificar-antes-de-cuantificar/) | cardiovascular | corazon | principiante | ✅ publicado |
| [Globo vesical](https://www.biosemiotics.net/globo-vesical-en-pocus-confirmar-retencion-antes-de-sondar/) | genitourinario | vejiga | principiante | ✅ publicado |
| [Colelitiasis](https://www.biosemiotics.net/colelitiasis-calculo-movil-con-sombra-posterior/) | digestivo | vesicula | principiante | ✅ publicado |
| [Hidronefrosis](https://www.biosemiotics.net/hidronefrosis-en-pocus-detectar-dilatacion-no-adivinar-la-piedra/) | genitourinario | riñon | principiante | ✅ publicado |
| [Aneurisma aórtico abdominal](https://www.biosemiotics.net/aneurisma-aortico-abdominal-en-pocus-medir-antes-de-que-el-dolor-engane/) | vascular | aorta-abdominal | principiante | ✅ publicado |
| [Neumotórax](https://www.biosemiotics.net/neumotorax-en-pocus-la-ausencia-de-sliding-no-basta/) | respiratorio | pleura | principiante | ✅ publicado |
| [Trombosis venosa profunda](https://www.biosemiotics.net/tvp-por-compresion-la-vena-que-no-desaparece/) | vascular | vena-profunda | principiante | ✅ publicado |
| [Taponamiento cardíaco](https://www.biosemiotics.net/taponamiento-cardiaco-el-derrame-que-impide-el-llenado/) | cardiovascular | pericardio | intermedio | ✅ publicado |
| [Ventrículo derecho (sobrecarga/TEP)](https://www.biosemiotics.net/sobrecarga-del-ventriculo-derecho-tep/) | cardiovascular | corazon | intermedio | ✅ publicado |
| [Colecistitis aguda](https://www.biosemiotics.net/colecistitis-aguda-cuando-la-piedra-ya-no-es-el-hallazgo/) | digestivo | vesicula | intermedio | ✅ publicado |

---

## 3. OLEADA 1 — los que desintimidan
*Alto impacto clínico, baja dificultad de adquisición. Reconocimiento casi binario. Son la prueba de que "POCUS se puede empezar hoy". Publica estos primero.*

| signo | sistema | organo | nivel | escenario | decisión que cambia | concepto base requerido | estado |
|---|---|---|---|---|---|---|---|
| Derrame pericárdico | cardiovascular | pericardio | principiante | urgencias, uci | ¿hay líquido alrededor del corazón? → vigilar/drenar | ventanas-cardiacas | ✅ publicado |
| Eyeball EF (función VI a ojo) | cardiovascular | corazon | principiante | urgencias, uci | ¿el VI se contrae bien o mal? → fluidos vs inotrópicos | ventanas-cardiacas | ✅ publicado |
| Globo vesical | genitourinario | vejiga | principiante | urgencias, consulta | ¿retención? → sondar (y explica creatinina alta) | conceptos ya en el banco | ✅ publicado |
| Colelitiasis | digestivo | vesicula | principiante | urgencias, consulta | ¿cálculos? → orienta dolor en hipocondrio derecho | conceptos ya en el banco | ✅ publicado |
| Litiasis nefroureteral / hidronefrosis | genitourinario | riñon | principiante | urgencias | ¿obstrucción? → causa reversible de fallo renal/dolor | conceptos ya en el banco | ✅ publicado |
| Aneurisma aórtico abdominal (AAA) | vascular | aorta-abdominal | principiante | urgencias | ¿aorta > 3 cm? → catástrofe potencial, no demorar | conceptos ya en el banco | ✅ publicado |
| Neumotórax (ausencia de sliding) | respiratorio | pleura | principiante | urgencias, uci | ¿pulmón deslizante? → descarta/sugiere neumotórax | sliding-lung-point, modo-m | ✅ publicado |
| Trombosis venosa profunda (compresión) | vascular | vena-profunda | principiante | urgencias | ¿vena compresible? → TVP, ancla el TEP | compresibilidad-venosa | ✅ publicado |

---

## 4. OLEADA 2 — urgencias que cambian conductas
*Más difíciles o más dramáticos. El mensaje pasa de "es fácil" a "esto salva vidas". Requieren más integración.*

| signo | sistema | organo | nivel | escenario | decisión que cambia |
|---|---|---|---|---|---|
| Taponamiento cardíaco | cardiovascular | pericardio | intermedio | urgencias, uci | derrame + colapso cámaras → drenaje urgente ✅ publicado |
| Ventrículo derecho (sobrecarga/TEP) | cardiovascular | corazon | intermedio | urgencias, uci | VD dilatado, septo en D → sospecha TEP ✅ publicado |
| [Colecistitis aguda](https://www.biosemiotics.net/colecistitis-aguda-cuando-la-piedra-ya-no-es-el-hallazgo/) | digestivo | vesicula | intermedio | urgencias | pared, Murphy ecográfico → cirugía/antibiótico ✅ publicado |
| Coledocolitiasis | digestivo | via-biliar | intermedio | urgencias | vía biliar dilatada → obstrucción, CPRE ✍ escrito, falta URL de Ghost |
| Apendicitis | digestivo | apendice | intermedio | urgencias | apéndice no compresible > 6 mm → cirugía ✍ escrito, falta URL de Ghost |
| Embarazo ectópico | genitourinario | utero | intermedio | urgencias | útero vacío + βhCG+ → emergencia |
| Absceso de partes blandas | musculoesqueletico | pared | intermedio | urgencias | colección con refuerzo posterior → drenar vs antibiótico ✍ escrito, falta URL de Ghost |
| Hernia complicada | musculoesqueletico | pared | intermedio | urgencias | contenido, reductibilidad → cirugía ✍ escrito, falta URL de Ghost |

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
- **Cuantificación y sus límites** → concepto transversal: toda fórmula es poblacional

**Completados:** Ventanas cardíacas, Modo M, sliding / lung point y
compresibilidad venosa ya están en el banco. Sustentan los ocho signos de la
Oleada 1 y las rutas avanzadas que reutilizarán esos conceptos.

---

## 8. Orden de trabajo recomendado

1. **Oleada 1 cerrada:** los ocho signos están publicados, con sus conceptos base incorporados.
2. **Ahora — Oleada 2:** publicados taponamiento cardíaco, sobrecarga del ventrículo derecho / TEP y colecistitis aguda. Escritos y esperando URL de Ghost: Coledocolitiasis, Apendicitis, Absceso de partes blandas y Hernia complicada. Queda **Embarazo ectópico**, el último de la oleada.
3. **Antes de los signos que lo necesiten:** escribir y validar Doppler y Cuantificación y sus límites.
4. **Conceptos base: regla dura.** Un signo NO se publica sin su concepto base ya en el banco. El concepto base requerido se escribe y valida ANTES que el signo, no en paralelo ni después.
5. **Después:** completar FAST/eFAST → Oleada 3 → Extensiones.

### La regla que no cambia
Cada cifra, verificada contra PubMed antes de publicar. Cada signo, con su sección de límites ("dónde NO confiar"). El orden por oleada mantiene vivo el mensaje: *empezar es más fácil de lo que te dijeron.*

### Conteo
- Banco actual: **34 entidades** (14 conceptos, 19 signos y 1 caso)
- Signos publicados: **15 de 19** (coledocolitiasis, apendicitis, absceso de partes blandas y hernia complicada escritos, esperando URL de Ghost)
- Oleada 1 completada: **8 de 8 signos**
- Oleada 2: **3 publicados, 4 escritos, 1 pendiente de 8 signos** (la fila «colección/absceso, hernia complicada» se desdobló en dos: son dos significantes y dos decisiones distintas)
- Conceptos base pendientes: **~2**
- Restan **~14 entidades** para llegar a las ~48 proyectadas del atlas maduro

Nota: FAST añade pocas fichas nuevas (Morrison, esplenorrenal, Douglas, hemotórax) porque reutiliza pericardio y neumotórax. El gradiente de FEVI añade 2 (lineales, Simpson) sobre el eyeball ya contado.

A un signo por semana, el núcleo (oleadas 1-2, incluido FAST) está completo en ~4-5 meses. Ritmo sostenible para un clínico en ejercicio.
