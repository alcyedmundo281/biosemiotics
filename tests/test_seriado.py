import json
import re
import unittest
from pathlib import Path

import yaml

from scripts.indice import jsonld, jsonld_seriado

RAIZ = Path(__file__).resolve().parents[1]
TITULO = "biosemiotics — atlas de POCUS para el médico de primer contacto"
ISSN = "3144-7813"


class SeriadoTest(unittest.TestCase):
    def test_cada_tipo_de_ficha_pertenece_al_seriado(self):
        for tipo in ("concepto", "signo", "caso"):
            with self.subTest(tipo=tipo):
                ld = jsonld({"tipo": tipo, "titulo": "Ficha de prueba"})
                self.assertEqual(ld["@type"], "ScholarlyArticle")
                self.assertNotIn("issn", ld)
                seriado = ld["isPartOf"]
                self.assertEqual(seriado["@type"], "Periodical")
                self.assertEqual(seriado["name"], TITULO)
                self.assertEqual(seriado["issn"], ISSN)
                self.assertEqual(seriado["@id"], "https://www.biosemiotics.net/#seriado")

    def test_pie_publico_y_fichas_comparten_la_identidad(self):
        html = (RAIZ / "artefactos/ghost-pie.html").read_text(encoding="utf-8")
        ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                  html, re.S).group(1))
        self.assertEqual(ld.pop("@context"), "https://schema.org")
        self.assertEqual(ld, jsonld_seriado())
        self.assertIn("ISSN 3144-7813 (en línea)", html)

    def test_identificadores_bibliograficos_sin_confundir_con_doi(self):
        zenodo = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))
        related = [x for x in zenodo["related_identifiers"] if x["identifier"] == ISSN]
        self.assertEqual(related, [{"identifier": ISSN, "scheme": "issn",
                                    "relation": "isDerivedFrom"}])
        cff = yaml.safe_load((RAIZ / "CITATION.cff").read_text(encoding="utf-8"))
        ids = [x for x in cff["identifiers"] if x["value"] == ISSN]
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0]["type"], "other")
        self.assertIn("ISSN", ids[0]["description"])
        self.assertNotEqual(cff["doi"], ISSN)


if __name__ == "__main__":
    unittest.main()
