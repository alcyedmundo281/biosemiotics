"""No se aprueban citas cuando la comprobación queda incompleta."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import refs
import verificar_citas as citas


class VerificarCitasTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.bib = "@article{demo,\n pmid={123},\n doi={10.1234/demo},\n title={Demo},\n}\n"
        (self.raiz / "refs.bib").write_text(self.bib, encoding="utf-8")
        self.pm = [{"pmid": "123", "doi": "10.1234/demo", "titulo": "Demo"}]
        self.cr = {"doi": "10.1234/demo", "title": "Demo"}
        self.parches = [patch.object(citas, "resumen", return_value=self.pm),
                        patch.object(citas, "crossref", return_value=self.cr),
                        patch.object(citas.time, "sleep")]
        self.pubmed, self.crossref, self.sleep = [p.start() for p in self.parches]
        for p in self.parches:
            self.addCleanup(p.stop)

    def ejecutar(self, *args):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = citas.main(["--raiz", str(self.raiz), *args])
        return codigo, salida.getvalue()

    def exencion(self, texto="demo # Revista sin depósito en Crossref\n"):
        (self.raiz / "refs-sin-crossref.txt").write_text(texto, encoding="utf-8")

    def test_exito_completo_con_y_sin_bandera(self):
        for args in ((), ("--estricto",)):
            codigo, salida = self.ejecutar(*args)
            self.assertEqual(codigo, 0)
            self.assertIn("Todas las referencias verificadas", salida)

    def test_pubmed_timeout_bloquea_y_reintenta_tres_veces(self):
        self.pubmed.side_effect = TimeoutError("timeout simulado")
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 2)
        self.assertIn("INCOMPLETA", salida)
        self.assertNotIn("✓", salida)
        self.assertEqual(self.pubmed.call_count, 3)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [1, 2])
        self.crossref.assert_not_called()

    def test_pubmed_se_recupera_tras_429_y_503(self):
        self.pubmed.side_effect = [urllib.error.HTTPError("url", 429, "", {}, None),
                                   urllib.error.HTTPError("url", 503, "", {}, None), self.pm]
        self.assertEqual(self.ejecutar()[0], 0)
        self.assertEqual(self.pubmed.call_count, 3)

    def test_crossref_agotado_detiene_el_banco_sin_verde(self):
        (self.raiz / "refs.bib").write_text(self.bib + self.bib.replace("demo,", "otro,"))
        self.crossref.side_effect = citas.RedError("HTTP 503")
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 2)
        self.assertEqual(self.crossref.call_count, 3)
        self.assertIn("demo:", salida)
        self.assertIn("1 entradas posteriores sin consultar", salida)
        self.assertNotIn("✓", salida)

    def test_crossref_se_recupera(self):
        self.crossref.side_effect = [citas.RedError("HTTP 429"), self.cr]
        self.assertEqual(self.ejecutar()[0], 0)
        self.assertEqual(self.crossref.call_count, 2)

    def test_404_sin_exencion_es_discrepancia_sin_reintento(self):
        self.crossref.side_effect = citas.DoiNoResuelve(404)
        self.assertEqual(self.ejecutar()[0], 1)
        self.assertEqual(self.crossref.call_count, 1)

    def test_exencion_solo_404_y_nunca_omite_pubmed(self):
        self.exencion()
        self.crossref.side_effect = citas.DoiNoResuelve(404)
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 0)
        self.assertIn("solo contra PubMed", salida)
        self.pubmed.return_value = []
        self.assertEqual(self.ejecutar()[0], 1)
        self.pubmed.return_value = [{"pmid": "123", "doi": None}]
        self.assertEqual(self.ejecutar()[0], 1)
        self.pubmed.return_value = self.pm
        self.crossref.side_effect = citas.DoiNoResuelve(400)
        self.assertEqual(self.ejecutar()[0], 1)
        self.crossref.side_effect = citas.RedError("HTTP 503")
        self.assertEqual(self.ejecutar()[0], 2)

    def test_exencion_sin_razon_desconocida_o_duplicada_bloquea(self):
        for texto in ("demo\n", "inexistente # razón\n", "demo # razón\ndemo # otra\n",
                      "10. # demasiado amplio\n"):
            with self.subTest(texto=texto):
                self.exencion(texto)
                self.assertEqual(self.ejecutar()[0], 1)
        self.pubmed.assert_not_called()

    def test_bibliografia_duplicada_vacia_o_incompleta_falla_antes_de_red(self):
        for texto in (self.bib * 2, "", self.bib.replace(" doi={10.1234/demo},\n", ""),
                      self.bib + "@article{incompleta,\n"):
            with self.subTest(texto=texto):
                (self.raiz / "refs.bib").write_text(texto)
                self.assertEqual(self.ejecutar()[0], 1)
        self.pubmed.assert_not_called()

    def test_doi_se_compara_sin_eliminar_puntuacion(self):
        self.crossref.return_value = dict(self.cr, doi="10.1234.demo")
        self.assertEqual(self.ejecutar()[0], 1)
        self.crossref.return_value = dict(self.cr, doi="10.1234/DEMO")
        self.assertEqual(self.ejecutar()[0], 0)


class ClientesCitasTest(unittest.TestCase):
    def test_clasifica_http_crossref(self):
        for codigo, clase, reintenta in ((404, citas.DoiNoResuelve, False),
                                        (400, citas.DoiNoResuelve, False),
                                        (429, citas.RedError, True), (503, citas.RedError, True),
                                        (403, citas.RedError, False)):
            with self.subTest(codigo=codigo), patch("urllib.request.urlopen", side_effect=
                    urllib.error.HTTPError("url", codigo, "", {}, None)):
                with self.assertRaises(clase) as error:
                    citas.crossref("10.1234/demo")
                if isinstance(error.exception, citas.RedError):
                    self.assertEqual(error.exception.reintentable, reintenta)

    def test_json_roto_y_respuesta_sin_doi_no_cuentan_como_verificacion(self):
        for datos in (b"no-json", b'{"message": {}}'):
            with patch("urllib.request.urlopen") as abrir:
                abrir.return_value.__enter__.return_value.read.return_value = datos
                with self.assertRaises(citas.RedError):
                    citas.crossref("10.1234/demo")

    def test_pubmed_respuesta_error_no_se_convierte_en_lista_vacia(self):
        for respuesta in ({"error": "rate limit"}, {}, {"result": {"error": "backend"}}):
            with patch.object(refs, "_get", return_value=json.dumps(respuesta)):
                with self.assertRaises(ValueError):
                    refs.resumen(["123"])

    def test_error_no_reintentable_no_duerme(self):
        with patch.object(citas.time, "sleep") as dormir:
            with self.assertRaises(citas.RedError):
                citas.reintentar(lambda: (_ for _ in ()).throw(citas.RedError("HTTP 403", False)))
            dormir.assert_not_called()


if __name__ == "__main__":
    unittest.main()
