# Banco biosemiotics — cómo arrancar

La fuente única son las fichas `.qmd` de `conceptos/`, `signos/` y `casos/`,
con metadatos YAML. `refs.bib` contiene la bibliografía y `scripts/` el pipeline.
Todo bajo `build/` es derivado; solo `build/index.json` se versiona.

## Preparación

Se admite Python 3.9 o posterior. Instala la dependencia fijada y comprueba el
banco antes de editar:

```bash
python -m pip install -r requirements.txt
python scripts/preflight.py
```

El preflight es de solo lectura y funciona desde cualquier directorio. Para
otro checkout o banco usa `--raiz <ruta>`.

## Uso diario

```bash
python scripts/nuevo.py signo nervio-optico "Vaina del nervio óptico"
python scripts/build.py
python scripts/refs.py
python scripts/refs.py --buscar
python scripts/indice.py
python scripts/verificar_publicacion.py
python scripts/consultas.py
```

`build.py` genera SQLite, grafo y Markdown para Ghost. `indice.py` genera
`build/index.json`, el buscador, JSON-LD y el XML experimental de `build/jats/`.
El libro se proyecta con Quarto:

```bash
python scripts/epub.py --salida build/atlas.epub --solo-publicados
python scripts/libro.py --salida build/libro.pdf --solo-publicados
python scripts/paquete_latex.py --salida build/biosemiotics-latex.zip
```

Antes de esas salidas completas ejecuta:

```bash
python scripts/preflight.py --publicacion
```

Este perfil exige Quarto, LuaLaTeX, Java, `rsvg-convert` y
EPUBCheck. Las versiones de referencia están en `.github/workflows/epub.yml`.

El XML de `build/jats/` usa vocabulario JATS para intercambio interno. No está
validado contra una DTD ni contra un perfil de depósito; no debe enviarse a
PMC, Crossref u otro repositorio sin adaptarlo y validarlo para ese destino.

Las reglas editoriales y el flujo de publicación en Ghost están en
[`CLAUDE.md`](CLAUDE.md). El orden del contenido está en
[`mapa-maestro-biosemiotics.md`](mapa-maestro-biosemiotics.md).
