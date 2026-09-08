#!/usr/bin/env python3
"""
Crea una entidad nueva a partir de la plantilla correspondiente.

  python3 nuevo.py signo lineas-b "Líneas B (pulmón húmedo)"
  python3 nuevo.py concepto ecogenicidad "El lenguaje de la ecogenicidad"
  python3 nuevo.py caso caso-02-disnea "El disneico: ¿húmedo o seco?"

El archivo queda con el front-matter completo y TODO: en los campos a llenar.
Nunca deja campos fuera: los campos obligatorios ausentes son el error #1 del banco.
"""
import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent
from rutas import raiz_argumentos, raiz_desde_argumentos
CARPETA = {"concepto": "conceptos", "signo": "signos", "caso": "casos"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    raiz_argumentos(ap)
    ap.add_argument("tipo", choices=tuple(CARPETA))
    ap.add_argument("ident")
    ap.add_argument("titulo", nargs="+")
    args = ap.parse_args()
    raiz = raiz_desde_argumentos(ap, args)
    tipo, ident, titulo = args.tipo, args.ident, " ".join(args.titulo)
    if tipo not in CARPETA:
        sys.exit(f"tipo debe ser: {', '.join(CARPETA)}")

    # Los signos llevan prefijo — es la convención del grafo.
    if tipo == "signo" and not ident.startswith("signo-"):
        ident = f"signo-{ident}"

    plantilla = BASE / "assets" / f"plantilla-{tipo}.qmd"
    if not plantilla.exists():
        sys.exit(f"No encuentro {plantilla}")

    destino = raiz / CARPETA[tipo] / f"{ident.removeprefix('signo-')}.qmd"
    if destino.exists():
        sys.exit(f"Ya existe: {destino}")
    destino.parent.mkdir(parents=True, exist_ok=True)

    txt = (plantilla.read_text(encoding="utf-8")
           .replace("{{ID}}", ident)
           .replace("{{TITULO}}", titulo))
    destino.write_text(txt, encoding="utf-8")

    print(f"✓ {destino.relative_to(raiz)}")
    print("\nLlena los TODO: y corre  python3 scripts/build.py  para validar.")
    print("Queda en estado: borrador y fuera de los derivados públicos.")
    print("Tras aprobación editorial, registra estado: revisado y fecha_revision.")
    if tipo == "signo":
        print("\nRecuerda: 'falsos_positivos' NO es opcional. Un signo sin límites")
        print("enseña a reconocer sin enseñar a dudar.")
    if tipo == "caso":
        print("\nRecuerda: una sola decisión semiótica. Si hay dos bifurcaciones,")
        print("son dos casos. Y consentimiento: pendiente hasta que esté documentado.")


if __name__ == "__main__":
    main()
