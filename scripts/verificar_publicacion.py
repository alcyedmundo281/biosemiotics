#!/usr/bin/env python3
"""Valida el estado de publicación entre fuente, índice y mapa maestro.

Uso general (CI):
  python scripts/verificar_publicacion.py

Verificación dirigida después de publicar en Ghost:
  python scripts/verificar_publicacion.py --id signo-ejemplo --url https://www.biosemiotics.net/ejemplo/

Siempre se valida, sin red, que cada signo publicable enlace a su Reto
enfocado y que el índice permita enfocarlo (artículo → Reto → artículo).

Recorrido público, deliberadamente opcional para que un fallo transitorio de
red no convierta la integridad local en una prueba inestable:
  python scripts/verificar_publicacion.py --id signo-ejemplo --comprobar-web

Revisa el artículo (imagen destacada descargable, enlace al Reto, sección
«Dónde NO confiar»), que la página del Reto ejecute el script actual de
artefactos/reto.html y que el índice público ya tenga la ficha con su URL.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Optional

from banco import cargar, estado_publicacion, seleccionar_publicables
from bibliografia import cargar_bibliografia
from ghost import URL_RETO, cuerpo_ghost, huella_cuerpo_ghost
from indice import URL_PRIMARIA, URL_RESPALDO, XLINK_NS
from rutas import blindar_salida, desde_raiz, raiz_argumentos, raiz_desde_argumentos


DOMINIO_PUBLICO = "https://www.biosemiotics.net/"
CAMPOS_DESTACADA = (
    "archivo_local",
    "credito",
    "fuente",
    "fuente_url",
    "licencia_img",
    "licencia_url",
)


# Mismo filtro que aplica artefactos/reto-embed.html antes de reenviar ?signo=.
PATRON_ID_RETO = re.compile(r"^[a-z0-9áéíóúñü-]{3,60}$", re.IGNORECASE)
RETO_LOCAL = Path("artefactos") / "reto.html"


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
    publicados = seleccionar_publicables(signos, solo_publicados=True)

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

    La fuente LaTeX la genera Quarto dentro del proyecto (`build/quarto/`),
    junto a las imágenes que `qmd.py` copia ahí, así que la ruta va sin el
    `../` que necesitaba el generador propio para salir de `build/`.
    """
    build = raiz / "build"
    atlas = build / "atlas-inject.html"
    tex = build / "quarto" / "libro.tex"
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
            if relativa.as_posix() not in tex_txt:
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


def motivo_fuera_del_reto(ficha: dict) -> str | None:
    """Replica el filtro de carga de artefactos/reto.html para una ficha."""
    if ficha.get("tipo") != "signo" or not ficha.get("titulo"):
        return "no es un signo con título"
    if not (ficha.get("significado") or ficha.get("decision") or ficha.get("pregunta_clinica")):
        return "no tiene significado, decisión ni pregunta clínica"
    return None


def validar_recorrido_reto(
    publicables: list[dict],
    fichas: dict[str, dict],
    bibliografia: dict,
    errores: list[str],
) -> None:
    """Artículo → Reto enfocado → artículo, con lo que se versiona.

    El cuerpo de Ghost enlaza al Reto con el id del signo. Ese id debe pasar el
    filtro del embed, existir en el índice que lee el Reto y superar su filtro
    de carga; si no, el Reto abre el modo general. Que el script genere
    preguntas y devuelva al artículo lo prueba tests/test_reto.py ejecutándolo.
    """
    for entidad in publicables:
        if entidad["tipo"] != "signo":
            continue
        id_ = entidad["id"]
        if URL_RETO.format(id=id_) not in cuerpo_ghost(entidad, bibliografia):
            error(errores, f"{id_}: el cuerpo de Ghost no enlaza a su Reto enfocado")
        if not PATRON_ID_RETO.match(id_):
            error(errores, f"{id_}: el embed del Reto descarta ese id y abre el modo general")
        ficha = fichas.get(id_)
        if ficha is None:
            error(errores, f"{id_}: ausente del índice; el Reto enfocado caería al modo general")
            continue
        motivo = motivo_fuera_del_reto(ficha)
        if motivo:
            error(errores, f"{id_}: el Reto no puede enfocarlo: {motivo}")


def descargar(url: str) -> tuple[bytes, str, str]:
    """Cuerpo, URL final y tipo de contenido. urllib lanza ante 4xx/5xx."""
    solicitud = urllib.request.Request(url, headers={"User-Agent": "biosemiotics-ci/1.0"})
    with urllib.request.urlopen(solicitud, timeout=20) as respuesta:
        return (
            respuesta.read(),
            respuesta.geturl(),
            respuesta.headers.get("Content-Type", ""),
        )


def scripts_reto(texto: str) -> list[str]:
    return re.findall(r"<script>\s*(\(function\(\)\{[\s\S]*?)</script>", texto)


def meta(texto: str, propiedad: str) -> str | None:
    m = re.search(
        rf'<meta\s+property="{re.escape(propiedad)}"\s+content="([^"]*)"', texto
    )
    return html.unescape(m.group(1)) if m else None


def comprobar_recorrido_web(raiz: Path, entidad: dict) -> list[str]:
    """Recorre en la web pública lo que haría un lector después de publicar.

    Artículo (dominio, título, imagen destacada descargable y enlace al Reto),
    página del Reto (responde y ejecuta el mismo script que artefactos/reto.html)
    e índice público que ese script lee (la ficha está, con su URL, y el Reto
    puede enfocarla). No ejecuta el JavaScript: su lógica la cubre test_reto.py.
    """
    problemas: list[str] = []
    url = entidad.get("url") or ""
    try:
        cuerpo, final, _ = descargar(url)
    except Exception as exc:  # la opción es manual; aquí sí interesa el detalle
        return [f"artículo: {exc}"]
    if not final.startswith(DOMINIO_PUBLICO):
        return [f"artículo: redirigió fuera del dominio público: {final}"]
    articulo = cuerpo.decode("utf-8", "replace")

    # El título de Ghost puede ser más largo que el de la ficha: no se compara.
    if not meta(articulo, "og:title"):
        problemas.append("artículo: sin título (og:title)")

    imagen = meta(articulo, "og:image")
    if not imagen:
        problemas.append("artículo: sin imagen destacada (og:image)")
    else:
        try:
            _, _, tipo = descargar(imagen)
            if not tipo.startswith("image/"):
                problemas.append(f"artículo: la imagen destacada responde {tipo!r}")
        except Exception as exc:
            problemas.append(f"artículo: la imagen destacada no descarga: {exc}")

    if entidad["tipo"] != "signo":
        return problemas

    id_ = entidad["id"]
    enlace = URL_RETO.format(id=id_)
    enlace_codificado = URL_RETO.format(id=urllib.parse.quote(id_))
    texto = html.unescape(articulo)
    if enlace not in texto and enlace_codificado not in texto:
        problemas.append(f"artículo: no enlaza a {enlace}")
    encabezados = re.findall(r"<h2[^>]*>([\s\S]*?)</h2>", texto)
    if not any(re.match(r"\s*dónde no confiar", h, re.IGNORECASE) for h in encabezados):
        problemas.append("artículo: falta la sección «Dónde NO confiar»")

    try:
        cuerpo, final, _ = descargar(enlace_codificado)
        if not final.startswith(DOMINIO_PUBLICO):
            problemas.append(f"Reto: redirigió fuera del dominio público: {final}")
        local = scripts_reto((raiz / RETO_LOCAL).read_text(encoding="utf-8"))
        publico = scripts_reto(cuerpo.decode("utf-8", "replace"))
        if not local or local[0] not in publico:
            problemas.append(
                f"Reto: la página pública no ejecuta el script actual de "
                f"{RETO_LOCAL.as_posix()}; hay que repegarlo en Ghost"
            )
    except Exception as exc:
        problemas.append(f"Reto: {exc}")

    fichas = None
    for fuente in (URL_PRIMARIA, URL_RESPALDO):
        try:
            datos = json.loads(descargar(fuente)[0].decode("utf-8"))
            fichas = {f["id"]: f for f in datos.get("fichas", [])}
            break
        except Exception as exc:
            problemas.append(f"índice público {fuente}: {exc}")
    if fichas is not None:
        ficha = fichas.get(id_)
        if ficha is None:
            problemas.append(
                "índice público: la ficha aún no está; el Reto enfocado caerá "
                "al modo general hasta que se fusione y se refresque el índice"
            )
        else:
            if ficha.get("url") != url:
                problemas.append(
                    f"índice público: URL {ficha.get('url')!r} != {url!r}; el Reto "
                    "no devolvería al artículo"
                )
            motivo = motivo_fuera_del_reto(ficha)
            if motivo:
                problemas.append(f"índice público: el Reto no puede enfocarlo: {motivo}")
    return problemas


def main() -> int:
    blindar_salida()
    ap = argparse.ArgumentParser()
    raiz_argumentos(ap)
    ap.add_argument("--id", dest="entidad_id")
    ap.add_argument("--url")
    ap.add_argument("--comprobar-web", action="store_true")
    ap.add_argument(
        "--verificar-derivados",
        action="store_true",
        help="valida atlas, JSON-LD, XML JATS experimental e imágenes en LaTeX",
    )
    ap.add_argument(
        "--epub",
        type=Path,
        help="además verifica que las imágenes publicadas estén incrustadas en el EPUB",
    )
    args = ap.parse_args()

    raiz = raiz_desde_argumentos(ap, args)
    entidades = cargar(raiz)
    publicables = seleccionar_publicables(entidades)
    bibliografia = cargar_bibliografia(raiz / "refs.bib")
    por_id = {e["id"]: e for e in entidades}
    indice = json.loads((raiz / "build" / "index.json").read_text(encoding="utf-8"))
    fichas = {f["id"]: f for f in indice["fichas"]}
    errores: list[str] = []
    esperados = {e["id"] for e in publicables}
    if set(fichas) != esperados:
        error(errores, f"índice: faltan {sorted(esperados - set(fichas))}; "
                      f"sobran {sorted(set(fichas) - esperados)}")
    for e in publicables:
        f = fichas.get(e["id"], {})
        for campo, valor in (("estado", estado_publicacion(e)),
                             ("fecha_revision", str(e["fecha_revision"]) if e.get("fecha_revision") else None),
                             ("ghost_id", e.get("ghost_id")),
                             ("ghost_sha256", huella_cuerpo_ghost(e, bibliografia))):
            if f.get(campo) != valor:
                error(errores, f"{e['id']}: {campo} distinto entre fuente e índice")
    objetivo_verificado: str | None = None

    for entidad in entidades:
        url = entidad.get("url") or ""
        if url:
            problema = validar_url(url)
            if problema:
                error(errores, f"{entidad['id']}: {problema}")
        if fichas.get(entidad["id"], {}).get("url", "") != url:
            error(errores, f"{entidad['id']}: URL distinta entre fuente e índice")

    validar_recorrido_reto(publicables, fichas, bibliografia, errores)
    validar_destacadas(raiz, entidades, errores)
    validar_mapa(
        (raiz / "mapa-maestro-biosemiotics.md").read_text(encoding="utf-8"),
        entidades,
        errores,
    )
    if args.verificar_derivados or args.epub:
        epub = args.epub
        if epub is not None and not epub.is_absolute():
            epub = desde_raiz(raiz, epub)
        validar_derivados(raiz, publicables, errores, epub)

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
                for problema in comprobar_recorrido_web(raiz, entidad):
                    error(errores, f"{args.entidad_id}: web pública: {problema}")
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
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        sys.exit(str(exc))
