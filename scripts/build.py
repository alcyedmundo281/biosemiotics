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
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from rutas import raiz_argumentos, raiz_desde_argumentos

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

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
def estado_publicacion(e):
    """Compatibilidad: URL histórica implica publicado; sin URL, borrador."""
    estado = e.get("estado", "publicado" if e.get("url") else "borrador")
    prefijo = f"[PUBLICACIÓN] {e.get('_archivo', '?')} ({e.get('id', '?')})"

    def fallo(mensaje):
        raise RuntimeError(f"{prefijo}: {mensaje}")

    if estado not in ("borrador", "revisado", "publicado"):
        fallo("estado debe ser borrador, revisado o publicado")
    url = e.get("url")
    if url is not None and not isinstance(url, str):
        fallo("url debe ser texto")
    if url:
        partes = urlsplit(url)
        if (url != url.strip() or partes.scheme != "https" or not partes.netloc or
                "/ghost/" in partes.path or partes.path.startswith("/p/")):
            fallo("url debe ser HTTPS pública, no el editor ni una vista previa")
    if bool(e.get("url")) != (estado == "publicado"):
        fallo("estado publicado requiere URL; borrador/revisado no admiten URL")
    if "publicado" in e and (not isinstance(e["publicado"], bool) or
                            e["publicado"] != (estado == "publicado")):
        fallo("publicado legado contradice estado/URL; elimina el booleano tras migrar")
    if e.get("tipo") == "caso" and estado != "borrador" and e.get("consentimiento") != "obtenido":
        fallo("consentimiento: obtenido es obligatorio para un caso revisado o publicado")
    revision = e.get("fecha_revision")
    if revision is not None:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(revision)):
                raise ValueError
            date.fromisoformat(str(revision))
        except ValueError:
            fallo("fecha_revision debe ser una fecha ISO YYYY-MM-DD o null si no consta")
    ghost_id = e.get("ghost_id")
    if ghost_id is not None and (not isinstance(ghost_id, str) or
                               not re.fullmatch(r"[0-9a-f]{24}", ghost_id)):
        fallo("ghost_id debe ser el identificador real de 24 caracteres hexadecimales o null")
    return estado


def seleccionar_publicables(entidades, solo_publicados=False):
    """Valida contradicciones antes de filtrar; nunca oculta un caso público inválido."""
    estados = [(e, estado_publicacion(e)) for e in entidades]
    permitidos = ("publicado",) if solo_publicados else ("revisado", "publicado")
    return [e for e, estado in estados if estado in permitidos]


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
            # los casos guardan su bifurcación en 'decision_semiotica'
            e.get("decision") or e.get("decision_semiotica"),
            e.get("umbral"), e.get("consentimiento"),
            int(estado == "publicado"), e.get("doi"),
            e["cuerpo"], e["_archivo"],
            estado, e.get("url"),
            str(e["fecha_revision"]) if e.get("fecha_revision") else None, e.get("ghost_id"),
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
    entidades = seleccionar_publicables(entidades)
    exigir_editorial(entidades, bib_path)
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
SECCIONES = {
    "signo": ("La pregunta clínica", "Por qué el examen físico no basta",
              "Cómo se obtiene la ventana", "El signo", "La bifurcación",
              "Dónde NO confiar", "Practica esto", "Discusión abierta"),
    "caso": ("Viñeta clínica", "El problema antes de la sonda", "La adquisición",
             "El signo", "La bifurcación", "Los límites", "Pregunta al parlamento"),
}


def errores_editoriales(entidades, bib_path: Path):
    """Contrato estructural; no sustituye la revisión clínica ni el consentimiento."""
    bib = cargar_bibliografia(bib_path) if bib_path.is_file() else {}
    errores = []
    for e in entidades:
        prefijo = f"[EDITORIAL] {e.get('_archivo', '?')} ({e.get('id', '?')})"

        def error(campo, mensaje):
            errores.append(f"{prefijo}: {campo}: {mensaje}")

        def texto(valor):
            return isinstance(valor, str) and bool(valor.strip()) and not re.search(
                r"\bTODO\b", valor)

        tipo = e.get("tipo")
        if tipo not in ("concepto", "signo", "caso"):
            error("tipo", "debe ser concepto, signo o caso")
        campos = ["id", "titulo", "abstract", "cuerpo"]
        if tipo == "signo":
            campos += ["organo", "ventana", "significante", "significado", "decision"]
        elif tipo == "caso":
            campos += ["organo", "decision_semiotica"]
        elif tipo == "concepto":
            campos += ["dominio"]
        for campo in campos:
            if not texto(e.get(campo)):
                error(campo, "requiere texto no vacío, sin TODO")
        resumen = e.get("abstract")
        if isinstance(resumen, str) and not 40 <= len(resumen.split()) <= 80:
            error("abstract", "debe contener entre 40 y 80 palabras")
        if not isinstance(e.get("nivel"), str) or e["nivel"] not in NIVELES:
            error("nivel", f"debe pertenecer a {sorted(NIVELES)}")
        if tipo == "signo" and e.get("sistema") not in [c for c, _ in SISTEMAS]:
            error("sistema", "valor obligatorio de la taxonomía del mapa maestro")
        listas = ["refs"]
        if tipo == "signo":
            listas += ["falsos_positivos", "sonda"]
        if tipo == "caso":
            listas += ["signos"]
        for campo in listas:
            valores = e.get(campo)
            if not isinstance(valores, list) or not valores or not all(map(texto, valores)):
                error(campo, "requiere una lista no vacía de textos, sin TODO")
        refs = e.get("refs")
        if isinstance(refs, list):
            for clave in refs:
                if isinstance(clave, str) and clave not in bib:
                    error("refs", f"'{clave}' no está en refs.bib")
        cuerpo = e.get("cuerpo")
        if isinstance(cuerpo, str):
            # Los ejemplos en bloques de código no cumplen secciones editoriales.
            sin_codigo = re.sub(r"(?ms)^(`{3,}|~{3,}).*?^\1\s*$", "", cuerpo)
            sin_codigo = re.sub(r"(?s)<!--.*?-->", "", sin_codigo)
            encabezados = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", sin_codigo))
            for seccion in SECCIONES.get(tipo if isinstance(tipo, str) else "", ()):
                encontrados = [i for i, h in enumerate(encabezados) if h[1] == seccion]
                if len(encontrados) != 1:
                    error(f"## {seccion}", "debe aparecer exactamente una vez")
                else:
                    i = encontrados[0]
                    fin = encabezados[i + 1].start() if i + 1 < len(encabezados) else len(sin_codigo)
                    contenido = sin_codigo[encabezados[i].end():fin]
                    contenido = re.sub(r"(?m)^#{1,6}\s+.*$", "", contenido)
                    contenido = re.sub(r"(?s)<!--.*?-->", "", contenido)
                    if not contenido.strip():
                        error(f"## {seccion}", "sección vacía")
    return errores


def exigir_editorial(entidades, bib_path: Path):
    errores = errores_editoriales(entidades, bib_path)
    if errores:
        raise RuntimeError("Contrato editorial incumplido:\n" + "\n".join(errores))


def validar(entidades, aristas, raiz: Path, permitir_borradores=False):
    """(errores, alertas). Errores rompen el grafo o bloquean publicación."""
    ids = {e["id"] for e in entidades}
    errores = [f"{a['origen']} --{a['clase']}--> {a['destino']} (NO EXISTE)"
               for a in aristas if a["destino"] not in ids]
    alertas = []
    estados = [(e, estado_publicacion(e)) for e in entidades]
    borradores = [e for e, estado in estados if permitir_borradores and estado == "borrador"]
    exigidas = [e for e, estado in estados if not permitir_borradores or estado != "borrador"]
    errores.extend(errores_editoriales(exigidas, raiz / "refs.bib"))
    alertas.extend(errores_editoriales(borradores, raiz / "refs.bib"))

    for e in entidades:

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

    return errores, alertas


def main():
    ap = argparse.ArgumentParser()
    raiz_argumentos(ap)
    ap.add_argument("--solo", choices=["db", "grafo", "ghost"])
    a = ap.parse_args()

    raiz = raiz_desde_argumentos(ap, a)
    build_dir = raiz / "build"

    ent = cargar(raiz)
    n = {t: sum(e["tipo"] == t for e in ent) for t in ("concepto", "signo", "caso")}
    print(f"Banco: {len(ent)} entidades  "
          f"({n['concepto']} conceptos, {n['signo']} signos, {n['caso']} casos)")

    # Solo las salidas locales de trabajo admiten borradores incompletos.
    aristas = [{"origen": e["id"], "destino": d, "clase": clase}
               for e in ent for clase in RELS for d in (e.get(clase) or [])]
    errores, alertas = validar(ent, aristas, raiz, permitir_borradores=True)
    if errores:
        raise RuntimeError("Validación fallida:\n" + "\n".join(errores))
    build_dir.mkdir(exist_ok=True)
    build_grafo(ent, build_dir)

    if a.solo in (None, "db"):
        print(f"  → atlas.db     ({len(aristas)} relaciones)")
        build_sqlite(ent, build_dir)
    if a.solo in (None, "grafo"):
        print("  → grafo.json")
    if a.solo in (None, "ghost"):
        ghost = build_ghost(ent, build_dir, raiz / "refs.bib")
        print(f"  → ghost/       ({len(seleccionar_publicables(ent))} artículos Ghost-ready)")

    if alertas:
        print(f"\n⚠ {len(alertas)} alertas de calidad:")
        for x in alertas:
            print(f"   {x}")
    if not alertas:
        print("\n✓ Integridad referencial y calidad OK")
    else:
        print("\n✓ Integridad referencial OK")



if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        sys.exit(str(exc))
