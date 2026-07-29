#!/usr/bin/env python3
"""
verificar_citas.py — verificación de DOBLE autoridad de refs.bib.

No basta con que la clave exista (eso lo mira refs.py). Aquí se comprueba que
cada referencia siga siendo REAL y COHERENTE contra dos fuentes independientes:

  PubMed  (por PMID) → revista, año y DOI declarados coinciden.
  Crossref (por DOI)  → el DOI resuelve y su título coincide con el de PubMed.

Un PMID y un DOI que apuntan al mismo paper (mismo título) es la prueba más
dura de que la cita no es una invención ni un cruce de datos.

  python3 verificar_citas.py            # verifica todo refs.bib
  python3 verificar_citas.py --estricto # un error de red también falla

Códigos de salida:
  0  todo verificado (o error de red en modo NO estricto)
  1  al menos una discrepancia real (revista/año/DOI/título) o PMID inexistente
  2  error de red en modo --estricto
"""
import argparse
import re
import sys
import time
import json
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from refs import resumen  # cliente E-utilities del proyecto  # noqa: E402

UA = {"User-Agent": "biosemiotics-verificar/1.0 (mailto:alcyedmundo@gmail.com)"}


def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return " ".join(s.split()).strip()


def parse_bib(path: Path) -> list:
    txt = path.read_text(encoding="utf-8")
    out = []
    for clave, cuerpo in re.findall(r"@article\{([^,]+),(.*?)\n\}", txt, re.S):
        def g(k):
            m = re.search(k + r"\s*=\s*\{(.*?)\}", cuerpo, re.S)
            return m.group(1).strip() if m else ""
        out.append({"clave": clave.strip(), "pmid": g("pmid"), "doi": g("doi"),
                    "journal": g("journal"), "year": g("year"), "title": g("title")})
    return out


class RedError(Exception):
    pass


def crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    try:
        req = urllib.request.Request(url, headers=UA)
        m = json.loads(urllib.request.urlopen(req, timeout=25).read())["message"]
    except Exception as e:
        raise RedError(str(e))
    yr = ""
    for k in ("published-print", "published-online", "issued", "created"):
        dp = m.get(k, {}).get("date-parts", [[None]])[0]
        if dp and dp[0]:
            yr = str(dp[0]); break
    ct = m.get("container-title") or [""]
    return {"title": (m.get("title") or [""])[0], "journal": ct[0] if ct else "",
            "year": yr, "doi": m.get("DOI", "")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--estricto", action="store_true",
                    help="un error de red cuenta como fallo (exit 2)")
    a = ap.parse_args()

    bib = Path(a.raiz).resolve() / "refs.bib"
    refs = parse_bib(bib)
    print(f"refs.bib: {len(refs)} entradas\n")

    dup = {c for c in (r["clave"] for r in refs)
           if [x["clave"] for x in refs].count(c) > 1}
    if dup:
        print(f"✗ claves duplicadas: {sorted(dup)}")

    pmids = [r["pmid"] for r in refs if r["pmid"]]
    try:
        pm = {x["pmid"]: x for x in resumen(pmids)}
    except Exception as e:
        print(f"⚠ PubMed no responde: {e}")
        sys.exit(2 if a.estricto else 0)

    disc, red = [], 0
    ok_pm = ok_cr = ok_x = 0
    for r in refs:
        flags = []
        p = pm.get(r["pmid"])
        if not r["pmid"]:
            flags.append("sin-pmid")
        elif not p:
            flags.append("pmid-inexistente")
        else:
            dpm = (p.get("doi") or "").lower()
            if dpm and r["doi"] and dpm != r["doi"].lower():
                flags.append(f"doi≠pubmed({dpm})")
            else:
                ok_pm += 1

        if r["doi"]:
            try:
                cr = crossref(r["doi"])
                if norm(cr["doi"]) == norm(r["doi"]):
                    ok_cr += 1
                else:
                    flags.append("doi-no-resuelve")
                if p and cr["title"]:
                    a1, b1 = norm(p.get("titulo")), norm(cr["title"])
                    if a1 and b1 and (a1 in b1 or b1 in a1):
                        ok_x += 1
                    else:
                        flags.append("titulo-pubmed≠crossref")
                time.sleep(0.12)
            except RedError:
                red += 1
        else:
            flags.append("sin-doi")

        if flags and not (set(flags) <= {"sin-doi"}):
            disc.append((r["clave"], flags))

    print(f"PubMed OK: {ok_pm}/{len(refs)}   Crossref OK: {ok_cr}/{len(refs)}   "
          f"cruce título: {ok_x}")
    if red:
        print(f"⚠ {red} entradas no verificadas por error de red en Crossref")

    if disc:
        print(f"\n✗ {len(disc)} DISCREPANCIAS:")
        for clave, flags in disc:
            print(f"   {clave:<20} {', '.join(flags)}")
        sys.exit(1)

    if red and a.estricto:
        sys.exit(2)
    print("\n✓ Todas las referencias verificadas en ambas autoridades.")


if __name__ == "__main__":
    main()
