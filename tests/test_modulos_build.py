"""Límites del compilador tras la separación del ciclo 6."""

import ast
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "scripts"
sys.path.insert(0, str(SCRIPTS))

import banco  # noqa: E402
import bibliografia  # noqa: E402
import build  # noqa: E402
import configuracion  # noqa: E402
import validacion  # noqa: E402


class ModulosBuildTest(unittest.TestCase):
    def test_fachada_conserva_api_historica(self):
        self.assertIs(build.cargar, banco.cargar)
        self.assertIs(build.estado_publicacion, banco.estado_publicacion)
        self.assertIs(build.resolver_citas, bibliografia.resolver_citas)
        self.assertIs(build.CAPITULOS, configuracion.CAPITULOS)
        self.assertIs(build.validar, validacion.validar)

    def test_comandos_no_dependen_de_la_fachada(self):
        consumidores = (
            "atlas.py", "epub.py", "indice.py", "libro.py", "qmd.py",
            "refs.py", "senuelo.py", "verificar_publicacion.py",
        )
        for nombre in consumidores:
            arbol = ast.parse((SCRIPTS / nombre).read_text(encoding="utf-8"))
            modulos = set()
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Import):
                    modulos.update(alias.name for alias in nodo.names)
                elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                    modulos.add(nodo.module)
            self.assertNotIn("build", modulos, nombre)


if __name__ == "__main__":
    unittest.main()
