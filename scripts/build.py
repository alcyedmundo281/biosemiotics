#!/usr/bin/env python3
"""Compila Markdown/YAML en SQLite, grafo y Markdown para Ghost.

Conserva sus importaciones históricas como fachada. La carga, configuración,
bibliografía y validación viven ahora en módulos independientes.
"""

import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

from banco import cargar, estado_publicacion, parse, seleccionar_publicables
from bibliografia import (
    BIBLIO_HEADING, CITA_BIBLATEX, autores_ghost, bibliografia_manual,
    cargar_bibliografia, cerrar_frase, excerpt_ghost,
    quitar_bibliografia_manual, referencia_ghost, resolver_citas,
)
from configuracion import CAPITULOS, NIVELES, ORGANOS, RELS, SISTEMAS, nombre_organo
from ghost import LINEA_RETO, markdown_ghost
from rutas import raiz_argumentos, raiz_desde_argumentos
from validacion import SECCIONES, errores_editoriales, exigir_editorial, validar

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def build_sqlite(entidades, build_dir: Path) -> Path:
    estados = [estado_publicacion(e) for e in entidades]
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
            cuerpo TEXT, archivo TEXT, estado TEXT, url TEXT,
            fecha_revision TEXT, ghost_id TEXT
        );
        CREATE TABLE relacion (origen TEXT, destino TEXT, clase TEXT);
        CREATE TABLE tag (entidad TEXT, tag TEXT);
        CREATE TABLE ref (entidad TEXT, clave TEXT);
        CREATE TABLE falso_positivo (entidad TEXT, texto TEXT);
        CREATE VIRTUAL TABLE busqueda USING fts5(
            id, titulo, cuerpo, tokenize="unicode61 remove_diacritics 2"
        );
    """)
    for e, estado in zip(entidades, estados):
        c.execute("INSERT INTO entidad VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            e["id"], e["tipo"], e["titulo"], e.get("nivel"), e.get("organo"),
            e.get("dominio"), e.get("capitulo"), e.get("orden"),
            e.get("significante"), e.get("significado"),
            e.get("decision") or e.get("decision_semiotica"),
            e.get("umbral"), e.get("consentimiento"),
            int(estado == "publicado"), e.get("doi"),
            e["cuerpo"], e["_archivo"], estado, e.get("url"),
            str(e["fecha_revision"]) if e.get("fecha_revision") else None,
            e.get("ghost_id"),
        ))
        c.execute("INSERT INTO busqueda VALUES (?,?,?)",
                  (e["id"], e["titulo"], e["cuerpo"]))
        for clase in RELS:
            for destino in (e.get(clase) or []):
                c.execute("INSERT INTO relacion VALUES (?,?,?)", (e["id"], destino, clase))
        for tag in (e.get("tags") or []):
            c.execute("INSERT INTO tag VALUES (?,?)", (e["id"], tag))
        for ref in (e.get("refs") or []):
            c.execute("INSERT INTO ref VALUES (?,?)", (e["id"], ref))
        for falso_positivo in (e.get("falsos_positivos") or []):
            c.execute("INSERT INTO falso_positivo VALUES (?,?)", (e["id"], falso_positivo))
    con.commit()
    con.close()
    return db


def build_grafo(entidades, build_dir: Path):
    nodos = [{"id": e["id"], "tipo": e["tipo"], "titulo": e["titulo"],
              "organo": e.get("organo"), "dominio": e.get("dominio"),
              "nivel": e.get("nivel")} for e in entidades]
    aristas = [{"origen": e["id"], "destino": destino, "clase": clase}
               for e in entidades for clase in RELS
               for destino in (e.get(clase) or [])]
    grafo = build_dir / "grafo.json"
    grafo.write_text(json.dumps({"nodos": nodos, "aristas": aristas},
                                ensure_ascii=False, indent=2), encoding="utf-8")
    return grafo, aristas


def build_ghost(entidades, build_dir: Path, bib_path: Path) -> Path:
    """Genera Markdown listo para copiar a Ghost sin alterar la fuente."""
    entidades = seleccionar_publicables(entidades)
    exigir_editorial(entidades, bib_path)
    destino = build_dir / "ghost"
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    bib = cargar_bibliografia(bib_path)
    for entidad in entidades:
        archivo = destino / entidad["_archivo"]
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(markdown_ghost(entidad, bib), encoding="utf-8")
    return destino


def main():
    ap = argparse.ArgumentParser()
    raiz_argumentos(ap)
    ap.add_argument("--solo", choices=["db", "grafo", "ghost"])
    args = ap.parse_args()
    raiz = raiz_desde_argumentos(ap, args)
    build_dir = raiz / "build"
    entidades = cargar(raiz)
    cantidades = {tipo: sum(e["tipo"] == tipo for e in entidades)
                  for tipo in ("concepto", "signo", "caso")}
    print(f"Banco: {len(entidades)} entidades  "
          f"({cantidades['concepto']} conceptos, {cantidades['signo']} signos, "
          f"{cantidades['caso']} casos)")
    aristas = [{"origen": e["id"], "destino": destino, "clase": clase}
               for e in entidades for clase in RELS
               for destino in (e.get(clase) or [])]
    errores, alertas = validar(entidades, aristas, raiz, permitir_borradores=True)
    if errores:
        raise RuntimeError("Validación fallida:\n" + "\n".join(errores))
    build_dir.mkdir(exist_ok=True)
    build_grafo(entidades, build_dir)
    if args.solo in (None, "db"):
        print(f"  → atlas.db     ({len(aristas)} relaciones)")
        build_sqlite(entidades, build_dir)
    if args.solo in (None, "grafo"):
        print("  → grafo.json")
    if args.solo in (None, "ghost"):
        build_ghost(entidades, build_dir, raiz / "refs.bib")
        print(f"  → ghost/       ({len(seleccionar_publicables(entidades))} artículos Ghost-ready)")
    if alertas:
        print(f"\n⚠ {len(alertas)} alertas de calidad:")
        for alerta in alertas:
            print(f"   {alerta}")
        print("\n✓ Integridad referencial OK")
    else:
        print("\n✓ Integridad referencial y calidad OK")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        sys.exit(str(exc))
