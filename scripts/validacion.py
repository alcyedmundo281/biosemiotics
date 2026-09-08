"""Contrato editorial, integridad del grafo y trazabilidad de medios."""

import re
from pathlib import Path

from banco import estado_publicacion
from bibliografia import bibliografia_manual, cargar_bibliografia
from configuracion import NIVELES, SISTEMAS

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
    """Devuelve errores que bloquean y alertas de calidad."""
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
        for medio in (e.get("medios") or []):
            if medio.get("tipo") != "imagen":
                continue
            faltan = [c for c in ("archivo_local", "fuente_url", "licencia_url")
                      if not medio.get(c)]
            if faltan:
                alertas.append(
                    f"[MEDIOS] {e['id']}: imagen sin {', '.join(faltan)} "
                    f"({medio.get('id')})")

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
                    errores.append(f"{prefijo}: adaptación sin '{campo}'")

            for campo in ("archivo_local", "original_local"):
                declarado = medio.get(campo)
                if not declarado:
                    continue
                ruta = (raiz / declarado).resolve()
                try:
                    ruta.relative_to(raiz)
                except ValueError:
                    errores.append(f"{prefijo}: '{campo}' apunta fuera del banco")
                    continue
                if not ruta.is_file():
                    errores.append(f"{prefijo}: no existe {declarado}")

            original = medio.get("original_local") or ""
            if Path(original).suffix.lower() in (".ogv", ".webm", ".mp4", ".mov"):
                referencia = medio.get("referencia")
                if not referencia:
                    errores.append(f"{prefijo}: fotograma de video sin 'referencia'")
                elif referencia not in (e.get("refs") or []):
                    errores.append(
                        f"{prefijo}: referencia '{referencia}' no incluida en refs")

        manual = bibliografia_manual(e["cuerpo"])
        declaradas = e.get("refs") or []
        if manual and len(manual) != len(declaradas):
            alertas.append(
                f"[EDITORIAL] {e['id']}: '## Evidencia' a mano lista "
                f"{len(manual)} entradas y 'refs' declara {len(declaradas)}; "
                f"se publica la de refs.bib")

    return errores, alertas
