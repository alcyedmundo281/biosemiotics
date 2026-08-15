#!/usr/bin/env python3
"""Genera la edición EPUB3 reproducible del atlas biosemiotics.

Interfaz contractual:
    python scripts/epub.py --salida build/atlas.epub [--solo-publicados]
"""

from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import build as banco

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


TITULO = "Biosemiótica del Cuerpo Vivo"
SUBTITULO = "Atlas de POCUS para el clínico"
AUTOR = "Dr. Alcy Edmundo Torres Guerrero"
ORCID = "0000-0002-9742-375X"
EDITORIAL = "BioSemiotics"
DOI = "10.5281/zenodo.21435362"
LICENCIA = "CC BY 4.0"
AVISO = (
    "Material exclusivamente educativo. No sustituye el juicio clínico, "
    "la evaluación integral del paciente ni los protocolos locales."
)
REQUERIDOS_IMAGEN = (
    "descripcion",
    "credito",
    "fuente",
    "fuente_url",
    "licencia_img",
    "licencia_url",
    "archivo_local",
)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument(
        "--solo-publicados",
        action="store_true",
        help="incluye únicamente fichas con URL pública de Ghost",
    )
    return parser.parse_args()


def version_git(raiz: Path) -> str:
    try:
        return subprocess.run(
            ["git", "describe", "--always", "--dirty"],
            cwd=raiz,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "sin-versión-git"


def imagenes(entidades: list[dict], raiz: Path) -> list[tuple[dict, dict, Path]]:
    resultado = []
    errores = []
    for entidad in entidades:
        for numero, medio in enumerate(entidad.get("medios") or [], 1):
            if medio.get("tipo") != "imagen":
                continue
            faltantes = [campo for campo in REQUERIDOS_IMAGEN if not medio.get(campo)]
            prefijo = f"{entidad['_archivo']} medio {numero}"
            if faltantes:
                errores.append(f"{prefijo}: faltan {', '.join(faltantes)}")
                continue
            ruta = (raiz / medio["archivo_local"]).resolve()
            try:
                ruta.relative_to(raiz.resolve())
            except ValueError:
                errores.append(f"{prefijo}: archivo_local apunta fuera del repositorio")
                continue
            if not ruta.is_file():
                errores.append(f"{prefijo}: no existe {medio['archivo_local']}")
                continue
            resultado.append((entidad, medio, ruta))
    if errores:
        detalle = "\n  - ".join(errores)
        raise RuntimeError(
            "Metadatos de imágenes incompletos; el EPUB no puede omitir ni "
            f"atribuir figuras por inferencia:\n  - {detalle}"
        )
    return resultado


def entidades_ordenadas(entidades: list[dict]):
    conceptos = sorted(
        (e for e in entidades if e["tipo"] == "concepto"),
        key=lambda e: (e.get("capitulo") or 99, e.get("orden") or 99),
    )
    signos = [e for e in entidades if e["tipo"] == "signo"]
    casos = sorted(
        (e for e in entidades if e["tipo"] == "caso"),
        key=lambda e: e["titulo"],
    )
    return conceptos, signos, casos


def figura_markdown(medio: dict) -> str:
    descripcion = medio["descripcion"]
    credito = medio["credito"]
    fuente = medio["fuente"]
    licencia = medio["licencia_img"]
    pie = (
        f"{descripcion}. {credito}. "
        f"[{fuente}]({medio['fuente_url']}). "
        f"[{licencia}]({medio['licencia_url']})."
    )
    return f"![{pie}]({medio['archivo_local']})"


def cuerpo_con_evidencia(entidad: dict, bibliografia: dict) -> str:
    cuerpo = banco.quitar_bibliografia_manual(entidad["cuerpo"])
    cuerpo, orden = banco.resolver_citas(cuerpo, entidad.get("refs") or [], bibliografia)
    refs = [
        banco.referencia_ghost(i, bibliografia[clave])
        for i, clave in enumerate(orden, 1)
    ]
    if refs:
        cuerpo = cuerpo.rstrip() + "\n\n#### Evidencia\n\n" + "\n".join(refs)
    return cuerpo.strip()


def ficha_markdown(entidad: dict, bibliografia: dict) -> str:
    lineas = [f"### {entidad['titulo']}", ""]
    for medio in entidad.get("medios") or []:
        if medio.get("tipo") == "imagen":
            lineas += [figura_markdown(medio), ""]
    if entidad["tipo"] == "signo":
        for etiqueta, campo in (
            ("Significante", "significante"),
            ("Significado", "significado"),
            ("Decisión", "decision"),
            ("Umbral", "umbral"),
        ):
            if entidad.get(campo):
                lineas += [f"**{etiqueta}.** {entidad[campo]}", ""]
    elif entidad["tipo"] == "caso" and entidad.get("decision_semiotica"):
        lineas += [f"**Decisión semiótica.** {entidad['decision_semiotica']}", ""]
    lineas += [cuerpo_con_evidencia(entidad, bibliografia), ""]
    return "\n".join(lineas)


def manuscrito(entidades: list[dict], bibliografia: dict, version: str) -> str:
    conceptos, signos, casos = entidades_ordenadas(entidades)
    partes = [
        "# Portadilla",
        "",
        f"## {TITULO}",
        "",
        f"**{SUBTITULO}**",
        "",
        f"{AUTOR} · ORCID [{ORCID}](https://orcid.org/{ORCID})",
        "",
        f"{EDITORIAL} · Compilación {date.today().isoformat()} · versión `{version}`",
        "",
        "# Créditos, licencia y uso",
        "",
        f"Autor: {AUTOR}. Editorial: {EDITORIAL}. Idioma: español.",
        "",
        f"Identificador DOI: [{DOI}](https://doi.org/{DOI}). ISBN EPUB: pendiente.",
        "",
        f"El conjunto se distribuye bajo {LICENCIA}. Las figuras conservan sus licencias propias, declaradas en cada pie y en los créditos finales.",
        "",
        f"**Aviso:** {AVISO}",
        "",
        "No existe afiliación, aval ni patrocinio del HECAM o del IESS.",
        "",
        "# Parte I — Fundamentos",
        "",
    ]
    por_capitulo: dict[int, list[dict]] = defaultdict(list)
    for entidad in conceptos:
        por_capitulo[entidad.get("capitulo") or 99].append(entidad)
    for capitulo in sorted(por_capitulo):
        partes += [f"## {banco.CAPITULOS.get(capitulo, f'Capítulo {capitulo}')}", ""]
        for entidad in por_capitulo[capitulo]:
            partes.append(ficha_markdown(entidad, bibliografia))

    ubicados = set()
    numero_parte = 2
    for clave, titulo in banco.SISTEMAS:
        grupo = [e for e in signos if e.get("sistema") == clave]
        if not grupo:
            continue
        partes += [f"# Parte {numero_parte} — {titulo}", ""]
        numero_parte += 1
        por_organo: dict[str, list[dict]] = defaultdict(list)
        for entidad in grupo:
            por_organo[entidad.get("organo") or "Otros"].append(entidad)
            ubicados.add(entidad["id"])
        for organo in sorted(por_organo):
            partes += [f"## {organo.replace('-', ' ').title()}", ""]
            for entidad in sorted(por_organo[organo], key=lambda e: e["titulo"]):
                partes.append(ficha_markdown(entidad, bibliografia))

    huerfanos = [e for e in signos if e["id"] not in ubicados]
    if huerfanos:
        partes += [f"# Parte {numero_parte} — Otros signos", ""]
        numero_parte += 1
        for entidad in sorted(huerfanos, key=lambda e: (e.get("organo") or "", e["titulo"])):
            partes.append(ficha_markdown(entidad, bibliografia))

    if casos:
        partes += [f"# Parte {numero_parte} — Casos", ""]
        for entidad in casos:
            partes.append(ficha_markdown(entidad, bibliografia))

    partes += ["# Créditos de imágenes", ""]
    for entidad in entidades:
        for medio in entidad.get("medios") or []:
            if medio.get("tipo") != "imagen":
                continue
            partes += [
                f"- **{entidad['titulo']}:** {medio['descripcion']}. "
                f"{medio['credito']}. [{medio['fuente']}]({medio['fuente_url']}). "
                f"[{medio['licencia_img']}]({medio['licencia_url']}).",
                "",
            ]
    return "\n".join(partes).rstrip() + "\n"


def portada(path: Path, version: str) -> None:
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2560" viewBox="0 0 1600 2560">
<rect width="1600" height="2560" fill="#071b2b"/>
<path d="M0 1840 C420 1640 720 2050 1110 1830 C1320 1710 1450 1680 1600 1750 L1600 2560 L0 2560 Z" fill="#0b7480"/>
<circle cx="1260" cy="360" r="170" fill="none" stroke="#69d3c5" stroke-width="20"/>
<text x="120" y="650" fill="#f4f0df" font-family="FreeSerif,serif" font-size="150">Biosemiótica</text>
<text x="120" y="825" fill="#f4f0df" font-family="FreeSerif,serif" font-size="150">del Cuerpo Vivo</text>
<text x="125" y="1020" fill="#69d3c5" font-family="FreeSerif,serif" font-size="72">Atlas de POCUS para el clínico</text>
<text x="125" y="2170" fill="#f4f0df" font-family="FreeSerif,serif" font-size="58">Dr. Alcy Edmundo Torres Guerrero</text>
<text x="125" y="2270" fill="#b9ddd8" font-family="FreeSerif,serif" font-size="40">BioSemiotics · {html.escape(version)}</text>
</svg>''',
        encoding="utf-8",
    )


def estilo(path: Path) -> None:
    path.write_text(
        """body{font-family:FreeSerif,serif;line-height:1.45;color:#17212b}h1{color:#075f69;page-break-before:always}h2{color:#16485a}h3{color:#071b2b}img{max-width:92%;max-height:70vh;display:block;margin:1.2em auto}.figure,figure{text-align:center}.caption,figcaption{font-size:.85em;color:#46535d}a{color:#075f69}blockquote{border-left:.3em solid #69d3c5;padding-left:1em}code{font-family:monospace}ul,ol{padding-left:1.5em}""",
        encoding="utf-8",
    )


def validar_epub(path: Path, entidades: int, figuras: int) -> str:
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
        if b"[?]" in textos:
            raise RuntimeError("se encontraron citas sin resolver ([?])")
        imagenes = [n for n in nombres if n.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".webp"))]
        if len(imagenes) < figuras + 1:  # figuras del banco + portada
            raise RuntimeError(
                f"faltan imágenes incrustadas: esperadas al menos {figuras + 1}, halladas {len(imagenes)}"
            )
    return f"contenedor EPUB3 válido ({entidades} entidades, {figuras} figuras)"


def main() -> int:
    args = argumentos()
    raiz = Path(__file__).resolve().parents[1]
    salida = args.salida if args.salida.is_absolute() else raiz / args.salida
    entidades = banco.cargar(raiz)
    if args.solo_publicados:
        entidades = [e for e in entidades if e.get("url")]
    if not entidades:
        raise RuntimeError("ninguna entidad cumple el alcance solicitado")

    figuras = imagenes(entidades, raiz)
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc no está instalado o no está disponible en PATH")

    bibliografia = banco.cargar_bibliografia(raiz / "refs.bib")
    version = version_git(raiz)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="epub-", dir=salida.parent) as temporal:
        trabajo = Path(temporal)
        md = trabajo / "atlas.md"
        css = trabajo / "epub.css"
        cover = trabajo / "portada.svg"
        md.write_text(manuscrito(entidades, bibliografia, version), encoding="utf-8")
        estilo(css)
        portada(cover, version)
        temporal_epub = trabajo / "atlas.epub"
        comando = [
            pandoc,
            str(md),
            "--from=gfm",
            "--to=epub3",
            f"--output={temporal_epub}",
            "--toc",
            "--toc-depth=3",
            "--epub-chapter-level=2",
            f"--css={css}",
            f"--epub-cover-image={cover}",
            f"--resource-path={raiz}",
            f"--metadata=title:{TITULO}",
            f"--metadata=subtitle:{SUBTITULO}",
            f"--metadata=author:{AUTOR}",
            "--metadata=lang:es",
            f"--metadata=date:{date.today().isoformat()}",
            f"--metadata=identifier:{DOI}",
            f"--metadata=publisher:{EDITORIAL}",
            f"--metadata=rights:{LICENCIA}",
        ]
        subprocess.run(comando, cwd=raiz, check=True)
        validacion = validar_epub(temporal_epub, len(entidades), len(figuras))
        os.replace(temporal_epub, salida)

    print(f"✓ Entidades incluidas: {len(entidades)}")
    print(f"✓ Figuras incrustadas: {len(figuras)}")
    print(f"✓ Versión: {version} · fecha: {date.today().isoformat()}")
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
