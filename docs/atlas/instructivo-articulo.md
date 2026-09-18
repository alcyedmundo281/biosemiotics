# Instructivo del artículo

El artículo se escribe en la fuente `.qmd`; Ghost muestra el texto completo.
El abstract pertenece al front-matter. Las secciones desarrollan adquisición,
interpretación, decisión, límites y evidencia con español claro para primer
contacto. La estructura obligatoria siguiente refleja `scripts/validacion.py`.

## Signos: ocho encabezados literales obligatorios

| Encabezado | Contenido |
|---|---|
| `## La pregunta clínica` | Duda concreta frente al paciente |
| `## Por qué el examen físico no basta` | Limitación que justifica el examen |
| `## Cómo se obtiene la ventana` | Sonda, preset, posición y adquisición |
| `## El signo` | Significante y significado; medios contextualizados |
| `## La bifurcación` | Qué decisión cambia y con qué condiciones |
| `## Dónde NO confiar` | Falsos positivos, mala ventana y límites de aplicación |
| `## Practica esto` | Ejercicio concreto apropiado al nivel |
| `## Discusión abierta` | Pregunta para discusión |

Cada encabezado aparece una sola vez y tiene contenido. La bibliografía sale
de `refs` y `refs.bib`; no se duplica manualmente para satisfacer un supuesto
noveno encabezado obligatorio. Si hay una sección `Evidencia`, debe concordar
con las fuentes declaradas; el render usa la bibliografía resuelta.

## Casos: siete encabezados literales obligatorios

| Encabezado | Contenido |
|---|---|
| `## Viñeta clínica` | Franja etaria, motivo y duda, sin datos identificadores |
| `## El problema antes de la sonda` | Qué faltaba para decidir |
| `## La adquisición` | Cómo se obtuvo la ventana |
| `## El signo` | Qué se vio y cómo se interpretó |
| `## La bifurcación` | Decisión y desenlace documentados |
| `## Los límites` | Qué no permite concluir este caso |
| `## Pregunta al parlamento` | Pregunta concreta a los lectores |

La plantilla añade `La evidencia` y `El puente a la práctica` como orientación
editorial. El paquete original proponía también `El escaneo`, `Lo que mostró`
y `La bifurcación y el desenlace`: no sustituyen los títulos obligatorios
actuales. Un caso se centra en una decisión semiótica.

## Conceptos

Conservan estructura libre. El material original sugiere `El fenómeno`,
`Por qué importa para leer la imagen` y `Cómo se ve en pantalla`, además de
evidencia. No hay que suprimir límites relevantes por tratarse de un concepto.

## Medios y evidencia

Presenta el loop o imagen junto a la explicación del signo y un pie que diga
qué ventana es, qué se observa y qué no permite concluir. Usa contraste normal
y patológico cuando esté disponible y sea pertinente. Los videos con proveedor
externo deben tener acceso e incrustación comprobados; no asumas que una URL
es reproducible. Declara todos los medios y su trazabilidad en el YAML.

Cada afirmación que cambia una conducta necesita evidencia que realmente la
respalde. Comprueba PMID, DOI y el contenido de la fuente. Ajusta la cifra a
la evidencia, no al revés. Un build correcto no valida la verdad clínica.

## Publicación en Ghost

El excerpt refleja `abstract`; etiquetas y metadatos deben concordar con la
ficha. El JSON-LD se genera en `build/jsonld/<id>.json` y, cuando el flujo lo
requiera, se incluye en el post como `application/ld+json`.
La URL definitiva se registra solo después de conocerla. Sigue los roles y
PR apilados de `CLAUDE.md` para actualizar imagen, índice y derivados.

La aprobación clínica, el consentimiento para publicar y la desidentificación
siguen siendo obligatorios. Revisa DICOM, banners, rostros, pulseras,
documentos y señales institucionales. Un caso raro puede ser identificable
sin etiquetas: no lo publiques como anónimo por haber recortado la imagen.
Los casos representativos se declaran como tales y no eluden estos controles.

## Núcleo y XML experimental

El paquete distingue conocimiento archivable de conversación comunitaria.
Actualmente `scripts/indice.py:SEC_MAP` exporta solo encabezados reconocidos;
`Practica esto`, `Discusión abierta` y `Evidencia` no se exportan como secciones
del cuerpo XML. Las referencias siguen su tratamiento separado.

Existe una limitación previa: varios títulos actuales de caso (por ejemplo
`El problema antes de la sonda`, `La adquisición` y `Los límites`) no están
en `SEC_MAP`. Pasar el contrato editorial no demuestra que el XML conserve
todo el caso. Esta incorporación documental no cambia el generador: antes
de usar ese XML para intercambio de casos hay que resolver y verificar el
mapeo. No renombres las secciones fuente para eludir el contrato.

El XML no está validado contra una DTD ni el perfil de PMC, Crossref u otro
depósito. Tampoco esta separación garantiza qué incluye Zenodo: la integración
de GitHub archiva el snapshot del repositorio, y los binarios necesitan el
flujo de depósito descrito en el manual.
