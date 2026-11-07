#!/usr/bin/env python3
"""Registra una publicación nueva desde la respuesta JSON de Ghost Admin API.

No publica, no consulta la red y no reasigna designaciones existentes.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import json
import os
from pathlib import Path
import re
import tempfile

import yaml

from banco import cargar, estado_publicacion
from rutas import blindar_salida, raiz_argumentos, raiz_desde_argumentos


@contextmanager
def bloqueo(raiz):
    ruta = raiz / '.registro-publicacion.lock'
    try:
        fd = os.open(str(ruta), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise RuntimeError('otro registro está activo; no se asigna ningún número')
    try:
        os.close(fd)
        yield
    finally:
        ruta.unlink()


def inventario(raiz):
    entidades = cargar(raiz)
    numeros = []
    ids = set()
    for e in entidades:
        if e['id'] in ids:
            raise RuntimeError('ID duplicado en banco: ' + e['id'])
        ids.add(e['id'])
        estado_publicacion(e)
        if 'numero' in e:
            n = e['numero']
            if type(n) is not int or n < 1:
                raise RuntimeError('numero inválido en ' + e['id'])
            numeros.append(n)
    if len(set(numeros)) != len(numeros):
        raise RuntimeError('numero duplicado en banco; no se asigna otro')
    return entidades, numeros


def registrar(raiz, identificador, respuesta):
    raiz = Path(raiz).resolve()
    posts = respuesta.get('posts') if isinstance(respuesta, dict) else None
    if not isinstance(posts, list) or len(posts) != 1 or not isinstance(posts[0], dict):
        raise RuntimeError('se exige la respuesta Admin API con exactamente un post')
    post = posts[0]
    fecha = post.get('published_at')
    if not isinstance(fecha, str) or not fecha:
        raise RuntimeError('Ghost no devolvió published_at; no se escribe nada')
    if post.get('status') != 'published':
        raise RuntimeError('Ghost no confirma status published')
    if not isinstance(post.get('id'), str) or not re.fullmatch(r'[0-9a-f]{24}', post['id']):
        raise RuntimeError('Ghost no devolvió un id válido')
    with bloqueo(raiz):
        entidades, numeros = inventario(raiz)
        candidatos = [e for e in entidades if e['id'] == identificador]
        if len(candidatos) != 1:
            raise RuntimeError('la ficha no existe una sola vez: ' + identificador)
        entidad = candidatos[0]
        if 'numero' in entidad:
            raise RuntimeError('la ficha ya tenía numero; está prohibido recalcularlo')
        if estado_publicacion(entidad) != 'revisado':
            raise RuntimeError('la ficha debe estar revisado antes de registrar publicación')
        if entidad.get('ghost_id') not in (None, post['id']):
            raise RuntimeError('ghost_id previo distinto del devuelto por Ghost')
        if 'fecha_publicacion' in entidad or 'volumen' in entidad:
            raise RuntimeError('designación parcial previa; requiere revisión, no sobrescritura')
        if any(e['id'] != identificador and
               (e.get('ghost_id') == post['id'] or e.get('url') == post.get('url'))
               for e in entidades):
            raise RuntimeError('el post de Ghost ya está asociado a otra ficha')
        numero = max(numeros, default=0) + 1
        nueva = dict(entidad, estado='publicado', url=post.get('url'),
                     ghost_id=post['id'], numero=numero, fecha_publicacion=fecha)
        estado_publicacion(nueva)  # exige timestamp completo, cadena y zona
        anio = datetime.fromisoformat(fecha.replace('Z', '+00:00')).year
        if anio < 2026:
            raise RuntimeError('año anterior al inicio del volumen 1 (2026)')
        nueva['volumen'] = anio - 2025
        ruta = raiz / entidad['_archivo']
        original = ruta.read_bytes()
        partes = original.split(b'---', 2)
        if len(partes) != 3 or partes[0]:
            raise RuntimeError('frontmatter no reconocido')
        fm = partes[1]
        salto = b'\r\n' if b'\r\n' in fm else b'\n'
        for campo in ('estado', 'url', 'ghost_id'):
            valor = nueva[campo]
            texto = 'publicado' if campo == 'estado' else json.dumps(valor, ensure_ascii=False)
            fm, cantidad = re.subn(
                rb'(?m)^' + campo.encode() + rb':[^\r\n]*(?=\r?$)',
                lambda m: campo.encode() + b': ' + texto.encode('utf-8'), fm)
            if cantidad != 1:
                raise RuntimeError('campo ausente o duplicado: ' + campo)
        bloque = (f'numero: {numero}'.encode() + salto +
                  f'volumen: {nueva["volumen"]}'.encode() + salto +
                  b'fecha_publicacion: ' + json.dumps(fecha).encode() + salto)
        fm, cantidad = re.subn(rb'(?m)^estado: publicado\r?\n', lambda m: m[0] + bloque, fm)
        if cantidad != 1:
            raise RuntimeError('no se pudo insertar designación')
        resultado = b'---' + fm + b'---' + partes[2]
        leida = yaml.safe_load(fm.decode('utf-8'))
        if type(leida['fecha_publicacion']) is not str or leida['fecha_publicacion'] != fecha:
            raise RuntimeError('published_at no se conservó carácter por carácter')
        # No se acepta ninguna alteración fuera de los seis campos del registro.
        esperada = {k: v for k, v in nueva.items() if k not in ('cuerpo', '_archivo')}
        if leida != esperada:
            raise RuntimeError('el registro alteraría otros metadatos')
        _, actuales = inventario(raiz)
        if numero in actuales:
            raise RuntimeError('el numero calculado ya existe; no se recalcula')
        if actuales != numeros or ruta.read_bytes() != original:
            raise RuntimeError('el banco cambió durante el registro; no se escribe')
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(dir=ruta.parent, delete=False) as f:
                temporal = Path(f.name)
                f.write(resultado)
                f.flush()
                os.fsync(f.fileno())
            os.chmod(temporal, ruta.stat().st_mode)
            os.replace(temporal, ruta)
        finally:
            if temporal is not None and temporal.exists():
                temporal.unlink()
        return {k: nueva[k] for k in ('id', 'estado', 'url', 'ghost_id', 'numero',
                                      'volumen', 'fecha_publicacion')}


def main():
    blindar_salida()
    parser = argparse.ArgumentParser(description=__doc__)
    raiz_argumentos(parser)
    parser.add_argument('--id', required=True)
    parser.add_argument('--respuesta', required=True, type=Path,
                        help='JSON exacto devuelto al publicar con Ghost Admin API')
    args = parser.parse_args()
    raiz = raiz_desde_argumentos(parser, args)
    try:
        respuesta = json.loads(args.respuesta.read_text(encoding='utf-8-sig'))
        print(json.dumps(registrar(raiz, args.id, respuesta), ensure_ascii=False, indent=2))
    except (RuntimeError, ValueError, OSError) as exc:
        parser.exit(1, 'ERROR PUBLICACIÓN: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
