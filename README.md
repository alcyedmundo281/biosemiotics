# biosemiotics

**Atlas de POCUS para el médico de primer contacto.** En español, con cada cifra
verificada contra la literatura y cada signo acompañado de sus límites.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21435362.svg)](https://doi.org/10.5281/zenodo.21435362)
[![Licencia: CC BY-NC 4.0](https://img.shields.io/badge/Licencia-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/deed.es)

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

**Una fuente, muchas salidas.** El banco de archivos Markdown con front-matter
YAML es la única fuente de verdad. Todo lo demás se genera y se regenera.

```
proyecto-biosemiotics/
├── conceptos/     ← el "por qué" (física, artefactos, técnica)
├── signos/        ← el "qué hago" (significante → significado → decisión)
├── casos/         ← el paciente real
├── scripts/       ← el pipeline en Python
├── refs.bib       ← bibliografía (solo desde PubMed, verificada)
└── build/         ← generado: SQLite, LaTeX, grafo, JSON-LD, JATS, índice
```

De esa fuente única salen:

- **`atlas.db`** — base SQLite navegable, con el grafo de relaciones entre signos y conceptos
- **`libro.tex`** — LaTeX/BibLaTeX para compilar el libro
- **`grafo.json`** — el grafo de conceptos
- **`jsonld/`** — fichas schema.org (`MedicalScholarlyArticle`, `MedicalSignOrSymptom`)
- **`jats/`** — XML JATS para depósito y archivo
- **`index.json`** — índice tipo PubMed que alimenta el buscador facetado del sitio

### Uso

```bash
pip install pyyaml

python scripts/nuevo.py signo <id> "<título>"   # crear una entrada
python scripts/build.py                          # compilar y validar
python scripts/refs.py                           # auditar qué referencias faltan
python scripts/refs.py --buscar                  # buscarlas en PubMed
python scripts/indice.py . <URL_DEL_INDICE>      # generar índice y derivados
python scripts/consultas.py                      # explorar el atlas en SQL
```

`build.py` no es cosmético: valida integridad referencial y bloquea la
publicación si falta un abstract, una referencia o una sección obligatoria.

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

[Creative Commons Atribución-NoComercial 4.0 Internacional (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/deed.es).
Texto legal completo en [`LICENSE`](LICENSE).

Puedes compartir y adaptar el material citando la autoría, con fines no
comerciales.

## Aviso

Material **educativo**. No sustituye el juicio clínico, la formación supervisada
ni la valoración presencial del paciente. Las decisiones clínicas son
responsabilidad de quien atiende.

Plataforma **independiente**: el contenido no implica aval ni representación de
ninguna institución sanitaria.
