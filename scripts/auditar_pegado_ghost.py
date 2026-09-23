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
try:
    from rutas import blindar_salida, desde_raiz, raiz_argumentos, raiz_desde_argumentos
except ModuleNotFoundError:  # importado como scripts.auditar_pegado_ghost
    from .rutas import blindar_salida, desde_raiz, raiz_argumentos, raiz_desde_argumentos


def cuerpo_markdown(texto: str) -> str:
    return re.sub(r"\A---\r?\n[\s\S]*?\r?\n---\r?\n", "", texto).strip()


def cabecera_canonica(texto: str) -> dict:
    """Campos de la cabecera de build/ghost: title, excerpt, imagen, alt, pie.

    build.py los escribe codificados en JSON, una línea cada uno, así que no
    hace falta un analizador YAML para leerlos.
    """
    bloque = re.match(r"\A---\r?\n([\s\S]*?)\r?\n---\r?\n", texto)
    campos = {}
    for linea in (bloque.group(1).splitlines() if bloque else []):
        clave, separador, valor = linea.partition(": ")
        if separador and valor.startswith(('"', "[")):
            campos[clave.strip()] = json.loads(valor)
    return campos


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


def auditar_pie(pie: str, pie_esperado: str) -> list[str]:
    """El pie observado debe ser el canónico, exactamente una vez."""
    errores: list[str] = []
    observado = normalizar(pie)
    esperado = normalizar(pie_esperado)
    if observado != esperado:
        errores.append("el pie no coincide exactamente con la atribución esperada")
    if observado and observado.count(esperado) > 1:
        errores.append("la atribución del pie está duplicada")
    return errores


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
        errores.extend(auditar_pie(pie, pie_esperado))
    return errores


def main() -> int:
    blindar_salida()
    ap = argparse.ArgumentParser()
    raiz_argumentos(ap)
    ap.add_argument("--canon", type=Path, required=True, help="Markdown de build/ghost")
    ap.add_argument("--captura", type=Path, help="texto visible extraído del editor")
    ap.add_argument("--pie", default="", help="pie observado en Ghost")
    ap.add_argument("--pie-esperado", default="")
    args = ap.parse_args()
    raiz = raiz_desde_argumentos(ap, args)
    canon = desde_raiz(raiz, args.canon)
    captura = desde_raiz(raiz, args.captura) if args.captura else None

    texto = canon.read_text(encoding="utf-8")
    cuerpo = cuerpo_markdown(texto)
    cabecera = cabecera_canonica(texto)
    resultado = huella(cuerpo)
    # Lo que hay que pegar en Ghost, tal cual: el publicador copia de aquí en
    # vez de componer el pie a mano, que es como salía duplicado o distinto.
    for clave in ("excerpt", "tags", "imagen", "alt", "pie"):
        if cabecera.get(clave):
            resultado[f"{clave}_esperado"] = cabecera[clave]
    # Sin --pie-esperado explícito, el esperado es el pie canónico.
    pie_esperado = args.pie_esperado or (cabecera.get("pie", "") if args.pie else "")
    if args.pie and not pie_esperado:
        print("✗ --pie sin pie canónico: la ficha no declara imagen destacada",
              file=sys.stderr)
        return 1
    if captura or args.pie:
        if captura:
            errores = auditar(
                cuerpo, captura.read_text(encoding="utf-8"), args.pie, pie_esperado)
        else:
            errores = auditar_pie(args.pie, pie_esperado)
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
