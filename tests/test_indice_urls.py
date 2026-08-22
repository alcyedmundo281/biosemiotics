import unittest
import xml.etree.ElementTree as ET

from scripts.indice import XLINK_NS, jats


class JatsUrlTest(unittest.TestCase):
    def test_incluye_url_publica_como_self_uri(self):
        url = "https://www.biosemiotics.net/concepto-prueba/"
        xml = jats({
            "id": "concepto-prueba",
            "tipo": "concepto",
            "titulo": "Concepto de prueba",
            "url": url,
            "cuerpo": "## Dónde NO confiar\n\nLímite de prueba.",
        })

        raiz = ET.fromstring(xml)
        self_uri = raiz.find("./front/article-meta/self-uri")
        self.assertIsNotNone(self_uri)
        self.assertEqual(self_uri.get("content-type"), "web")
        self.assertEqual(self_uri.get(f"{{{XLINK_NS}}}href"), url)


if __name__ == "__main__":
    unittest.main()
