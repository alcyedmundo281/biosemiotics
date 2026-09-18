# Esquema del banco

Cada fuente `.qmd` tiene front-matter YAML y cuerpo Markdown. Los metadatos
describen la entidad y sus relaciones; el cuerpo desarrolla la explicación.
El contrato comprobable está en [validacion.py](../../scripts/validacion.py),
los estados en [banco.py](../../scripts/banco.py) y la taxonomía en el
[mapa maestro](../../mapa-maestro-biosemiotics.md).

## Campos comunes

| Campo | Contenido |
|---|---|
| `id` | Identificador estable en kebab-case; los signos usan `signo-` |
| `tipo` | `concepto`, `signo` o `caso` |
| `titulo` | Título humano no vacío |
| `nivel` | `principiante`, `intermedio` o `avanzado` |
| `abstract` | Resumen de 40–80 palabras |
| `refs` | Lista no vacía de claves existentes en `refs.bib` |
| `estado` | `borrador`, `revisado` o `publicado` |
| `url` | Vacía en borrador/revisado; URL pública real en publicado |
| `fecha_revision`, `ghost_id` | Evidencia real de revisión y registro; `null` si no consta |
| `tags` | Lista opcional de etiquetas |

Una ficha seleccionada para una salida pública necesita cuerpo, campos y
secciones completas. No se admiten campos obligatorios vacíos o con `TODO`.
Los borradores incompletos permanecen fuera de las salidas públicas; build los
conserva en la base y el grafo de trabajo con alertas. No distribuyas estos como
una edición revisada. Una referencia existente no demuestra que apoye una cifra.

## Concepto

Explica por qué la imagen se ve así. `dominio` identifica física, artefacto,
técnica, knobology o semiótica (`fisica`, `artefacto`, `tecnica`, `knobology`,
`semiotica`). `capitulo` y `orden` organizan su recorrido editorial.
`relacionado_con` enlaza entidades y `prerequisito_de` declara una ruta dirigida
de aprendizaje. El concepto conserva estructura libre; los títulos sugeridos
en el instructivo no son una lista de secciones obligatorias del validador.

## Signo

| Campo | Función |
|---|---|
| `sistema`, `organo` | Clasificación según mapa maestro; sistema válido obligatorio |
| `ventana` | Dónde y cómo se obtiene la vista |
| `sonda` | Lista no vacía de sondas |
| `significante` | Lo que se observa, descrito sin sustituirlo por la interpretación |
| `significado` | Realidad física o patológica a la que remite |
| `decision` | Qué cambia en el manejo |
| `umbral` | Punto de corte si corresponde, sustentado por evidencia |
| `se_basa_en` | IDs de conceptos que sustentan el signo |
| `contrasta_con` | IDs de signos con los que se compara |
| `falsos_positivos` | Lista obligatoria no vacía de imitadores o situaciones engañosas |

El contraste enseña la bifurcación. Los falsos positivos no se confunden con
variantes del signo real. Los conceptos base se escriben y validan antes de
publicar el signo. No inventes relaciones para rellenar listas.

## Caso

Un caso organiza una sola decisión semiótica, no solo una imagen interesante.
Requiere `organo`, `decision_semiotica` y una lista no vacía de `signos`.
`conceptos` enlaza el fundamento. `fecha`, `taller`, `video_lure`,
`video_archivo`, `doi` y `composite` registran datos que realmente existan.
Los campos de video usan `yt:<ID>` cuando se emplea ese proveedor.

Para casos revisados o publicados se exige `consentimiento: obtenido`.
El permiso para escanear y el permiso para publicar son distintos. El estado
no acredita por sí mismo consentimiento ni desidentificación. Si se usa un
caso representativo, se declara `composite: true` y se explica en el texto;
no debe servir para ocultar un paciente identificable ni eludir los controles.

## Relaciones y consultas

Clases: `relacionado_con`, `prerequisito_de`, `se_basa_en`, `contrasta_con`,
`signos`, `conceptos`. Los destinos deben existir. Cambiar un ID exige revisar
sus referencias; no es una corrección cosmética.

La base generada contiene entidades, relaciones, etiquetas, referencias,
falsos positivos y búsqueda FTS5. Consulta las tablas actuales mediante
`scripts/consultas.py`; no edites SQLite como fuente de contenido.
