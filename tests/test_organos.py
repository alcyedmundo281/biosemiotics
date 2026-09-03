"""El nombre de presentación de cada órgano en el libro.

La taxonomía del mapa maestro usa slugs ASCII porque son claves de datos. El
libro necesita el nombre escrito como se lee en español, y derivarlo con
`.title()` producía "Pulmon", "Riñon" y "Aorta Abdominal".
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import build  # noqa: E402


class NombreOrganoTest(unittest.TestCase):
    def test_restituye_las_tildes_de_la_taxonomia(self):
        self.assertEqual(build.nombre_organo("pulmon"), "Pulmón")
        self.assertEqual(build.nombre_organo("riñon"), "Riñón")
        self.assertEqual(build.nombre_organo("corazon"), "Corazón")
        self.assertEqual(build.nombre_organo("via-biliar"), "Vía biliar")

    def test_usa_mayuscula_solo_en_la_primera_palabra(self):
        # `.title()` daba "Aorta Abdominal"; en español la segunda palabra va
        # en minúscula.
        self.assertEqual(build.nombre_organo("aorta-abdominal"), "Aorta abdominal")
        self.assertEqual(build.nombre_organo("vena-profunda"), "Vena profunda")

    def test_un_organo_sin_mapear_no_rompe_la_compilacion(self):
        self.assertEqual(build.nombre_organo("nervio-optico"), "Nervio optico")

    def test_sin_organo_cae_en_otros(self):
        self.assertEqual(build.nombre_organo(""), "Otros")
        self.assertEqual(build.nombre_organo(None), "Otros")

    def test_cubre_todos_los_organos_del_banco(self):
        usados = {
            e.get("organo")
            for e in build.cargar(RAIZ)
            if e["tipo"] == "signo" and e.get("organo")
        }
        sin_mapear = sorted(usados - set(build.ORGANOS))
        self.assertEqual(sin_mapear, [], f"órganos sin nombre de presentación: {sin_mapear}")


if __name__ == "__main__":
    unittest.main()
