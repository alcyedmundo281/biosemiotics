import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import registrar_publicacion as registro


class RegistrarPublicacionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'conceptos').mkdir()
        self.target = self.root/'conceptos/nuevo.qmd'
        self.original = (b'---\r\nestado: revisado\r\nfecha_revision: 2026-11-06\r\n'
                         b'ghost_id: null\r\nid: nuevo\r\ntipo: concepto\r\n'
                         b'titulo: Nuevo\r\nurl: ""\r\n---\r\nCuerpo intacto.\r\n')
        self.target.write_bytes(self.original)
        for n in (1, 56):
            m=dict(id='viejo'+str(n), tipo='concepto', titulo='Viejo', estado='borrador',
                   url='', numero=n)
            (self.root/f'conceptos/viejo{n}.qmd').write_text('---\n'+yaml.safe_dump(m)+'---\nCuerpo')
        self.post = dict(id='abcdef0123456789abcdef01',url='https://www.biosemiotics.net/nuevo/',
                         status='published',published_at='2026-11-07T22:30:17.000+00:00')

    def ejecutar(self, **changes):
        return registro.registrar(self.root,'nuevo',dict(posts=[dict(self.post,**changes)]))

    def test_registro_atomico_maximo_global_y_fecha_exacta(self):
        result=self.ejecutar()
        self.assertEqual(result['numero'],57)  # no rellena los huecos 2..55
        self.assertEqual(result['volumen'],1)
        raw=self.target.read_bytes()
        self.assertIn(b'fecha_publicacion: "2026-11-07T22:30:17.000+00:00"\r\n',raw)
        fm=yaml.safe_load(raw.decode().split('---',2)[1])
        self.assertIs(type(fm['fecha_publicacion']),str)
        self.assertEqual(fm['fecha_publicacion'],self.post['published_at'])
        self.assertEqual(fm['url'],self.post['url'])
        self.assertEqual(fm['ghost_id'],self.post['id'])
        self.assertTrue(raw.endswith(b'---\r\nCuerpo intacto.\r\n'))
        self.assertIn(b'fecha_revision: 2026-11-06\r\n',raw)
        with self.assertRaisesRegex(RuntimeError,'ya tenía numero'):
            self.ejecutar()
        self.assertEqual(self.target.read_bytes(),raw)

    def test_volumen_avanza_sin_reiniciar_numero(self):
        r=self.ejecutar(published_at='2027-01-01T00:00:00.123+00:00')
        self.assertEqual((r['volumen'],r['numero']),(2,57))

    def test_respuesta_incompleta_o_invalida_no_escribe(self):
        for change in ({'published_at':None},{'published_at':''},
                       {'published_at':'2026-11-07'},{'published_at':'2026-11-07T22:30:17'},
                       {'published_at':'2026-02-30T22:30:17+00:00'},
                       {'status':'draft'},{'url':None},{'id':'inventado'}):
            with self.subTest(change=change),self.assertRaises(RuntimeError):
                self.ejecutar(**change)
            self.assertEqual(self.target.read_bytes(),self.original)
        p=copy.deepcopy(self.post);p.pop('published_at')
        with self.assertRaisesRegex(RuntimeError,'published_at'):
            registro.registrar(self.root,'nuevo',{'posts':[p]})

    def test_ficha_ya_numerada_no_se_recalcula(self):
        raw=self.original.replace(b'estado: revisado',b'estado: revisado\r\nnumero: 12')
        self.target.write_bytes(raw)
        with self.assertRaisesRegex(RuntimeError,'ya tenía numero'):
            self.ejecutar()
        self.assertEqual(self.target.read_bytes(),raw)

    def test_colision_entre_calculo_y_escritura_falla_sin_reintentar(self):
        real=registro.inventario
        calls=[]
        def cambio(root):
            es,ns=real(root);calls.append(1)
            return es,ns+([57] if len(calls)==2 else [])
        with patch.object(registro,'inventario',side_effect=cambio):
            with self.assertRaisesRegex(RuntimeError,'calculado ya existe'):
                self.ejecutar()
        self.assertEqual(len(calls),2)
        self.assertEqual(self.target.read_bytes(),self.original)

    def test_bloqueo_y_fallo_de_replace_no_dejan_publicacion_parcial(self):
        lock=self.root/'.registro-publicacion.lock'
        lock.touch()
        with self.assertRaisesRegex(RuntimeError,'otro registro'):
            self.ejecutar()
        self.assertTrue(lock.exists())
        lock.unlink()
        with patch.object(registro.os,'replace',side_effect=OSError('fallo simulado')):
            with self.assertRaises(OSError):
                self.ejecutar()
        self.assertEqual(self.target.read_bytes(),self.original)
        self.assertFalse(lock.exists())
        self.assertEqual(sorted(p.name for p in (self.root/'conceptos').iterdir()),
                         ['nuevo.qmd','viejo1.qmd','viejo56.qmd'])
