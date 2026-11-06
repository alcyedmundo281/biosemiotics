"""El banco conserva la asignación aprobada y bloquea publicaciones incompletas."""
import csv
from datetime import datetime
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from banco import cargar, estado_publicacion


class MetadatosSeriadoTest(unittest.TestCase):
    def test_banco_coincide_caracter_por_caracter_con_csv(self):
        path=ROOT/'docs/auditorias/2026-11-06-numeracion/propuesta-numeracion.csv'
        with path.open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        bank={e['id']:e for e in cargar(ROOT) if e.get('estado')=='publicado'}
        self.assertEqual(len(rows),56)
        self.assertEqual(set(bank),{r['id_banco'] for r in rows})
        for row in rows:
            e=bank[row['id_banco']]
            with self.subTest(id=e['id']):
                self.assertIs(type(e['fecha_publicacion']),str)
                self.assertEqual(e['fecha_publicacion'],row['published_at'])
                self.assertEqual(e['numero'],int(row['numero_propuesto']))
                self.assertEqual(e['ghost_id'],row['ghost_id'])

    def test_publicado_exige_metadatos_validos(self):
        valid=dict(id='nuevo',tipo='concepto',estado='publicado',
                   url='https://example.org/nuevo/',numero=57,
                   fecha_publicacion='2026-11-06T12:34:56.000+00:00')
        self.assertEqual(estado_publicacion(valid),'publicado')
        for key in ('numero','fecha_publicacion'):
            missing=valid.copy(); missing.pop(key)
            with self.subTest(missing=key), self.assertRaisesRegex(RuntimeError,key):
                estado_publicacion(missing)
        for key,values in [('numero',[None,True,0,-1,'57',57.0]),
                           ('fecha_publicacion',[None,'','2026-11-06',
                            '2026-11-06T12:34:56.000','2026-02-30T12:00:00+00:00',
                            datetime(2026,11,6,12,34,56)])]:
            for value in values:
                with self.subTest(key=key,value=value), self.assertRaisesRegex(RuntimeError,key):
                    estado_publicacion(dict(valid,**{key:value}))

    def test_borrador_y_revisado_no_requieren_asignacion(self):
        for state in ('borrador','revisado'):
            self.assertEqual(estado_publicacion(dict(tipo='concepto',estado=state,url='')),state)
