#!/usr/bin/env python3
"""
biosemiotics — compilador del banco.
UNA fuente (Markdown + front-matter YAML) → MUCHAS salidas.

  build/atlas.db     SQLite consultable (atlas navegable)
  build/grafo.json   nodos + aristas (exploración tipo aventura)
  build/ghost/       Markdown con citas numéricas listo para Ghost

El libro (EPUB, PDF y su fuente LaTeX) ya no sale de aquí: lo proyecta
scripts/qmd.py a un proyecto Quarto, y lo renderizan scripts/epub.py y
scripts/libro.py. Este módulo aporta el orden canónico (CAPITULOS, SISTEMAS,
ORGANOS) y el motor de citas que aquellos reutilizan.

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

# Cierre de cada signo publicado en Ghost: el enlace al Reto.
# El Reto (artefactos/reto.html) lee el MISMO index.json y arma sus preguntas
# desde la ficha, así que basta el id para enfocar la ronda en ESE signo
# (parámetro ?signo=). Solo lo llevan los signos: conceptos y casos no generan
# preguntas. Si cambia el slug de la página en Ghost, se cambia aquí y se
# recompila; no está incrustado en build_ghost().
LINEA_RETO = (
    "---\n"
    "\n"
    "**¿Reconoces este signo cuando no te avisan?** "
    "[Ponte a prueba en el Reto](https://www.biosemiotics.net/reto/?signo={id})"
)

CITA_BIBLATEX = re.compile(r"\[([A-Za-z][A-Za-z0-9_:-]*)\]")
BIBLIO_HEADING = re.compile(
    r"^(#{2,6})\s+(?:Evidencia|Referencias|Bibliograf[ií]a)\s*$",
    re.IGNORECASE,
)

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
            ent += [parse(f, raiz) for f in sorted(d.glob("*.qmd"))]
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


# Taxonomía cerrada de `nivel`, según el mapa maestro.
NIVELES = {"principiante", "intermedio", "avanzado"}

# Títulos de los capítulos de Fundamentos. El banco numera cada capítulo en el
# front-matter (`capitulo`) pero no guarda su título, que obligaría a repetir el
# mismo texto en cada ficha del capítulo. Un número sin mapear se degrada a
# "Capítulo N" en vez de romper la compilación.
CAPITULOS = {
    2: "Física del ultrasonido",
    3: "El lenguaje de la imagen",
    4: "Técnica, sondas y ventanas",
    5: "Artefactos",
    6: "Instrumentación y medición",
}

# Nombre de presentación de cada `organo`. La taxonomía del mapa maestro usa
# slugs ASCII (`riñon`, `pulmon`, `via-biliar`) porque son claves de datos; el
# libro necesita el nombre escrito como se lee en español. Derivarlo con
# `.title()` daba "Pulmon", "Riñon" y "Aorta Abdominal" —sin tilde y con
# mayúscula intercalada, que en español no lleva—. Las formas de aquí son las
# que el propio mapa maestro usa en prosa.
ORGANOS = {
    "aorta-abdominal": "Aorta abdominal",
    "apendice": "Apéndice",
    "corazon": "Corazón",
    "higado": "Hígado",
    "intestino": "Intestino",
    "pared": "Pared",
    "pericardio": "Pericardio",
    "pleura": "Pleura",
    "pulmon": "Pulmón",
    "riñon": "Riñón",
    "utero": "Útero",
    "vejiga": "Vejiga",
    "vena-profunda": "Vena profunda",
    "vesicula": "Vesícula",
    "via-biliar": "Vía biliar",
}


def nombre_organo(clave: str) -> str:
    """Nombre legible de un órgano; un slug sin mapear no rompe la compilación.

    El respaldo usa `capitalize()`, no `title()`: en español solo va en
    mayúscula la primera palabra.
    """
    if not clave:
        return "Otros"
    return ORGANOS.get(clave) or clave.replace("-", " ").capitalize()


# Partes del atlas, en el orden canónico de la taxonomía `sistema` del mapa
# maestro —no alfabético—. Un atlas impreso se recorre por aparatos; lo que
# cruza sistemas va al final. Un `sistema` que no esté aquí no se pierde: cae
# en "Otros signos".
SISTEMAS = [
    ("respiratorio", "Sistema respiratorio"),
    ("cardiovascular", "Sistema cardiovascular"),
    ("digestivo", "Sistema digestivo"),
    ("genitourinario", "Sistema genitourinario"),
    ("vascular", "Sistema vascular"),
    ("musculoesqueletico", "Musculoesquelético y pared"),
    ("endocrino", "Sistema endocrino"),
    ("nervioso", "Sistema nervioso"),
    ("multiorgano", "Multiórgano y protocolos"),
]


# ─────────────────────── SALIDA 2: GRAFO ───────────────────────
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


# ─────────────────────── SALIDA 3: GHOST ───────────────────────
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

        # Al final del cuerpo, después de la Evidencia regenerada.
        if e["tipo"] == "signo":
            cuerpo = cuerpo.rstrip() + "\n\n" + LINEA_RETO.format(id=e["id"])

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
        # La taxonomía del mapa maestro es cerrada. Un valor inventado no rompe
        # la compilación, y por eso es peligroso: corrompe en silencio las
        # facetas del buscador y saca al signo de su parte en el libro.
        if e.get("nivel") and e["nivel"] not in NIVELES:
            alertas.append(f"[TAXONOMÍA] {e['id']}: nivel={e['nivel']!r} "
                           f"no está en la taxonomía {sorted(NIVELES)}")
        if e["tipo"] == "signo":
            if not e.get("sistema"):
                alertas.append(f"[TAXONOMÍA] {e['id']}: sin 'sistema' "
                               f"(queda fuera de su parte en el libro)")
            elif e["sistema"] not in {c for c, _ in SISTEMAS}:
                alertas.append(f"[TAXONOMÍA] {e['id']}: sistema={e['sistema']!r} "
                               f"no está en la taxonomía")
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

        # Una imagen sin trazabilidad completa no se puede redistribuir: el
        # generador de ePub debe FALLAR antes que incrustarla sin atribución
        # auditable. Hasta ahora solo se validaban los medios marcados
        # `destacada`, y por eso 22 fichas publicadas llegaron sin estos campos.
        for m in (e.get("medios") or []):
            if m.get("tipo") != "imagen":
                continue
            faltan = [c for c in ("archivo_local", "fuente_url", "licencia_url")
                      if not m.get(c)]
            if faltan:
                alertas.append(
                    f"[MEDIOS] {e['id']}: imagen sin {', '.join(faltan)} "
                    f"({m.get('id')})")

        # Toda adaptación debe conservar la cadena de trazabilidad completa.
        # En particular, un fotograma es una obra derivada del video: además
        # de atribuir y declarar la licencia, el original debe quedar local
        # para que el cambio sea auditable. Si el original es audiovisual, su
        # artículo fuente también debe viajar a LuaLaTeX mediante `refs`.
        for i, medio in enumerate(e.get("medios") or [], 1):
            if not medio.get("adaptacion"):
                continue
            prefijo = f"[IMAGEN] {e['id']} medio {i}"
            obligatorios = (
                "archivo_local", "original_local", "credito", "fuente",
                "fuente_url", "licencia_img", "licencia_url",
            )
            for campo in obligatorios:
                if not medio.get(campo):
                    errores.append(
                        f"{prefijo}: adaptación sin '{campo}'")

            for campo in ("archivo_local", "original_local"):
                declarado = medio.get(campo)
                if not declarado:
                    continue
                ruta = (raiz / declarado).resolve()
                try:
                    ruta.relative_to(raiz)
                except ValueError:
                    errores.append(
                        f"{prefijo}: '{campo}' apunta fuera del banco")
                    continue
                if not ruta.is_file():
                    errores.append(
                        f"{prefijo}: no existe {declarado}")

            original = medio.get("original_local") or ""
            if Path(original).suffix.lower() in (".ogv", ".webm", ".mp4", ".mov"):
                referencia = medio.get("referencia")
                if not referencia:
                    errores.append(
                        f"{prefijo}: fotograma de video sin 'referencia'")
                elif referencia not in (e.get("refs") or []):
                    errores.append(
                        f"{prefijo}: referencia '{referencia}' no incluida en refs")

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
    ap.add_argument("--solo", choices=["db", "grafo", "ghost"])
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
