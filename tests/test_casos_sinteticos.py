"""Synthetic disclosure and real-patient consent remain separate."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from banco import estado_publicacion

class CasosSinteticosTest(unittest.TestCase):
    def caso(self, **extra):
        return dict(tipo="caso", estado="revisado", url="", sintetico=True,
                    consentimiento="no_aplica",
                    cuerpo="**Caso sintético con fines docentes.**", **extra)

    def test_sintetico_declarado_admite_revision_y_publicacion(self):
        e = self.caso()
        self.assertEqual(estado_publicacion(e), "revisado")
        e.update(estado="publicado", url="https://example.org/caso/")
        self.assertEqual(estado_publicacion(e), "publicado")

    def test_no_aplica_no_exime_caso_real(self):
        e = self.caso()
        e["sintetico"] = False
        with self.assertRaisesRegex(RuntimeError, "consentimiento"):
            estado_publicacion(e)

    def test_sintetico_requiere_aviso_tipo_y_consentimiento_coherentes(self):
        for cambio in ({"cuerpo": "sin aviso"}, {"sintetico": "true"},
                       {"consentimiento": "obtenido"}):
            e = self.caso()
            e.update(cambio)
            with self.subTest(cambio=cambio), self.assertRaises(RuntimeError):
                estado_publicacion(e)
