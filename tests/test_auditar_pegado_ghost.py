import unittest

from scripts.auditar_pegado_ghost import auditar, cuerpo_markdown, huella


CANON = """---
title: Prueba
---
## Inicio

Un cuerpo que solo debe aparecer una vez.

## Evidencia

Una referencia.

## Cierre

Fin.
"""


class AuditoriaGhostTest(unittest.TestCase):
    def setUp(self):
        self.cuerpo = cuerpo_markdown(CANON)

    def test_huella_extrae_encabezados(self):
        self.assertEqual(huella(self.cuerpo)["encabezados"], ["Inicio", "Evidencia", "Cierre"])

    def test_acepta_cuerpo_unico_y_pie_exacto(self):
        errores = auditar(self.cuerpo, self.cuerpo, "Autor / Commons, CC0.", "Autor / Commons, CC0.")
        self.assertEqual(errores, [])

    def test_rechaza_cuerpo_duplicado(self):
        errores = auditar(self.cuerpo, self.cuerpo + "\n" + self.cuerpo)
        self.assertTrue(any("apariciones" in e for e in errores))
        self.assertTrue(any("demasiado largo" in e for e in errores))

    def test_rechaza_pie_duplicado(self):
        pie = "Autor / Commons, CC0."
        errores = auditar(self.cuerpo, self.cuerpo, pie + pie, pie)
        self.assertTrue(any("pie no coincide" in e for e in errores))


if __name__ == "__main__":
    unittest.main()
