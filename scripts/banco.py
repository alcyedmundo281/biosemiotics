"""Carga del banco y estado de publicación de sus entidades."""

import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

import yaml


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
    if e.get("tipo") == "caso":
        sintetico = e.get("sintetico", False)
        if not isinstance(sintetico, bool):
            fallo("sintetico debe ser booleano")
        if sintetico:
            if e.get("consentimiento") != "no_aplica":
                fallo("un caso sintético requiere consentimiento: no_aplica")
            if "**Caso sintético con fines docentes.**" not in e.get("cuerpo", ""):
                fallo("un caso sintético requiere declaración visible en el cuerpo")
        elif estado != "borrador" and e.get("consentimiento") != "obtenido":
            fallo("consentimiento: obtenido es obligatorio para un caso real revisado o publicado")
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
    if estado == "publicado":
        numero = e.get("numero")
        if type(numero) is not int or numero < 1:
            fallo("numero debe ser un entero positivo en toda ficha publicada")
        fecha = e.get("fecha_publicacion")
        if not isinstance(fecha, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", fecha):
            fallo("fecha_publicacion debe ser una cadena ISO completa con zona, entre comillas en YAML")
        try:
            datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        except ValueError:
            fallo("fecha_publicacion contiene un timestamp inválido")
    return estado


def seleccionar_publicables(entidades, solo_publicados=False):
    """Valida contradicciones antes de filtrar; nunca oculta un caso público inválido."""
    estados = [(e, estado_publicacion(e)) for e in entidades]
    permitidos = ("publicado",) if solo_publicados else ("revisado", "publicado")
    return [e for e, estado in estados if estado in permitidos]


def limite_edicion(fecha_corte):
    """Límite exclusivo: medianoche UTC siguiente al día de corte inclusivo."""
    try:
        if not isinstance(fecha_corte, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha_corte):
            raise ValueError
        dia = date.fromisoformat(fecha_corte)
        return datetime.combine(dia + timedelta(days=1), time.min, timezone.utc)
    except (ValueError, OverflowError):
        raise RuntimeError("FECHA_CORTE es obligatoria y debe ser una fecha válida YYYY-MM-DD")


def seleccionar_edicion(entidades, fecha_corte):
    """El libro con ISBN: publicadas hasta el corte. El seriado no usa esto."""
    limite = limite_edicion(fecha_corte)
    publicadas = seleccionar_publicables(entidades, solo_publicados=True)
    return [e for e in publicadas
            if datetime.fromisoformat(e["fecha_publicacion"].replace("Z", "+00:00")) < limite]
