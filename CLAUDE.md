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
- **Sección de límites obligatoria** ("Dónde NO confiar"). Sin ella, el signo no se publica. Es el firewall clínico.
- **Consentimiento antes de publicar un caso.** El consentimiento clínico para escanear NO es consentimiento para publicar: son dos "sí" distintos. Sin `consentimiento: obtenido`, el caso no se publica. Verifica de-identificación: sin DICOM metadata, sin rostro, sin identificadores, sin señalética institucional.
- **Nada que implique aval del HECAM/IESS.** La plataforma es independiente.
- **No edites `build/` a mano.** Regenéralo.
- **Casos raros → composite.** Un diagnóstico infrecuente en comunidad pequeña re-identifica. Usa caso representativo y decláralo.

## Ciclo de publicación (cuando un artículo ya está en Ghost)

El texto completo del artículo se escribe/edita en Ghost directamente (Claude Code NO tiene acceso a Ghost). Cuando Alcy publique y dé la URL:

1. Pon la URL pública (`https://www.biosemiotics.net/<slug>/`) en el campo `url` del `.md`. Nunca la URL del editor (`/ghost/#/...`).
2. `python scripts/build.py` (validar)
3. `python scripts/indice.py . "https://cdn.jsdelivr.net/gh/alcyedmundo281/biosemiotics@main/build/index.json"`
4. `git add -f build/index.json` + los `.md` tocados
5. `git commit` + `git push`
6. Recuérdale a Alcy purgar jsDelivr: `https://purge.jsdelivr.net/gh/alcyedmundo281/biosemiotics@main/build/index.json`

**El paso 3 no es opcional, y es el que más se olvida.** `build.py` NO regenera `index.json` — eso lo hace `indice.py`. Si commiteas `.md` y `refs.bib` sin correr `indice.py`, el buscador del sitio queda sirviendo datos viejos: entradas sin su URL, sin su conteo de referencias. Ya pasó dos veces. Regla práctica: **si tocaste un `.md`, corre los dos scripts antes de commitear.**

**Verifica antes de commitear.** Después de `indice.py`, confirma que la ficha quedó como esperas:
```bash
python -c "import json; d=json.load(open('build/index.json',encoding='utf-8'))['fichas']; print([f['url'] for f in d if f['id']=='<id>'])"
```
El contador `⚠ N sin url` que imprime `indice.py` debe BAJAR cuando publicas algo. Si no baja, la URL no entró.

**Distinción crítica de URLs:** las de artículos usan `www.biosemiotics.net`. La URL del índice que consume el buscador (`var IDX` en atlas-inject.html) usa `cdn.jsdelivr.net/...` y NO cambia. No las confundas.

## Trabajo en paralelo (dos sesiones)

Si hay dos sesiones sobre el mismo repo: auditoría antes de fusionar. Verifica qué versión es superset, rebase o reset según corresponda, y **nunca fusiones contenido con citas sin re-verificar** que sobrevivieron intactas.

## Higiene de Git

Después de cada tarea significativa: `git add`, `git commit` con mensaje claro, `git push`. Es el punto de restauración. Con un agente editando de forma autónoma, commitear seguido no es opcional — es la red de seguridad.

## Lo que NO debes hacer

- No reescribir arquitectura que ya funciona "para mejorarla" sin que Alcy lo pida.
- No saltar de oleada en el mapa maestro por iniciativa propia.
- No publicar, borrar, ni hacer push destructivo sin confirmación.
- No completar contenido clínico "de tu conocimiento general" — este atlas se apoya en fuentes verificadas y en el criterio de un médico, no en lo que un modelo recuerda.

## El norte

Cada cifra verificada. Cada signo con sus límites. El orden por oleada mantiene vivo el mensaje del proyecto: *empezar POCUS es más fácil de lo que te dijeron.* La arquitectura ya está hecha; tu trabajo es hacerla crecer sin degradar su rigor.
