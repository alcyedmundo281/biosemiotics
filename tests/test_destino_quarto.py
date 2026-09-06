"""La regeneración nunca debe borrar fuentes ni perder el proyecto anterior."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import qmd
from build import SECCIONES


class DestinoQuartoTest(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name).resolve()
        self.bib = "@article{demo,\n title={Demo},\n}\n"
        (self.raiz / "refs.bib").write_text(self.bib, encoding="utf-8")
        self.destino = self.raiz / "build" / "quarto"
        self.entidades = [{"id": "signo-demo", "tipo": "signo", "titulo": "Demo",
                           "_archivo": "signos/demo.qmd",
                           "cuerpo": "\n\n".join("## " + s + "\nTexto." for s in SECCIONES["signo"]),
                           "abstract": "palabra " * 40, "refs": ["demo"],
                           "nivel": "principiante", "ventana": "Ventana",
                           "sonda": ["sectorial"], "falsos_positivos": ["Imitador"],
                           "significante": "Imagen", "significado": "Interpretación",
                           "decision": "Decisión",
                           "sistema": "cardiovascular", "organo": "corazon"}]
        self.raster = patch.object(qmd, "rasterizar_portada", return_value=False)
        self.raster.start()
        self.addCleanup(self.raster.stop)

    def generar(self, destino=None):
        return qmd.generar(self.entidades, self.raiz, destino or self.destino)

    def test_rechaza_fuentes_raiz_build_y_escape_sin_tocarlos(self):
        for ruta in (self.raiz, self.raiz / "build", self.raiz / "signos",
                     self.raiz / "assets", self.raiz / ".git",
                     self.raiz / "build" / ".." / "signos", self.raiz.parent):
            with self.subTest(ruta=ruta), patch.object(qmd, "_generar_en") as generar:
                with self.assertRaises(RuntimeError):
                    self.generar(ruta)
                generar.assert_not_called()
        self.assertEqual((self.raiz / "refs.bib").read_text(), self.bib)

    def test_no_reemplaza_directorio_ajeno_ni_archivo(self):
        self.destino.mkdir(parents=True)
        nota = self.destino / "nota.txt"
        nota.write_text("conservar")
        with self.assertRaisesRegex(RuntimeError, "ajeno"):
            self.generar()
        self.assertEqual(nota.read_text(), "conservar")
        with self.assertRaisesRegex(RuntimeError, "no es un directorio"):
            self.generar(nota)

    def test_regenera_y_limpia_solo_el_proyecto_reconocido(self):
        informe = self.generar()
        self.assertEqual(informe["destino"], self.destino)
        self.assertTrue((self.destino / "_quarto.yml").is_file())
        (self.destino / "obsoleto.txt").write_text("derivado antiguo")
        self.generar()
        self.assertFalse((self.destino / "obsoleto.txt").exists())
        self.assertEqual(list(self.destino.parent.glob(".quarto-*")), [])

    def test_admite_ruta_relativa_y_personalizada_marcada(self):
        ruta = Path("build") / "edicion-prueba"
        self.generar(ruta)
        self.generar(ruta)
        self.assertTrue((self.raiz / ruta / qmd.MARCADOR_PROYECTO).is_file())

    def test_migra_proyecto_historico_solo_en_ruta_convencional(self):
        self.generar()
        (self.destino / qmd.MARCADOR_PROYECTO).unlink()
        self.generar()
        self.assertTrue((self.destino / qmd.MARCADOR_PROYECTO).exists())
        (self.destino / qmd.MARCADOR_PROYECTO).unlink()
        otro = self.destino.with_name("ajeno")
        self.destino.rename(otro)
        with self.assertRaisesRegex(RuntimeError, "ajeno"):
            self.generar(otro)

    def test_fallo_de_ensamblado_conserva_anterior(self):
        self.generar()
        antes = (self.destino / "libro-plano.md").read_bytes()
        with patch.object(qmd, "parte_markdown", side_effect=RuntimeError("fallo")):
            with self.assertRaisesRegex(RuntimeError, "fallo"):
                self.generar()
        self.assertEqual((self.destino / "libro-plano.md").read_bytes(), antes)
        self.assertEqual(list(self.destino.parent.glob(".quarto-*")), [])

    def test_fallo_de_instalacion_restaura_anterior(self):
        self.generar()
        antes = (self.destino / "libro-plano.md").read_bytes()
        rename = Path.rename

        def fallar_nuevo(origen, destino):
            if origen.name == "nuevo":
                raise OSError("destino bloqueado")
            return rename(origen, destino)

        with patch.object(Path, "rename", fallar_nuevo):
            with self.assertRaisesRegex(OSError, "bloqueado"):
                self.generar()
        self.assertEqual((self.destino / "libro-plano.md").read_bytes(), antes)
        self.assertEqual(list(self.destino.parent.glob(".quarto-*")), [])

    def test_si_restaurar_falla_conserva_respaldo(self):
        self.generar()
        rename = Path.rename

        def fallar(origen, destino):
            if origen.name in ("nuevo", "anterior"):
                raise OSError("bloqueado")
            return rename(origen, destino)

        with patch.object(Path, "rename", fallar):
            with self.assertRaisesRegex(RuntimeError, "copia conservada"):
                self.generar()
        copias = list(self.destino.parent.glob(".quarto-*/anterior/libro-plano.md"))
        self.assertEqual(len(copias), 1)

    def test_rechaza_enlace_en_destino_o_ancestro(self):
        self.destino.parent.mkdir(parents=True)
        fuente = self.raiz / "signos"
        fuente.mkdir()
        nota = fuente / "nota.txt"
        nota.write_text("conservar")
        enlace = self.destino.parent / "enlace"
        try:
            enlace.symlink_to(fuente, target_is_directory=True)
        except OSError:
            self.skipTest("El sistema no permite crear symlinks")
        for ruta in (enlace, enlace / "hijo"):
            with self.subTest(ruta=ruta), self.assertRaises(RuntimeError):
                self.generar(ruta)
        self.assertEqual(nota.read_text(), "conservar")


if __name__ == "__main__":
    unittest.main()
