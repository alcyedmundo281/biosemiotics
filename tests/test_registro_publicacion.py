import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import ghost  # noqa: E402
import indice  # noqa: E402
from auditar_pegado_ghost import cuerpo_markdown, huella  # noqa: E402


class RegistroPublicacionTest(unittest.TestCase):
    def setUp(self):
        self.entidad = {
            "id": "signo-demo",
            "tipo": "signo",
            "titulo": "Signo demo",
            "abstract": "Resumen clínico",
            "estado": "revisado",
            "nivel": "principiante",
            "refs": ["demo2026"],
            "cuerpo": "## El signo\n\nHallazgo [demo2026].\n\n## Practica esto\n\nEjercicio.",
        }
        self.bibliografia = {
            "demo2026": {
                "author": "Uno, A",
                "title": "Estudio",
                "journal": "Revista",
                "year": "2026",
                "doi": "10.1/demo",
                "pmid": "123",
            }
        }

    def test_indice_registra_huella_del_mismo_cuerpo_que_ghost(self):
        ficha = indice.ficha(self.entidad, self.bibliografia)
        self.assertEqual(
            ficha["ghost_sha256"],
            ghost.huella_cuerpo_ghost(self.entidad, self.bibliografia),
        )
        markdown = ghost.markdown_ghost(self.entidad, self.bibliografia)
        self.assertEqual(
            ficha["ghost_sha256"], huella(cuerpo_markdown(markdown))["sha256"]
        )
        modificada = dict(self.entidad, cuerpo=self.entidad["cuerpo"] + "\nCambio")
        self.assertNotEqual(
            ficha["ghost_sha256"],
            ghost.huella_cuerpo_ghost(modificada, self.bibliografia),
        )

    def test_xml_declara_intercambio_educativo_y_no_investigacion(self):
        raiz = ET.fromstring(indice.jats(self.entidad))
        self.assertEqual(raiz.get("article-type"), "other")
        self.assertEqual(
            raiz.get("specific-use"), "biosemiotics-educational-interchange"
        )
        titulos = [n.text for n in raiz.findall("./body/sec/title")]
        self.assertIn("El signo", titulos)
        self.assertNotIn("Practica esto", titulos)


if __name__ == "__main__":
    unittest.main()
