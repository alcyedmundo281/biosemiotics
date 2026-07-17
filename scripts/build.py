#!/usr/bin/env python3
"""
biosemiotics — compilador del banco.
UNA fuente (Markdown + front-matter YAML) → MUCHAS salidas.

  build/atlas.db     SQLite consultable (atlas navegable)
  build/libro.tex    LaTeX/BibLaTeX (libro: DOI, ISBN, sello)
  build/grafo.json   nodos + aristas (exploración tipo aventura)

Uso:
  python3 build.py                 # todo + validación
  python3 build.py --solo db       # solo SQLite
  python3 build.py --raiz ../banco
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

import yaml

RELS = ("relacionado_con", "prerequisito_de", "se_basa_en",
        "contrasta_con", "signos", "conceptos")


# ─────────────────────────── PARSER ───────────────────────────
def parse(path: Path, raiz: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path}: sin front-matter YAML")
    _, fm, body = raw.split("---", 2)
    meta = yaml.safe_load(fm) or {}
    meta["cuerpo"] = body.strip()
    meta["_archivo"] = str(path.relative_to(raiz))
    for campo in ("id", "tipo", "titulo"):
        if not meta.get(campo):
            raise ValueError(f"{path}: falta campo obligatorio '{campo}'")
    return meta


def cargar(raiz: Path) -> list:
    ent = []
    for carpeta in ("conceptos", "signos", "casos"):
        d = raiz / carpeta
        if d.exists():
            ent += [parse(f, raiz) for f in sorted(d.glob("*.md"))]
    if not ent:
        sys.exit(f"Banco vacío en {raiz}. ¿Faltan conceptos/ signos/ casos/?")
    return ent


# ─────────────────────── SALIDA 1: SQLITE ───────────────────────
def build_sqlite(entidades, build_dir: Path) -> Path:
    db = build_dir / "atlas.db"
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    c = con.cursor()
    c.executescript("""
        CREATE TABLE entidad (
            id TEXT PRIMARY KEY, tipo TEXT NOT NULL, titulo TEXT NOT NULL,
            nivel TEXT, organo TEXT, dominio TEXT, capitulo INTEGER, orden INTEGER,
            significante TEXT, significado TEXT, decision TEXT, umbral TEXT,
            consentimiento TEXT, publicado INTEGER, doi TEXT,
            cuerpo TEXT, archivo TEXT
        );
        CREATE TABLE relacion (origen TEXT, destino TEXT, clase TEXT);
        CREATE TABLE tag (entidad TEXT, tag TEXT);
        CREATE TABLE ref (entidad TEXT, clave TEXT);
        CREATE TABLE falso_positivo (entidad TEXT, texto TEXT);
        CREATE VIRTUAL TABLE busqueda USING fts5(
            id, titulo, cuerpo, tokenize="unicode61 remove_diacritics 2"
        );
    """)
    for e in entidades:
        c.execute("INSERT INTO entidad VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            e["id"], e["tipo"], e["titulo"], e.get("nivel"), e.get("organo"),
            e.get("dominio"), e.get("capitulo"), e.get("orden"),
            e.get("significante"), e.get("significado"),
            # los casos guardan su bifurcación en 'decision_semiotica'
            e.get("decision") or e.get("decision_semiotica"),
            e.get("umbral"), e.get("consentimiento"),
            int(bool(e.get("publicado"))), e.get("doi"),
            e["cuerpo"], e["_archivo"],
        ))
        c.execute("INSERT INTO busqueda VALUES (?,?,?)",
                  (e["id"], e["titulo"], e["cuerpo"]))
        for clase in RELS:
            for d in (e.get(clase) or []):
                c.execute("INSERT INTO relacion VALUES (?,?,?)", (e["id"], d, clase))
        for t in (e.get("tags") or []):
            c.execute("INSERT INTO tag VALUES (?,?)", (e["id"], t))
        for r in (e.get("refs") or []):
            c.execute("INSERT INTO ref VALUES (?,?)", (e["id"], r))
        for fp in (e.get("falsos_positivos") or []):
            c.execute("INSERT INTO falso_positivo VALUES (?,?)", (e["id"], fp))
    con.commit()
    con.close()
    return db


# ─────────────────────── SALIDA 2: LATEX ───────────────────────
def build_latex(entidades, build_dir: Path, autor="Alcy") -> Path:
    conceptos = sorted([e for e in entidades if e["tipo"] == "concepto"],
                       key=lambda e: (e.get("capitulo") or 99, e.get("orden") or 99))
    signos = sorted([e for e in entidades if e["tipo"] == "signo"],
                    key=lambda e: (e.get("organo") or "", e["titulo"]))

    L = [r"\documentclass[11pt]{book}",
         r"\usepackage[utf8]{inputenc}",
         r"\usepackage[spanish]{babel}",
         r"\usepackage[backend=biber,style=numeric]{biblatex}",
         r"\addbibresource{refs.bib}",
         r"\title{Biosemiótica del Cuerpo Vivo\\\large Manual de POCUS para el clínico}",
         rf"\author{{{autor}}}",
         r"\begin{document}", r"\maketitle", r"\tableofcontents",
         "", r"\part{Fundamentos}"]

    cap = None
    for e in conceptos:
        if e.get("capitulo") != cap:
            cap = e.get("capitulo")
            L.append(f"\n\\chapter{{Capítulo {cap}}}")
        L += [f"\n\\section{{{e['titulo']}}}", f"\\label{{sec:{e['id']}}}", e["cuerpo"]]
        L += [f"\\cite{{{r}}}" for r in (e.get("refs") or [])]

    L.append("\n" + r"\part{Atlas de signos}")
    for e in signos:
        L += [f"\n\\chapter{{{e['titulo']}}}", f"\\label{{sec:{e['id']}}}"]
        for etiqueta, campo in (("Significante", "significante"),
                                ("Significado", "significado"),
                                ("Decisión", "decision"),
                                ("Umbral", "umbral")):
            if e.get(campo):
                L.append(f"\\paragraph{{{etiqueta}.}} {e[campo]}")
        if e.get("falsos_positivos"):
            L.append(r"\paragraph{Dónde NO confiar.}\begin{itemize}")
            L += [f"  \\item {fp}" for fp in e["falsos_positivos"]]
            L.append(r"\end{itemize}")
        L.append(e["cuerpo"])
        L += [f"\\cite{{{r}}}" for r in (e.get("refs") or [])]

    L += [r"\printbibliography", r"\end{document}"]
    tex = build_dir / "libro.tex"
    tex.write_text("\n".join(L), encoding="utf-8")
    return tex


# ─────────────────────── SALIDA 3: GRAFO ───────────────────────
def build_grafo(entidades, build_dir: Path):
    nodos = [{"id": e["id"], "tipo": e["tipo"], "titulo": e["titulo"],
              "organo": e.get("organo"), "dominio": e.get("dominio"),
              "nivel": e.get("nivel")} for e in entidades]
    aristas = [{"origen": e["id"], "destino": d, "clase": clase}
               for e in entidades for clase in RELS for d in (e.get(clase) or [])]
    g = build_dir / "grafo.json"
    g.write_text(json.dumps({"nodos": nodos, "aristas": aristas},
                            ensure_ascii=False, indent=2), encoding="utf-8")
    return g, aristas


# ─────────────────────── VALIDACIÓN ───────────────────────
def validar(entidades, aristas, raiz: Path):
    """(errores, alertas). Errores rompen el grafo o bloquean publicación."""
    ids = {e["id"] for e in entidades}
    errores = [f"{a['origen']} --{a['clase']}--> {a['destino']} (NO EXISTE)"
               for a in aristas if a["destino"] not in ids]
    alertas = []

    for e in entidades:
        if e["tipo"] == "signo":
            # Un signo sin límites enseña a reconocer sin enseñar a dudar.
            if not e.get("falsos_positivos"):
                alertas.append(f"[CLÍNICO] {e['id']}: sin 'falsos_positivos'")
            for campo in ("significante", "significado", "decision"):
                if not e.get(campo):
                    alertas.append(f"[SEMIÓTICA] {e['id']}: falta '{campo}'")
        if e["tipo"] == "caso" and e.get("publicado"):
            if e.get("consentimiento") != "obtenido":
                errores.append(
                    f"[BLOQUEO] {e['id']}: publicado=true pero "
                    f"consentimiento={e.get('consentimiento')!r}")
        if e["tipo"] in ("signo", "caso") and not e.get("refs"):
            alertas.append(f"[REFS] {e['id']}: sin referencias BibLaTeX")

    bib = raiz / "refs.bib"
    if bib.exists():
        txt = bib.read_text(encoding="utf-8")
        for e in entidades:
            for r in (e.get("refs") or []):
                if f"{{{r}," not in txt:
                    alertas.append(f"[REFS] {e['id']}: '{r}' no está en refs.bib")
    return errores, alertas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--solo", choices=["db", "tex", "grafo"])
    ap.add_argument("--autor", default="Alcy")
    a = ap.parse_args()

    raiz = Path(a.raiz).resolve()
    build_dir = raiz / "build"
    build_dir.mkdir(exist_ok=True)

    ent = cargar(raiz)
    n = {t: sum(e["tipo"] == t for e in ent) for t in ("concepto", "signo", "caso")}
    print(f"Banco: {len(ent)} entidades  "
          f"({n['concepto']} conceptos, {n['signo']} signos, {n['caso']} casos)")

    _, aristas = build_grafo(ent, build_dir)

    if a.solo in (None, "db"):
        print(f"  → atlas.db     ({len(aristas)} relaciones)")
        build_sqlite(ent, build_dir)
    if a.solo in (None, "tex"):
        build_latex(ent, build_dir, a.autor)
        print("  → libro.tex")
    if a.solo in (None, "grafo"):
        print("  → grafo.json")

    errores, alertas = validar(ent, aristas, raiz)
    if errores:
        print(f"\n✗ {len(errores)} ERRORES:")
        for x in errores:
            print(f"   {x}")
    if alertas:
        print(f"\n⚠ {len(alertas)} alertas de calidad:")
        for x in alertas:
            print(f"   {x}")
    if not errores and not alertas:
        print("\n✓ Integridad referencial y calidad OK")
    elif not errores:
        print("\n✓ Integridad referencial OK")

    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
