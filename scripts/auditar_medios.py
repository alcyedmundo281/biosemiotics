#!/usr/bin/env python3
"""
auditar_medios.py — completa la trazabilidad de las imágenes VERIFICÁNDOLA.

Muchas fichas antiguas declaran una imagen con crédito y licencia pero sin los
tres campos que hacen auditable esa atribución: `archivo_local`, `licencia_url`
y `fuente_url`. Sin ellos, el generador de ePub no puede incrustar la figura con
su atribución, y el contrato dice que debe FALLAR, no inventar la ruta.

Este script no inventa nada. Resuelve cada campo por una vía comprobable y, si
alguna no se puede comprobar, la deja vacía y la reporta:

  archivo_local  se busca en assets/img/ y se confirma que el archivo existe.
  licencia_url   es una tabla fija: la URL canónica de cada licencia CC.
  fuente_url     se verifica contra la API de Wikimedia Commons. Primero por
                 SHA-1 del archivo local —si coincide, ESE es el original, sin
                 lugar a dudas—; si no coincide (copia derivada: recorte,
                 fotograma, reescalado), se intenta por título. Lo que no
                 resuelva se reporta y NO se rellena.

  python3 auditar_medios.py            # informe, no escribe
  python3 auditar_medios.py --escribir # aplica lo verificado
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia exige un User-Agent identificable y con contacto; sin él responde
# 429 con mucha facilidad.
UA = {"User-Agent": "biosemiotics-atlas/1.0 "
                    "(https://github.com/alcyedmundo281/biosemiotics; "
                    "mailto:alcyedmundo@gmail.com)"}

# URL canónica por licencia declarada. Cualquier valor fuera de esta tabla se
# reporta en vez de adivinarse.
LICENCIAS = {
    "CC0 1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/",
    "CC BY 2.5": "https://creativecommons.org/licenses/by/2.5/",
    "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC BY 3.0 DE": "https://creativecommons.org/licenses/by/3.0/de/",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "Dominio público": "https://commons.wikimedia.org/wiki/Commons:Licensing",
}


_ultima = [0.0]
PAUSA = 2.5          # s entre llamadas: Commons corta con 429 si se le insiste
REINTENTOS = 5


def _api(params: dict) -> dict:
    params = {**params, "format": "json"}
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=UA)
    for intento in range(REINTENTOS):
        espera = PAUSA - (time.monotonic() - _ultima[0])
        if espera > 0:
            time.sleep(espera)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento == REINTENTOS - 1:
                raise SinRed("429 tras agotar reintentos")
            if e.code != 429:
                raise
            # Backoff creciente: 429 es "vuelve luego", no "no existe".
            time.sleep(3 * (intento + 1))
        finally:
            _ultima[0] = time.monotonic()
    raise RuntimeError("inalcanzable")


class SinRed(Exception):
    """No se pudo preguntar. Distinto de haber preguntado y no encontrar."""


def por_sha1(ruta: Path):
    """Identidad probada: si el binario local está en Commons, ese es el origen."""
    h = hashlib.sha1(ruta.read_bytes()).hexdigest()
    d = _api({"action": "query", "list": "allimages", "aisha1": h, "ailimit": 1})
    imgs = d.get("query", {}).get("allimages") or []
    return (imgs[0].get("descriptionurl"), "sha1") if imgs else (None, None)


def por_titulo(titulo: str):
    """Fallback para copias derivadas (recorte, fotograma, reescalado)."""
    d = _api({"action": "query", "titles": f"File:{titulo}",
              "prop": "imageinfo", "iiprop": "url"})
    for _, pag in d.get("query", {}).get("pages", {}).items():
        info = pag.get("imageinfo")
        if info:
            return info[0].get("descriptionurl"), "titulo"
    return None, None


def resolver_fuente(medio: dict, local):
    ident = str(medio.get("id") or "")
    if not ident.startswith("wikimedia:"):
        return None, "no-wikimedia"
    try:
        if local and local.exists():
            url, via = por_sha1(local)
            if url:
                return url, via
        titulo = ident.split(":", 1)[1].strip().replace(" ", "_")
        # Commons acepta espacios o guiones bajos indistintamente.
        url, via = por_titulo(titulo)
        if url:
            return url, via
        # Varios ids historicos se guardaron SIN extension, y Commons no
        # resuelve un titulo incompleto. Se prueban las extensiones posibles y
        # solo se acepta si EXACTAMENTE UNA existe: si resuelven dos, son dos
        # archivos distintos y elegir seria adivinar.
        if "." not in titulo.rsplit("_", 1)[-1]:
            hallados = {}
            for ext in (".jpg", ".jpeg", ".png", ".svg", ".gif", ".tif", ".webp", ".ogv"):
                u, _ = por_titulo(titulo + ext)
                if u:
                    hallados[ext] = u
            if len(hallados) == 1:
                return next(iter(hallados.values())), "extension"
            if len(hallados) > 1:
                # Si existen varios, manda la extension del archivo que de
                # verdad tenemos en assets/img: no es una preferencia, es el
                # binario que se va a incrustar.
                if local and local.suffix.lower() in hallados:
                    return hallados[local.suffix.lower()], "extension-local"
                return None, f"ambiguo-{len(hallados)}"
        return None, "no-resuelve"
    except SinRed:
        return None, "sin-red"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--escribir", action="store_true",
                    help="aplica al .md lo que se pudo verificar")
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()
    img_dir = raiz / "assets" / "img"
    porext = {}
    for p in img_dir.iterdir() if img_dir.exists() else []:
        porext.setdefault(p.stem, []).append(p)

    resueltos, pendientes = [], []
    for carpeta in ("conceptos", "signos", "casos"):
        for f in sorted((raiz / carpeta).glob("*.md")):
            texto = f.read_text(encoding="utf-8")
            eid = re.search(r"^id:\s*(\S+)", texto, re.M)
            if not eid:
                continue
            eid = eid.group(1)
            stem = eid.replace("signo-", "").replace("ñ", "n")
            local = None
            for cand in (eid.replace("signo-", ""), stem):
                if cand in porext:
                    local = porext[cand][0]
                    break

            bloques = re.findall(
                r"(  - tipo: imagen\n(?:    .*\n)*)", texto)
            for bloque in bloques:
                falta = [c for c in ("archivo_local", "licencia_url", "fuente_url")
                         if f"    {c}:" not in bloque]
                if not falta:
                    continue
                medio = {k: v.strip().strip('"')
                         for k, v in re.findall(r"    (\w+): (.*)", bloque)}
                nuevo = dict.fromkeys(falta)

                if "archivo_local" in falta and local:
                    nuevo["archivo_local"] = f"assets/img/{local.name}"
                if "licencia_url" in falta:
                    nuevo["licencia_url"] = LICENCIAS.get(medio.get("licencia_img", ""))
                if "fuente_url" in falta:
                    url, via = resolver_fuente(medio, local)
                    nuevo["fuente_url"] = url
                    if not url:
                        pendientes.append((eid, "fuente_url", via, medio.get("id")))

                for campo, valor in nuevo.items():
                    if valor is None:
                        if campo != "fuente_url":
                            pendientes.append((eid, campo, "sin-dato", medio.get("id")))
                        continue
                    resueltos.append((eid, campo, valor))
                    if a.escribir:
                        anclas = ("licencia_img", "credito", "descripcion")
                        for ancla in anclas:
                            m = re.search(rf"(    {ancla}: .*\n)", bloque)
                            if m:
                                nb = bloque.replace(
                                    m.group(1), m.group(1) + f'    {campo}: "{valor}"\n')
                                texto = texto.replace(bloque, nb)
                                bloque = nb
                                break
            if a.escribir:
                f.write_text(texto, encoding="utf-8")

    print(f"VERIFICADOS: {len(resueltos)}")
    for eid, campo, valor in resueltos:
        print(f"  {eid:40} {campo:14} {valor}")
    print(f"\nPENDIENTES (no se rellenan): {len(pendientes)}")
    for eid, campo, via, ident in pendientes:
        print(f"  {eid:40} {campo:14} [{via}] {ident}")
    return 1 if pendientes else 0


if __name__ == "__main__":
    sys.exit(main())
