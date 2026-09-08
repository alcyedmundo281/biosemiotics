# CLAUDE.md — Manual de operación del atlas biosemiotics

Este archivo le enseña a cualquier sesión de Claude Code cómo trabajar en este repositorio. **Léelo completo al arrancar.** No improvises el flujo: está escrito aquí por una razón.

---

## Qué es este proyecto

Un atlas educativo de POCUS (ecografía en el punto de atención) para el médico de primer contacto, en español. Su tesis es semiótica: cada hallazgo ecográfico es un **signo** que une un **significante** (lo que se ve), un **significado** (la realidad clínica) y una **decisión** (qué cambia en el manejo).

Autor y responsable clínico: Dr. Alcy Torres. Toda decisión clínica final es suya.

## Regla de oro del sistema

**Una fuente, muchas salidas.** El banco de archivos `.qmd` es la ÚNICA fuente de verdad. Todo lo demás (`build/`, el índice, el HTML, el XML experimental de `build/jats/`, el proyecto Quarto de `build/quarto/`) es **derivado** y se regenera. NUNCA edites archivos en `build/` a mano: el siguiente `indice.py` o `qmd.py` los sobrescribe. Si algo está mal en una salida, se arregla en el `.qmd` de origen y se recompila.

## Mapa del repositorio

```
proyecto-biosemiotics/
├── CLAUDE.md                    ← este archivo
├── mapa-maestro-biosemiotics.md ← QUÉ escribir y en qué orden (léelo siempre)
├── conceptos/*.qmd              ← el "por qué" (física, artefactos, técnica)
├── signos/*.qmd                 ← el "qué hago" (significante→significado→decisión)
├── casos/*.qmd                  ← el paciente real
├── scripts/                     ← build.py, qmd.py, epub.py, libro.py, indice.py, refs.py
├── refs.bib                     ← bibliografía (SOLO desde PubMed vía refs.py)
├── assets/                      ← plantillas para nuevo.py
└── build/                       ← GENERADO, no versionar salvo index.json
```

La documentación de referencia (esquema completo, instructivo del artículo) vive en la skill `biosemiotics-atlas`. Consúltala si necesitas el detalle de un campo.

## Compilar el libro en PDF (`build/libro.pdf`)

```bash
python scripts/libro.py --salida build/libro.pdf --solo-publicados
```

**El LaTeX ya no se escribe a mano.** `build_latex()` y sus auxiliares
—`markdown_a_latex()`, `escape_latex()`, `figura_latex()`— se jubilaron: eran
~350 líneas que reimplementaban la conversión y el escape en paralelo al
ensamblado del EPUB, con el riesgo permanente de que las dos ediciones
divergieran. Ahora el PDF sale del **mismo proyecto Quarto** que el EPUB, y
`libro.py` solo renderiza y valida.

El compilador sigue siendo **LuaLaTeX, no pdflatex**. El banco escribe umbrales
y decisiones con símbolos Unicode estructurales (`≥`, `→`, `±`) porque así se
leen en la clínica. `_quarto.yml` fija `pdf-engine: lualatex` y
`mainfont: FreeSerif`, la única fuente disponible que cubre esos glifos sin
fallback silencioso. Con pdflatex verías `Missing character` en cuanto el texto
traiga `≥`/`→`/`±`: no es un error del banco, es el compilador equivocado.

**La fuente LaTeX es un entregable, no un intermedio.** `keep-tex` la deja en
**`build/quarto/libro.tex`** —no en `build/libro.tex`, que ya no existe— junto
a las imágenes que `qmd.py` copió al proyecto. Ese directorio compila tal cual,
sin depender del checkout:

```bash
cd build/quarto
lualatex -halt-on-error -interaction=nonstopmode libro.tex
```

Eso es lo que empaqueta `paquete_latex.py`: el proyecto entero menos `_salida/`.
El ZIP anterior mezclaba `build/libro.tex` con el árbol `assets/` del
repositorio y traía rutas `../assets/...` que solo resolvían desde `build/`.

**Dependencias de sistema:** `texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-lang-spanish`, `texlive-luatex` y
`fonts-freefont-ttf`. **`biber` ya no hace falta**: el `.tex` de Quarto no usa
biblatex porque la bibliografía se emite ya resuelta por
`bibliografia.referencia_ghost()`.

## Compilar el EPUB (`build/atlas.epub`)

La primera edición citable incluye solo fichas que ya pasaron por la revisión
editorial en Ghost:

```bash
python scripts/build.py
python scripts/epub.py --salida build/atlas.epub --solo-publicados
```

**El manuscrito ya no se ensambla a mano.** `scripts/qmd.py` proyecta el banco a
un proyecto **Quarto book** en `build/quarto/` (`_quarto.yml` + un capítulo por
capítulo temático u órgano) y `epub.py` solo elige motor, renderiza y valida.
De ese mismo árbol salen EPUB, PDF y HTML con `quarto render build/quarto --to
<formato>`; ya no hay tres renderizadores del mismo contenido.

`epub.py` prefiere `quarto` y cae a `pandoc` sobre `build/quarto/libro-plano.md`
—el mismo libro aplanado, derivado de las mismas funciones— cuando Quarto no
está instalado. Fuerza uno u otro con `--motor quarto|pandoc`. Si las dos
salidas difieren en contenido, es un fallo de `qmd.py`, no una variante
editorial aceptable.

**Destinos de generación:** `qmd.py --destino` y las opciones `--proyecto`
de EPUB/PDF solo aceptan subdirectorios del `build/` real del repositorio;
no aceptan `build/` entero, enlaces ni junctions. Un directorio no vacío debe
ser un proyecto reconocido por `.biosemiotics-quarto`. Los proyectos anteriores
en `build/quarto/` se reconocen por sus archivos generados característicos.
El ensamblado se prepara en un temporal antes de reemplazar el proyecto previo.
Si falla también la restauración, el error indica la copia conservada para
recuperarla; no la borres. Esto no protege de ejecuciones concurrentes ni
convierte el render posterior de Quarto en una transacción.

La jerarquía es **parte (`#`) → capítulo temático u órgano (`##`) → ficha
(`###`) → cuerpo (`####`)**. El ensamblado anterior ponía la ficha en `###`
dejando el cuerpo en `##`, así que "La pregunta clínica" quedaba por encima del
título de su propia ficha y `--split-level=2` partía el EPUB dentro de cada
signo. No lo reintroduzcas.

**No uses la clave `part:` de Quarto.** Su escritor de EPUB no emite páginas
divisorias de parte: "Fundamentos" y las ocho partes de sistema desaparecían
del contenedor y del índice, y solo sobrevivían en la barra lateral del HTML.
Por eso `_quarto.yml` lleva una lista plana de capítulos y la parte se convierte
en el capítulo del libro. Tampoco declares `identifier` ni `rights` bajo
`book:`: no son propiedades válidas de ese esquema, y al nivel superior Quarto
las pasa a pandoc *además* del `epub-metadata.xml`, dejando dos
`dc:identifier` en el OPF.

Las citas **no** pasan a citeproc: el banco cita poco en línea y su evidencia
vive en `refs`, así que se sigue usando `bibliografia.resolver_citas()` +
`bibliografia.referencia_ghost()`, que numeran por ficha y emiten el estilo de la casa
con DOI y PMID. Cada ficha conserva su sección «Evidencia» y el libro cierra
con la bibliografía en orden de aparición.

El piso soportado del repositorio es Python 3.9. El generador requiere Python
3.9 o posterior, PyYAML y Quarto o Pandoc. El job de integridad debe probar
tanto 3.9 como la versión moderna fijada en CI; el job de citas no se duplica
para evitar repetir llamadas a PubMed. El generador lee el banco de
forma dinámica y hereda de `configuracion.py` el orden de capítulos y sistemas; no usa
listas manuales. El archivo resultante vive en `build/` y no se versiona. El
workflow `.github/workflows/epub.yml` se ejecuta automáticamente en cada cambio
relevante fusionado a `main`: instala Quarto, valida con EPUBCheck, compila el PDF
con LuaLaTeX desde el mismo proyecto y publica EPUB, PDF, TEX y ZIP LaTeX como
artifacts durante 90 días. En un release, además los adjunta al release. `workflow_dispatch` queda
solo como recuperación o para generar una edición de prueba.

**El EPUB es el puente con Ghost, no una copia muerta.** Cada ficha publicada
abre con `*Edición en línea:* <url>`, de modo que el lector salta del libro al
artículo vivo —donde están los loops y las correcciones posteriores—. Las
figuras salen como `<figure>` con `<figcaption>`, y el pie conserva fuente y
licencia **como enlaces**. Esto obliga a usar el lector `markdown` de pandoc:
`gfm` acepta `implicit_figures` pero la ignora, y aplana el pie a un `alt=` de
texto plano, con lo que los enlaces de crédito y licencia desaparecen sin que
falle nada.

El CSS del EPUB **no usa unidades `vh`**: los lectores basados en Adobe Digital
Editions las resuelven como 0 y la imagen queda embebida pero invisible.

El OPF declara el DOI dereferenciable (`https://doi.org/…`, con
`identifier-type` ONIX 06), la licencia con su URL en `dc:rights`, descripción,
fuente y los términos MeSH del banco como `dc:subject`. Título, autor, fecha,
idioma y editorial los aporta pandoc por `--metadata`; **no los dupliques** en
`epub-metadata.xml` o el OPF sale con dos `dc:title` y dos `dc:identifier`.
`validar_epub()` verifica todo esto —incluidos el recuento de `figcaption`, los
enlaces a Ghost y la portada declarada— y aborta si algo se perdió.

Cada figura debe declarar en `medios`: descripción, crédito, fuente y URL,
licencia y URL, y `archivo_local`. La ausencia de cualquiera de esos datos o
del archivo local aborta la compilación: no se omiten imágenes ni se infiere su
atribución. Para una edición futura con todo el banco se omite
`--solo-publicados`, únicamente después de la revisión editorial pendiente.

Metadatos actuales: DOI `10.5281/zenodo.21435362`; ISBN EPUB pendiente. La
portada tipográfica es original, CC BY 4.0, sin logos ni identidad visual del
HECAM/IESS. El EPUB incluye el aviso de uso exclusivamente educativo y una
página final de créditos de imágenes. Zenodo archiva el snapshot del
repositorio, no el asset del release; incorporar el binario al registro DOI
requiere una carga separada.

**Cicatriz de licencia (23/08/2026).** El atlas nació CC BY-NC 4.0 y pasó a
**CC BY 4.0** el 15/08/2026 por decisión explícita de Alcy (#41: "El atlas
pasa a CC BY 4.0"), que tocó los seis lugares donde vivía la licencia —fichas,
`indice.py`, `.zenodo.json`, README y el texto legal de `LICENSE`—. El
depósito de Zenodo de v0.1.0 (19/07/2026) es **anterior** a esa decisión y
quedó correctamente archivado con la licencia de su momento, CC BY-NC 4.0; lo
que pasó es que ningún release posterior volvió a depositar hasta ahora, así
que el DOI de concepto siguió resolviendo a esa versión desactualizada durante
más de una semana. v0.2.0 (23/08/2026) cierra esa brecha: hereda
`.zenodo.json` con CC BY 4.0 y es lo que resuelve hoy el DOI de concepto.
Zenodo no permite editar los metadatos de una versión ya publicada, así que
v0.1.0 conserva la licencia de su momento para siempre —verificable en
`https://api.datacite.org/dois/10.5281/zenodo.21435363`—, y eso es correcto,
no un error a corregir. **Lección:** un cambio de licencia en el repositorio
no se propaga solo al DOI ya acuñado; exige un release nuevo el mismo día,
o el registro citable queda diciendo algo que el repositorio ya no dice.

## Lo primero al arrancar una sesión

### Raíz y rutas de los comandos

Los scripts usan por defecto la raíz real del repositorio, obtenida desde su
propio archivo; el directorio actual no cambia el banco ni la carpeta `build/`.
Para otro banco usa `--raiz <ruta>`. Una raíz explícita relativa se resuelve
desde el directorio actual; `--destino`, `--proyecto`, `--salida` y `--db`
relativos se resuelven desde esa raíz. Las rutas absolutas se conservan.
`indice.py <raiz>` y `atlas.py <raiz>` siguen admitiendo la forma posicional
antigua, pero no se puede combinar con `--raiz`. La forma canónica es la bandera.

`consultas.py` y `senuelo.py` leen una única base, `build/atlas.db` bajo la raíz,
y aceptan `--db` para una ruta distinta. Si falta, fallan con la ruta exacta y
el comando de compilación. `nuevo.py` escribe siempre en la raíz seleccionada.
Este contrato no cambia la protección de `qmd.py`: el proyecto Quarto todavía
debe estar bajo el `build/` real del banco y no se amplía ningún permiso de borrado.

Instala la dependencia Python exacta y ejecuta el preflight de solo lectura:

```bash
python -m pip install -r requirements.txt
python scripts/preflight.py
```

Ese comando comprueba Python 3.9+, PyYAML, la estructura, el contrato editorial
y la coherencia de publicación e índice. Antes de generar EPUB/PDF/LaTeX usa
`python scripts/preflight.py --publicacion`; exige además Quarto, LuaLaTeX,
Java, `rsvg-convert` y EPUBCheck. Las versiones de referencia viven en CI.

1. Corre `git status` y reporta el estado. Si hay cambios sin commitear, avísalo antes de empezar.
2. Lee `mapa-maestro-biosemiotics.md` y di **qué signo toca según la oleada** (no saltes de oleada sin que Alcy lo pida).
3. Corre `python scripts/build.py` y reporta las alertas actuales (qué falta: abstracts, refs, urls).

## Flujo para agregar un signo

1. **Ubícalo en el mapa maestro.** Copia su fila: `sistema`, `organo`, `nivel`, oleada. No inventes estos valores — están definidos en la taxonomía del mapa.
2. **Crea el archivo** con `python scripts/nuevo.py signo <id> "<título>"` o partiendo de la plantilla.
3. **Contenido:** sigue la estructura estándar del instructivo (encabezados `##` LITERALES, que el XML de intercambio mapea automáticamente). Registro: permiso para el principiante, frases cortas, español claro.
4. **Abstract obligatorio:** 40-80 palabras, patrón qué se ve → qué significa → qué decide → dónde falla.
5. **`falsos_positivos` obligatorio:** un signo sin límites enseña a reconocer sin enseñar a dudar. Distingue *falso positivo* (algo que imita el signo sin serlo) de *variante* (el signo real con otra textura) — van en campos distintos.
6. **Referencias:** ver la regla dura abajo.
7. **`url` vacía por ahora.** La plantilla ya trae el campo `url: ""`. Déjalo vacío hasta que el artículo exista en Ghost — el atlas lo mostrará como "(sin publicar)", que es la verdad. **No inventes ni adivines el slug:** el de líneas B resultó ser `lineas-b-ultrasonido-pulmonar`, no `lineas-b`. La URL la da Alcy después de publicar.
8. **Valida:** `python scripts/build.py`. No continúes con errores.

## Reglas duras (no se rompen nunca)

### Contrato editorial antes de generar

`build.py`, `indice.py`, `atlas.py` y `qmd.generar()` bloquean la generación
antes de escribir si alguna ficha seleccionada incumple el contrato. Los errores
identifican archivo, entidad y campo o encabezado. EPUB/PDF heredan este control
mediante `qmd.generar()`; `--solo-publicados` valida las fichas seleccionadas.

Todos los tipos requieren título, cuerpo, nivel válido, abstract de 40–80 palabras
y una lista no vacía de claves existentes en `refs.bib`. Los conceptos requieren
dominio; conservan su estructura libre. Los signos requieren sistema válido,
órgano, ventana, sondas, significante, significado, decisión y falsos positivos,
además de las ocho secciones literales del instructivo. Los casos requieren
órgano, decisión semiótica, signos y sus siete secciones. Las secciones obligatorias
deben aparecer una sola vez y contener texto; los campos obligatorios no admiten
`TODO`. Las listas deben contener textos no vacíos.

Las fichas con `estado: borrador` pueden estar incompletas y quedan fuera de
Ghost, índice, atlas HTML y Quarto. `build.py` las conserva en SQLite y el grafo
de trabajo con alertas, también con `--solo db|grafo`. No distribuyas la base o
el grafo de trabajo como una edición revisada. Toda ficha seleccionada para un
derivado público debe cumplir el contrato editorial.

Este control comprueba estructura, no calidad clínica, veracidad de citas ni
autorización para publicar; una ficha estructuralmente válida aún necesita
revisión clínica y editorial.

### Estado de publicación y trazabilidad

`estado` es la autoridad común; la URL debe concordar con él:

| Estado | URL | Salidas públicas |
|---|---|---|
| `borrador` | Vacía | Excluido; solo trabajo local |
| `revisado` | Vacía | Ghost, índice y edición completa |
| `publicado` | URL pública real | Lo anterior y edición `--solo-publicados` |

Solo se pasa a `revisado` después de la aprobación editorial. Para un caso,
`consentimiento: obtenido` es obligatorio tanto en `revisado` como en `publicado`;
un estado público sin consentimiento hace fallar el comando antes de escribir.
Tener consentimiento no convierte por sí solo un borrador en revisado. Esto no
sustituye comprobar de-identificación y autorización real para publicar.

Registra `fecha_revision` (YYYY-MM-DD) cuando se aprueba la ficha y `ghost_id`
(ID real del post, 24 caracteres hexadecimales) cuando se crea en Ghost.
La migración histórica deja ambos en `null` cuando no constan en la fuente;
no usa la fecha del commit ni deduce un ID del slug. Estos campos se conservan
en SQLite e índice para completarlos con evidencia durante el flujo editorial.
Una fecha o ID sintácticamente válido no demuestra por sí solo una revisión.
El índice añade `ghost_sha256`, calculado sobre el mismo cuerpo canónico que
`build.py` deja en `build/ghost/`. `verificar_publicacion.py` vuelve a calcularlo
y bloquea una deriva entre fuente, bibliografía y registro. Para comparar ese
cuerpo con el editor de Ghost usa `auditar_pegado_ghost.py`.

Compatibilidad: si falta `estado`, una URL implica `publicado`; sin URL se
interpreta `borrador`. El booleano antiguo `publicado` solo se acepta si coincide
con estado y URL, y debe retirarse al migrar. SQLite conserva esa columna como
valor derivado para consultas existentes. Nunca hay dos autoridades de estado.

Para retirar una ficha, cambia a `borrador`, vacía la URL y regenera: Ghost-ready,
índice, atlas y libro la excluyen; el índice retira sus JSON-LD/XML anteriores.
Esto no retira automáticamente un artículo ya publicado en Ghost ni una edición
archivada. La operación de Ghost requiere su propio flujo editorial.

### Alcance del XML de `build/jats/`

Es un intercambio experimental que conserva metadatos, secciones clínicas,
medios y claves bibliográficas con vocabulario JATS. Las fichas se marcan como
material educativo, no como artículos de investigación. El XML no declara una
DTD, no expande las referencias y no se valida contra las reglas de PMC,
Crossref ni otro repositorio. Nunca lo llames «listo para depósito»: adapta y
valida cada archivo contra el perfil concreto del destino antes de enviarlo.

### Reglas clínicas y de publicación

- **CITAS: solo desde PubMed, verificadas.** Usa `scripts/refs.py`. NUNCA escribas una referencia de memoria ni aceptes una que produjo un LLM sin verificar el PMID. Cualquier cifra clínica (umbral, tasa, fórmula) debe tener una fuente que la diga *exactamente*. Si un LLM "recuerda" una cita, trátala como falsa hasta probar lo contrario en PubMed. Este proyecto ya fue salvado de tres referencias inventadas — no repitas el episodio.
- **Verifica que la fuente diga la cifra.** No basta con que el paper trate el tema. Abre el abstract; si dice 1.2%, tu texto dice 1.2%, no "1-4%". Ajusta el texto a la fuente, nunca al revés.
- **Un DOI que Crossref no resuelve no se publica.** `verificar_citas.py` distingue un 404 (Crossref no conoce ese DOI: verificación fallida, sale con código 1) de un error de red transitorio (timeout, 429, 5xx: reintenta). Si la revista es real y simplemente no deposita en Crossref, decláralo en `refs-sin-crossref.txt` con su razón por escrito; esa exención renuncia a la segunda autoridad, así que confirma el PMID a mano antes de usarla. Lo que no se hace es dejar pasar un 404 en silencio.
- **Verificación incompleta bloquea la integración.** `verificar_citas.py` es
  siempre estricto; `--estricto` se conserva como alias compatible. Código 0
  significa verificación completa o exención declarada de Crossref con PubMed
  correcto; 1 indica entrada inválida o discrepancia; 2, servicio no disponible
  o respuesta inválida. Nunca se acepta 2 como éxito ni se añade una exención
  para resolver un timeout. Hay hasta tres intentos por consulta, con esperas
  de 1 y 2 segundos. Agotados los intentos de Crossref se detiene el banco y se
  informa qué quedó sin consultar; volver a ejecutar cuando se recupere el servicio.
  El job obligatorio de integridad exige también citas correctas en PR, ejecución
  manual y semanal. En push a `main` no repite la red; exige la integridad local.
  El job de citas tiene un límite total de diez minutos.
- **Exenciones acotadas y revisadas.** Requieren una razón no vacía y una clave
  existente o prefijo de registrador DOI (`10.NNNN/`). Solo pueden justificar un
  404 de Crossref, nunca un 400/422, un fallo de red ni un PMID/DOI inconsistente.
  La identidad DOI se compara conservando puntuación; las variantes de título
  son informativas únicamente cuando el DOI coincide en ambas autoridades.
- **Sección de límites obligatoria** ("Dónde NO confiar"). Sin ella, el signo no se publica. Es el firewall clínico.
- **Consentimiento antes de publicar un caso.** El consentimiento clínico para escanear NO es consentimiento para publicar: son dos "sí" distintos. Sin `consentimiento: obtenido`, el caso no se publica. Verifica de-identificación: sin DICOM metadata, sin rostro, sin identificadores, sin señalética institucional.
- **Nada que implique aval del HECAM/IESS.** La plataforma es independiente.
- **No edites `build/` a mano.** Regenéralo.
- **Casos raros → composite.** Un diagnóstico infrecuente en comunidad pequeña re-identifica. Usa caso representativo y decláralo.

## Ciclo de publicación en Ghost

Una misma sesión conserva los dos roles del ciclo, pero nunca los mezcla en un
mismo paso ni en un mismo commit:

- **Publicador:** opera Ghost y registra imagen, licencia, URL definitiva y
  salidas editoriales.
- **Proveedor:** valida la fuente, regenera índice, mapa y metadatos derivados.

La separación es operativa, no personal: cada rol usa su propia rama y su PR
apilado. El cambio de rol ocurre solo después de crear y congelar el PR padre
del publicador. Se trabaja de forma secuencial en el único worktree principal;
no se crea un segundo worktree para simular otra sesión.

### Límite de responsabilidad — obligatorio

Esta sección prevalece sobre las instrucciones generales de creación,
compilación y Git cuando la tarea solicitada sea publicar un artículo.

El publicador puede usar la sesión autorizada de Ghost y, sobre una ficha `.qmd`
**ya creada, revisada y validada durante la fase proveedora**, modificar `url`,
`estado` y `ghost_id` para registrar la publicación real, además de `medios`;
puede añadir el archivo licenciado a `assets/img/`, ejecutar
`build.py`, verificar el libro con `libro.py` y entregar esos cambios en
una rama/PR de publicación.

No puede crear fichas, modificar el cuerpo editorial, `refs`, PMID, DOI o
Crossref, ni ejecutar `indice.py` o modificar `build/index.json`. Tampoco
actualiza el mapa maestro ni purga la caché: esas acciones pertenecen al flujo
separado del **proveedor del índice**.

Si falta la ficha o el cuerpo canónico, o si fallan sus referencias, la fase
publicadora se detiene. La misma sesión vuelve explícitamente a una rama de
proveedor para crear o reparar ese contenido, lo integra y solo después inicia
de nuevo la publicación. `build.py` se permite en la fase publicadora únicamente
después de añadir `medios` o la URL para validar la imagen y su salida
LuaLaTeX; `indice.py` sigue prohibido hasta el cambio de rol.

### 0. Preflight — evitar colisiones

Antes de abrir Ghost:

```bash
python scripts/auditar_pegado_ghost.py \
  --canon build/ghost/<carpeta>/<archivo>.qmd
```

- Busca el título en Ghost entre borradores y publicados. Si ya existe,
  **detente** y abre el artículo existente; nunca crees un segundo post.
- Confirma que el artefacto canónico existe y que su huella es válida. Esta
  auditoría es de lectura; no genera ni reescribe archivos.
- Confirma que la ficha fuente ya existe y no tiene cambios editoriales
  pendientes. Crea una rama de publicación; en ella solo podrán cambiar
  `url`, `estado`, `ghost_id`, `medios`, `assets/img/` y las salidas LuaLaTeX correspondientes.

### 1. Preparar y revisar Ghost

1. Usa exclusivamente `build/ghost/<carpeta>/<archivo>.qmd` como cuerpo. No lo
   regeneres. Antes de tocar Ghost, guarda su huella esperada:

   ```bash
   python scripts/auditar_pegado_ghost.py --canon build/ghost/<carpeta>/<archivo>.qmd
   ```

   **Pegado idempotente (obligatorio).** El cuerpo de Ghost usa Lexical y
   `fill()` sobre un editor no vacío puede **anexar** en lugar de reemplazar.
   Nunca repitas `fill`, `type` o pegar sobre un cuerpo que ya contiene texto.
   Si hay que restaurarlo: enfoca el cuerpo, `Ctrl/Cmd+A`, `Backspace`, confirma
   longitud cero, pega una sola vez y vuelve a leer el texto visible. Si el
   cuerpo ya coincide con el canónico, no lo toques.
2. Selecciona una imagen de licencia libre, guarda una copia auditable en
   `assets/img/` y declárala en `medios` con `destacada: true`, descripción,
   crédito, fuente y URL, licencia y URL de licencia, y `archivo_local`. Esta
   es responsabilidad exclusiva del publicador porque debe ser exactamente la
   misma imagen subida a Ghost. Ejecuta `build.py` y confirma que aparece en
   `build/quarto/libro.tex`; compílalo con `libro.py` cuando el entorno lo permita.
3. En Ghost configura: título, cuerpo, imagen, pie y texto alternativo, tags,
   excerpt, autor y acceso. Meta title/description y tarjetas sociales pueden
   quedar vacíos solo cuando se quiere heredar título, excerpt e imagen, como
   en los artículos anteriores.
   El pie también se reemplaza de forma idempotente: selecciona todo su valor,
   bórralo, confirma que quedó vacío e insértalo **una vez**. No encadenes
   `fill()` y `type()`. Si el control colapsado de Ghost mide 0 px, ábrelo desde
   la interfaz antes de escribir; nunca hagas clic por coordenadas porque puede
   insertar el crédito dentro del primer encabezado del cuerpo.
4. Revisa las vistas previas web y email: título, excerpt, imagen, atribución,
   evidencia y enlace al Reto.
   La revisión debe confirmar además que el contador de palabras no aumentó
   aproximadamente al doble y que cada encabezado canónico aparece una vez.
   Ante cualquier edición posterior, repite esta comprobación antes de abrir
   el diálogo de publicación. Para auditar una captura textual del editor:

   ```bash
   python scripts/auditar_pegado_ghost.py \
     --canon build/ghost/<carpeta>/<archivo>.qmd \
     --captura <texto-visible-del-editor.txt> \
     --pie "<pie observado>" --pie-esperado "<atribución canónica>"
   ```
5. Justo antes del último botón, confirma explícitamente si se publicará solo
   en web o también se enviará por email, con el número exacto de suscriptores.
6. Después de publicar, exige evidencia de Ghost (`Published` o
   `Published and sent`) y copia la URL pública definitiva. Nunca uses la URL
   del editor (`/ghost/#/...`) ni una vista previa (`/p/...`).

### 2. Registrar los artefactos y cerrar la fase publicadora

1. Registra `estado: publicado`, el `ghost_id` real y la URL pública definitiva
   en `url` de la ficha existente. No
   cambies ningún otro campo salvo `medios`.
2. Ejecuta `build.py` y `libro.py`, y valida que `build/quarto/libro.tex` use exactamente el
   `archivo_local` subido a Ghost y compila LuaLaTeX si está disponible. La
   misma imagen debe poder entrar en el EPUB. **No ejecutes `indice.py` ni
   agregues `build/index.json`: esa regeneración sigue en el PR hijo.**
3. Abre un **PR borrador de publicación** limitado a la ficha existente,
   `assets/img/` y las salidas LuaLaTeX que correspondan. Es normal que el
   check de deriva del índice señale que aún falta la regeneración; no la
   resuelvas desde el rol publicador.
4. Registra en el PR el `id`, la URL definitiva y el nombre de la rama. Cambia
   explícitamente al rol proveedor y crea desde esa rama el PR hijo de
   regeneración. El traspaso no termina con una nota: debe existir ese PR hijo.
5. Devuelve un informe con: `id`, título, URL pública, id de Ghost, estado,
   fecha/hora, audiencia y destinatarios, tags, excerpt, autor, acceso, imagen,
   alt, crédito, fuente, licencia, archivos cambiados y PR.

Esta división evita mezclar autoridades: la fase proveedora crea contenido y
verifica PMID/Crossref; la fase publicadora nunca toca esos campos. El rol
publicador aporta lo que no existe antes de Ghost —URL e imagen finales— y el
rol proveedor lo propaga después a los derivados.

### 3. Traspaso atómico del índice — obligatorio

Para que el buscador nunca quede mostrando «(sin publicar)» después de que el
artículo ya está vivo, los dos PR se apilan:

1. El PR padre del publicador contiene URL, `medios`, imagen y LuaLaTeX, pero
   no `build/index.json`; permanece en borrador.
2. La misma sesión, ahora declarada en rol proveedor, crea una rama desde la
   rama del publicador, ejecuta
   `indice.py`, actualiza índice, mapa y metadatos globales, y abre un **PR hijo
   de regeneración cuya base es la rama del publicador**, no `main`.
   Antes de regenerar, compara la rama padre con `origin/main`. Si el padre se
   quedó atrás, fusiona `origin/main` en la rama hija con un **merge real, no
   squash**; verifica que sobrevivan tanto la URL/imagen del padre como los
   datos vigentes del banco y solo entonces ejecuta `indice.py`. Antes de
   commitear el hijo debe pasar `python scripts/verificar_publicacion.py` para
   la entidad publicada.
   La regeneración se hace después de congelar **todos** los campos del padre:
   tanto `url` como `medios` alimentan `build/index.json`. Si el publicador
   corrige una atribución, licencia o `fuente_url` después de crear o fusionar
   el hijo, ese hijo queda obsoleto y debe regenerarse otra vez antes de cerrar
   el padre.
3. Cuando la CI del PR hijo pasa, el rol proveedor lo fusiona en la rama del
   publicador. El PR padre incorpora así el índice regenerado sin mezclar los
   commits ni los límites de cada fase.
4. Se vuelve a ejecutar la CI del PR padre. Solo entonces se marca listo y se
   fusiona a `main`.

5. El flujo de publicación no está completo hasta regenerar y verificar las
   **ocho salidas** posteriores a Ghost:

   ```bash
   python scripts/build.py
   python scripts/indice.py
   python scripts/epub.py --salida build/atlas.epub --solo-publicados
   python scripts/libro.py --salida build/libro.pdf --solo-publicados
   python scripts/paquete_latex.py --salida build/biosemiotics-latex.zip
   python scripts/verificar_publicacion.py --id <id> --url <url> \
     --verificar-derivados --epub build/atlas.epub
   ```

   La verificación de derivados va **al final**: comprueba
   `build/quarto/libro.tex`, que solo existe una vez renderizado el PDF.

   Las salidas son `index.json`, `atlas-inject.html`, `jsonld/`, el XML
   experimental de `jats/`,
   el proyecto Quarto `build/quarto/` (con `libro.tex` dentro), `libro.pdf`,
   `atlas.epub` y el paquete `biosemiotics-latex.zip`. Solo
   `build/index.json` se versiona; las otras se regeneran. La verificación
   compara la URL en los cuatro derivados web/metadatos y exige que cada
   imagen publicada sea la declarada en `archivo_local`, tanto en LaTeX como
   dentro del contenedor EPUB. El ZIP debe conservar `libro.tex`,
   `refs.bib` y las imágenes del proyecto para recompilar sin depender del
   checkout original. El workflow `epub.yml` reproduce este contrato en cada PR
   que toca contenido, imágenes o generadores y vuelve a generarlo
   automáticamente al fusionarse en `main`; no requiere una ejecución manual.

Antes de fusionar el padre, su CI debe mostrar en verde **todas** las variantes
del job de integridad (Python 3.9 y 3.13) y el job de citas. El piso 3.9 no es
solo documentación: evita fusionar sintaxis que funcione en CI moderna pero no
en el runtime local compartido.

Esta secuencia mantiene un único dueño de `build/index.json` en cada fase,
evita conflictos de responsabilidad y reduce a **cero** la ventana visible de
desincronización en `main`. La misma sesión debe completar ambos PR; no puede
declarar terminado el flujo únicamente porque Ghost ya publicó.

## Fase proveedora — separada de la fase publicadora

Lo que sigue documenta el rol proveedor del índice. La misma sesión solo queda
autorizada a ejercerlo después de congelar el PR padre y crear una rama hija;
no autoriza al rol publicador activo a ejecutar `indice.py` ni a tocar
`build/index.json`. En la fase proveedora, `build.py` NO regenera
`index.json` — eso lo hace `indice.py`. Si el proveedor modifica un `.qmd`, debe
correr ambos scripts antes de commitear para no servir entradas obsoletas.
Cuando recibe un PR de publicación, el proveedor crea el PR hijo de
regeneración descrito arriba y lo fusiona sobre la rama del publicador antes de
que el PR padre llegue a `main`.

**Verifica antes de commitear.** Después de `indice.py`, confirma que la ficha quedó como esperas:
```bash
python -c "import json; d=json.load(open('build/index.json',encoding='utf-8'))['fichas']; print([f['url'] for f in d if f['id']=='<id>'])"
```
El contador `⚠ N sin url` es solo informativo: puede quedarse igual si otra
rama añade simultáneamente una ficha sin publicar. La autoridad es
`verificar_publicacion.py`, que compara la entidad concreta con el índice.

**Distinción crítica de URLs.** Hay dos clases y NO son lo mismo:

- **URLs de artículos** (campo `url` de cada `.qmd`, y las del JSON-LD) → `www.biosemiotics.net`.
- **URL del índice** que consume el buscador → **siempre desde GitHub, JAMÁS desde `biosemiotics.net`.** El `index.json` vive en el repositorio, no en el sitio. Apuntar el buscador al dominio lo rompe.

**El índice se pide con dos fuentes, primario y respaldo** (`var IDX` e `IDX2` en atlas-inject.html):

| | URL | Caché |
|---|---|---|
| **Primario** | `raw.githubusercontent.com/alcyedmundo281/biosemiotics/main/build/index.json` | 5 min |
| **Respaldo** | `cdn.jsdelivr.net/gh/alcyedmundo281/biosemiotics@main/build/index.json` | 12 h |

Las dos sirven **el mismo archivo del mismo repositorio**. El buscador pide la primaria con `cache: 'no-cache'` y solo cae a la segunda si falla (rate-limit de GitHub, corte).

**Por qué este diseño, y no solo jsDelivr:** jsDelivr cachea las rutas de RAMA (`@main`) durante 12 horas (`s-maxage=43200`). Purgar no siempre basta, y está comprobado que **ni `@latest` ni un `?v=<timestamp>` la esquivan** —jsDelivr ignora los query strings, y `@latest` resuelve al último *tag*, que congelaría el atlas en el release en vez de seguir a `main`. El resultado era publicar un signo y que el atlas siguiera diciendo "(sin publicar)" medio día. Por eso raw va primero: se actualiza en 5 minutos.

Las dos URLs (primaria raw, respaldo jsDelivr) son **constantes fijas en `indice.py`** (`URL_PRIMARIA` / `URL_RESPALDO`); NO se pasan por argumento. El comando es `python scripts/indice.py .` a secas —si le pasas una URL, falla con `unrecognized arguments` en vez de ignorarla en silencio. `indice.py` imprime las dos al terminar; verifícalas ahí. Si algún día hay que reconfigurarlas, será una bandera explícita, no un positional.

**Cuándo hay que repegar `atlas-inject.html` en Ghost:** solo si cambia la estructura del buscador (diseño, facetas, lógica de fetch). Para publicar contenido NO hace falta —basta el ciclo de arriba.

## Flujo del proveedor: ramas y Pull Requests

**`main` está protegida: no se le hace push directo.** Todo cambio entra por un Pull Request que la CI debe aprobar antes de fusionar. Los dos roles se representan con ramas y PR distintos, aunque los ejecute la misma sesión.

El ciclo, para cualquier cambio:

```bash
git switch -c <rama-descriptiva>        # p. ej. signo-neumotorax, fix-url-ecogenicidad
# ...editas .qmd, corres build.py + indice.py, commiteas...
git push -u origin <rama-descriptiva>
gh pr create --fill                     # abre el PR
# espera a que la CI pase (gh pr checks --watch)
gh pr merge --merge --delete-branch     # merge real; nunca squash
git switch main                          # abandona la rama ya fusionada
git pull --ff-only                       # trae el merge commit de GitHub
git fetch --prune                        # elimina referencias origin/* ya borradas
gh pr list --state open                  # confirma que no quedan PR pendientes
git branch -vv                           # detecta ramas locales cuyo remoto está gone
git worktree list                        # no borres ramas ocupadas por un worktree
git status -sb                           # main debe coincidir con origin/main
```

**Los PR hacia `main` se fusionan con merge real, nunca con squash.** Así los
commits revisados de la rama quedan como ancestros de `main`; después de
actualizar el repositorio, Git no los presenta como trabajo pendiente ni obliga
a reconciliar una historia equivalente con SHA distintos. La misma regla rige
los PR hijo apilados. No termines el flujo desde la rama de trabajo: vuelve
siempre a `main`, actualiza, poda y verifica. Una rama todavía asociada a un
worktree no se borra a ciegas; primero identifica ese worktree y conserva
cualquier cambio que no pertenezca al PR.

Reglas:
- **Una rama por unidad de trabajo** (un signo, un arreglo). PRs chicos se revisan y se fusionan sin fricción.
- **No fusiones con la CI en rojo.** El job *Integridad* es obligatorio: si falla, algo real está mal (índice sin regenerar, arista rota, caso sin consentimiento).
- **Trabajo concurrente excepcional:** cada unidad permanece en su rama. Si dos ramas tocan lo mismo, la que fusiona segundo actualiza desde `main` y resuelve en su rama —nunca en `main`. Y **nunca fusiones contenido con citas sin re-verificar** que sobrevivieron intactas (`python scripts/verificar_citas.py`).

## Higiene de Git

Después de cada tarea significativa: `git add`, `git commit` con mensaje claro. Es el punto de restauración. Con un agente editando de forma autónoma, commitear seguido no es opcional — es la red de seguridad. El `push` va a **tu rama**, no a `main` (ver arriba).

### Worktree único y ramas por rol

El flujo normal usa exclusivamente el worktree principal. Publicador y
proveedor se separan mediante ramas/PR apilados y cambios secuenciales de rama,
no mediante worktrees adicionales. Antes y después de cada tarea se ejecuta
`git worktree list`: cualquier worktree extra debe identificarse y retirarse
solo con autorización explícita, después de comprobar que no contiene cambios
sin guardar. Nunca se usa `--force` ni se borra manualmente su directorio. Las
ramas remotas ya fusionadas sí puede eliminarlas quien fusiona el PR.

## Lo que NO debes hacer

- No reescribir arquitectura que ya funciona "para mejorarla" sin que Alcy lo pida.
- No saltar de oleada en el mapa maestro por iniciativa propia.
- No publicar, borrar, ni hacer push destructivo sin confirmación.
- No completar contenido clínico "de tu conocimiento general" — este atlas se apoya en fuentes verificadas y en el criterio de un médico, no en lo que un modelo recuerda.

## El norte

Cada cifra verificada. Cada signo con sus límites. El orden por oleada mantiene vivo el mensaje del proyecto: *empezar POCUS es más fácil de lo que te dijeron.* La arquitectura ya está hecha; tu trabajo es hacerla crecer sin degradar su rigor.
