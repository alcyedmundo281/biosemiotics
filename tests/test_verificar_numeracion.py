from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verificar_numeracion import verificar


def ficha(numero, identificador=None, volumen=1):
    return dict(id=identificador or f'articulo-{numero}', tipo='concepto',
                estado='publicado', url=f'https://example.org/{identificador or numero}/',
                numero=numero, volumen=volumen,
                fecha_publicacion='2026-11-06T12:00:00.000+00:00')


class NumeracionGlobalTest(unittest.TestCase):
    def test_orden_de_archivos_y_cambio_de_volumen_no_reinician(self):
        self.assertEqual(verificar([ficha(3,volumen=2),ficha(1),ficha(2)]),3)

    def test_dos_ramas_validas_fallan_al_combinarse(self):
        base=[ficha(n) for n in range(1,57)]
        rama_a=ficha(57,'rama-a')
        rama_b=ficha(57,'rama-b')
        self.assertEqual(verificar(base+[rama_a]),57)
        self.assertEqual(verificar(base+[rama_b]),57)
        with self.assertRaisesRegex(RuntimeError,'57 duplicado: rama-a, rama-b'):
            verificar(base+[rama_a,rama_b])

    def test_hueco_no_se_acepta_aunque_no_haya_duplicados(self):
        with self.assertRaisesRegex(RuntimeError,r'huecos desde 1: \[2\]'):
            verificar([ficha(1),ficha(3)])

    def test_no_puede_empezar_en_dos(self):
        with self.assertRaisesRegex(RuntimeError,r'huecos desde 1: \[1\]'):
            verificar([ficha(2)])

    def test_borrador_no_oculta_hueco_de_publicadas(self):
        borrador=dict(ficha(2),estado='borrador',url='')
        with self.assertRaisesRegex(RuntimeError,'huecos'):
            verificar([ficha(1),borrador,ficha(3)])

    def test_falta_de_numero_es_error(self):
        e=ficha(1);e.pop('numero')
        with self.assertRaisesRegex(RuntimeError,'numero'):
            verificar([e])
