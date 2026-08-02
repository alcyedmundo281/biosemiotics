#!/usr/bin/env python3
"""
biosemiotics — compilador del banco.
UNA fuente (Markdown + front-matter YAML) → MUCHAS salidas.

  build/atlas.db     SQLite consultable (atlas navegable)
  build/libro.tex    LaTeX/BibLaTeX (libro: DOI, ISBN, sello)
  build/grafo.json   nodos + aristas (exploración tipo aventura)
  build/ghost/       Markdown con citas numéricas listo para Ghost

Uso:
  python3 build.py                 # todo + validación
  python3 build.py --solo db       # solo SQLite
  python3 build.py --raiz ../banco
"""
import argparse
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

RELS = ("relacionado_con", "prerequisito_de", "se_basa_en",
        "contrasta_con", "signos", "conceptos")

CITA_BIBLATEX = re.compile(r"\[([A-Za-z][A-Za-z0-9_:-]*)\]")
BIBLIO_HEADING = re.compile(
    r"^(#{2,6})\s+(?:Evidencia|Referencias|Bibliograf[ií]a)\s*$",
    re.IGNORECASE,
)

# Caracteres especiales de LaTeX. El orden de las claves no importa: se
# recorre el string original una sola vez, así que una sustitución nunca
# vuelve a procesarse (evita el doble escape de p.ej. '\' → '\textbackslash{}').
_LATEX_ESPECIALES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
}


def escape_latex(s) -> str:
    """Escapa caracteres especiales de LaTeX en texto libre (títulos, cuerpo).

    Sin esto, un '%' suelto (p.ej. "1,2 % de complicaciones") comenta el
    resto de la línea en silencio y el texto que sigue desaparece del PDF.
    """
    if s is None:
        return ""
    return "".join(_LATEX_ESPECIALES.get(c, c) for c in str(s))


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
# DPI mínimo para impresión: por debajo de esto una imagen se ve pixelada.
# Se usa para NO agrandar una imagen más allá de su resolución nativa.
DPI_IMPRESION = 150


def _dims_px(path: Path):
    """(ancho, alto) en píxeles leyendo solo la cabecera. Sin dependencias
    (la CI corre build.py sin Pillow). Devuelve None si no la reconoce."""
    try:
        with path.open("rb") as f:
            head = f.read(24)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                import struct
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":  # JPEG: buscar el marcador SOF
                import struct
                f.seek(2)
                b = f.read(1)
                while b:
                    while b == b"\xff":
                        b = f.read(1)
                    if b[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                                0xC9, 0xCA, 0xCB):
                        f.read(3)
                        h, w = struct.unpack(">HH", f.read(4))
                        return w, h
                    seg = struct.unpack(">H", f.read(2))[0]
                    f.seek(seg - 2, 1)
                    b = f.read(1)
    except Exception:
        pass
    return None


def figura_latex(e: dict, raiz: Path) -> str:
    """Figura flotante con su imagen y la cita al pie (crédito + licencia).

    La imagen vive en assets/img/<id sin 'signo-', sin ñ>.{jpg,jpeg,png}.
    libro.tex se compila desde build/, así que la ruta es ../assets/img/...
    Devuelve '' si no hay imagen declarada o el archivo no existe.
    """
    med = next((m for m in (e.get("medios") or [])
                if m.get("tipo") == "imagen" and m.get("credito")), None)
    if not med:
        return ""
    base = e["id"].replace("signo-", "").replace("ñ", "n")
    ruta = next((p for ext in (".jpg", ".jpeg", ".png")
                 if (p := raiz / "assets" / "img" / f"{base}{ext}").exists()), None)
    if not ruta:
        return ""
    partes = [med["credito"]]
    if med.get("fuente"):
        partes.append(med["fuente"])
    if med.get("licencia_img"):
        partes.append(med["licencia_img"])
    credito = escape_latex(". ".join(partes) + ".")
    desc = escape_latex(med.get("descripcion", ""))

    # Ancho objetivo: el nativo a DPI_IMPRESION (para no pixelar), pero nunca
    # más que 0.85\textwidth. Una imagen pequeña sale más chica y nítida en vez
    # de estirada; una grande llena el ancho como antes. 'max width' de
    # adjustbox impone el tope sin necesitar saber el \textwidth real.
    dims = _dims_px(ruta)
    if dims:
        ancho_in = dims[0] / DPI_IMPRESION
        spec = (rf"width={ancho_in:.2f}in,max width=0.85\textwidth,"
                r"max height=0.45\textheight,keepaspectratio")
    else:
        spec = r"width=0.85\textwidth,height=0.45\textheight,keepaspectratio"
    return "\n".join([
        r"\begin{figure}[H]",
        r"  \centering",
        rf"  \includegraphics[{spec}]{{../assets/img/{base}{ruta.suffix}}}",
        rf"  \caption{{{desc} \textit{{Fuente: {credito}}}}}",
        r"\end{figure}",
    ])


def build_latex(entidades, build_dir: Path, autor="Alcy") -> Path:
    conceptos = sorted([e for e in entidades if e["tipo"] == "concepto"],
                       key=lambda e: (e.get("capitulo") or 99, e.get("orden") or 99))
    signos = sorted([e for e in entidades if e["tipo"] == "signo"],
                    key=lambda e: (e.get("organo") or "", e["titulo"]))

    # Se compila con LuaLaTeX (ver CLAUDE.md), no pdflatex: el banco usa
    # símbolos Unicode estructurales (≥ → ±) en umbrales y decisiones, y
    # fontspec los renderiza directo sin parchear cada uno a mano.
    L = [r"\documentclass[11pt]{book}",
         r"\usepackage{fontspec}",
         r"\setmainfont{FreeSerif}",
         r"\usepackage[spanish]{babel}",
         r"\usepackage{graphicx}",
         r"\usepackage{float}",
         r"\usepackage[export]{adjustbox}",  # habilita 'max width' en includegraphics
         r"\usepackage[backend=biber,style=numeric]{biblatex}",
         r"\addbibresource{refs.bib}",
         r"\title{Biosemiótica del Cuerpo Vivo\\\large Manual de POCUS para el clínico}",
         rf"\author{{{escape_latex(autor)}}}",
         r"\begin{document}", r"\maketitle", r"\tableofcontents",
         "", r"\part{Fundamentos}"]

    cap = None
    for e in conceptos:
        if e.get("capitulo") != cap:
            cap = e.get("capitulo")
            L.append(f"\n\\chapter{{Capítulo {cap}}}")
        L += [f"\n\\section{{{escape_latex(e['titulo'])}}}",
              f"\\label{{sec:{e['id']}}}"]
        fig = figura_latex(e, build_dir.parent)
        if fig:
            L.append(fig)
        L.append(escape_latex(e["cuerpo"]))
        L += [f"\\cite{{{r}}}" for r in (e.get("refs") or [])]

    L.append("\n" + r"\part{Atlas de signos}")
    for e in signos:
        L += [f"\n\\chapter{{{escape_latex(e['titulo'])}}}", f"\\label{{sec:{e['id']}}}"]
        fig = figura_latex(e, build_dir.parent)
        if fig:
            L.append(fig)
        for etiqueta, campo in (("Significante", "significante"),
                                ("Significado", "significado"),
                                ("Decisión", "decision"),
                                ("Umbral", "umbral")):
            if e.get(campo):
                L.append(f"\\paragraph{{{etiqueta}.}} {escape_latex(e[campo])}")
        if e.get("falsos_positivos"):
            L.append(r"\paragraph{Dónde NO confiar.}\begin{itemize}")
            L += [f"  \\item {escape_latex(fp)}" for fp in e["falsos_positivos"]]
            L.append(r"\end{itemize}")
        L.append(escape_latex(e["cuerpo"]))
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


# ─────────────────────── SALIDA 4: GHOST ───────────────────────
def cargar_bibliografia(path: Path) -> dict:
    """Lee los campos usados por la salida Ghost desde refs.bib.

    refs.py genera entradas planas delimitadas por llaves. Mantener este lector
    local evita añadir una dependencia que no está disponible en la CI.
    """
    txt = path.read_text(encoding="utf-8")
    refs = {}
    for tipo, clave, cuerpo in re.findall(
            r"@(\w+)\{([^,]+),(.*?)\n\}", txt, re.DOTALL):
        campos = {}
        for campo, valor in re.findall(
                r"(\w+)\s*=\s*\{(.*?)\}\s*,?", cuerpo, re.DOTALL):
            campos[campo.lower()] = " ".join(valor.split())
        campos["tipo"] = tipo.lower()
        refs[clave.strip()] = campos
    return refs


def quitar_bibliografia_manual(cuerpo: str) -> str:
    """Quita listas bibliográficas mantenidas a mano antes de regenerarlas."""
    lineas = cuerpo.splitlines()
    salida = []
    i = 0
    while i < len(lineas):
        m = BIBLIO_HEADING.match(lineas[i].strip())
        if not m:
            salida.append(lineas[i])
            i += 1
            continue

        nivel = len(m.group(1))
        i += 1
        while i < len(lineas):
            encabezado = re.match(r"^(#{1,6})\s+", lineas[i])
            if encabezado and len(encabezado.group(1)) <= nivel:
                break
            # Riñón crónico termina su lista con esta nota editorial, que no es
            # parte de la bibliografía y debe conservarse antes de Evidencia.
            if lineas[i].startswith("**Nota de alcance:**"):
                break
            i += 1
        while salida and not salida[-1].strip():
            salida.pop()
        if salida:
            salida.append("")
    return "\n".join(salida).strip()


def bibliografia_manual(cuerpo: str) -> list:
    """Entradas numeradas de una lista bibliográfica escrita a mano.

    Esa lista NO se publica: build_ghost la descarta y regenera la sección
    desde refs.bib. Se cuenta solo para avisar cuando diverge del front matter.
    """
    lineas = cuerpo.splitlines()
    entradas = []
    i = 0
    while i < len(lineas):
        m = BIBLIO_HEADING.match(lineas[i].strip())
        if not m:
            i += 1
            continue
        nivel = len(m.group(1))
        i += 1
        while i < len(lineas):
            encabezado = re.match(r"^(#{1,6})\s+", lineas[i])
            if encabezado and len(encabezado.group(1)) <= nivel:
                break
            if lineas[i].startswith("**Nota de alcance:**"):
                break
            if re.match(r"^\s*\d+\.\s+\S", lineas[i]):
                entradas.append(lineas[i].strip())
            i += 1
    return entradas


def autores_ghost(valor: str) -> str:
    autores = [a.strip() for a in valor.split(" and ") if a.strip()]
    if len(autores) > 2:
        return f"{autores[0]}, et al"
    return ", ".join(autores)


def cerrar_frase(valor: str) -> str:
    valor = valor.strip()
    return valor if valor.endswith((".", "?", "!")) else valor + "."


def referencia_ghost(numero: int, ref: dict) -> str:
    autores = autores_ghost(ref.get("author", ""))
    titulo = ref.get("title", "")
    revista = ref.get("journal", "").rstrip(".")
    anio = ref.get("year", "")
    volumen = ref.get("volume", "")
    paginas = ref.get("pages", "").replace("--", "–")
    doi = ref.get("doi", "")
    pmid = ref.get("pmid", "")
    localizacion = anio
    if volumen:
        localizacion += f";{volumen}"
    if paginas:
        localizacion += f":{paginas}"
    return (f"{numero}. {cerrar_frase(autores)} {cerrar_frase(titulo)} "
            f"*{revista}.* {localizacion}. "
            f"DOI: {doi}. PMID: {pmid}.")


def resolver_citas(cuerpo: str, claves_declaradas: list, bib: dict):
    """Convierte claves a números y devuelve el orden bibliográfico estable."""
    orden = []
    numeros = {}

    def reemplazar(match):
        clave = match.group(1)
        if clave not in bib:
            return match.group(0)
        if clave not in numeros:
            numeros[clave] = len(orden) + 1
            orden.append(clave)
        return f"[{numeros[clave]}]"

    resuelto = CITA_BIBLATEX.sub(reemplazar, cuerpo)
    # Algunas fichas antiguas solo declaran las fuentes en `refs` y todavía no
    # tienen citas en línea. Se conservan después de las citadas, en el orden
    # editorial del front matter, para no perder su bibliografía publicada.
    for clave in claves_declaradas:
        if clave not in numeros:
            numeros[clave] = len(orden) + 1
            orden.append(clave)
    return resuelto, orden


def excerpt_ghost(valor: str, limite: int = 300) -> str:
    """Normaliza y limita el excerpt al máximo aceptado por Ghost."""
    texto = " ".join(str(valor or "").split())
    if len(texto) <= limite:
        return texto
    recorte = texto[:limite - 1].rsplit(" ", 1)[0].rstrip(" ,;:")
    return recorte + "…"


def build_ghost(entidades, build_dir: Path, bib_path: Path) -> Path:
    """Genera Markdown listo para copiar a Ghost sin alterar la fuente."""
    destino = build_dir / "ghost"
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    bib = cargar_bibliografia(bib_path)

    for e in entidades:
        cuerpo = quitar_bibliografia_manual(e["cuerpo"])
        cuerpo, orden = resolver_citas(cuerpo, e.get("refs") or [], bib)
        referencias = [referencia_ghost(i, bib[clave])
                       for i, clave in enumerate(orden, 1)]
        if referencias:
            cuerpo = cuerpo.rstrip() + "\n\n## Evidencia\n\n" + "\n".join(referencias)

        abstract = excerpt_ghost(e.get("abstract"))
        cabecera = "\n".join([
            "---",
            f"title: {json.dumps(str(e['titulo']), ensure_ascii=False)}",
            f"excerpt: {json.dumps(abstract, ensure_ascii=False)}",
            "---",
            "",
        ])
        archivo = destino / e["_archivo"]
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(cabecera + cuerpo.rstrip() + "\n", encoding="utf-8")
    return destino


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

        # La sección 'Evidencia' escrita a mano es contenido muerto: se publica
        # la que build_ghost regenera desde refs.bib. Cuando ambas divergen, el
        # editor que lee el .md ve una bibliografía que no es la real —así se
        # perdió de vista que fink2000, fuente de las cifras de AAA, no figuraba
        # en su lista a mano. No se corrige el texto: se avisa de la deriva.
        manual = bibliografia_manual(e["cuerpo"])
        declaradas = e.get("refs") or []
        if manual and len(manual) != len(declaradas):
            alertas.append(
                f"[EDITORIAL] {e['id']}: '## Evidencia' a mano lista "
                f"{len(manual)} entradas y 'refs' declara {len(declaradas)}; "
                f"se publica la de refs.bib")

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
    ap.add_argument("--solo", choices=["db", "tex", "grafo", "ghost"])
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
    if a.solo in (None, "ghost"):
        ghost = build_ghost(ent, build_dir, raiz / "refs.bib")
        print(f"  → ghost/       ({len(ent)} artículos Ghost-ready)")

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
