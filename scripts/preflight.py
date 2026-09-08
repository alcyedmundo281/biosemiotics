#!/usr/bin/env python3
"""Comprueba el entorno y la coherencia del banco antes de editar o publicar.

Uso diario, sin escribir derivados::

    python scripts/preflight.py

Antes de generar EPUB, PDF y el paquete LuaLaTeX::

    python scripts/preflight.py --publicacion
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Mapping, Sequence

from rutas import raiz_argumentos, raiz_desde_argumentos

PYTHON_MINIMO = (3, 9)
PYYAML_REQUERIDO = "6.0.3"
ARCHIVOS_REQUERIDOS = (
    "refs.bib",
    "mapa-maestro-biosemiotics.md",
    "build/index.json",
    "scripts/build.py",
    "scripts/indice.py",
)
DIRECTORIOS_REQUERIDOS = ("conceptos", "signos", "casos")
HERRAMIENTAS_PUBLICACION = ("quarto", "lualatex", "java", "rsvg-convert")


def comprobar_python(version: Sequence[int]) -> list[str]:
    if tuple(version[:2]) < PYTHON_MINIMO:
        actual = ".".join(map(str, version[:3]))
        return [f"Python {actual}; se requiere Python 3.9 o posterior"]
    return []


def comprobar_pyyaml(
    version_distribucion: Callable[[str], str] = importlib.metadata.version,
    importar: Callable[[str], object] = importlib.import_module,
) -> list[str]:
    try:
        version = version_distribucion("PyYAML")
        modulo = importar("yaml")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        return ["falta PyYAML; ejecuta `python -m pip install -r requirements.txt`"]
    if version != PYYAML_REQUERIDO:
        return [
            f"PyYAML {version}; requirements.txt fija {PYYAML_REQUERIDO}. "
            "Ejecuta `python -m pip install -r requirements.txt`"
        ]
    if not callable(getattr(modulo, "safe_load", None)):
        return ["el módulo yaml cargado no expone safe_load; reinstala requirements.txt"]
    return []


def comprobar_estructura(raiz: Path) -> list[str]:
    errores = [f"falta {ruta}/" for ruta in DIRECTORIOS_REQUERIDOS
               if not (raiz / ruta).is_dir()]
    errores.extend(f"falta {ruta}" for ruta in ARCHIVOS_REQUERIDOS
                   if not (raiz / ruta).is_file())
    return errores


def comprobar_herramientas_publicacion(
    buscar: Callable[[str], str | None] = shutil.which,
    entorno: Mapping[str, str] = os.environ,
) -> list[str]:
    errores = [f"falta `{nombre}` en PATH" for nombre in HERRAMIENTAS_PUBLICACION
               if not buscar(nombre)]
    epubcheck = entorno.get("EPUBCHECK_JAR")
    if epubcheck:
        if not Path(epubcheck).is_file():
            errores.append(f"EPUBCHECK_JAR no existe: {epubcheck}")
    elif not buscar("epubcheck"):
        errores.append("falta epubcheck o la variable EPUBCHECK_JAR")
    return errores


def comprobar_banco(raiz: Path) -> tuple[list[str], str]:
    from banco import cargar
    from configuracion import RELS
    from validacion import validar

    entidades = cargar(raiz)
    aristas = [
        {"origen": e["id"], "destino": destino, "clase": clase}
        for e in entidades for clase in RELS for destino in (e.get(clase) or [])
    ]
    errores, alertas = validar(entidades, aristas, raiz, permitir_borradores=True)
    detalle = f"{len(entidades)} entidades, {len(aristas)} relaciones"
    if alertas:
        detalle += f", {len(alertas)} alertas de borrador"
    return errores, detalle


def comprobar_indice(raiz: Path) -> tuple[list[str], str]:
    comando = [
        sys.executable,
        str(raiz / "scripts" / "verificar_publicacion.py"),
        "--raiz",
        str(raiz),
    ]
    resultado = subprocess.run(
        comando,
        cwd=raiz,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    salida = (resultado.stdout or resultado.stderr).strip()
    if resultado.returncode:
        return [salida or "verificar_publicacion.py falló sin mensaje"], ""
    return [], salida


def argumentos() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(description=__doc__)
    raiz_argumentos(parser)
    parser.add_argument(
        "--publicacion",
        action="store_true",
        help="exige además Quarto, LuaLaTeX, Java, rsvg-convert y EPUBCheck",
    )
    return parser, parser.parse_args()


def main() -> int:
    parser, args = argumentos()
    raiz = raiz_desde_argumentos(parser, args)
    comprobaciones = [
        ("Python", comprobar_python(sys.version_info)),
        ("PyYAML", comprobar_pyyaml()),
        ("estructura", comprobar_estructura(raiz)),
    ]
    if args.publicacion:
        comprobaciones.append(
            ("herramientas de publicación", comprobar_herramientas_publicacion())
        )

    errores = []
    for nombre, fallos in comprobaciones:
        if fallos:
            errores.extend(f"{nombre}: {fallo}" for fallo in fallos)
        else:
            print(f"✓ {nombre}")
    if errores:
        for fallo in errores:
            print(f"✗ {fallo}", file=sys.stderr)
        return 1

    errores_banco, detalle_banco = comprobar_banco(raiz)
    if errores_banco:
        for fallo in errores_banco:
            print(f"✗ banco: {fallo}", file=sys.stderr)
        return 1
    print(f"✓ banco: {detalle_banco}")

    errores_indice, detalle_indice = comprobar_indice(raiz)
    if errores_indice:
        for fallo in errores_indice:
            print(f"✗ índice: {fallo}", file=sys.stderr)
        return 1
    print(detalle_indice)
    perfil = "publicación" if args.publicacion else "banco"
    print(f"✓ Preflight listo: perfil {perfil}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
