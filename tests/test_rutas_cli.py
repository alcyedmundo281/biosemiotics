"""Los comandos resuelven el banco y sus artefactos sin depender del cwd."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
import rutas


class RutasTest(unittest.TestCase):
    def test_raiz_por_defecto_es_estable_desde_cualquier_directorio(self):
        with tempfile.TemporaryDirectory() as temporal, patch.object(Path, "cwd", return_value=Path(temporal)):
            self.assertEqual(rutas.resolver_raiz(), REPO)

    def test_raiz_explicita_relativa_se_interpreta_desde_cwd(self):
        with tempfile.TemporaryDirectory() as temporal:
            base = Path(temporal)
            banco = base / "banco"
            banco.mkdir()
            anterior = Path.cwd()
            os.chdir(base)
            try:
                self.assertEqual(rutas.resolver_raiz("banco"), banco.resolve())
            finally:
                os.chdir(anterior)

    def test_salida_relativa_pertenece_al_banco_y_absoluta_se_respeta(self):
        salida = rutas.desde_raiz(REPO, "build/prueba.txt")
        self.assertEqual(salida, REPO / "build/prueba.txt")
        with tempfile.TemporaryDirectory() as temporal:
            absoluta = Path(temporal).resolve() / "salida.txt"
            self.assertEqual(rutas.desde_raiz(REPO, absoluta), absoluta)

    def test_raiz_inexistente_da_error_accionable(self):
        with tempfile.TemporaryDirectory() as temporal:
            inexistente = Path(temporal) / "no-existe"
            with self.assertRaisesRegex(RuntimeError, "no existe"):
                rutas.resolver_raiz(inexistente)


class ComandosDesdeOtroDirectorioTest(unittest.TestCase):
    def ejecutar(self, script, *args, cwd):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args], cwd=cwd,
            capture_output=True, encoding="utf-8", timeout=30,
        )

    def test_auditoria_referencias_default_desde_scripts_y_fuera_del_repo(self):
        with tempfile.TemporaryDirectory() as temporal:
            for cwd in (SCRIPTS, Path(temporal)):
                with self.subTest(cwd=cwd):
                    resultado = self.ejecutar("refs.py", cwd=cwd)
                    self.assertEqual(resultado.returncode, 0, resultado.stderr)
                    self.assertIn("Todas las claves citadas", resultado.stdout)

    def test_interfaces_diarias_cargan_desde_fuera_del_repo(self):
        scripts = (
            "atlas.py", "auditar_medios.py", "auditar_pegado_ghost.py", "build.py",
            "consultas.py", "epub.py", "indice.py", "libro.py", "nuevo.py",
            "paquete_latex.py", "preflight.py", "qmd.py", "refs.py", "senuelo.py",
            "verificar_citas.py", "verificar_publicacion.py",
        )
        with tempfile.TemporaryDirectory() as temporal:
            for script in scripts:
                with self.subTest(script=script):
                    resultado = self.ejecutar(script, "--help", cwd=Path(temporal))
                    self.assertEqual(resultado.returncode, 0, resultado.stderr)
                    self.assertIn("usage:", resultado.stdout.lower())

    def test_preflight_completo_funciona_desde_fuera_del_repo(self):
        with tempfile.TemporaryDirectory() as temporal:
            resultado = self.ejecutar("preflight.py", cwd=Path(temporal))
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Preflight listo: perfil banco", resultado.stdout)

    def test_nuevo_escribe_en_raiz_explicita_desde_otro_cwd(self):
        with tempfile.TemporaryDirectory() as temporal, tempfile.TemporaryDirectory() as cwd:
            banco = Path(temporal)
            resultado = self.ejecutar(
                "nuevo.py", "--raiz", str(banco), "signo", "ruta-demo", "Ruta demo",
                cwd=Path(cwd),
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertTrue((banco / "signos/ruta-demo.qmd").is_file())
            self.assertFalse((Path(cwd) / "signos/ruta-demo.qmd").exists())

    def test_consultas_busca_db_bajo_raiz_y_explica_como_generarla(self):
        with tempfile.TemporaryDirectory() as temporal, tempfile.TemporaryDirectory() as cwd:
            banco = Path(temporal)
            resultado = self.ejecutar("consultas.py", "--raiz", str(banco), cwd=Path(cwd))
            self.assertNotEqual(resultado.returncode, 0)
            self.assertIn(str(banco / "build/atlas.db"), resultado.stderr)
            self.assertIn("scripts/build.py", resultado.stderr)

    def test_indice_con_raiz_duplicada_falla_claro(self):
        resultado = self.ejecutar(
            "indice.py", str(REPO), "--raiz", str(REPO), cwd=REPO,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("no ambas", resultado.stderr)


if __name__ == "__main__":
    unittest.main()
