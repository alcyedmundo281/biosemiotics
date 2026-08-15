#!/usr/bin/env python3
"""Genera una huella del cuerpo Ghost y detecta pegados duplicados.

El editor de Ghost es un ``contenteditable`` gestionado por Lexical: volver a
usar ``fill`` sobre un cuerpo no vacío puede anexar el Markdown en vez de
reemplazarlo. Esta auditoría compara una captura de texto del editor con los
encabezados y cierres únicos del Markdown canónico.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def cuerpo_markdown(texto: str) -> str:
    return re.sub(r"\A---\r?\n[\s\S]*?\r?\n---\r?\n", "", texto).strip()


def normalizar(texto: str) -> str:
    texto = re.sub(r"[`*_>#\[\]()]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def encabezados(cuerpo: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^#{2,6}\s+(.+)$", cuerpo, re.M)]


def huella(cuerpo: str) -> dict:
    limpio = normalizar(cuerpo)
    titulos = encabezados(cuerpo)
    return {
        "sha256": hashlib.sha256(cuerpo.encode("utf-8")).hexdigest(),
        "caracteres_normalizados": len(limpio),
        "palabras_aproximadas": len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b", limpio)),
        "encabezados": titulos,
        "inicio": titulos[0] if titulos else "",
        "cierre": titulos[-1] if titulos else "",
    }


def auditar(cuerpo: str, captura: str, pie: str = "", pie_esperado: str = "") -> list[str]:
    errores: list[str] = []
    vista = normalizar(captura)
    base = normalizar(cuerpo)
    for titulo in encabezados(cuerpo):
        apariciones = len(re.findall(re.escape(normalizar(titulo)), vista, re.I))
        if apariciones != 1:
            errores.append(f"encabezado {titulo!r}: {apariciones} apariciones (esperada 1)")

    # Una captura casi dos veces más larga es la señal secundaria que protege
    # incluso artículos sin encabezados o con un título repetido legítimamente.
    if base and len(vista) > len(base) * 1.65:
        errores.append(
            f"cuerpo demasiado largo: {len(vista)} caracteres normalizados "
            f"frente a {len(base)} canónicos"
        )

    if pie_esperado:
        observado = normalizar(pie)
        esperado = normalizar(pie_esperado)
        if observado != esperado:
            errores.append("el pie no coincide exactamente con la atribución esperada")
        if observado and observado.count(esperado) != 1:
            errores.append("la atribución del pie está duplicada")
    return errores


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canon", type=Path, required=True, help="Markdown de build/ghost")
    ap.add_argument("--captura", type=Path, help="texto visible extraído del editor")
    ap.add_argument("--pie", default="", help="pie observado en Ghost")
    ap.add_argument("--pie-esperado", default="")
    args = ap.parse_args()

    cuerpo = cuerpo_markdown(args.canon.read_text(encoding="utf-8"))
    resultado = huella(cuerpo)
    if args.captura:
        errores = auditar(
            cuerpo,
            args.captura.read_text(encoding="utf-8"),
            args.pie,
            args.pie_esperado,
        )
        resultado["errores"] = errores
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        if errores:
            for mensaje in errores:
                print(f"✗ {mensaje}", file=sys.stderr)
            return 1
    else:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
