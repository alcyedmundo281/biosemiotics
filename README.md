# biosemiotics

**Atlas de POCUS para el médico de primer contacto.** En español, con cada cifra
verificada contra la literatura y cada signo acompañado de sus límites.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21435362.svg)](https://doi.org/10.5281/zenodo.21435362)
[![Licencia: CC BY 4.0](https://img.shields.io/badge/Licencia-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/deed.es)

🔗 **[www.biosemiotics.net](https://www.biosemiotics.net/)**

---

## La tesis

Un hallazgo ecográfico no es una imagen bonita: es un **signo**. Y como todo
signo, une tres cosas:

| | |
|---|---|
| **Significante** | lo que se ve en pantalla |
| **Significado** | la realidad clínica a la que remite |
| **Decisión** | qué cambia en el manejo del paciente |

Sin la tercera, el hallazgo es trivia. El atlas está construido sobre esa
estructura: cada entrada del banco declara las tres, y el pipeline las propaga a
todas las salidas.

El mensaje que sostiene el proyecto: **empezar POCUS es más fácil de lo que te
dijeron.** Por eso los signos se publican por oleadas, empezando por los que
desintimidan —reconocimiento casi binario, alto impacto clínico.

## Cómo está hecho

**Una fuente, muchas salidas.** El banco de archivos `.qmd` con front-matter
YAML es la única fuente de verdad. Todo lo demás se genera y se regenera.

```
proyecto-biosemiotics/
├── conceptos/     ← el "por qué" (física, artefactos, técnica)
├── signos/        ← el "qué hago" (significante → significado → decisión)
├── casos/         ← el paciente real
├── scripts/       ← el pipeline en Python
├── refs.bib       ← bibliografía (solo desde PubMed, verificada)
└── build/         ← derivados; solo build/index.json se versiona
```

De esa fuente única salen:

- **`build/atlas.db`** — SQLite navegable y grafo de relaciones
- **`build/quarto/libro.tex`** — fuente LuaLaTeX junto con sus imágenes
- **`build/grafo.json`** — grafo de conceptos
- **`build/jsonld/`** — fichas schema.org
- **`build/jats/`** — XML experimental de intercambio con vocabulario JATS
- **`build/index.json`** — índice que alimenta el buscador facetado
- **`build/atlas-inject.html`** — buscador para la página Atlas de Ghost
- **`build/atlas.epub`** — edición EPUB3
- **`build/libro.pdf`** — libro compilado con LuaLaTeX
- **`build/biosemiotics-latex.zip`** — fuente compilable autocontenida

GitHub Actions regenera automáticamente EPUB, PDF, TEX y el ZIP LaTeX
autocontenido después de cada cambio relevante fusionado a `main`. Los
artefactos quedan disponibles durante 90 días; no hace falta ejecutar el
workflow manualmente.

### Preparar el entorno

```bash
python -m pip install -r requirements.txt
python scripts/preflight.py
```

El preflight normal comprueba Python 3.9+, la versión fijada de PyYAML, la
estructura del banco, el contrato editorial y la coherencia entre fuentes,
`build/index.json` y el mapa maestro. Es de solo lectura. Para generar todos
los artefactos editoriales, instala además Quarto 1.5.57, LuaLaTeX con
FreeSerif, Java, `rsvg-convert` y EPUBCheck 5.1.0, y ejecuta:

```bash
python scripts/preflight.py --publicacion
```

Las versiones y paquetes usados en Linux están declarados en
`.github/workflows/epub.yml`; ese workflow es el entorno reproducible de
referencia para EPUB, PDF y LuaLaTeX.

### Uso diario

```bash
python scripts/nuevo.py signo <id> "<título>"   # crear una entrada
python scripts/build.py                          # compilar y validar
python scripts/refs.py                           # auditar qué referencias faltan
python scripts/refs.py --buscar                  # buscarlas en PubMed
python scripts/indice.py                         # generar índice y derivados
python scripts/epub.py --salida build/atlas.epub --solo-publicados
python scripts/libro.py --salida build/libro.pdf --solo-publicados
python scripts/paquete_latex.py --salida build/biosemiotics-latex.zip
python scripts/verificar_publicacion.py --verificar-derivados --epub build/atlas.epub
python scripts/consultas.py                      # explorar el atlas en SQL
```

Los comandos localizan el repositorio por la ubicación de `scripts/`, de modo
que producen el mismo resultado aunque se invoquen desde `scripts/` o desde otro
directorio. `--raiz <ruta>` permite operar sobre otro banco; una raíz relativa
se interpreta desde el directorio actual. `--destino`, `--proyecto`, `--salida`
y `--db` relativos se interpretan desde la raíz elegida. Las rutas absolutas se
respetan. `indice.py <raiz>` sigue aceptado por compatibilidad, pero el uso nuevo
es `indice.py --raiz <ruta>`.

Si falta una compilación, `consultas.py` informa la ruta exacta esperada de
`build/atlas.db` y el comando para generarla.

`build.py` no es cosmético: valida integridad referencial y bloquea la
publicación si falta un abstract, una referencia o una sección obligatoria.

El XML de `build/jats/` conserva metadatos, secciones, medios y claves de
referencia con nombres de elementos JATS, pero no declara DTD, no expande las
referencias bibliográficas y no se valida contra el perfil de un repositorio.
Por ello no es un paquete listo para PMC, Crossref ni otro depósito: antes de
enviarlo hay que adaptarlo y validarlo contra las reglas del destino.

## Las reglas que no se rompen

Están escritas en [`CLAUDE.md`](CLAUDE.md), el manual de operación del
repositorio. Las tres que gobiernan todo lo demás:

1. **Toda cita nace de un PMID verificado.** Nunca de la memoria de un modelo ni
   de un apunte. Si el paper dice 1,2 %, el texto dice 1,2 % —el texto se ajusta
   a la fuente, jamás al revés.
2. **Todo signo lleva su sección de límites** («dónde NO confiar»). Un signo sin
   límites enseña a reconocer sin enseñar a dudar, y produce el escaneador con
   exceso de confianza: el riesgo clínico real del proyecto.
3. **Consentimiento como doble sí.** El consentimiento para escanear no es
   consentimiento para publicar. Sin el segundo, el caso no se publica.

El plan completo de crecimiento —taxonomía, oleadas, las ~48 entidades
proyectadas— vive en
[`mapa-maestro-biosemiotics.md`](mapa-maestro-biosemiotics.md).

## Cómo citar

> Torres Guerrero, A. E. (2026). *biosemiotics — atlas de POCUS para el médico
> de primer contacto* [Software]. Zenodo.
> https://doi.org/10.5281/zenodo.21435362

Ese es el **DOI de concepto**: agrupa todas las versiones y siempre resuelve a
la más reciente. Úsalo para citar el atlas en general.

Si necesitas referirte a un estado exacto y reproducible del banco —por ejemplo
para respaldar un dato citado en una fecha concreta—, usa el DOI específico de
esa versión, que aparece en su página de Zenodo.

## Licencia

[Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es).
Texto legal completo en [`LICENSE`](LICENSE).

Puedes compartir y adaptar el material —incluso con fines comerciales— siempre
que cites la autoría e indiques si hiciste cambios.

**Las imágenes tienen su propia licencia**, declarada en el bloque `medios` de
cada ficha: hay archivos en CC0, dominio público, CC BY y CC BY-SA. Las CC BY-SA
imponen *share-alike* a las obras derivadas de esa imagen concreta. Al reutilizar
una figura, respeta la licencia de esa figura, no la del atlas.

## Aviso

Material **educativo**. No sustituye el juicio clínico, la formación supervisada
ni la valoración presencial del paciente. Las decisiones clínicas son
responsabilidad de quien atiende.

Plataforma **independiente**: el contenido no implica aval ni representación de
ninguna institución sanitaria.
