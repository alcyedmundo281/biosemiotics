import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import banco
import qmd


def ficha(numero,fecha):
    return dict(id=f'ficha-{numero}',tipo='concepto',titulo='Prueba',estado='publicado',
                numero=numero,url=f'https://example.org/{numero}/',fecha_publicacion=fecha)


class CorteEdicionTest(unittest.TestCase):
    def test_anterior_entra_posterior_no_y_seriado_conserva_ambas(self):
        antes=ficha(1,'2026-11-12T23:00:00.000+00:00')
        despues=ficha(2,'2026-11-20T12:00:00.000+00:00')
        self.assertEqual(banco.seleccionar_edicion([antes,despues],'2026-11-13'),[antes])
        self.assertEqual(banco.seleccionar_publicables([antes,despues],True),[antes,despues])

    def test_corte_inclusivo_hasta_fin_del_dia_en_utc(self):
        ultimo=ficha(1,'2026-11-13T23:59:59.999999+00:00')
        siguiente=ficha(2,'2026-11-14T00:00:00.000+00:00')
        misma_hora=ficha(3,'2026-11-14T01:59:59.999999+02:00')
        self.assertEqual(banco.seleccionar_edicion([ultimo,siguiente,misma_hora],'2026-11-13'),[ultimo,misma_hora])

    def test_publicada_sin_fecha_aborta(self):
        e=ficha(1,None)
        for valor in (None,'','2026-11-12'):
            with self.subTest(valor=valor),self.assertRaisesRegex(RuntimeError,'fecha_publicacion'):
                banco.seleccionar_edicion([dict(e,fecha_publicacion=valor)],'2026-11-13')
        e.pop('fecha_publicacion')
        with self.assertRaisesRegex(RuntimeError,'fecha_publicacion'):
            banco.seleccionar_edicion([e],'2026-11-13')

    def test_corte_ausente_o_invalido_aborta_incluso_con_banco_vacio(self):
        for corte in (None,'','ayer','2026-02-30','20261113',123,'2026-11-13T00:00:00Z'):
            with self.subTest(corte=corte),self.assertRaisesRegex(RuntimeError,'FECHA_CORTE'):
                banco.seleccionar_edicion([],corte)

    def test_ensamblado_sin_corte_no_modifica_proyecto(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'build/quarto'
            with self.assertRaisesRegex(RuntimeError,'FECHA_CORTE'):
                qmd.generar([],root,out)
            self.assertFalse(out.exists())

    def test_edicion_real_sigue_en_56_con_articulo_57_del_20(self):
        entidades=banco.cargar(ROOT)
        antes=banco.seleccionar_edicion(entidades,'2026-11-13')
        futura=ficha(57,'2026-11-20T12:00:00.000+00:00')
        despues=banco.seleccionar_edicion(entidades+[futura],'2026-11-13')
        self.assertEqual(len(antes),56)
        self.assertEqual(despues,antes)
        self.assertEqual(len(banco.seleccionar_publicables(entidades+[futura],True)),57)
