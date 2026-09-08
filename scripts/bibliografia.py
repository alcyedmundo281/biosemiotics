"""Lectura de BibLaTeX y proyección de referencias para Ghost y Quarto."""

import re
from pathlib import Path

CITA_BIBLATEX = re.compile(r"\[([A-Za-z][A-Za-z0-9_:-]*)\]")
BIBLIO_HEADING = re.compile(
    r"^(#{2,6})\s+(?:Evidencia|Referencias|Bibliograf[ií]a)\s*$",
    re.IGNORECASE,
)


def cargar_bibliografia(path: Path) -> dict:
    """Lee los campos usados por la salida Ghost desde refs.bib."""
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
            if lineas[i].startswith("**Nota de alcance:**"):
                break
            i += 1
        while salida and not salida[-1].strip():
            salida.pop()
        if salida:
            salida.append("")
    return "\n".join(salida).strip()


def bibliografia_manual(cuerpo: str) -> list:
    """Devuelve entradas numeradas de una bibliografía escrita a mano."""
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
