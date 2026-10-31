#!/usr/bin/env python3
"""Proyecta el banco a un proyecto Quarto book (`build/quarto/`).

    python scripts/qmd.py [--destino build/quarto] [--solo-publicados]

El banco `.qmd` de `conceptos/`, `signos/` y `casos/` sigue siendo la única
fuente de verdad; este script NO lo modifica. Lo que produce es un proyecto
Quarto derivado y desechable, del que salen EPUB, PDF y HTML con un solo
`quarto render`. Es el reemplazo del ensamblado manual que vivía en
`epub.py::manuscrito()` y del renderizador LaTeX propio de `build.py`.

Tres decisiones que no son de estilo:

1.  **Jerarquía.** Cada ficha es una sección `##` dentro del capítulo de su
    capítulo temático (conceptos) u órgano (signos), y su cuerpo se degrada un
    nivel. El ensamblado anterior ponía la ficha en `###` y dejaba el cuerpo en
    `##`, de modo que "La pregunta clínica" quedaba POR ENCIMA del título de su
    propia ficha; con `--split-level=2` eso partía el EPUB dentro de cada signo.
2.  **Citas.** NO se delega en citeproc. El banco cita en línea muy poco y su
    evidencia vive sobre todo en `refs`; con citeproc el libro terminaría con
    una bibliografía global y sin la sección «Evidencia» de cada ficha, que es
    justo lo que un atlas de signos necesita. Se reutiliza el motor ya
    verificado del proyecto —`bibliografia.resolver_citas()` y
    `bibliografia.referencia_ghost()`— que numera por ficha y emite el estilo de la
    casa con DOI y PMID.
3.  **Imágenes.** Se copian dentro del proyecto en lugar de referenciarse con
    `../../assets/`. Así el directorio generado es autocontenido y se puede
    empaquetar o mover sin arrastrar el checkout.

El contrato de figuras de CLAUDE.md se mantiene aquí sin excepción: a una
figura le faltan datos de atribución y la generación aborta. No se omite la
imagen ni se infiere su crédito.

La declaración de uso de IA del libro NO vive aquí: es texto firmado por el
autor y está en `paratextos/declaracion-ia.md`, la única fuente que leen EPUB
y PDF. Su marcador `{N}` se sustituye por las citas de la edición, y la
generación aborta si alguna no es verificable: así la frase es un hecho.
"""

from __future__ import annotations

import argparse
import re
import secrets
import shutil
import subprocess
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

import banco
import bibliografia as refs_bibliograficas
import configuracion
import verificar_citas
from rutas import blindar_salida, desde_raiz, escribir_texto, raiz_argumentos, resolver_raiz
from validacion import exigir_editorial


TITULO = "Biosemiótica del Cuerpo Vivo"
SUBTITULO = "Atlas de POCUS para el clínico"
AUTOR = "Dr. Alcy Edmundo Torres Guerrero"
ORCID = "0000-0002-9742-375X"
# El ISBN está registrado a nombre de este sello: cualquier otra cadena en
# créditos o metadatos es una incoherencia de catalogación.
EDITORIAL = "Powersemiotics"
ISBN_EPUB = "979-8-953844-01-7"
ISBN_RUSTICA = "979-8-953844-00-0"
# El DOI de concepto resuelve siempre a la versión más reciente: identifica la
# obra, no esta edición. `DOI_EDICION` es el depósito de ESTA edición y queda en
# None hasta que exista; entonces los créditos pasan a citarlo.
DOI_CONCEPTO = "10.5281/zenodo.21435362"
DOI_EDICION = None
# Las entradas publicadas hasta esta fecha forman la primera edición.
FECHA_CORTE = "2026-11-13"
OBRA_EN_LINEA = "biosemiotics — atlas de POCUS para el médico de primer contacto"
LICENCIA = "CC BY 4.0"
LICENCIA_URL = "https://creativecommons.org/licenses/by/4.0/"
DOI_URL = f"https://doi.org/{DOI_CONCEPTO}"
LICENCIA_LARGA = f"{LICENCIA} — {LICENCIA_URL}"
AVISO = (
    "Material exclusivamente educativo. No sustituye el juicio clínico, "
    "la evaluación integral del paciente ni los protocolos locales."
)

# Paratexto del libro, relativo a la raíz del banco. AI-USE.md remite a este
# archivo para que la declaración larga y la del colofón no diverjan.
DECLARACION_IA = Path("paratextos") / "declaracion-ia.md"
# Opcional: mientras no exista, el libro sale sin prólogo y sin advertencias.
PROLOGO = Path("paratextos") / "prologo.md"
MARCADOR_CITAS = "{N}"
# Cualquier `{MAYÚSCULAS}` que sobreviva a la sustitución es un marcador que
# nadie resolvió; `{.unnumbered}` y `{#sec-…}` no encajan.
MARCADOR_PENDIENTE = re.compile(r"\{[A-ZÁÉÍÓÚÑ_]+\}")
# Profundidad del índice: parte → capítulo → ficha. La misma para los tres
# formatos; en PDF la usa el índice que emite `portadilla()`.
TOC_PROFUNDIDAD = 2
# Altura máxima de una imagen en el PDF, como fracción de \textheight. Cada
# ficha abre página con título, enlace, figura y pie (diseño de #130, elegido
# por Alcy frente al 0.90 de #129): con 0.62 caben los cuatro juntos y ninguna
# figura salta a la página siguiente dejando el título solo. Si cambias el
# tope, mide de nuevo que las 50 sigan en la página de apertura de su ficha.
ALTURA_MAXIMA_FIGURA = 0.62
# Las plantillas de Quarto escalan de dos maneras según la versión de pandoc:
# las recientes envuelven cada imagen en `\pandocbounded`; las anteriores (la
# CI fija Quarto 1.5) fijan `height=\maxheight` en las claves de graphicx. El
# tope se aplica a la que exista, al empezar el documento, cuando \textheight
# ya es definitivo y la plantilla ya definió sus macros. La macro de reemplazo
# se define fuera del gancho para no anidar parámetros `#1` en él.
PANDOCBOUNDED_CON_TOPE = (
    "\\makeatletter\n"
    "\\newdimen\\bios@alturamax\n"
    "\\newsavebox\\bios@caja\n"
    "\\newcommand*\\bios@pandocbounded[1]{%\n"
    "  \\sbox\\bios@caja{#1}%\n"
    "  \\Gscale@div\\@tempa{\\bios@alturamax}"
    "{\\dimexpr\\ht\\bios@caja+\\dp\\bios@caja\\relax}%\n"
    "  \\Gscale@div\\@tempb{\\linewidth}{\\wd\\bios@caja}%\n"
    "  \\ifdim\\@tempb\\p@<\\@tempa\\p@\\let\\@tempa\\@tempb\\fi\n"
    "  \\ifdim\\@tempa\\p@<\\p@\\scalebox{\\@tempa}{\\usebox\\bios@caja}%\n"
    "  \\else\\usebox{\\bios@caja}%\n"
    "  \\fi%\n"
    "}\n"
    "\\AtBeginDocument{%\n"
    f"  \\bios@alturamax={ALTURA_MAXIMA_FIGURA}\\textheight\n"
    "  \\ifdefined\\pandocbounded\\let\\pandocbounded\\bios@pandocbounded\\fi\n"
    "  \\ifdefined\\maxheight\\def\\maxheight{\\ifdim\\Gin@nat@height>"
    "\\bios@alturamax\\bios@alturamax\\else\\Gin@nat@height\\fi}\\fi\n"
    "}\n"
    "\\makeatother"
)

# Diseño del libro impreso. El preámbulo y el filtro son del generador, no del
# banco: se leen junto a este script aunque se use `--raiz`, y se copian al
# proyecto. El filtro actúa SOLO en LaTeX, así que EPUB y HTML reciben
# exactamente el mismo Markdown.
DISENO_LIBRO = Path(__file__).resolve().parent.parent / "assets" / "libro"
PREAMBULO_LIBRO = "preambulo-libro.tex"
FILTRO_LIBRO = "diseno-pdf.lua"
# Libertinus cubre ≥ → ± − ≈ ≠, griego y cirílico en serif y sans, y tiene
# variante de portada. En Linux la aporta el paquete `fonts-libertinus`.
FUENTE_LIBRO = "Libertinus Serif"
FUENTE_LIBRO_SANS = "Libertinus Sans"

# Los mismos campos que exige el EPUB desde siempre. Si falta uno, la figura no
# se publica: es la condición de la licencia, no una preferencia editorial.
REQUERIDOS_IMAGEN = (
    "descripcion",
    "credito",
    "fuente",
    "fuente_url",
    "licencia_img",
    "licencia_url",
    "archivo_local",
)

ENCABEZADO = re.compile(r"^(#{1,5})(\s+)", re.MULTILINE)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    raiz_argumentos(parser)
    parser.add_argument(
        "--destino",
        type=Path,
        default=Path("build/quarto"),
        help="subdirectorio de build/ para el proyecto generado (se reemplaza al terminar)",
    )
    parser.add_argument(
        "--solo-publicados",
        action="store_true",
        help="incluye únicamente fichas con URL pública de Ghost",
    )
    return parser.parse_args()


def version_git(raiz: Path) -> str:
    try:
        return subprocess.run(
            ["git", "describe", "--always", "--dirty"],
            cwd=raiz,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "sin-versión-git"


def slug(texto: str) -> str:
    """Nombre de archivo estable y ASCII para un capítulo generado."""
    plano = unicodedata.normalize("NFKD", str(texto))
    plano = plano.encode("ascii", "ignore").decode("ascii").lower()
    plano = re.sub(r"[^a-z0-9]+", "-", plano).strip("-")
    return plano or "seccion"


def figuras_validadas(entidades: list, raiz: Path) -> list:
    """(entidad, medio, ruta) por cada imagen, o aborta con el detalle."""
    resultado = []
    errores = []
    for entidad in entidades:
        for numero, medio in enumerate(entidad.get("medios") or [], 1):
            if medio.get("tipo") != "imagen":
                continue
            prefijo = f"{entidad['_archivo']} medio {numero}"
            faltantes = [c for c in REQUERIDOS_IMAGEN if not medio.get(c)]
            if faltantes:
                errores.append(f"{prefijo}: faltan {', '.join(faltantes)}")
                continue
            ruta = (raiz / medio["archivo_local"]).resolve()
            try:
                ruta.relative_to(raiz.resolve())
            except ValueError:
                errores.append(f"{prefijo}: archivo_local apunta fuera del repositorio")
                continue
            if not ruta.is_file():
                errores.append(f"{prefijo}: no existe {medio['archivo_local']}")
                continue
            resultado.append((entidad, medio, ruta))
    if errores:
        detalle = "\n  - ".join(errores)
        raise RuntimeError(
            "Metadatos de imágenes incompletos; el libro no puede omitir ni "
            f"atribuir figuras por inferencia:\n  - {detalle}"
        )
    return resultado


def degradar(cuerpo: str, niveles: int = 1) -> str:
    """Baja los encabezados del cuerpo para que cuelguen del título de su ficha.

    El cuerpo del banco arranca en `##`; la ficha vive en `##` dentro de su
    capítulo, así que el cuerpo pasa a `###` y queda como hermano de
    «Evidencia». Se topa en `#####` para no generar encabezados que HTML no
    representa.
    """
    return ENCABEZADO.sub(
        lambda m: "#" * min(len(m.group(1)) + niveles, 5) + m.group(2), cuerpo
    )


def bibliografia_para_libro(bib: dict) -> dict:
    """Escapa los asteriscos literales de los campos bibliográficos.

    Hay títulos que traen un `*` de verdad —`...evaluation of proficiency*` es
    el título tal como lo publicó Crit Care Med—. `referencia_ghost()` envuelve
    el nombre de la revista en `*...*`, así que ese asterisco suelto se empareja
    con el de la emfasis y el renglón sale en cursiva a partir del lugar
    equivocado. Se escapa aquí, en la ruta del libro, y no en
    `referencia_ghost()`: esa función alimenta los cuerpos canónicos de Ghost,
    cuya huella se audita.
    """
    limpia = {}
    for clave, campos in bib.items():
        copia = dict(campos)
        for campo in ("title", "journal", "author"):
            if copia.get(campo):
                copia[campo] = str(copia[campo]).replace("*", r"\*")
        limpia[clave] = copia
    return limpia


def figura_markdown(medio: dict) -> str:
    """Figura con su pie completo de atribución, en ruta interna al proyecto."""
    pie = (
        f"{medio['descripcion']}. {medio['credito']}. "
        f"[{medio['fuente']}]({medio['fuente_url']}). "
        f"[{medio['licencia_img']}]({medio['licencia_url']})."
    )
    return f"![{pie}]({medio['archivo_local']})"


def ficha_markdown(entidad: dict, bibliografia: dict, orden_global: list,
                   nivel: int = 0) -> str:
    """Una ficha como sección, con su cuerpo degradado bajo su propio título.

    `orden_global` acumula, en orden de aparición, las claves que alimentan la
    bibliografía final del libro.
    """
    marca = "#" * (2 + nivel)
    lineas = [f"{marca} {entidad['titulo']} {{#sec-{slug(entidad['id'])}}}", ""]

    # El libro y el sitio son la misma obra en dos soportes: la ficha impresa
    # apunta a su artículo vivo en Ghost, que es donde están los loops, las
    # imágenes en movimiento y las correcciones posteriores a esta edición.
    if entidad.get("url"):
        lineas += [f"*Edición en línea:* <{entidad['url']}>", ""]

    for medio in entidad.get("medios") or []:
        if medio.get("tipo") == "imagen":
            lineas += [figura_markdown(medio), ""]

    if entidad["tipo"] == "signo":
        for etiqueta, campo in (
            ("Significante", "significante"),
            ("Significado", "significado"),
            ("Decisión", "decision"),
            ("Umbral", "umbral"),
        ):
            if entidad.get(campo):
                lineas += [f"**{etiqueta}.** {entidad[campo]}", ""]
    elif entidad["tipo"] == "caso" and entidad.get("decision_semiotica"):
        lineas += [f"**Decisión semiótica.** {entidad['decision_semiotica']}", ""]

    # Mismo motor de citas que Ghost y que el EPUB anterior: numera por ficha
    # y devuelve el orden bibliográfico estable, incluidas las fuentes que la
    # ficha declara en `refs` pero todavía no cita en línea.
    cuerpo = refs_bibliograficas.quitar_bibliografia_manual(entidad["cuerpo"])
    cuerpo, orden = refs_bibliograficas.resolver_citas(
        cuerpo, entidad.get("refs") or [], bibliografia)
    cuerpo = degradar(cuerpo, 1 + nivel)

    lineas += [cuerpo.strip(), ""]
    if orden:
        lineas += [f"{marca}# Evidencia", ""]
        lineas += [refs_bibliograficas.referencia_ghost(i, bibliografia[c])
                   for i, c in enumerate(orden, 1)]
        lineas += [""]

    for clave in orden:
        if clave not in orden_global:
            orden_global.append(clave)
    return "\n".join(lineas)


def parte_markdown(parte: str, capitulos: list, bibliografia: dict,
                   orden_global: list) -> str:
    """Una parte entera del atlas como un capítulo del libro.

    NO se usa la clave `part:` de Quarto: su escritor de EPUB no emite páginas
    divisorias de parte, así que "Sistema respiratorio" y sus hermanas
    desaparecían del contenedor y del índice —solo sobrevivían en la barra
    lateral del HTML—. Con la parte convertida en capítulo, los dos motores
    producen exactamente la misma estructura.

    Jerarquía: `#` parte · `##` capítulo temático u órgano · `###` ficha ·
    `####` cuerpo.
    """
    bloques = [f"# {parte}", ""]
    for titulo, grupo in capitulos:
        bloques += [f"## {titulo}", ""]
        for entidad in grupo:
            bloques.append(ficha_markdown(entidad, bibliografia, orden_global, nivel=1))
    return "\n".join(bloques).rstrip() + "\n"


def citas_verificables(orden: list, raiz: Path) -> int:
    """Número de citas de la edición; aborta si alguna no es verificable.

    El colofón afirma que las N citas se verificaron contra PubMed y Crossref.
    Verificable es lo que `verificar_citas.py` comprueba de verdad: una entrada
    `@article` de `refs.bib` con PMID y DOI y sin exención de Crossref. Se usa
    su mismo lector y su misma lista de exenciones para que las dos lecturas
    no puedan discrepar. La consulta de red sigue siendo de ese script y de la
    CI; aquí se garantiza que ninguna cita quede fuera de su alcance.
    """
    entradas = {e["clave"]: e for e in verificar_citas.parse_bib(raiz / "refs.bib")}
    exenciones = verificar_citas.cargar_exenciones(raiz)
    errores = []
    for clave in orden:
        entrada = entradas.get(clave)
        if entrada is None:
            errores.append(f"{clave}: no es una entrada @article de refs.bib")
        elif not entrada["pmid"] or not entrada["doi"]:
            errores.append(f"{clave}: le falta PMID o DOI")
        elif verificar_citas.exento(clave, entrada["doi"], exenciones):
            errores.append(f"{clave}: exenta de Crossref en refs-sin-crossref.txt")
    if errores:
        detalle = "\n  - ".join(errores)
        raise RuntimeError(
            "Citas de la edición fuera de la verificación PubMed + Crossref; "
            f"la declaración de uso de IA no sería cierta:\n  - {detalle}"
        )
    return len(orden)


def declaracion_ia(raiz: Path, citas: int) -> str:
    """El paratexto del banco con `{N}` resuelto; aborta ante cualquier marcador."""
    ruta = raiz / DECLARACION_IA
    if not ruta.is_file():
        raise RuntimeError(
            f"falta {DECLARACION_IA.as_posix()}: el libro no sale sin su "
            "declaración de uso de IA"
        )
    texto = ruta.read_text(encoding="utf-8").strip()
    if texto.count(MARCADOR_CITAS) != 1:
        raise RuntimeError(
            f"{DECLARACION_IA.as_posix()} debe contener el marcador "
            f"{MARCADOR_CITAS} exactamente una vez"
        )
    texto = texto.replace(MARCADOR_CITAS, str(citas))
    pendiente = MARCADOR_PENDIENTE.search(texto)
    if pendiente:
        raise RuntimeError(
            f"{DECLARACION_IA.as_posix()}: marcador sin sustituir {pendiente.group(0)}"
        )
    return texto


def titulo_declaracion(texto: str) -> str:
    """El título del paratexto, sin almohadillas ni atributos, para validar."""
    primera = texto.strip().splitlines()[0]
    return re.sub(r"\s*\{[^}]*\}\s*$", "", primera.lstrip("#")).strip()


MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def fecha_larga(iso: str) -> str:
    """`2026-11-13` → `13 de noviembre de 2026`."""
    dia = date.fromisoformat(iso)
    return f"{dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def prologo(raiz: Path) -> str | None:
    """El prólogo del banco con su encabezado, o None si aún no existe.

    El archivo trae solo el texto y la firma; el encabezado sin numerar lo pone
    el generador para que el prólogo sea un capítulo propio, detrás del índice.
    """
    ruta = raiz / PROLOGO
    if not ruta.is_file():
        return None
    texto = ruta.read_text(encoding="utf-8").strip()
    if not texto:
        raise RuntimeError(f"{PROLOGO.as_posix()} está vacío")
    pendiente = MARCADOR_PENDIENTE.search(texto)
    if pendiente:
        raise RuntimeError(
            f"{PROLOGO.as_posix()}: marcador sin sustituir {pendiente.group(0)}"
        )
    return f"# Prólogo {{.unnumbered}}\n\n{texto}\n"


def creditos_identificadores() -> str:
    """ISBN de las dos ediciones y el DOI que corresponde citar."""
    if DOI_EDICION:
        doi = (f"DOI de esta edición: [{DOI_EDICION}](https://doi.org/{DOI_EDICION}). "
               f"DOI de la obra: [{DOI_CONCEPTO}]({DOI_URL}).")
    else:
        doi = f"DOI de la obra: [{DOI_CONCEPTO}]({DOI_URL})."
    return f"{doi} ISBN EPUB: {ISBN_EPUB}. ISBN tapa blanda: {ISBN_RUSTICA}."


def portadilla(version: str, declaracion: str) -> str:
    """Portadilla, créditos y declaración de uso de IA.

    En el PDF este bloque va ANTES del índice, como la página de créditos de un
    libro impreso. Quarto pone `\\tableofcontents` justo tras la portada, así
    que el índice automático del PDF se apaga y se emite aquí en LaTeX crudo,
    que EPUB y HTML ignoran: ellos conservan su propio índice.

    No se intenta pasar este bloque a romanos: Quarto coloca cualquier
    contenido de este capítulo detrás de su `\\chapter*`, ya en `\\mainmatter`,
    y reiniciar ahí la numeración duplica las anclas de página de hyperref.
    """
    return "\n".join(
        [
            "# Portadilla {.unnumbered}",
            "",
            f"**{SUBTITULO}**",
            "",
            f"{AUTOR} · ORCID [{ORCID}](https://orcid.org/{ORCID})",
            "",
            "Primera edición. Contiene las entradas publicadas hasta el "
            f"{fecha_larga(FECHA_CORTE)}.",
            "",
            f"{EDITORIAL} · Compilación {date.today().isoformat()} · "
            f"versión `{version}`",
            "",
            "## Créditos, licencia y uso {.unnumbered}",
            "",
            f"Autor: {AUTOR}. Editorial: {EDITORIAL}. Idioma: español.",
            "",
            f"Edición impresa derivada del atlas en línea *{OBRA_EN_LINEA}*.",
            "",
            creditos_identificadores(),
            "",
            f"El conjunto se distribuye bajo [{LICENCIA}]({LICENCIA_URL}). "
            "Las figuras conservan sus licencias propias, declaradas en cada "
            "pie y en los créditos finales.",
            "",
            f"**Aviso:** {AVISO}",
            "",
            "No existe afiliación, aval ni patrocinio del HECAM o del IESS.",
            "",
            declaracion,
            "",
            "```{=latex}",
            # En `book` el capítulo es el nivel 0: `tocdepth` 2 llega hasta la
            # subsección, que es la ficha. El índice impreso lista así las
            # fichas, que es lo que se busca en un atlas. El título
            # «Tabla de contenidos» ya lo fija su preámbulo.
            "{",
            f"\\setcounter{{tocdepth}}{{{TOC_PROFUNDIDAD}}}",
            "\\tableofcontents",
            "}",
            "```",
            "",
        ]
    )


def bibliografia_capitulo(orden: list, bibliografia: dict) -> str:
    """Bibliografía del libro, en orden de aparición y con el estilo de la casa."""
    partes = ["# Bibliografía {.unnumbered}", ""]
    for numero, clave in enumerate(orden, 1):
        partes += [refs_bibliograficas.referencia_ghost(numero, bibliografia[clave]), ""]
    return "\n".join(partes)


def creditos_imagenes(figuras: list) -> str:
    partes = ["# Créditos de imágenes {.unnumbered}", ""]
    for entidad, medio, _ in figuras:
        partes.append(
            f"- **{entidad['titulo']}:** {medio['descripcion']}. "
            f"{medio['credito']}. [{medio['fuente']}]({medio['fuente_url']}). "
            f"[{medio['licencia_img']}]({medio['licencia_url']})."
        )
    partes.append("")
    return "\n".join(partes)


def escapar_xml(valor: str) -> str:
    return (str(valor).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def rasterizar_portada(svg: Path, png: Path) -> bool:
    """Convierte la portada a PNG. Devuelve False si no hay con qué.

    La portada es SVG por diseño —es tipográfica y se versiona en texto—, pero
    como portada del contenedor es frágil: Kindle no admite portadas SVG y
    Calibre necesita un motor de navegador para rasterizarla, de modo que en
    varios lectores la portada sale en blanco. Se declara el PNG cuando hay
    rasterizador; si no lo hay, se cae al SVG con aviso en vez de abortar.
    """
    herramienta = shutil.which("rsvg-convert")
    if not herramienta:
        return False
    try:
        subprocess.run(
            [herramienta, "--width=1600", "--keep-aspect-ratio",
             "--format=png", "--output", str(png), str(svg)],
            check=True, capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return png.is_file() and png.stat().st_size > 0


def metadatos_epub(entidades: list, version: str) -> str:
    """Dublin Core del contenedor, para `pandoc --epub-metadata`.

    Aporta SOLO lo que pandoc no genera por su cuenta: el DOI con su esquema,
    la licencia con URL, la descripción, la fuente y las materias MeSH. Título,
    autor, fecha, idioma y editorial siguen llegando por `--metadata` para que
    pandoc arme su portadilla; duplicarlos aquí produce dos `dc:title` y dos
    `dc:identifier` en el OPF.
    """
    materias = []
    for entidad in entidades:
        for termino in (entidad.get("mesh") or []):
            if termino not in materias:
                materias.append(termino)

    lineas = [
        f"<dc:identifier opf:scheme=\"DOI\">{escapar_xml(DOI_URL)}</dc:identifier>",
        f"<dc:contributor opf:role=\"aut\">ORCID {escapar_xml(ORCID)}</dc:contributor>",
        # La editorial se declara AQUÍ y no por `--metadata`: Quarto no lleva
        # `book: publisher:` al OPF, así que por la ruta Quarto el contenedor
        # salía sin `dc:publisher`.
        f"<dc:publisher>{escapar_xml(EDITORIAL)}</dc:publisher>",
        f"<dc:rights>{escapar_xml(LICENCIA)} — {escapar_xml(LICENCIA_URL)}. "
        "Las figuras conservan sus licencias propias, declaradas en cada pie y "
        "en los créditos finales.</dc:rights>",
        f"<dc:description>{escapar_xml(SUBTITULO)}. {escapar_xml(AVISO)} "
        f"Compilación {date.today().isoformat()}, versión {escapar_xml(version)}."
        "</dc:description>",
        f"<dc:source>{escapar_xml(DOI_URL)}</dc:source>",
        "<dc:type>Text</dc:type>",
    ]
    lineas += [f"<dc:subject>{escapar_xml(m)}</dc:subject>" for m in materias]
    return "\n".join(lineas) + "\n"


def portada_svg(version: str) -> str:
    seguro = escapar_xml(version)
    subtitulo = escapar_xml(SUBTITULO)
    editorial = escapar_xml(EDITORIAL)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2560" viewBox="0 0 1600 2560">
<rect width="1600" height="2560" fill="#071b2b"/>
<path d="M0 1840 C420 1640 720 2050 1110 1830 C1320 1710 1450 1680 1600 1750 L1600 2560 L0 2560 Z" fill="#0b7480"/>
<circle cx="1260" cy="360" r="170" fill="none" stroke="#69d3c5" stroke-width="20"/>
<text x="120" y="650" fill="#f4f0df" font-family="FreeSerif,serif" font-size="150">Biosemiótica</text>
<text x="120" y="825" fill="#f4f0df" font-family="FreeSerif,serif" font-size="150">del Cuerpo Vivo</text>
<text x="125" y="1020" fill="#69d3c5" font-family="FreeSerif,serif" font-size="72">{subtitulo}</text>
<text x="125" y="2170" fill="#f4f0df" font-family="FreeSerif,serif" font-size="58">Dr. Alcy Edmundo Torres Guerrero</text>
<text x="125" y="2270" fill="#b9ddd8" font-family="FreeSerif,serif" font-size="40">{editorial} · {seguro}</text>
</svg>
'''


# Sin unidades `vh`: los lectores basados en Adobe Digital Editions no las
# soportan y las resuelven como 0, de modo que la imagen queda embebida en el
# contenedor pero invisible en pantalla. `max-width` en porcentaje más
# `height:auto` funciona en todos.
ESTILO = (
    "body{font-family:FreeSerif,serif;line-height:1.45;color:#17212b}"
    "h1{color:#075f69;page-break-before:always}h2{color:#16485a}"
    "h3{color:#071b2b}"
    "img{max-width:100%;height:auto;display:block;margin:1.2em auto}"
    "figure{text-align:center;margin:1.4em 0;page-break-inside:avoid}"
    "figcaption{font-size:.85em;color:#46535d;text-align:left;margin-top:.4em}"
    "a{color:#075f69}blockquote{border-left:.3em solid #69d3c5;padding-left:1em}"
    "code{font-family:monospace}ul,ol{padding-left:1.5em}"
    "table{border-collapse:collapse;width:100%}"
    "th,td{border:1px solid #c8d3d8;padding:.35em .5em;text-align:left}"
)


def estructura(entidades: list) -> list:
    """[(parte, [(titulo_capitulo, [entidades])])] en el orden canónico del atlas.

    Hereda `CAPITULOS` y `SISTEMAS` de `build.py`: el orden del libro impreso se
    define una sola vez y aquí no se duplica ninguna lista.
    """
    partes: list = []

    conceptos = sorted(
        (e for e in entidades if e["tipo"] == "concepto"),
        key=lambda e: (e.get("capitulo") or 99, e.get("orden") or 99),
    )
    if conceptos:
        por_capitulo: dict = defaultdict(list)
        for entidad in conceptos:
            por_capitulo[entidad.get("capitulo") or 99].append(entidad)
        capitulos = [
            (configuracion.CAPITULOS.get(numero, f"Capítulo {numero}"), por_capitulo[numero])
            for numero in sorted(por_capitulo)
        ]
        partes.append(("Fundamentos", capitulos))

    signos = [e for e in entidades if e["tipo"] == "signo"]
    ubicados = set()
    for clave, titulo in configuracion.SISTEMAS:
        grupo = [e for e in signos if e.get("sistema") == clave]
        if not grupo:
            continue
        por_organo: dict = defaultdict(list)
        for entidad in grupo:
            por_organo[entidad.get("organo") or "otros"].append(entidad)
            ubicados.add(entidad["id"])
        capitulos = [
            (
                configuracion.nombre_organo(organo),
                sorted(por_organo[organo], key=lambda e: e["titulo"]),
            )
            for organo in sorted(por_organo)
        ]
        partes.append((titulo, capitulos))

    huerfanos = [e for e in signos if e["id"] not in ubicados]
    if huerfanos:
        partes.append(
            (
                "Otros signos",
                [
                    (
                        "Sin sistema asignado",
                        sorted(huerfanos, key=lambda e: e["titulo"]),
                    )
                ],
            )
        )

    casos = sorted((e for e in entidades if e["tipo"] == "caso"), key=lambda e: e["titulo"])
    if casos:
        partes.append(("Casos", [("Casos clínicos", casos)]))
    return partes


def preambulo_libro(version: str) -> str:
    """Preámbulo de diseño del PDF, con la versión de la edición para la portada."""
    plantilla = (DISENO_LIBRO / "preambulo.tex").read_text(encoding="utf-8")

    def seguro(texto: str) -> str:
        return re.sub(r"([\\#$%&_{}~^])", r"\\\1", texto)

    # Portada y portadilla parten el título en dos líneas, como portada.svg.
    primera, _, resto = TITULO.partition(" ")
    macros = {
        "titulolineas": f"{seguro(primera)}\\\\{seguro(resto)}",
        "subtitulolibro": seguro(SUBTITULO),
        "autorlibro": seguro(AUTOR),
        "editoriallibro": seguro(EDITORIAL),
        "versionlibro": seguro(version),
    }
    cabecera = "".join(
        f"\\newcommand{{\\{nombre}}}{{{valor}}}\n" for nombre, valor in macros.items()
    )
    # El tope de figuras va al final, después de cualquier ajuste del diseño.
    return cabecera + plantilla + "\n" + PANDOCBOUNDED_CON_TOPE + "\n"


def yaml_texto(valor: str) -> str:
    """Escalar YAML entrecomillado; el banco trae acentos, `:` y comillas."""
    return '"' + str(valor).replace("\\", "\\\\").replace('"', '\\"') + '"'


def quarto_yml(partes: list, archivos: dict, version: str, portada: str,
               con_prologo: bool = False) -> str:
    lineas = [
        "# GENERADO por scripts/qmd.py — no editar a mano.",
        "# La fuente de verdad es el banco .qmd de conceptos/, signos/ y casos/.",
        "project:",
        "  type: book",
        "  output-dir: _salida",
        "",
        "book:",
        f"  title: {yaml_texto(TITULO)}",
        f"  subtitle: {yaml_texto(SUBTITULO)}",
        "  author:",
        f"    - name: {yaml_texto(AUTOR)}",
        f"      orcid: {yaml_texto(ORCID)}",
        f"  date: {yaml_texto(date.today().isoformat())}",
        f"  publisher: {yaml_texto(EDITORIAL)}",
        "  language: es",
        # En un libro Quarto el nombre de salida se declara aquí, no bajo el
        # formato: `libro.pdf` / `libro.tex` / `atlas.epub`, los nombres que el
        # repositorio usa desde siempre, en vez del título con acentos.
        "  output-file: libro",
        f"  cover-image: {portada}",
        "  chapters:",
        "    - index.qmd",
    ]
    # El prólogo va detrás de `index.qmd`, que cierra con el índice del PDF, y
    # antes del primer capítulo.
    if con_prologo:
        lineas.append("    - prologo.qmd")
    # Lista plana de capítulos, sin `part:`: el escritor de EPUB de Quarto no
    # emite páginas divisorias de parte, así que declararlas ahí borraba
    # "Fundamentos" y las ocho partes de sistema del contenedor y del índice.
    for parte, _ in partes:
        lineas.append(f"    - {archivos[parte]}")
    lineas += [
        "  appendices:",
        # La bibliografía se emite ya resuelta por `bibliografia.referencia_ghost()`,
        # no por citeproc: por eso es un capítulo más y no una `bibliography:`.
        "    - bibliografia.qmd",
        "    - creditos-imagenes.qmd",
        "",
        # `identifier` y `rights` no se declaran aquí: no son propiedades
        # válidas de `book:` en el esquema de Quarto, y al nivel superior
        # Quarto las pasa a pandoc ADEMÁS del `epub-metadata.xml`, con lo que
        # el OPF sale con dos `dc:identifier`. El XML es la única autoridad.
        "lang: es",
        f"date-meta: {yaml_texto(date.today().isoformat())}",
        f"version: {yaml_texto(version)}",
        "",
        "format:",
        "  epub:",
        "    toc: true",
        # Nivel 2 = parte → capítulo → ficha. Bajar más metería en el índice
        # cada "La pregunta clínica" de cada signo.
        f"    toc-depth: {TOC_PROFUNDIDAD}",
        "    css: epub.css",
        f"    epub-cover-image: {portada}",
        # El mismo Dublin Core que usa la ruta pandoc: DOI con esquema,
        # licencia con URL, descripción y materias MeSH.
        "    epub-metadata: epub-metadata.xml",
        "  pdf:",
        # KOMA-Script: cabeceras, índice y encabezados se configuran desde
        # `preambulo-libro.tex` sin reescribir la plantilla de Quarto.
        "    documentclass: scrbook",
        "    classoption: [open=any, fontsize=10.5pt]",
        # La fuente LaTeX es un entregable, no un intermedio: alimenta el ZIP
        # autocontenido y la verificación de imágenes.
        "    keep-tex: true",
        "    pdf-engine: lualatex",
        f"    mainfont: {FUENTE_LIBRO}",
        f"    sansfont: {FUENTE_LIBRO_SANS}",
        # El índice del PDF lo emite `portadilla()` detrás de créditos y
        # declaración de uso de IA; el automático iría antes que ellos.
        "    toc: false",
        # 6,69 × 9,61 pulgadas = 170 × 244 mm, tamaño de catálogo de KDP e
        # IngramSpark. Los 4 mm extra respecto a la maqueta de 240 mm van a
        # los márgenes superior e inferior (+2 mm c/u): la caja de texto sigue
        # en 132 × 192 mm y la paginación no cambia.
        "    geometry: [paperwidth=170mm, paperheight=244mm, inner=20mm, "
        "outer=18mm, top=26mm, bottom=26mm, headsep=7mm, footskip=11mm]",
        # Lleva también el tope de altura de las figuras (PANDOCBOUNDED_CON_TOPE).
        f"    include-in-header: {PREAMBULO_LIBRO}",
        f"    filters: [{FILTRO_LIBRO}]",
        # Cada figura queda bajo el título de su ficha, en el orden del texto.
        "    fig-pos: H",
        "  html:",
        "    toc: true",
        f"    toc-depth: {TOC_PROFUNDIDAD}",
        "",
    ]
    return "\n".join(lineas)


def manuscrito_plano(partes: list, bibliografia: dict, orden_global: list,
                     version: str, declaracion: str,
                     texto_prologo: str | None = None) -> str:
    """El mismo libro en un solo Markdown, para pandoc sin Quarto.

    No es una segunda versión del ensamblado: es la concatenación literal de
    los mismos capítulos que consume Quarto, producidos por `parte_markdown()`.
    Existe porque Quarto no siempre está disponible y porque conviene poder
    validar la salida sin él; si diverge del proyecto Quarto, es un fallo.
    """
    bloques = [portadilla(version, declaracion)]
    if texto_prologo:
        bloques.append(texto_prologo)
    for parte, capitulos in partes:
        bloques.append(parte_markdown(parte, capitulos, bibliografia, orden_global))
    bloques.append(bibliografia_capitulo(orden_global, bibliografia))
    return "\n".join(bloques)


def render(ejecutable: str, proyecto: Path, formato: str, sufijo: str) -> Path:
    """Renderiza el proyecto a un formato y devuelve el archivo producido.

    Compartida por `epub.py` y `libro.py` para que las dos ediciones salgan
    del mismo árbol con la misma invocación.
    """
    subprocess.run(
        [ejecutable, "render", str(proyecto), "--to", formato],
        cwd=proyecto,
        check=True,
    )
    salidas = sorted((proyecto / "_salida").glob(f"*{sufijo}"))
    if not salidas:
        raise RuntimeError(
            f"quarto no dejó ningún {sufijo} en {proyecto / '_salida'}"
        )
    return salidas[0]


MARCADOR_PROYECTO = ".biosemiotics-quarto"
MARCA_PROYECTO = "biosemiotics-quarto-v1\n"


def validar_destino(raiz: Path, destino: Path) -> Path:
    """Solo reemplaza proyectos derivados dentro del build real del banco."""
    raiz = raiz.resolve()
    destino = destino if destino.is_absolute() else raiz / destino
    # Rechaza enlaces y junctions también antes de normalizar '..'.
    for tramo in (destino, *destino.parents):
        if tramo.is_symlink() or getattr(tramo, "is_junction", lambda: False)():
            raise RuntimeError(f"Destino inseguro: enlace o junction en {tramo}")
    base = raiz / "build"
    destino = destino.resolve()
    try:
        relativo = destino.relative_to(base)
    except ValueError:
        raise RuntimeError("El proyecto Quarto debe estar dentro de build/")
    if not relativo.parts:
        raise RuntimeError("No se puede reemplazar build/ entero; usa build/quarto")
    if destino.exists():
        if not destino.is_dir():
            raise RuntimeError(f"El destino no es un directorio: {destino}")
        if any(destino.iterdir()):
            marcador = destino / MARCADOR_PROYECTO
            propio = (marcador.is_file() and not marcador.is_symlink()
                      and marcador.read_text(encoding="utf-8") == MARCA_PROYECTO)
            # Compatibilidad con proyectos anteriores al marcador, únicamente
            # en la ruta histórica y con los archivos característicos.
            anterior = destino == base / "quarto" and all(
                (destino / nombre).is_file() and not (destino / nombre).is_symlink()
                for nombre in ("_quarto.yml", "index.qmd", "libro-plano.md", "refs.bib")
            )
            if not (propio or anterior):
                raise RuntimeError(f"No se reemplaza un directorio ajeno: {destino}")
    return destino


def _temporal_heredable(padre: Path) -> Path:
    """Crea el directorio de ensamblado con los permisos heredados de `padre`.

    No usa `tempfile.mkdtemp`: en Windows crea el directorio con una ACL
    protegida solo para su dueño (modo 0o700), y al renombrar el proyecto a
    `build/quarto` quedaba inaccesible para cualquier otra cuenta que regenere
    el libro, como el sandbox de Codex (WinError 5).
    """
    for _ in range(100):
        candidato = padre / f".quarto-{secrets.token_hex(6)}"
        try:
            candidato.mkdir()
        except FileExistsError:
            continue
        return candidato
    raise RuntimeError(f"No se pudo crear un directorio temporal en {padre}")


def generar(entidades: list, raiz: Path, destino: Path) -> dict:
    """Ensambla primero; conserva el proyecto previo si falla la generación.

    El intercambio usa renombres en el mismo filesystem. No garantiza una
    transacción frente a corte eléctrico o procesos concurrentes.
    """
    raiz = raiz.resolve()
    destino = validar_destino(raiz, destino)
    entidades = banco.seleccionar_publicables(entidades)
    if not entidades:
        raise RuntimeError("ninguna entidad cumple el alcance solicitado")
    exigir_editorial(entidades, raiz / "refs.bib")
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = _temporal_heredable(destino.parent)
    nuevo, anterior = temporal / "nuevo", temporal / "anterior"
    try:
        informe = _generar_en(entidades, raiz, nuevo)
        escribir_texto(nuevo / MARCADOR_PROYECTO, MARCA_PROYECTO)
        validar_destino(raiz, destino)
        if destino.exists():
            destino.rename(anterior)
        try:
            nuevo.rename(destino)
        except OSError:
            if anterior.exists():
                try:
                    anterior.rename(destino)
                except OSError as exc:
                    raise RuntimeError(
                        f"No se pudo restaurar {destino}; copia conservada en {anterior}"
                    ) from exc
            raise
        if anterior.exists():
            shutil.rmtree(anterior)
        informe["destino"] = destino
        return informe
    finally:
        # Si restaurar el anterior también falla, conserva la copia recuperable.
        if not anterior.exists():
            shutil.rmtree(temporal)


def _generar_en(entidades: list, raiz: Path, destino: Path) -> dict:
    figuras = figuras_validadas(entidades, raiz)
    bibliografia = bibliografia_para_libro(
        refs_bibliograficas.cargar_bibliografia(raiz / "refs.bib"))
    version = version_git(raiz)

    destino.mkdir(parents=True)

    partes = estructura(entidades)
    archivos: dict = {}
    usados: set = set()
    orden_global: list = []
    for parte, capitulos in partes:
        nombre = f"{slug(parte)}.qmd"
        sufijo = 2
        while nombre in usados:
            nombre = f"{slug(parte)}-{sufijo}.qmd"
            sufijo += 1
        usados.add(nombre)
        archivos[parte] = nombre
        escribir_texto(
            destino / nombre,
            parte_markdown(parte, capitulos, bibliografia, orden_global),
        )

    # {N} son las citas de ESTA edición —`orden_global`, ya poblado por los
    # capítulos—, no las entradas de refs.bib.
    citas = citas_verificables(orden_global, raiz)
    declaracion = declaracion_ia(raiz, citas)
    escribir_texto(destino / "index.qmd", portadilla(version, declaracion))
    texto_prologo = prologo(raiz)
    if texto_prologo:
        escribir_texto(destino / "prologo.qmd", texto_prologo)
    # El manuscrito plano se arma DESPUÉS de los capítulos para heredar el
    # `orden_global` ya poblado; `resolver_citas` es determinista, así que
    # ambos caminos numeran igual.
    plano = manuscrito_plano(partes, bibliografia, orden_global, version, declaracion,
                             texto_prologo)
    plano += "\n" + creditos_imagenes(figuras)
    escribir_texto(destino / "libro-plano.md", plano)

    escribir_texto(
        destino / "bibliografia.qmd",
        bibliografia_capitulo(orden_global, bibliografia),
    )
    escribir_texto(destino / "creditos-imagenes.qmd", creditos_imagenes(figuras))
    svg = destino / "portada.svg"
    escribir_texto(svg, portada_svg(version))
    portada = "portada.png" if rasterizar_portada(svg, destino / "portada.png") else "portada.svg"

    escribir_texto(
        destino / "_quarto.yml",
        quarto_yml(partes, archivos, version, portada, bool(texto_prologo)),
    )
    escribir_texto(destino / "epub.css", ESTILO)
    escribir_texto(destino / PREAMBULO_LIBRO, preambulo_libro(version))
    shutil.copy2(DISENO_LIBRO / FILTRO_LIBRO, destino / FILTRO_LIBRO)
    escribir_texto(
        destino / "epub-metadata.xml", metadatos_epub(entidades, version)
    )
    shutil.copy2(raiz / "refs.bib", destino / "refs.bib")

    # Las imágenes viajan dentro del proyecto para que sea autocontenido, pero
    # conservan su ruta relativa: `archivo_local` sigue siendo la única
    # autoridad y `verificar_publicacion.py` la puede comparar tal cual.
    copiadas = set()
    for _, medio, ruta in figuras:
        interno = destino / medio["archivo_local"]
        interno.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ruta, interno)
        copiadas.add(medio["archivo_local"])

    return {
        "destino": destino,
        "entidades": len(entidades),
        "figuras": len(figuras),
        "figuras_detalle": figuras,
        "imagenes_copiadas": len(copiadas),
        "capitulos": len(usados),
        "portada": portada,
        "referencias": len(orden_global),
        "declaracion_ia": titulo_declaracion(declaracion),
        "prologo": bool(texto_prologo),
        "partes": [parte for parte, _ in partes],
        "version": version,
    }


def main() -> int:
    blindar_salida()
    args = argumentos()
    raiz = resolver_raiz(args.raiz)
    destino = desde_raiz(raiz, args.destino)

    entidades = banco.cargar(raiz)
    entidades = banco.seleccionar_publicables(entidades, args.solo_publicados)
    if not entidades:
        raise RuntimeError("ninguna entidad cumple el alcance solicitado")

    informe = generar(entidades, raiz, destino)

    print(f"→ {destino.relative_to(raiz)}/")
    print(f"  {informe['entidades']} entidades · {informe['capitulos']} capítulos "
          f"· {len(informe['partes'])} partes")
    print(f"  {informe['figuras']} figuras · "
          f"{informe['imagenes_copiadas']} imágenes copiadas")
    print(f"  versión {informe['version']}")
    print("  render:  quarto render build/quarto --to epub")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, KeyError, ValueError, OSError) as exc:
        print(f"ERROR QMD: {exc}", file=sys.stderr)
        raise SystemExit(1)
