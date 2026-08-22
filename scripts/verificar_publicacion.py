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
import hashlib
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Optional

from build import cargar
from indice import URL_PRIMARIA, URL_RESPALDO, XLINK_NS


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


def validar_derivados(
    raiz: Path,
    entidades: list[dict],
    errores: list[str],
    epub: Optional[Path] = None,
) -> None:
    """Comprueba URL e imágenes en cada salida posterior a Ghost.

    Los binarios EPUB/PDF no se versionan. El EPUB se inspecciona cuando el
    llamador entrega `--epub`; LuaLaTeX se valida compilando `libro.tex` en CI.
    Aquí se comprueba antes que el .tex apunte exactamente a `archivo_local`.
    """
    build = raiz / "build"
    atlas = build / "atlas-inject.html"
    tex = build / "libro.tex"
    for ruta in (atlas, tex):
        if not ruta.is_file():
            error(errores, f"falta derivado {ruta.relative_to(raiz)}")
    atlas_txt = atlas.read_text(encoding="utf-8") if atlas.is_file() else ""
    for url_indice in (URL_PRIMARIA, URL_RESPALDO):
        if url_indice not in atlas_txt:
            error(errores, f"atlas-inject.html no contiene {url_indice}")
    tex_txt = tex.read_text(encoding="utf-8") if tex.is_file() else ""

    huellas_epub: Optional[set[bytes]] = None
    if epub is not None:
        if not epub.is_file():
            error(errores, f"no existe el EPUB {epub}")
        else:
            try:
                with zipfile.ZipFile(epub) as zf:
                    huellas_epub = {
                        hashlib.sha256(zf.read(nombre)).digest()
                        for nombre in zf.namelist()
                        if Path(nombre).suffix.lower()
                        in (".png", ".jpg", ".jpeg", ".svg", ".webp")
                    }
            except (OSError, zipfile.BadZipFile) as exc:
                error(errores, f"EPUB inválido {epub}: {exc}")

    for entidad in entidades:
        url = entidad.get("url") or ""
        if not url:
            continue
        jsonld_path = build / "jsonld" / f"{entidad['id']}.json"
        jats_path = build / "jats" / f"{entidad['id']}.xml"
        if not jsonld_path.is_file():
            error(errores, f"{entidad['id']}: falta JSON-LD")
        else:
            datos = json.loads(jsonld_path.read_text(encoding="utf-8"))
            if datos.get("url") != url or datos.get("mainEntityOfPage") != url:
                error(errores, f"{entidad['id']}: URL ausente o distinta en JSON-LD")
        if not jats_path.is_file():
            error(errores, f"{entidad['id']}: falta JATS")
        else:
            try:
                raiz_xml = ET.fromstring(jats_path.read_text(encoding="utf-8"))
                self_uri = raiz_xml.find("./front/article-meta/self-uri")
                href = None if self_uri is None else self_uri.get(
                    f"{{{XLINK_NS}}}href"
                )
                if href != url:
                    error(errores, f"{entidad['id']}: URL ausente o distinta en JATS")
            except ET.ParseError as exc:
                error(errores, f"{entidad['id']}: JATS inválido: {exc}")

        for medio in entidad.get("medios") or []:
            if medio.get("tipo") != "imagen" or not medio.get("archivo_local"):
                continue
            relativa = Path(medio["archivo_local"])
            token_tex = "../" + relativa.as_posix()
            if token_tex not in tex_txt:
                error(
                    errores,
                    f"{entidad['id']}: {relativa.as_posix()} no está en libro.tex",
                )
            if huellas_epub is not None:
                original = raiz / relativa
                if original.is_file():
                    huella = hashlib.sha256(original.read_bytes()).digest()
                    if huella not in huellas_epub:
                        error(
                            errores,
                            f"{entidad['id']}: {relativa.as_posix()} no está incrustada en EPUB",
                        )


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
    ap.add_argument(
        "--verificar-derivados",
        action="store_true",
        help="valida atlas, JSON-LD, JATS y referencias de imagen en LaTeX",
    )
    ap.add_argument(
        "--epub",
        type=Path,
        help="además verifica que las imágenes publicadas estén incrustadas en el EPUB",
    )
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
    if args.verificar_derivados or args.epub:
        epub = args.epub
        if epub is not None and not epub.is_absolute():
            epub = raiz / epub
        validar_derivados(raiz, entidades, errores, epub)

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
