#!/usr/bin/env python3
"""Genera la edición EPUB3 reproducible del atlas biosemiotics.

Interfaz contractual (la que espera `.github/workflows/epub.yml`):
    python scripts/epub.py --salida build/atlas.epub [--solo-publicados]

Este script ya NO ensambla el manuscrito. Esa responsabilidad vive en
`scripts/qmd.py`, que proyecta el banco a un proyecto Quarto book en
`build/quarto/`. Aquí solo se elige el motor, se renderiza y se valida.

Dos motores, un solo manuscrito:

  · `quarto` — el camino previsto. Renderiza el proyecto book completo y da
    además PDF y HTML del mismo árbol con `--to pdf` / `--to html`.
  · `pandoc` — el respaldo. Renderiza `build/quarto/libro-plano.md`, que
    `qmd.py` deriva de las MISMAS funciones que los capítulos. No es una
    edición distinta: es el mismo libro aplanado.

El respaldo existe porque Quarto no está disponible en todos los entornos. Si
las dos salidas difieren en contenido, es un fallo de `qmd.py`, no una variante
editorial aceptable.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import build as banco
import qmd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument(
        "--solo-publicados",
        action="store_true",
        help="incluye únicamente fichas con URL pública de Ghost",
    )
    parser.add_argument(
        "--motor",
        choices=("auto", "quarto", "pandoc"),
        default="auto",
        help="auto usa quarto si está en PATH y cae a pandoc si no",
    )
    parser.add_argument(
        "--proyecto",
        type=Path,
        default=Path("build/quarto"),
        help="dónde se deja el proyecto Quarto generado",
    )
    return parser.parse_args()


def elegir_motor(preferido: str) -> tuple:
    """(nombre, ejecutable). Falla con un mensaje accionable si no hay ninguno."""
    quarto = shutil.which("quarto")
    pandoc = shutil.which("pandoc")
    if preferido == "quarto":
        if not quarto:
            raise RuntimeError(
                "se pidió --motor quarto pero quarto no está en PATH. "
                "Instálalo desde https://quarto.org/docs/get-started/ o usa "
                "--motor pandoc."
            )
        return "quarto", quarto
    if preferido == "pandoc":
        if not pandoc:
            raise RuntimeError("se pidió --motor pandoc pero pandoc no está en PATH")
        return "pandoc", pandoc
    if quarto:
        return "quarto", quarto
    if pandoc:
        return "pandoc", pandoc
    raise RuntimeError(
        "no hay motor de render: instala quarto (preferido) o pandoc"
    )


def render_pandoc(ejecutable: str, proyecto: Path, destino: Path, informe: dict) -> Path:
    comando = [
        ejecutable,
        "libro-plano.md",
        # El lector `markdown` de pandoc es el que usa Quarto, así que los dos
        # motores parsean igual. Con `gfm` se perdían dos cosas: los atributos
        # `{#sec-...}` se filtraban como texto al índice, y el pie de figura se
        # aplanaba a un `alt=` de texto plano —el lector gfm acepta
        # `implicit_figures` pero la ignora—, de modo que los enlaces de crédito
        # y licencia de cada imagen desaparecían del EPUB.
        "--from=markdown",
        "--to=epub3",
        f"--output={destino}",
        "--toc",
        "--toc-depth=3",
        # Nivel 2 = un archivo por capítulo (capítulo temático u órgano), que
        # es la unidad de lectura real. Nivel 1 dejaba una parte entera —hasta
        # varios MB— en un solo XHTML, y los lectores lo pagan al paginar.
        "--split-level=2",
        "--css=epub.css",
        f"--epub-cover-image={informe['portada']}",
        # Dublin Core completo: DOI dereferenciable, licencia con URL,
        # descripción y materias MeSH. Sin esto el DOI queda como cadena
        # suelta y la licencia como un nombre sin referencia.
        "--epub-metadata=epub-metadata.xml",
        f"--metadata=title:{qmd.TITULO}",
        f"--metadata=subtitle:{qmd.SUBTITULO}",
        f"--metadata=author:{qmd.AUTOR}",
        "--metadata=lang:es",
        f"--metadata=date:{date.today().isoformat()}",
    ]
    subprocess.run(comando, cwd=proyecto, check=True)
    return destino


def validar_epub(path: Path, entidades: int, figuras: int, enlaces_ghost: int) -> str:
    """Las garantías editoriales del atlas, verificadas sobre el contenedor.

    No dependen del motor: son las mismas para quarto y para pandoc. Incluyen
    lo que no se ve leyendo el texto —DOI y licencia en el OPF, portada
    declarada, figuras con pie clicable y el puente al artículo vivo de Ghost—
    porque son justo las que se pierden sin que nadie lo note.
    """
    if not path.is_file() or path.stat().st_size < 50 * 1024:
        raise RuntimeError("el EPUB no existe o es sospechosamente pequeño")
    with zipfile.ZipFile(path) as zf:
        nombres = zf.namelist()
        if not nombres or nombres[0] != "mimetype":
            raise RuntimeError("mimetype no es la primera entrada del contenedor")
        if zf.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            raise RuntimeError("mimetype debe almacenarse sin compresión")
        if zf.read("mimetype") != b"application/epub+zip":
            raise RuntimeError("mimetype EPUB incorrecto")
        for requerido in ("META-INF/container.xml",):
            if requerido not in nombres:
                raise RuntimeError(f"falta {requerido}")
        textos = b"".join(zf.read(n) for n in nombres if n.endswith((".xhtml", ".html")))
        comprobaciones = {
            "citas sin resolver ([?])": b"[?]" not in textos,
            "marcadores TODO": b"TODO" not in textos,
            "DOI": qmd.DOI.encode() in textos,
            "ISBN pendiente": b"ISBN EPUB: pendiente" in textos,
            "aviso educativo": b"material educativo" in textos.lower(),
            "bibliografía final": "Bibliografía".encode() in textos,
            "créditos de imágenes": "Créditos de imágenes".encode() in textos,
        }
        fallos = [nombre for nombre, correcto in comprobaciones.items() if not correcto]
        if fallos:
            raise RuntimeError("validación editorial EPUB fallida: " + ", ".join(fallos))
        for simbolo in ("≥", "→", "±"):
            if simbolo.encode() not in textos:
                raise RuntimeError(f"el símbolo Unicode {simbolo!r} no quedó incrustado")
        # Figuras reales, no <img> sueltos: el pie lleva los enlaces de crédito
        # y licencia de cada imagen, y con el lector equivocado se aplana a un
        # `alt=` de texto plano sin que falle nada.
        if textos.count(b"<figcaption") < figuras:
            raise RuntimeError(
                f"solo {textos.count(b'<figcaption')} de {figuras} figuras "
                "tienen pie: los enlaces de crédito y licencia se perdieron"
            )
        ghost = textos.count(b'href="https://www.biosemiotics.net/')
        if ghost < enlaces_ghost:
            raise RuntimeError(
                f"faltan enlaces al artículo publicado: {ghost} de {enlaces_ghost}"
            )

        opf = [n for n in nombres if n.endswith(".opf")]
        if not opf:
            raise RuntimeError("el contenedor no declara ningún paquete OPF")
        paquete = zf.read(opf[0]).decode("utf-8")
        metadatos = {
            "DOI en dc:identifier": qmd.DOI_URL in paquete,
            "licencia con URL en dc:rights": qmd.LICENCIA_URL in paquete,
            "portada declarada": 'properties="cover-image"' in paquete,
            "editorial": "<dc:publisher" in paquete,
            "identificador único": paquete.count("<dc:identifier") == 1,
            "descripción": "<dc:description" in paquete,
        }
        ausentes = [n for n, ok in metadatos.items() if not ok]
        if ausentes:
            raise RuntimeError("metadatos EPUB incompletos: " + ", ".join(ausentes))

        navegacion = [n for n in nombres if n.endswith("nav.xhtml")]
        if not navegacion:
            raise RuntimeError("el contenedor no trae índice de navegación")

        imagenes = [
            n for n in nombres
            if n.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".webp"))
        ]
        if len(imagenes) < figuras + 1:  # figuras del banco + portada
            raise RuntimeError(
                f"faltan imágenes incrustadas: esperadas al menos {figuras + 1}, "
                f"halladas {len(imagenes)}"
            )
    return f"contenedor EPUB3 válido ({entidades} entidades, {figuras} figuras)"


def main() -> int:
    args = argumentos()
    raiz = Path(__file__).resolve().parents[1]
    salida = args.salida if args.salida.is_absolute() else raiz / args.salida
    proyecto = args.proyecto if args.proyecto.is_absolute() else raiz / args.proyecto

    entidades = banco.cargar(raiz)
    if args.solo_publicados:
        entidades = [e for e in entidades if e.get("url")]
    if not entidades:
        raise RuntimeError("ninguna entidad cumple el alcance solicitado")

    nombre_motor, ejecutable = elegir_motor(args.motor)
    informe = qmd.generar(entidades, raiz, proyecto)

    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = proyecto / "atlas-temporal.epub"
    if nombre_motor == "quarto":
        producido = qmd.render(ejecutable, proyecto, "epub", ".epub")
    else:
        producido = render_pandoc(ejecutable, proyecto, temporal, informe)

    enlaces_ghost = sum(1 for e in entidades if e.get("url"))
    validacion = validar_epub(
        producido, informe["entidades"], informe["figuras"], enlaces_ghost
    )
    os.replace(producido, salida)

    print(f"✓ Motor: {nombre_motor} ({ejecutable})")
    print(f"✓ Proyecto: {proyecto.relative_to(raiz)} "
          f"({informe['capitulos']} capítulos, {len(informe['partes'])} partes)")
    print(f"✓ Entidades incluidas: {informe['entidades']}")
    print(f"✓ Figuras incrustadas: {informe['figuras']} (con pie y enlaces)")
    print(f"✓ Enlaces al artículo en Ghost: {enlaces_ghost}")
    print(f"✓ Portada: {informe['portada']}")
    print(f"✓ Referencias: {informe['referencias']}")
    print(f"✓ Versión: {informe['version']} · fecha: {date.today().isoformat()}")
    print(f"✓ Tamaño: {salida.stat().st_size:,} bytes")
    print(f"✓ Validación interna: {validacion}")
    print(f"✓ Salida: {salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, KeyError, ValueError) as exc:
        print(f"ERROR EPUB: {exc}", file=sys.stderr)
        raise SystemExit(1)
