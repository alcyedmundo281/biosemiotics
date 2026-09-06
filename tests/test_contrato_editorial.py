"""Una ficha incompleta no debe reemplazar salidas públicas válidas."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build
import qmd


class ContratoEditorialTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name).resolve()
        self.bib = self.raiz / "refs.bib"
        self.bib.write_text("@article{demo,\n title={Demo},\n}\n", encoding="utf-8")
        self.ficha = dict(
            id="demo", tipo="signo", titulo="Demo", _archivo="signos/demo.qmd",
            estado="revisado",
            abstract="palabra " * 40, refs=["demo"], nivel="principiante",
            sistema="cardiovascular", organo="corazon", ventana="Ventana",
            sonda=["sectorial"], significante="Imagen", significado="Lectura",
            decision="Decisión", falsos_positivos=["Imitador"],
            cuerpo="\n\n".join(f"## {s}\nTexto." for s in build.SECCIONES["signo"]))

    def errores(self, ficha):
        return "\n".join(build.errores_editoriales([ficha], self.bib))

    def guardar(self, ficha):
        carpeta = self.raiz / "signos"
        carpeta.mkdir(exist_ok=True)
        meta = {k: v for k, v in ficha.items() if k not in ("cuerpo", "_archivo")}
        (carpeta / "demo.qmd").write_text(
            "---\n" + yaml.safe_dump(meta, allow_unicode=True) + "---\n" + ficha["cuerpo"],
            encoding="utf-8")

    def ejecutar(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                              cwd=self.raiz, capture_output=True, encoding="utf-8")

    def test_contratos_por_tipo(self):
        self.assertEqual(self.errores(self.ficha), "")
        concepto = dict(self.ficha, tipo="concepto", dominio="fisica", cuerpo="Explicación sin secciones.")
        self.assertEqual(self.errores(concepto), "")
        caso = dict(self.ficha, tipo="caso", decision_semiotica="Decisión", signos=["demo"],
                    cuerpo="\n\n".join(f"## {s}\nTexto." for s in build.SECCIONES["caso"]))
        self.assertEqual(self.errores(caso), "")
        caso["cuerpo"] = caso["cuerpo"].replace("## Los límites", "## Otra sección")
        self.assertIn("## Los límites", self.errores(caso))

    def test_campos_obligatorios_y_tipos_invalidos(self):
        for campo, valor in (("abstract", None), ("abstract", "corto"),
                             ("abstract", "palabra " * 81), ("refs", []),
                             ("refs", "demo"), ("refs", ["desconocida"]),
                             ("refs", [None]), ("decision", "TODO: completar"),
                             ("significante", " "), ("falsos_positivos", []),
                             ("sonda", []), ("ventana", None), ("sistema", []),
                             ("nivel", []), ("tipo", []), ("cuerpo", None)):
            with self.subTest(campo=campo, valor=valor):
                errores = self.errores(dict(self.ficha, **{campo: valor}))
                self.assertIn(campo, errores)
                self.assertIn("signos/demo.qmd (demo)", errores)

    def test_limites_ausentes_vacios_duplicados_o_en_codigo(self):
        for reemplazo in ("", "## Dónde NO confiar\n<!-- pendiente -->",
                          "## Dónde NO confiar\n### Subtítulo",
                          "```markdown\n## Dónde NO confiar\nTexto.\n```",
                          "<!--\n## Dónde NO confiar\nTexto.\n-->",
                          "## Dónde NO confiar\nTexto.\n## Dónde NO confiar\nOtro."):
            with self.subTest(reemplazo=reemplazo):
                ficha = dict(self.ficha, cuerpo=self.ficha["cuerpo"].replace(
                    "## Dónde NO confiar\nTexto.", reemplazo))
                self.assertIn("## Dónde NO confiar", self.errores(ficha))

    def test_bibliografia_ausente_bloquea(self):
        self.bib.unlink()
        self.assertIn("refs.bib", self.errores(self.ficha))

    def test_validar_eleva_faltas_editoriales_a_error(self):
        ficha = dict(self.ficha, decision="")
        errores, _ = build.validar([ficha], [], self.raiz)
        self.assertTrue(any("decision" in e for e in errores))
        errores, alertas = build.validar([dict(ficha, estado="borrador")], [], self.raiz, permitir_borradores=True)
        self.assertEqual(errores, [])
        self.assertTrue(any("decision" in a for a in alertas))

    def test_generadores_preservan_salida_anterior(self):
        ficha = dict(self.ficha, abstract="")
        destino = self.raiz / "build"
        (destino / "ghost").mkdir(parents=True)
        anterior = destino / "ghost" / "anterior.md"
        anterior.write_text("Conservar")
        with self.assertRaisesRegex(RuntimeError, "abstract"):
            build.build_ghost([ficha], destino, self.bib)
        self.assertEqual(anterior.read_text(), "Conservar")
        quarto = destino / "quarto"
        quarto.mkdir()
        (quarto / qmd.MARCADOR_PROYECTO).write_text(qmd.MARCA_PROYECTO)
        anterior = quarto / "anterior.md"
        anterior.write_text("Conservar")
        with self.assertRaisesRegex(RuntimeError, "abstract"):
            qmd.generar([ficha], self.raiz, quarto)
        self.assertEqual(anterior.read_text(), "Conservar")

    def test_comandos_publicos_fallan_antes_de_escribir(self):
        self.guardar(dict(self.ficha, abstract=""))
        destino = self.raiz / "build"
        destino.mkdir()
        for nombre in ("grafo.json", "atlas.db", "index.json", "atlas.html"):
            (destino / nombre).write_text("Conservar")
        for script, args in (("build.py", ()), ("indice.py", (str(self.raiz),)),
                             ("atlas.py", ())):
            with self.subTest(script=script):
                resultado = self.ejecutar(script, *args)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn("abstract", resultado.stderr)
                for archivo in destino.iterdir():
                    self.assertEqual(archivo.read_text(), "Conservar")

    def test_borrador_local_admitido_publicado_incompleto_bloqueado(self):
        ficha = dict(self.ficha, abstract="", estado="borrador")
        self.guardar(ficha)
        for modo in ("db", "grafo"):
            resultado = self.ejecutar("build.py", "--solo", modo)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertIn("abstract", resultado.stdout)
        for estado in ({"estado": "publicado", "url": "https://example.org/demo/"},
                       {"estado": "publicado", "publicado": True, "url": "https://example.org/demo/"}):
            self.guardar(dict(ficha, **estado))
            resultado = self.ejecutar("build.py", "--solo", "db")
            self.assertNotEqual(resultado.returncode, 0)
            self.assertIn("abstract", resultado.stderr)


if __name__ == "__main__":
    unittest.main()
