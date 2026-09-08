"""Render puro del cuerpo canónico que se copia al editor de Ghost."""

import hashlib
import json

from bibliografia import (
    excerpt_ghost,
    quitar_bibliografia_manual,
    referencia_ghost,
    resolver_citas,
)

LINEA_RETO = (
    "---\n"
    "\n"
    "**¿Reconoces este signo cuando no te avisan?** "
    "[Ponte a prueba en el Reto](https://www.biosemiotics.net/reto/?signo={id})"
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


def markdown_ghost(entidad: dict, bibliografia: dict) -> str:
    cabecera = "\n".join([
        "---",
        f"title: {json.dumps(str(entidad['titulo']), ensure_ascii=False)}",
        f"excerpt: {json.dumps(excerpt_ghost(entidad.get('abstract')), ensure_ascii=False)}",
        "---",
        "",
    ])
    return cabecera + cuerpo_ghost(entidad, bibliografia) + "\n"


def huella_cuerpo_ghost(entidad: dict, bibliografia: dict) -> str:
    return hashlib.sha256(cuerpo_ghost(entidad, bibliografia).encode("utf-8")).hexdigest()
