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

    def test_no_confunde_menciones_en_parrafos_con_encabezados(self):
        cuerpo = self.cuerpo.replace("Un cuerpo que solo debe aparecer una vez.",
                                    "La evidencia orienta. Otra evidencia ayuda.")
        captura = cuerpo.replace("## ", "")
        self.assertEqual(auditar(cuerpo, captura), [])

    def test_mencion_en_parrafo_no_sustituye_encabezado_ausente(self):
        captura = self.cuerpo.replace("## Evidencia", "La evidencia orienta.")
        errores = auditar(self.cuerpo, captura)
        self.assertTrue(any("'Evidencia': 0 apariciones" in e for e in errores))

    def test_rechaza_pie_duplicado(self):
        pie = "Autor / Commons, CC0."
        errores = auditar(self.cuerpo, self.cuerpo, pie + pie, pie)
        self.assertTrue(any("pie no coincide" in e for e in errores))


if __name__ == "__main__":
    unittest.main()
