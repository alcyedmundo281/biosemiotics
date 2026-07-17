#!/usr/bin/env python3
"""
refs.py — llena refs.bib desde PubMed.

Lee las claves BibLaTeX declaradas en el banco (campo `refs:`), detecta las que
faltan en refs.bib, y las busca en PubMed vía E-utilities (API pública del NCBI).

  python3 refs.py                      # reporta qué falta
  python3 refs.py --buscar             # busca las faltantes e interactúa
  python3 refs.py --pmid 18403664 --clave lichtenstein2008
  python3 refs.py --query "optic nerve sheath diameter meta-analysis"

PRINCIPIO: nunca inventar una referencia. Cada entrada del .bib nace de un PMID
real, con DOI verificable. Si PubMed no la encuentra, la clave queda pendiente
y el artículo NO se publica.

UpToDate y similares son fuentes TERCIARIAS: sirven para encontrar la primaria,
no para citarse. Esto trae la primaria.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import cargar  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "biosemiotics-atlas/1.0 (educational medical atlas)"}


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def buscar(term: str, n: int = 5) -> list[str]:
    """Devuelve PMIDs."""
    q = urllib.parse.urlencode({
        "db": "pubmed", "term": term, "retmax": n,
        "retmode": "json", "sort": "relevance",
    })
    data = json.loads(_get(f"{EUTILS}/esearch.fcgi?{q}"))
    return data.get("esearchresult", {}).get("idlist", [])


def resumen(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    q = urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids), "retmode": "json",
    })
    data = json.loads(_get(f"{EUTILS}/esummary.fcgi?{q}")).get("result", {})
    out = []
    for p in pmids:
        r = data.get(p)
        if not r:
            continue
        doi = next((i["value"] for i in r.get("articleids", [])
                    if i.get("idtype") == "doi"), None)
        out.append({
            "pmid": p,
            "titulo": r.get("title", "").rstrip("."),
            "autores": [a["name"] for a in r.get("authors", [])
                        if a.get("authtype") == "Author"],
            "revista": r.get("source", ""),
            "anio": (r.get("pubdate", "") or "")[:4],
            "volumen": r.get("volume", ""),
            "paginas": r.get("pages", ""),
            "doi": doi,
        })
    return out


def a_bibtex(r: dict, clave: str) -> str:
    def esc(s):  # LaTeX no perdona estos
        for a, b in (("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")):
            s = s.replace(a, b)
        return s

    campos = [
        ("author", " and ".join(r["autores"]) or "Anon"),
        ("title", esc(r["titulo"])),
        ("journal", esc(r["revista"])),
        ("year", r["anio"]),
        ("volume", r["volumen"]),
        ("pages", r["paginas"].replace("-", "--")),
        ("doi", r["doi"] or ""),
        ("pmid", r["pmid"]),
    ]
    cuerpo = ",\n".join(f"  {k} = {{{v}}}" for k, v in campos if v)
    return f"@article{{{clave},\n{cuerpo}\n}}\n"


def claves_del_banco(raiz: Path) -> dict:
    """clave -> [entidades que la citan]"""
    uso = {}
    for e in cargar(raiz):
        for r in (e.get("refs") or []):
            uso.setdefault(r, []).append(e["id"])
    return uso


def claves_en_bib(bib: Path) -> set:
    if not bib.exists():
        return set()
    return set(re.findall(r"@\w+\{([^,]+),", bib.read_text(encoding="utf-8")))


def sugerir(clave: str) -> str:
    """De 'lichtenstein2008' saca 'lichtenstein 2008' como semilla de búsqueda."""
    m = re.match(r"([a-zA-Z]+)(\d{4})", clave)
    return f"{m.group(1)} {m.group(2)}" if m else clave


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--buscar", action="store_true",
                    help="busca en PubMed cada clave faltante")
    ap.add_argument("--query", help="búsqueda libre en PubMed")
    ap.add_argument("--pmid", help="agrega un PMID concreto")
    ap.add_argument("--clave", help="clave BibLaTeX para --pmid")
    a = ap.parse_args()

    raiz = Path(a.raiz).resolve()
    bib = raiz / "refs.bib"

    # ── modo: búsqueda libre ──────────────────────────────────────────
    if a.query:
        rs = resumen(buscar(a.query, 6))
        if not rs:
            sys.exit("Sin resultados.")
        print(f"\nPubMed — «{a.query}»\n")
        for i, r in enumerate(rs, 1):
            au = r["autores"][0] + " et al." if len(r["autores"]) > 1 else \
                 (r["autores"][0] if r["autores"] else "—")
            print(f"[{i}] {r['titulo']}")
            print(f"    {au}  {r['revista']} {r['anio']}"
                  f"{'  ·  doi:' + r['doi'] if r['doi'] else ''}")
            print(f"    PMID {r['pmid']}\n")
        print("Para agregar:  python3 refs.py --pmid <PMID> --clave <clave>")
        return

    # ── modo: agregar un PMID ─────────────────────────────────────────
    if a.pmid:
        if not a.clave:
            sys.exit("--pmid requiere --clave")
        rs = resumen([a.pmid])
        if not rs:
            sys.exit(f"PMID {a.pmid} no encontrado.")
        entry = a_bibtex(rs[0], a.clave)
        if a.clave in claves_en_bib(bib):
            sys.exit(f"'{a.clave}' ya está en refs.bib")
        with bib.open("a", encoding="utf-8") as f:
            f.write("\n" + entry)
        print(f"✓ {a.clave} → refs.bib")
        print(entry)
        return

    # ── modo: auditoría (default) ─────────────────────────────────────
    uso = claves_del_banco(raiz)
    tengo = claves_en_bib(bib)
    faltan = {k: v for k, v in uso.items() if k not in tengo}
    huerfanas = tengo - set(uso)

    print(f"Banco: {len(uso)} claves citadas · refs.bib: {len(tengo)} entradas")

    if not faltan:
        print("\n✓ Todas las claves citadas están en refs.bib")
    else:
        print(f"\n⚠ {len(faltan)} claves SIN entrada bibliográfica:\n")
        for k, ents in sorted(faltan.items()):
            print(f"   {k:<22} ← citada en: {', '.join(ents)}")

    if huerfanas:
        print(f"\n· {len(huerfanas)} entradas en refs.bib que nadie cita: "
              f"{', '.join(sorted(huerfanas))}")

    # ── modo: --buscar ────────────────────────────────────────────────
    if a.buscar and faltan:
        print("\n" + "─" * 62)
        for k in sorted(faltan):
            term = sugerir(k)
            print(f"\n▸ {k}   (búsqueda: «{term}»)")
            try:
                rs = resumen(buscar(term, 4))
            except Exception as ex:
                print(f"   error consultando PubMed: {ex}")
                continue
            if not rs:
                print("   sin resultados — busca con --query")
                continue
            for i, r in enumerate(rs, 1):
                au = (r["autores"][0] + " et al.") if len(r["autores"]) > 1 else \
                     (r["autores"][0] if r["autores"] else "—")
                print(f"   [{i}] {r['titulo'][:76]}")
                print(f"       {au}  {r['revista']} {r['anio']}  PMID {r['pmid']}")
            print(f"\n   → python3 refs.py --pmid <PMID> --clave {k}")
            time.sleep(0.4)  # cortesía con el NCBI

        print("\n" + "─" * 62)
        print("NUNCA aceptes un resultado sin abrirlo. La clave sugerida es una")
        print("heurística del apellido+año: puede traer el paper equivocado.")


if __name__ == "__main__":
    main()
