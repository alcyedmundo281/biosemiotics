#!/usr/bin/env python3
"""Compila el libro en PDF desde el proyecto Quarto.

    python scripts/libro.py --salida build/libro.pdf [--solo-publicados]

Sustituye a `build.build_latex()`, que emitía LaTeX a mano: ~300 líneas de
escape, conversión de markdown y armado de figuras que había que mantener en
paralelo al ensamblado del EPUB. Ahora las dos ediciones salen del mismo
proyecto `build/quarto/` que genera `scripts/qmd.py`, así que el libro impreso
y el electrónico no pueden divergir.

La fuente LaTeX no es un intermedio desechable: `keep-tex` la deja en
`build/quarto/libro.tex`, junto a las imágenes que `qmd.py` copió al proyecto.
Ese directorio compila tal cual —`lualatex libro.tex` desde ahí— sin depender
del checkout, que es justo lo que promete el ZIP de `paquete_latex.py`. El
generador anterior escribía rutas `../assets/...` que solo resolvían desde
`build/`.

Requiere Quarto y LuaLaTeX. A diferencia del EPUB no hay respaldo con pandoc a
secas: el preámbulo (fontspec con FreeSerif para `≥ → ±`, babel en español,
biblatex) lo arma Quarto, y reconstruirlo a mano sería volver justo a lo que
este script jubila.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import banco
import qmd
from rutas import desde_raiz, raiz_argumentos, resolver_raiz

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    raiz_argumentos(parser)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument(
        "--solo-publicados",
        action="store_true",
        help="incluye únicamente fichas con URL pública de Ghost",
    )
    parser.add_argument(
        "--proyecto",
        type=Path,
        default=Path("build/quarto"),
        help="dónde se deja el proyecto Quarto generado",
    )
    return parser.parse_args()


def validar_libro(tex: Path, pdf: Path, figuras: list, enlaces_ghost: int) -> str:
    """Comprueba el .tex y el PDF antes de darlos por buenos.

    El grueso de la verificación va contra el `.tex` a propósito: es texto, se
    inspecciona entero sin dependencias, y todo lo que falte ahí falta también
    en el PDF. Del PDF se comprueba que exista y que no sea un cascarón.
    """
    if not tex.is_file():
        raise RuntimeError(f"Quarto no dejó la fuente LaTeX en {tex}")
    fuente = tex.read_text(encoding="utf-8", errors="replace")

    comprobaciones = {
        "citas sin resolver ([?])": "[?]" not in fuente,
        "marcadores TODO": "TODO" not in fuente,
        "DOI": qmd.DOI in fuente,
        "ISBN pendiente": "ISBN EPUB: pendiente" in fuente,
        "aviso educativo": "material educativo" in fuente.lower(),
        "bibliografía final": "Bibliografía" in fuente,
        "créditos de imágenes": "Créditos de imágenes" in fuente,
        "fuente FreeSerif": "FreeSerif" in fuente,
    }
    fallos = [nombre for nombre, correcto in comprobaciones.items() if not correcto]
    if fallos:
        raise RuntimeError("validación editorial del libro fallida: " + ", ".join(fallos))

    for simbolo in ("≥", "→", "±"):
        if simbolo not in fuente:
            raise RuntimeError(
                f"el símbolo Unicode {simbolo!r} no llegó al LaTeX: revisa que "
                "el preámbulo siga usando fontspec con FreeSerif"
            )

    # Cada figura entra por el `archivo_local` declarado, la misma autoridad que
    # usan el EPUB y Ghost. Una ruta inventada por el renderizador sería una
    # atribución rota.
    faltantes = [
        medio["archivo_local"]
        for _, medio, _ in figuras
        if medio["archivo_local"] not in fuente
    ]
    if faltantes:
        raise RuntimeError(
            "figuras ausentes del LaTeX: " + ", ".join(sorted(set(faltantes)))
        )

    enlaces = fuente.count("https://www.biosemiotics.net/")
    if enlaces < enlaces_ghost:
        raise RuntimeError(
            f"faltan enlaces al artículo publicado: {enlaces} de {enlaces_ghost}"
        )

    if not pdf.is_file() or pdf.stat().st_size < 500 * 1024:
        raise RuntimeError("el PDF no existe o es sospechosamente pequeño")
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise RuntimeError("el archivo generado no es un PDF")

    return f"LaTeX y PDF coherentes ({len(figuras)} figuras, {enlaces_ghost} enlaces)"


def main() -> int:
    args = argumentos()
    raiz = resolver_raiz(args.raiz)
    salida = desde_raiz(raiz, args.salida)
    proyecto = desde_raiz(raiz, args.proyecto)

    quarto = shutil.which("quarto")
    if not quarto:
        raise RuntimeError(
            "quarto no está en PATH. El PDF se compila desde el proyecto Quarto; "
            "instálalo desde https://quarto.org/docs/get-started/"
        )
    if not shutil.which("lualatex"):
        raise RuntimeError(
            "lualatex no está en PATH. El banco escribe ≥ → ± y solo LuaLaTeX "
            "con fontspec los compone sin parchear cada glifo"
        )

    entidades = banco.cargar(raiz)
    entidades = banco.seleccionar_publicables(entidades, args.solo_publicados)
    if not entidades:
        raise RuntimeError("ninguna entidad cumple el alcance solicitado")

    informe = qmd.generar(entidades, raiz, proyecto)
    producido = qmd.render(quarto, proyecto, "pdf", ".pdf")
    tex = proyecto / "libro.tex"

    enlaces_ghost = sum(1 for e in entidades if e.get("url"))
    validacion = validar_libro(tex, producido, informe["figuras_detalle"], enlaces_ghost)

    salida.parent.mkdir(parents=True, exist_ok=True)
    os.replace(producido, salida)

    print(f"✓ Motor: quarto ({quarto}) + lualatex")
    print(f"✓ Proyecto: {proyecto.relative_to(raiz)} "
          f"({informe['capitulos']} capítulos, {len(informe['partes'])} partes)")
    print(f"✓ Entidades incluidas: {informe['entidades']}")
    print(f"✓ Figuras: {informe['figuras']}")
    print(f"✓ Enlaces al artículo en Ghost: {enlaces_ghost}")
    print(f"✓ Fuente LaTeX: {tex.relative_to(raiz)} (compila desde su directorio)")
    print(f"✓ Tamaño: {salida.stat().st_size:,} bytes")
    print(f"✓ Validación interna: {validacion}")
    print(f"✓ Salida: {salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, KeyError, ValueError, OSError) as exc:
        print(f"ERROR LIBRO: {exc}", file=sys.stderr)
        raise SystemExit(1)
