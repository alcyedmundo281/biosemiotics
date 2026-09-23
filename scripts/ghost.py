"""Render puro del cuerpo canónico que se copia al editor de Ghost."""

import hashlib
import json

from bibliografia import (
    excerpt_ghost,
    quitar_bibliografia_manual,
    referencia_ghost,
    resolver_citas,
)

URL_RETO = "https://www.biosemiotics.net/reto/?signo={id}"
LINEA_RETO = (
    "---\n"
    "\n"
    "**¿Reconoces este signo cuando no te avisan?** "
    "[Ponte a prueba en el Reto](" + URL_RETO + ")"
)


def cuerpo_ghost(entidad: dict, bibliografia: dict) -> str:
    cuerpo = quitar_bibliografia_manual(entidad["cuerpo"])
    cuerpo, orden = resolver_citas(cuerpo, entidad.get("refs") or [], bibliografia)
    referencias = [
        referencia_ghost(numero, bibliografia[clave])
        for numero, clave in enumerate(orden, 1)
    ]
    if referencias:
        cuerpo = cuerpo.rstrip() + "\n\n## Evidencia\n\n" + "\n".join(referencias)
    if entidad["tipo"] == "signo":
        cuerpo = cuerpo.rstrip() + "\n\n" + LINEA_RETO.format(id=entidad["id"])
    return cuerpo.rstrip()


def imagen_destacada(entidad: dict):
    """El medio `destacada: true` de tipo imagen, o None si la ficha no lo tiene."""
    for medio in entidad.get("medios") or []:
        if medio.get("tipo") == "imagen" and medio.get("destacada"):
            return medio
    return None


def _sin_punto(texto) -> str:
    return " ".join(str(texto or "").split()).rstrip(" .")


def pie_ghost(medio: dict) -> str:
    """Pie canónico de la imagen destacada, tal cual se pega en Ghost.

    Reproduce el formato de la publicación más reciente (VExUS, 2026-09-22):
    «descripción. crédito, vía fuente. licencia.». Hasta ahora no existía un
    texto canónico —los pies publicados tenían tres formatos distintos— y sin
    él no había contra qué comprobar que el pie quedó pegado una sola vez.
    """
    return (f"{_sin_punto(medio.get('descripcion'))}. "
            f"{_sin_punto(medio.get('credito'))}, vía {_sin_punto(medio.get('fuente'))}. "
            f"{_sin_punto(medio.get('licencia_img'))}.")


def alt_ghost(medio: dict) -> str:
    """Texto alternativo: la descripción, sin el resto de la atribución."""
    return _sin_punto(medio.get("descripcion"))


def markdown_ghost(entidad: dict, bibliografia: dict) -> str:
    campos = [
        f"title: {json.dumps(str(entidad['titulo']), ensure_ascii=False)}",
        f"excerpt: {json.dumps(excerpt_ghost(entidad.get('abstract')), ensure_ascii=False)}",
        f"tags: {json.dumps([str(t) for t in entidad.get('tags') or []], ensure_ascii=False)}",
    ]
    # La cabecera no entra en huella_cuerpo_ghost: añadir la imagen no altera
    # el ghost_sha256 registrado en el índice.
    medio = imagen_destacada(entidad)
    if medio:
        campos += [
            f"imagen: {json.dumps(str(medio.get('archivo_local') or ''), ensure_ascii=False)}",
            f"alt: {json.dumps(alt_ghost(medio), ensure_ascii=False)}",
            f"pie: {json.dumps(pie_ghost(medio), ensure_ascii=False)}",
        ]
    cabecera = "\n".join(["---", *campos, "---", ""])
    return cabecera + cuerpo_ghost(entidad, bibliografia) + "\n"


def huella_cuerpo_ghost(entidad: dict, bibliografia: dict) -> str:
    return hashlib.sha256(cuerpo_ghost(entidad, bibliografia).encode("utf-8")).hexdigest()
