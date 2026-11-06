#!/usr/bin/env python3
"""Bloquea designaciones publicadas duplicadas o con huecos en cualquier volumen."""
import argparse
from collections import defaultdict

from banco import cargar, estado_publicacion
from rutas import blindar_salida, raiz_argumentos, raiz_desde_argumentos


def verificar(entidades):
    publicadas = [e for e in entidades if estado_publicacion(e) == 'publicado']
    por_numero = defaultdict(list)
    for e in publicadas:
        por_numero[e['numero']].append(e['id'])
    errores = []
    for numero, ids in sorted(por_numero.items()):
        if len(ids) > 1:
            errores.append(f'numero {numero} duplicado: {", ".join(ids)}')
    esperados = set(range(1, len(publicadas) + 1))
    encontrados = set(por_numero)
    faltantes = sorted(esperados - encontrados)
    sobrantes = sorted(encontrados - esperados)
    if faltantes:
        errores.append(f'huecos desde 1: {faltantes}')
    if sobrantes:
        errores.append(f'números fuera de la secuencia 1..{len(publicadas)}: {sobrantes}')
    if errores:
        raise RuntimeError('designaciones globales inválidas:\n  - ' + '\n  - '.join(errores))
    return len(publicadas)


def main():
    blindar_salida()
    parser = argparse.ArgumentParser(description=__doc__)
    raiz_argumentos(parser)
    args = parser.parse_args()
    raiz = raiz_desde_argumentos(parser, args)
    try:
        cantidad = verificar(cargar(raiz))
    except (RuntimeError, ValueError, OSError) as exc:
        parser.exit(1, 'ERROR NUMERACIÓN: ' + str(exc) + '\n')
    print(f'✓ Numeración global: {cantidad} fichas publicadas, única y contigua desde 1')


if __name__ == '__main__':
    main()
