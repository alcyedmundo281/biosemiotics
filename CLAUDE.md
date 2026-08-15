# CLAUDE.md — Manual de operación del atlas biosemiotics

Este archivo le enseña a cualquier sesión de Claude Code cómo trabajar en este repositorio. **Léelo completo al arrancar.** No improvises el flujo: está escrito aquí por una razón.

---

## Qué es este proyecto

Un atlas educativo de POCUS (ecografía en el punto de atención) para el médico de primer contacto, en español. Su tesis es semiótica: cada hallazgo ecográfico es un **signo** que une un **significante** (lo que se ve), un **significado** (la realidad clínica) y una **decisión** (qué cambia en el manejo).

Autor y responsable clínico: Dr. Alcy Torres. Toda decisión clínica final es suya.

## Regla de oro del sistema

**Una fuente, muchas salidas.** El banco de archivos `.md` es la ÚNICA fuente de verdad. Todo lo demás (`build/`, el índice, el HTML, el JATS) es **derivado** y se regenera. NUNCA edites archivos en `build/` a mano: el siguiente `indice.py` los sobrescribe. Si algo está mal en una salida, se arregla en el `.md` de origen y se recompila.

## Mapa del repositorio

```
proyecto-biosemiotics/
├── CLAUDE.md                    ← este archivo
├── mapa-maestro-biosemiotics.md ← QUÉ escribir y en qué orden (léelo siempre)
├── conceptos/*.md               ← el "por qué" (física, artefactos, técnica)
├── signos/*.md                  ← el "qué hago" (significante→significado→decisión)
├── casos/*.md                   ← el paciente real
├── scripts/                     ← build.py, indice.py, refs.py, nuevo.py, senuelo.py
├── refs.bib                     ← bibliografía (SOLO desde PubMed vía refs.py)
├── assets/                      ← plantillas para nuevo.py
└── build/                       ← GENERADO, no versionar salvo index.json
```

La documentación de referencia (esquema completo, instructivo del artículo) vive en la skill `biosemiotics-atlas`. Consúltala si necesitas el detalle de un campo.

## Compilar el libro (`build/libro.tex`)

El compilador correcto es **LuaLaTeX, no pdflatex**. El banco escribe umbrales y decisiones con símbolos Unicode estructurales (`≥`, `→`, `±`) porque así se leen en la clínica — parchearlos uno por uno no escala. El preámbulo que genera `build_latex()` usa `fontspec` (sin `inputenc`/`fontenc`, que son cosas de pdflatex) y fija `\setmainfont{FreeSerif}`, la única fuente disponible que cubre esos glifos sin fallback silencioso.

**Paquetes LaTeX requeridos** (además de lo básico de `book`): `fontspec`, `babel` (spanish), `biblatex`+`biber`, y para las figuras de los signos con imagen: `graphicx`, `float`, `adjustbox`. En Debian/Ubuntu, `texlive-latex-recommended` + `texlive-latex-extra` + `texlive-lang-spanish` + `texlive-luatex` + `biber` cubren todo. Si falta `adjustbox.sty`, la compilación aborta de inmediato con `File 'adjustbox.sty' not found` — no es un error del banco.

```bash
cd build
lualatex -interaction=nonstopmode libro.tex
biber libro
lualatex -interaction=nonstopmode libro.tex
lualatex -interaction=nonstopmode libro.tex   # segunda pasada: referencias cruzadas
```

Si compilas con pdflatex vas a ver `Missing character` o `Unicode character not set up for use with LaTeX` en cuanto el texto traiga `≥`/`→`/`±` — no es un error del banco, es el compilador equivocado.

## Lo primero al arrancar una sesión

1. Corre `git status` y reporta el estado. Si hay cambios sin commitear, avísalo antes de empezar.
2. Lee `mapa-maestro-biosemiotics.md` y di **qué signo toca según la oleada** (no saltes de oleada sin que Alcy lo pida).
3. Corre `python scripts/build.py` y reporta las alertas actuales (qué falta: abstracts, refs, urls).

## Flujo para agregar un signo

1. **Ubícalo en el mapa maestro.** Copia su fila: `sistema`, `organo`, `nivel`, oleada. No inventes estos valores — están definidos en la taxonomía del mapa.
2. **Crea el archivo** con `python scripts/nuevo.py signo <id> "<título>"` o partiendo de la plantilla.
3. **Contenido:** sigue la estructura estándar del instructivo (encabezados `##` LITERALES, que el JATS mapea automáticamente). Registro: permiso para el principiante, frases cortas, español claro.
4. **Abstract obligatorio:** 40-80 palabras, patrón qué se ve → qué significa → qué decide → dónde falla.
5. **`falsos_positivos` obligatorio:** un signo sin límites enseña a reconocer sin enseñar a dudar. Distingue *falso positivo* (algo que imita el signo sin serlo) de *variante* (el signo real con otra textura) — van en campos distintos.
6. **Referencias:** ver la regla dura abajo.
7. **`url` vacía por ahora.** La plantilla ya trae el campo `url: ""`. Déjalo vacío hasta que el artículo exista en Ghost — el atlas lo mostrará como "(sin publicar)", que es la verdad. **No inventes ni adivines el slug:** el de líneas B resultó ser `lineas-b-ultrasonido-pulmonar`, no `lineas-b`. La URL la da Alcy después de publicar.
8. **Valida:** `python scripts/build.py`. No continúes con errores.

## Reglas duras (no se rompen nunca)

- **CITAS: solo desde PubMed, verificadas.** Usa `scripts/refs.py`. NUNCA escribas una referencia de memoria ni aceptes una que produjo un LLM sin verificar el PMID. Cualquier cifra clínica (umbral, tasa, fórmula) debe tener una fuente que la diga *exactamente*. Si un LLM "recuerda" una cita, trátala como falsa hasta probar lo contrario en PubMed. Este proyecto ya fue salvado de tres referencias inventadas — no repitas el episodio.
- **Verifica que la fuente diga la cifra.** No basta con que el paper trate el tema. Abre el abstract; si dice 1.2%, tu texto dice 1.2%, no "1-4%". Ajusta el texto a la fuente, nunca al revés.
- **Un DOI que Crossref no resuelve no se publica.** `verificar_citas.py` distingue un 404 (Crossref no conoce ese DOI: verificación fallida, sale con código 1) de un error de red transitorio (timeout, 429, 5xx: reintenta). Si la revista es real y simplemente no deposita en Crossref, decláralo en `refs-sin-crossref.txt` con su razón por escrito; esa exención renuncia a la segunda autoridad, así que confirma el PMID a mano antes de usarla. Lo que no se hace es dejar pasar un 404 en silencio.
- **Sección de límites obligatoria** ("Dónde NO confiar"). Sin ella, el signo no se publica. Es el firewall clínico.
- **Consentimiento antes de publicar un caso.** El consentimiento clínico para escanear NO es consentimiento para publicar: son dos "sí" distintos. Sin `consentimiento: obtenido`, el caso no se publica. Verifica de-identificación: sin DICOM metadata, sin rostro, sin identificadores, sin señalética institucional.
- **Nada que implique aval del HECAM/IESS.** La plataforma es independiente.
- **No edites `build/` a mano.** Regenéralo.
- **Casos raros → composite.** Un diagnóstico infrecuente en comunidad pequeña re-identifica. Usa caso representativo y decláralo.

## Ciclo de publicación en Ghost

Este rol publica en Ghost y es dueño de los artefactos que solo nacen durante
la publicación: imagen destacada, licencia, URL pública definitiva y su
integración en el banco de imágenes/LuaLaTeX. El repositorio de contenidos y
`build/index.json` siguen siendo provistos por la otra sesión.

### Límite de responsabilidad — obligatorio

Esta sección prevalece sobre las instrucciones generales de creación,
compilación y Git cuando la tarea solicitada sea publicar un artículo.

El publicador puede usar la sesión autorizada de Ghost y, sobre una ficha `.md`
**ya creada y validada por el proveedor**, modificar solamente `url` y
`medios`; puede añadir el archivo licenciado a `assets/img/`, ejecutar
`build.py`, verificar `build/libro.tex` con LuaLaTeX y entregar esos cambios en
una rama/PR de publicación.

No puede crear fichas, modificar el cuerpo editorial, `refs`, PMID, DOI o
Crossref, ni ejecutar `indice.py` o modificar `build/index.json`. Tampoco
actualiza el mapa maestro ni purga la caché: esas acciones pertenecen al flujo
separado del **proveedor del índice**.

Si falta la ficha o el cuerpo canónico, o si fallan sus referencias, el
publicador se detiene y entrega un bloqueo al proveedor. No crea ni repara ese
contenido. `build.py` se permite únicamente después de añadir `medios` o la URL
para validar la imagen y su salida LuaLaTeX; `indice.py` sigue prohibido.

### 0. Preflight — evitar colisiones

Antes de abrir Ghost:

```bash
python scripts/auditar_pegado_ghost.py \
  --canon build/ghost/<carpeta>/<archivo>.md
```

- Busca el título en Ghost entre borradores y publicados. Si ya existe,
  **detente** y abre el artículo existente; nunca crees un segundo post.
- Confirma que el artefacto canónico existe y que su huella es válida. Esta
  auditoría es de lectura; no genera ni reescribe archivos.
- Confirma que la ficha fuente ya existe y no tiene cambios editoriales
  pendientes. Crea una rama de publicación; en ella solo podrán cambiar
  `url`, `medios`, `assets/img/` y las salidas LuaLaTeX correspondientes.

### 1. Preparar y revisar Ghost

1. Usa exclusivamente `build/ghost/<carpeta>/<archivo>.md` como cuerpo. No lo
   regeneres. Antes de tocar Ghost, guarda su huella esperada:

   ```bash
   python scripts/auditar_pegado_ghost.py --canon build/ghost/<carpeta>/<archivo>.md
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
   `build/libro.tex`; compila con LuaLaTeX cuando el entorno lo permita.
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
     --canon build/ghost/<carpeta>/<archivo>.md \
     --captura <texto-visible-del-editor.txt> \
     --pie "<pie observado>" --pie-esperado "<atribución canónica>"
   ```
5. Justo antes del último botón, confirma explícitamente si se publicará solo
   en web o también se enviará por email, con el número exacto de suscriptores.
6. Después de publicar, exige evidencia de Ghost (`Published` o
   `Published and sent`) y copia la URL pública definitiva. Nunca uses la URL
   del editor (`/ghost/#/...`) ni una vista previa (`/p/...`).

### 2. Registrar los artefactos de publicación y entregar al proveedor

1. Copia la URL pública definitiva al campo `url` de la ficha existente. No
   cambies ningún otro campo salvo `medios`.
2. Ejecuta `build.py`, valida la inclusión de la figura y su atribución en
   `build/libro.tex`, y compila LuaLaTeX si está disponible. **No ejecutes
   `indice.py` ni agregues `build/index.json`.**
3. Abre un PR de publicación limitado a la ficha existente, `assets/img/` y
   las salidas LuaLaTeX que correspondan. La sesión proveedora consume la URL
   definitiva desde ese PR y se ocupa del índice, mapa y metadatos globales.
4. Devuelve un informe con: `id`, título, URL pública, id de Ghost, estado,
   fecha/hora, audiencia y destinatarios, tags, excerpt, autor, acceso, imagen,
   alt, crédito, fuente, licencia, archivos cambiados y PR.

Esta división evita choques: la sesión proveedora crea contenido y verifica
PMID/Crossref; el publicador nunca toca esos campos. El publicador aporta la
información que el proveedor no puede conocer antes de Ghost: URL e imagen
finales.

## Mantenimiento del proveedor — fuera del rol de publicación

Lo que sigue documenta al proveedor del índice y no autoriza al publicador de
Ghost a ejecutar `indice.py` ni a tocar `build/index.json`. En el flujo
proveedor, `build.py` NO regenera
`index.json` — eso lo hace `indice.py`. Si el proveedor modifica un `.md`, debe
correr ambos scripts antes de commitear para no servir entradas obsoletas.

**Verifica antes de commitear.** Después de `indice.py`, confirma que la ficha quedó como esperas:
```bash
python -c "import json; d=json.load(open('build/index.json',encoding='utf-8'))['fichas']; print([f['url'] for f in d if f['id']=='<id>'])"
```
El contador `⚠ N sin url` es solo informativo: puede quedarse igual si otra
rama añade simultáneamente una ficha sin publicar. La autoridad es
`verificar_publicacion.py`, que compara la entidad concreta con el índice.

**Distinción crítica de URLs.** Hay dos clases y NO son lo mismo:

- **URLs de artículos** (campo `url` de cada `.md`, y las del JSON-LD) → `www.biosemiotics.net`.
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

**`main` está protegida: no se le hace push directo.** Todo cambio entra por un Pull Request que la CI debe aprobar antes de fusionar. Esto nació de varias colisiones entre dos sesiones empujando a `main` a la vez; el PR convierte el choque en una revisión ordenada.

El ciclo, para cualquier cambio:

```bash
git switch -c <rama-descriptiva>        # p. ej. signo-neumotorax, fix-url-ecogenicidad
# ...editas .md, corres build.py + indice.py, commiteas...
git push -u origin <rama-descriptiva>
gh pr create --fill                     # abre el PR
# espera a que la CI pase (gh pr checks --watch)
gh pr merge --squash --delete-branch    # fusiona cuando esté verde
git switch main                          # abandona la rama ya fusionada
git pull --ff-only                       # trae el SHA nuevo creado por el squash
git fetch --prune                        # elimina referencias origin/* ya borradas
gh pr list --state open                  # confirma que no quedan PR pendientes
git branch -vv                           # detecta ramas locales cuyo remoto está gone
git worktree list                        # no borres ramas ocupadas por un worktree
git status -sb                           # main debe coincidir con origin/main
```

**El cierre post-squash no es opcional.** GitHub crea un commit nuevo al fusionar con squash; por eso el commit de la rama no aparece como ancestro de `main` y puede parecer pendiente aunque el PR ya esté fusionado. No termines el flujo desde la rama de trabajo: vuelve siempre a `main`, actualiza, poda y verifica. Una rama todavía asociada a un worktree no se borra a ciegas; primero identifica ese worktree y conserva cualquier cambio que no pertenezca al PR.

Reglas:
- **Una rama por unidad de trabajo** (un signo, un arreglo). PRs chicos se revisan y se fusionan sin fricción.
- **No fusiones con la CI en rojo.** El job *Integridad* es obligatorio: si falla, algo real está mal (índice sin regenerar, arista rota, caso sin consentimiento).
- **Trabajo en paralelo:** cada sesión en su rama. Si dos ramas tocan lo mismo, la que fusiona segundo hace `git pull` de `main` y resuelve en su rama —nunca en `main`. Y **nunca fusiones contenido con citas sin re-verificar** que sobrevivieron intactas (`python scripts/verificar_citas.py`).

## Higiene de Git

Después de cada tarea significativa: `git add`, `git commit` con mensaje claro. Es el punto de restauración. Con un agente editando de forma autónoma, commitear seguido no es opcional — es la red de seguridad. El `push` va a **tu rama**, no a `main` (ver arriba).

## Lo que NO debes hacer

- No reescribir arquitectura que ya funciona "para mejorarla" sin que Alcy lo pida.
- No saltar de oleada en el mapa maestro por iniciativa propia.
- No publicar, borrar, ni hacer push destructivo sin confirmación.
- No completar contenido clínico "de tu conocimiento general" — este atlas se apoya en fuentes verificadas y en el criterio de un médico, no en lo que un modelo recuerda.

## El norte

Cada cifra verificada. Cada signo con sus límites. El orden por oleada mantiene vivo el mensaje del proyecto: *empezar POCUS es más fácil de lo que te dijeron.* La arquitectura ya está hecha; tu trabajo es hacerla crecer sin degradar su rigor.
