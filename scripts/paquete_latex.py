#!/usr/bin/env python3
"""Empaqueta una fuente LuaLaTeX autocontenida con todos sus assets."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


INSTRUCCIONES = """# Fuente LuaLaTeX de BioSemiotics

Este paquete conserva la estructura de rutas esperada por `build/libro.tex`.

```bash
cd build
lualatex -halt-on-error -interaction=nonstopmode libro.tex
biber libro
lualatex -halt-on-error -interaction=nonstopmode libro.tex
lualatex -halt-on-error -interaction=nonstopmode libro.tex
```

Requiere LuaLaTeX, Biber, FreeSerif, biblatex, babel-spanish, graphicx,
adjustbox, tabularx, array, hyperref y los paquetes LaTeX recomendados.
"""


def crear_paquete(raiz: Path, salida: Path) -> tuple[int, int]:
    raiz = raiz.resolve()
    tex = raiz / "build" / "libro.tex"
    bib = raiz / "refs.bib"
    assets = raiz / "assets"
    faltantes = [p for p in (tex, bib, assets) if not p.exists()]
    if faltantes:
        raise RuntimeError(
            "faltan componentes del paquete: "
            + ", ".join(str(p.relative_to(raiz)) for p in faltantes)
        )

    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="biosemiotics-latex-", suffix=".zip", dir=salida.parent, delete=False
    ) as temporal:
        temporal_path = Path(temporal.name)
    try:
        archivos = [tex, bib] + sorted(p for p in assets.rglob("*") if p.is_file())
        with zipfile.ZipFile(
            temporal_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as zf:
            prefijo = Path("biosemiotics-latex")
            for archivo in archivos:
                zf.write(archivo, (prefijo / archivo.relative_to(raiz)).as_posix())
            zf.writestr((prefijo / "COMPILAR.md").as_posix(), INSTRUCCIONES)

        with zipfile.ZipFile(temporal_path) as zf:
            error = zf.testzip()
            if error:
                raise RuntimeError(f"entrada ZIP corrupta: {error}")
            nombres = set(zf.namelist())
            esperados = {
                "biosemiotics-latex/build/libro.tex",
                "biosemiotics-latex/refs.bib",
                "biosemiotics-latex/COMPILAR.md",
            }
            if not esperados.issubset(nombres):
                raise RuntimeError("el ZIP no conserva la estructura compilable")
        os.replace(temporal_path, salida)
    finally:
        temporal_path.unlink(missing_ok=True)

    return len(archivos), salida.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--salida", type=Path, default=Path("build/biosemiotics-latex.zip")
    )
    parser.add_argument(
        "--raiz", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    salida = args.salida if args.salida.is_absolute() else args.raiz / args.salida
    archivos, bytes_ = crear_paquete(args.raiz, salida)
    print(f"✓ Paquete LuaLaTeX: {archivos} archivos · {bytes_:,} bytes")
    print(f"✓ Salida: {salida}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"ERROR PAQUETE LATEX: {exc}")
        raise SystemExit(1)
