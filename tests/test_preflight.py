import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import preflight  # noqa: E402


class ModuloYaml:
    @staticmethod
    def safe_load(valor):
        return valor


class PreflightTest(unittest.TestCase):
    def test_rechaza_python_anterior_al_piso(self):
        self.assertTrue(preflight.comprobar_python((3, 8, 20)))
        self.assertFalse(preflight.comprobar_python((3, 9, 0)))

    def test_exige_version_reproducible_de_pyyaml(self):
        self.assertFalse(preflight.comprobar_pyyaml(lambda _: "6.0.3", lambda _: ModuloYaml))
        errores = preflight.comprobar_pyyaml(lambda _: "6.0.2", lambda _: ModuloYaml)
        self.assertIn("requirements.txt fija 6.0.3", errores[0])

    def test_detecta_estructura_incompleta(self):
        with tempfile.TemporaryDirectory() as temporal:
            errores = preflight.comprobar_estructura(Path(temporal))
        self.assertIn("falta conceptos/", errores)
        self.assertIn("falta build/index.json", errores)

    def test_publicacion_exige_toolchain_y_epubcheck(self):
        presentes = {nombre: f"/bin/{nombre}" for nombre in preflight.HERRAMIENTAS_PUBLICACION}
        buscar = lambda nombre: presentes.get(nombre)
        errores = preflight.comprobar_herramientas_publicacion(buscar, {})
        self.assertEqual(errores, ["falta epubcheck o la variable EPUBCHECK_JAR"])

    def test_acepta_epubcheck_en_path(self):
        buscar = lambda nombre: f"/bin/{nombre}"
        self.assertFalse(preflight.comprobar_herramientas_publicacion(buscar, {}))


if __name__ == "__main__":
    unittest.main()
