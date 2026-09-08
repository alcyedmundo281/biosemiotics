#!/usr/bin/env python3
"""
verificar_citas.py — verificación de DOBLE autoridad de refs.bib.

No basta con que la clave exista (eso lo mira refs.py). Aquí se comprueba que
cada referencia siga siendo REAL y COHERENTE contra dos fuentes independientes:

  PubMed  (por PMID) → la entrada existe y su DOI coincide con el declarado.
  Crossref (por DOI)  → el DOI resuelve y coincide con el devuelto por PubMed.

Los títulos se comparan normalizados como control editorial: minúsculas, sin
puntuación y sin el subtítulo posterior al primer punto. Los catálogos antiguos
pueden contener errores de OCR en el título; por eso la prueba de identidad es
la coincidencia exacta del DOI declarado, PubMed y Crossref.

Un DOI que Crossref dice NO CONOCER (404) no es un problema de red: es una
verificación fallida y cuenta como discrepancia. Confundir las dos cosas dejaba
pasar el control a una referencia que nadie había comprobado. Existen revistas
legítimas cuyos DOI no se depositan en Crossref; para esas —y solo para esas—
hay una lista de exención explícita en `refs-sin-crossref.txt`, que obliga a
declarar el caso por escrito en vez de resolverlo con silencio.

  python3 verificar_citas.py            # verifica todo refs.bib
  python3 verificar_citas.py --estricto # alias compatible; siempre estricto

Códigos de salida:
  0  todo verificado (o exención explícita de Crossref con PubMed verificado)
  1  entrada inválida, duplicada, PMID inexistente, DOI distinto,
     o un DOI que Crossref no resuelve y no está exento
  2  verificación incompleta por servicio no disponible o respuesta inválida
"""
import argparse
import re
import sys
import time
import json
import http.client
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from refs import resumen  # cliente E-utilities del proyecto  # noqa: E402
from rutas import raiz_argumentos, raiz_desde_argumentos  # noqa: E402

UA = {"User-Agent": "biosemiotics-verificar/1.0 (mailto:alcyedmundo@gmail.com)"}


def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return " ".join(s.split()).strip()


def norm_title(s: str) -> str:
    """Normaliza el título principal, ignorando el subtítulo tras el punto."""
    principal = re.sub(r"<[^>]+>", "", s or "").split(".", 1)[0]
    return norm(principal)


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
    """Fallo TRANSITORIO: timeout, conexión caída, 429 o 5xx. Se reintenta."""

    def __init__(self, mensaje, reintentable=True):
        self.reintentable = reintentable
        super().__init__(mensaje)


def reintentar(operacion, *args):
    """Tres intentos como máximo, esperas de 1 y 2 segundos; nunca reintenta DOI inválido."""
    for intento in range(3):
        try:
            return operacion(*args)
        except urllib.error.HTTPError as exc:
            fallo = RedError(f"HTTP {exc.code}", exc.code == 429 or exc.code >= 500)
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException,
                ValueError, KeyError, TypeError, IndexError) as exc:
            fallo = RedError(str(exc))
        except RedError as exc:
            fallo = exc
        if not fallo.reintentable or intento == 2:
            raise fallo
        time.sleep(2 ** intento)


class DoiNoResuelve(Exception):
    """Crossref responde que ese DOI no existe (404) o es inválido (400/422).

    NO es un problema de red: es una verificación que falló. Tratarlo como
    error de red hacía que una referencia sin comprobar pasara el control.
    """

    def __init__(self, codigo: int):
        self.codigo = codigo
        super().__init__(f"HTTP {codigo}")


def cargar_exenciones(raiz: Path) -> dict:
    """Lee refs-sin-crossref.txt: claves o prefijos de DOI exentos, con razón.

    Formato: un token por línea (clave BibLaTeX o prefijo de DOI), razón
    obligatoria tras '#'. Sirve para revistas reales cuyos DOI no se depositan
    en Crossref; obliga a dejar constancia escrita en vez de silenciar.
    """
    f = raiz / "refs-sin-crossref.txt"
    if not f.exists():
        return {}
    out = {}
    for numero, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        cuerpo, _, razon = linea.partition("#")
        token = cuerpo.strip()
        if token:
            if not razon.strip():
                raise ValueError(f"{f.name}:{numero}: exención sin razón declarada")
            if token.lower() in out:
                raise ValueError(f"{f.name}:{numero}: exención duplicada: {token}")
            if token.startswith("10.") and not re.fullmatch(r"10\.\d{4,9}/", token):
                raise ValueError(f"{f.name}:{numero}: prefijo DOI debe identificar un registrador")
            out[token.lower()] = razon.strip()
    return out


def exento(clave: str, doi: str, exenciones: dict) -> "str | None":
    """Devuelve la razón si la entrada está exenta de resolver en Crossref."""
    if clave.lower() in exenciones:
        return exenciones[clave.lower()]
    for token, razon in exenciones.items():
        if token.startswith("10.") and doi.lower().startswith(token):
            return razon
    return None


def crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as respuesta:
            datos = json.loads(respuesta.read())
        m = datos["message"]
        if not isinstance(m, dict) or not isinstance(m.get("DOI"), str) or not m["DOI"]:
            raise ValueError("respuesta Crossref sin DOI")
    except urllib.error.HTTPError as e:
        # Los problemas de autenticación o servicio no demuestran que el DOI no exista.
        if e.code == 429 or e.code >= 500:
            raise RedError(f"HTTP {e.code}") from e
        if e.code in (400, 404, 422):
            raise DoiNoResuelve(e.code) from e
        raise RedError(f"HTTP {e.code}", reintentable=False) from e
    except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError) as e:
        raise RedError(str(e)) from e
    yr = ""
    for k in ("published-print", "published-online", "issued", "created"):
        dp = m.get(k, {}).get("date-parts", [[None]])[0]
        if dp and dp[0]:
            yr = str(dp[0]); break
    ct = m.get("container-title") or [""]
    return {"title": (m.get("title") or [""])[0], "journal": ct[0] if ct else "",
            "year": yr, "doi": m.get("DOI", "")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    raiz_argumentos(ap)
    ap.add_argument("--estricto", action="store_true",
                    help="compatibilidad: la verificación siempre es estricta (red: exit 2)")
    a = ap.parse_args(argv)

    try:
        raiz = raiz_desde_argumentos(ap, a)
    except RuntimeError as exc:
        print(f"✗ Entrada inválida: {exc}")
        return 1
    bib = raiz / "refs.bib"
    try:
        refs = parse_bib(bib)
        exenciones = cargar_exenciones(raiz)
    except (OSError, ValueError) as exc:
        print(f"✗ Entrada inválida: {exc}")
        return 1
    print(f"refs.bib: {len(refs)} entradas\n")

    dup = {c for c in (r["clave"] for r in refs)
           if [x["clave"] for x in refs].count(c) > 1}
    if dup:
        print(f"✗ claves duplicadas: {sorted(dup)}")
        return 1
    entradas = re.findall(r"@\w+\s*\{", bib.read_text(encoding="utf-8"))
    incompletas = [r["clave"] for r in refs if not r["pmid"] or not r["doi"]]
    if not refs or len(entradas) != len(refs) or incompletas:
        print(f"✗ Bibliografía vacía, formato no admitido o entradas sin PMID/DOI: {incompletas}")
        return 1
    desconocidas = set(exenciones) - {r["clave"].lower() for r in refs}
    if any(not token.startswith("10.") for token in desconocidas):
        print(f"✗ Exenciones con claves inexistentes: {sorted(desconocidas)}")
        return 1

    pmids = [r["pmid"] for r in refs if r["pmid"]]
    try:
        pm = {x["pmid"]: x for x in reintentar(resumen, pmids)}
    except RedError as e:
        print(f"✗ Verificación INCOMPLETA: PubMed no disponible: {e}")
        return 2

    disc, avisos_titulo, exentas, red = [], [], [], []
    ok_pm = ok_cr = ok_x = 0
    for numero, r in enumerate(refs, 1):
        flags = []
        p = pm.get(r["pmid"])
        if not r["pmid"]:
            flags.append("sin-pmid")
        elif not p:
            flags.append("pmid-inexistente")
        else:
            dpm = (p.get("doi") or "").lower()
            if dpm != r["doi"].lower():
                flags.append(f"doi≠pubmed({dpm})")
            else:
                ok_pm += 1

        if r["doi"]:
            try:
                cr = reintentar(crossref, r["doi"])
                doi_ref = r["doi"].strip().lower()
                doi_pm = (p.get("doi") or "").strip().lower() if p else ""
                doi_cr = cr["doi"].strip().lower()
                if doi_ref and doi_pm == doi_ref == doi_cr:
                    ok_cr += 1
                else:
                    flags.append(
                        f"doi-pubmed≠crossref({doi_pm or '∅'}≠{doi_cr or '∅'})")
                if p and cr["title"] and doi_pm == doi_ref == doi_cr:
                    a1 = norm_title(p.get("titulo"))
                    b1 = norm_title(cr["title"])
                    if a1 and b1 and a1 == b1:
                        ok_x += 1
                    else:
                        # Un DOI idéntico en ambas autoridades demuestra la
                        # identidad aunque un catálogo tenga un OCR defectuoso.
                        # Se informa la variante sin convertirla en excepción
                        # por clave ni en un falso negativo de identidad.
                        avisos_titulo.append((r["clave"], a1, b1))
                time.sleep(0.12)
            except RedError as e:
                red.append(f"{r['clave']}: {e}; {len(refs) - numero} entradas posteriores sin consultar")
            except DoiNoResuelve as e:
                razon = exento(r["clave"], r["doi"], exenciones)
                if razon and e.codigo == 404 and p and not flags:
                    exentas.append((r["clave"], r["doi"], e.codigo, razon))
                else:
                    flags.append(f"crossref-no-resuelve(HTTP {e.codigo})")
        else:
            flags.append("sin-doi")

        if flags and not (set(flags) <= {"sin-doi"}):
            disc.append((r["clave"], flags))
        if red:
            # Agotados los intentos, no martillar un servicio caído con el resto del banco.
            break

    print(f"PubMed OK: {ok_pm}/{len(refs)}   Crossref OK: {ok_cr}/{len(refs)}   "
          f"cruce título: {ok_x}")
    if red:
        print("✗ Verificación INCOMPLETA en Crossref: " + "; ".join(red))

    if exentas:
        print(f"\n⚠ {len(exentas)} ENTRADAS EXENTAS DE CROSSREF "
              f"(declaradas en refs-sin-crossref.txt):")
        for clave, doi, codigo, razon in exentas:
            print(f"   {clave:<20} {doi}  HTTP {codigo} — {razon}")
        print("   Verificadas solo contra PubMed. Revisa que la exención siga "
              "siendo válida.")

    if avisos_titulo:
        print(f"\n⚠ {len(avisos_titulo)} VARIANTES DE TÍTULO CON DOI IDÉNTICO:")
        for clave, pubmed_title, crossref_title in avisos_titulo:
            print(f"   {clave:<20} PubMed={pubmed_title!r}  Crossref={crossref_title!r}")

    if disc:
        print(f"\n✗ {len(disc)} DISCREPANCIAS:")
        for clave, flags in disc:
            print(f"   {clave:<20} {', '.join(flags)}")
        if any("crossref-no-resuelve" in f for _, fl in disc for f in fl):
            print("\n   Un DOI que Crossref no resuelve no se publica. Si la "
                  "revista es real y\n   simplemente no deposita ahí, decláralo "
                  "en refs-sin-crossref.txt con su razón.")
        return 1

    if red:
        return 2
    elif exentas:
        print(f"\n✓ Sin discrepancias. {len(exentas)} entradas verificadas solo "
              f"contra PubMed por exención declarada.")
    else:
        print("\n✓ Todas las referencias verificadas en ambas autoridades.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
