"""Los comandos imprimen ✓, ✗ y → aunque la consola no sea UTF-8.

En Windows la consola es cp1252 y `print("✓ …")` aborta con UnicodeEncodeError.
CI corre en Ubuntu, donde la codificación por defecto ya es UTF-8, así que este
fallo era invisible para la integración y solo aparecía en la máquina del autor
—justo en `preflight.py`, el primer comando de cada sesión—.

Estas pruebas fijan el contrato en ambas direcciones: la salida normal y la de
error sobreviven a una consola cp1252, y ningún módulo vuelve a blindar la
salida como efecto secundario de importarse.
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
from rutas import escribir_texto

# Todo lo que tiene interfaz de línea de comandos.
CLI = [
    "atlas.py", "auditar_medios.py", "auditar_pegado_ghost.py", "build.py",
    "consultas.py", "epub.py", "indice.py", "libro.py", "nuevo.py",
    "paquete_latex.py", "preflight.py", "qmd.py", "refs.py", "senuelo.py",
    "verificar_citas.py", "verificar_publicacion.py",
]


def ejecutar(argumentos, codificacion="cp1252"):
    """Corre un script con una consola hostil a los símbolos del banco."""
    entorno = dict(os.environ, PYTHONIOENCODING=codificacion)
    entorno.pop("PYTHONUTF8", None)
    return subprocess.run(
        [sys.executable, *argumentos], cwd=REPO, env=entorno,
        capture_output=True, text=True, encoding="utf-8", timeout=300,
    )


class SalidaEnConsolaNoUTF8Test(unittest.TestCase):
    def test_preflight_no_muere_al_imprimir_el_visto_bueno(self):
        """La regresión concreta: exit 1 antes de decir nada útil."""
        resultado = ejecutar([str(SCRIPTS / "preflight.py")])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("✓", resultado.stdout)
        self.assertNotIn("UnicodeEncodeError", resultado.stderr)

    def test_verificar_publicacion_no_depende_de_importar_indice(self):
        """Antes funcionaba de rebote: indice.py blindaba stdout al importarse."""
        resultado = ejecutar([str(SCRIPTS / "verificar_publicacion.py")])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("✓", resultado.stdout)

    def test_la_ayuda_de_cada_cli_sobrevive_a_una_consola_cp1252(self):
        for nombre in CLI:
            with self.subTest(script=nombre):
                resultado = ejecutar([str(SCRIPTS / nombre), "--help"])
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                self.assertNotIn("UnicodeEncodeError", resultado.stderr)

    def test_los_errores_salen_en_utf8_no_en_la_codificacion_local(self):
        """stderr importa tanto como stdout: es lo que se lee cuando algo falla."""
        for nombre in ("indice.py", "atlas.py", "verificar_citas.py"):
            with self.subTest(script=nombre):
                with tempfile.TemporaryDirectory() as temporal:
                    inexistente = Path(temporal) / "no-existe"
                    resultado = ejecutar(
                        [str(SCRIPTS / nombre), "--raiz", str(inexistente)])
                self.assertNotEqual(resultado.returncode, 0)
                # 'raíz' llega entero: si stderr fuera cp1252, la í sería 0xed
                # y este texto no habría podido decodificarse como UTF-8.
                self.assertIn("raíz", resultado.stderr)


class BlindajeExplicitoTest(unittest.TestCase):
    def test_ningun_modulo_blinda_la_salida_al_importarse(self):
        """El blindaje se llama desde main(), nunca como efecto de import.

        Cuando vivía a nivel de módulo, que un script funcionara dependía de si
        casualmente importaba otro que reconfiguraba; retirar un import
        'que solo trae constantes' lo rompía a distancia.
        """
        patron = re.compile(r"(?m)^\s{0,3}(if hasattr\(sys\.stdout|sys\.(stdout|stderr)\.reconfigure)")
        for archivo in sorted(SCRIPTS.glob("*.py")):
            with self.subTest(script=archivo.name):
                texto = archivo.read_text(encoding="utf-8")
                if archivo.name == "rutas.py":
                    continue
                self.assertIsNone(patron.search(texto),
                                  f"{archivo.name} blinda la salida al importarse")

    def test_importar_indice_ya_no_altera_la_salida_del_proceso(self):
        codigo = (
            "import sys; sys.path.insert(0, %r);"
            "antes = sys.stdout.encoding;"
            "import indice;"
            "print(antes == sys.stdout.encoding)" % str(SCRIPTS)
        )
        resultado = ejecutar(["-c", codigo])
        self.assertEqual(resultado.stdout.strip(), "True", resultado.stderr)

    def test_cada_cli_blinda_su_salida_al_arrancar(self):
        for nombre in CLI:
            with self.subTest(script=nombre):
                texto = (SCRIPTS / nombre).read_text(encoding="utf-8")
                self.assertIn("blindar_salida()", texto)


class SaltoDeLineaTest(unittest.TestCase):
    def test_escribir_texto_usa_lf_en_cualquier_plataforma(self):
        with tempfile.TemporaryDirectory() as temporal:
            destino = Path(temporal) / "salida.txt"
            escribir_texto(destino, "primera\nsegunda\n")
            self.assertEqual(destino.read_bytes(), b"primera\nsegunda\n")

    def test_el_indice_generado_no_lleva_crlf(self):
        """Con CRLF, en Windows aparecía modificado tras cada indice.py.

        index.json es el caso comprobable: .gitattributes le fija `eol=lf`, así
        que git lo deja en LF al sacarlo y cualquier CRLF aquí lo puso el
        generador. atlas-inject.html no sirve para esto: es `text=auto` y con
        core.autocrlf=true git lo entrega en CRLF en Windows —lo cual es
        correcto, porque al compararlo lo normaliza a LF—.
        """
        archivo = REPO / "build" / "index.json"
        if not archivo.is_file():
            self.skipTest("falta build/index.json; corre indice.py")
        self.assertNotIn(b"\r\n", archivo.read_bytes())

    def test_los_generadores_fijan_el_salto_al_escribir(self):
        """Path.write_text no acepta newline hasta 3.10 y el piso es 3.9."""
        for nombre in ("indice.py", "build.py", "qmd.py", "atlas.py", "nuevo.py",
                       "auditar_medios.py"):
            with self.subTest(script=nombre):
                texto = (SCRIPTS / nombre).read_text(encoding="utf-8")
                self.assertNotIn(".write_text(", texto)
                self.assertIn("escribir_texto(", texto)


class DerivadosVersionadosTest(unittest.TestCase):
    """Lo que se versiona en build/ debe poder añadirse sin -f.

    Con el patrón `build/` git no re-incluye nada dentro del directorio
    excluido: las excepciones `!build/...` no surtían efecto y los derivados
    versionados solo se salvaban por estar ya rastreados. `git add` explícito
    los rechazaba, justo al regenerar el buscador.
    """

    def test_los_derivados_versionados_no_estan_ignorados(self):
        if not (REPO / ".git").exists():
            self.skipTest("no es un checkout de git")
        for relativo in ("build/index.json", "build/atlas-inject.html"):
            with self.subTest(derivado=relativo):
                resultado = subprocess.run(
                    ["git", "check-ignore", "-q", relativo], cwd=REPO)
                self.assertEqual(resultado.returncode, 1,
                                 f"{relativo} está ignorado por .gitignore")

    def test_el_resto_de_build_sigue_ignorado(self):
        if not (REPO / ".git").exists():
            self.skipTest("no es un checkout de git")
        for relativo in ("build/ghost/x.qmd", "build/quarto/libro.tex",
                         "build/atlas.db", "build/grafo.json"):
            with self.subTest(derivado=relativo):
                resultado = subprocess.run(
                    ["git", "check-ignore", "-q", relativo], cwd=REPO)
                self.assertEqual(resultado.returncode, 0,
                                 f"{relativo} dejó de estar ignorado")


if __name__ == "__main__":
    unittest.main()
