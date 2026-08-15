#!/usr/bin/env python3
"""Valida el estado de publicación entre fuente, índice y mapa maestro.

Uso general (CI):
  python scripts/verificar_publicacion.py

Verificación dirigida después de publicar en Ghost:
  python scripts/verificar_publicacion.py --id signo-ejemplo --url https://www.biosemiotics.net/ejemplo/

La comprobación web es deliberadamente opcional para que un fallo transitorio
de red no convierta la integridad local en una prueba inestable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

from build import cargar


DOMINIO_PUBLICO = "https://www.biosemiotics.net/"
CAMPOS_DESTACADA = (
    "archivo_local",
    "credito",
    "fuente",
    "fuente_url",
    "licencia_img",
    "licencia_url",
)


def error(errores: list[str], mensaje: str) -> None:
    errores.append(mensaje)


def validar_url(url: str) -> str | None:
    if not url.startswith(DOMINIO_PUBLICO):
        return f"no usa el dominio público {DOMINIO_PUBLICO}"
    if "/ghost/" in url or "/p/" in url:
        return "apunta al editor o a una vista previa, no al artículo público"
    if not url.endswith("/"):
        return "debe terminar en /"
    return None


def validar_mapa(mapa: str, entidades: list[dict], errores: list[str]) -> None:
    signos = [e for e in entidades if e["tipo"] == "signo"]
    publicados = [e for e in signos if e.get("url")]

    banco = re.search(
        r"Banco actual:\s*\*\*(\d+) entidades\*\*\s*"
        r"\((\d+) conceptos,\s*(\d+) signos y\s*(\d+) caso",
        mapa,
    )
    if not banco:
        error(errores, "mapa maestro: no se pudo leer el conteo del banco")
    else:
        conceptos = sum(e["tipo"] == "concepto" for e in entidades)
        casos = sum(e["tipo"] == "caso" for e in entidades)
        esperado = (len(entidades), conceptos, len(signos), casos)
        encontrado = tuple(map(int, banco.groups()))
        if encontrado != esperado:
            error(
                errores,
                f"mapa maestro: conteo del banco {encontrado} != {esperado}",
            )

    conteo = re.search(r"Signos publicados:\s*\*\*(\d+) de (\d+)\*\*", mapa)
    if not conteo:
        error(errores, "mapa maestro: no se pudo leer 'Signos publicados'")
    elif tuple(map(int, conteo.groups())) != (len(publicados), len(signos)):
        error(
            errores,
            "mapa maestro: 'Signos publicados' no coincide con las URLs del banco",
        )

    oleada = re.search(r"## 4\. OLEADA 2(?P<cuerpo>[\s\S]*?)### FAST", mapa)
    if not oleada:
        error(errores, "mapa maestro: no se pudo aislar la tabla de Oleada 2")
        return

    filas = [
        linea
        for linea in oleada.group("cuerpo").splitlines()
        if linea.startswith("|") and "---" not in linea and "| signo |" not in linea
    ]
    filas_publicadas = [f for f in filas if "✅ publicado" in f]
    filas_pendientes = [f for f in filas if "✍ escrito" in f]
    for fila in filas_publicadas:
        if not re.match(r"\| \[[^]]+\]\(https://www\.biosemiotics\.net/[^)]+/\) \|", fila):
            error(errores, f"mapa maestro: fila publicada sin enlace público: {fila}")
    for fila in filas_pendientes:
        if "](https://www.biosemiotics.net/" in fila:
            error(errores, f"mapa maestro: fila pendiente ya contiene URL: {fila}")

    resumen = re.search(
        r"Oleada 2 \*\*escrita completa: 8 de 8 signos\*\* "
        r"\((\d+) publicados, (\d+) esperando URL\)",
        mapa,
    )
    esperado_oleada = (len(filas_publicadas), len(filas_pendientes))
    if not resumen:
        error(errores, "mapa maestro: no se pudo leer el resumen de Oleada 2")
    elif tuple(map(int, resumen.groups())) != esperado_oleada:
        error(
            errores,
            f"mapa maestro: resumen de Oleada 2 no coincide con su tabla {esperado_oleada}",
        )


def validar_destacadas(raiz: Path, entidades: list[dict], errores: list[str]) -> None:
    for entidad in entidades:
        destacadas = [m for m in entidad.get("medios") or [] if m.get("destacada")]
        if len(destacadas) > 1:
            error(errores, f"{entidad['id']}: declara más de una imagen destacada")
        for medio in destacadas:
            if medio.get("tipo") != "imagen":
                error(errores, f"{entidad['id']}: el medio destacado no es imagen")
            for campo in CAMPOS_DESTACADA:
                if not medio.get(campo):
                    error(errores, f"{entidad['id']}: imagen destacada sin '{campo}'")
            archivo = medio.get("archivo_local")
            if archivo:
                ruta = (raiz / archivo).resolve()
                try:
                    ruta.relative_to(raiz.resolve())
                except ValueError:
                    error(errores, f"{entidad['id']}: imagen destacada fuera del banco")
                else:
                    if not ruta.is_file():
                        error(errores, f"{entidad['id']}: no existe {archivo}")


def comprobar_web(url: str) -> str | None:
    solicitud = urllib.request.Request(url, headers={"User-Agent": "biosemiotics-ci/1.0"})
    try:
        with urllib.request.urlopen(solicitud, timeout=20) as respuesta:
            if respuesta.status != 200:
                return f"respondió HTTP {respuesta.status}"
            if not respuesta.geturl().startswith(DOMINIO_PUBLICO):
                return f"redirigió fuera del dominio público: {respuesta.geturl()}"
    except Exception as exc:  # la opción es manual; aquí sí interesa el detalle
        return str(exc)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--id", dest="entidad_id")
    ap.add_argument("--url")
    ap.add_argument("--comprobar-web", action="store_true")
    args = ap.parse_args()

    raiz = args.raiz.resolve()
    entidades = cargar(raiz)
    por_id = {e["id"]: e for e in entidades}
    indice = json.loads((raiz / "build" / "index.json").read_text(encoding="utf-8"))
    fichas = {f["id"]: f for f in indice["fichas"]}
    errores: list[str] = []
    objetivo_verificado: str | None = None

    for entidad in entidades:
        url = entidad.get("url") or ""
        if url:
            problema = validar_url(url)
            if problema:
                error(errores, f"{entidad['id']}: {problema}")
        if fichas.get(entidad["id"], {}).get("url", "") != url:
            error(errores, f"{entidad['id']}: URL distinta entre fuente e índice")

    validar_destacadas(raiz, entidades, errores)
    validar_mapa(
        (raiz / "mapa-maestro-biosemiotics.md").read_text(encoding="utf-8"),
        entidades,
        errores,
    )

    if args.entidad_id:
        entidad = por_id.get(args.entidad_id)
        if not entidad:
            error(errores, f"no existe la entidad {args.entidad_id}")
        else:
            url = entidad.get("url") or ""
            if not url:
                error(errores, f"{args.entidad_id}: sigue sin URL pública")
            if args.url and url != args.url:
                error(errores, f"{args.entidad_id}: URL {url!r} != {args.url!r}")
            if args.comprobar_web and url:
                problema = comprobar_web(url)
                if problema:
                    error(errores, f"{args.entidad_id}: URL pública inválida: {problema}")
            objetivo_verificado = f"✓ {args.entidad_id}: {url}"
    elif args.url:
        error(errores, "--url requiere --id")

    if errores:
        for mensaje in errores:
            print(f"✗ {mensaje}", file=sys.stderr)
        return 1

    if objetivo_verificado:
        print(objetivo_verificado)
    print(
        f"✓ Publicación coherente: {len(entidades)} entidades, "
        f"{sum(bool(e.get('url')) for e in entidades)} URLs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
