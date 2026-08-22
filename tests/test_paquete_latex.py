import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.paquete_latex import crear_paquete


class PaqueteLatexTest(unittest.TestCase):
    def test_incluye_tex_bibliografia_y_todos_los_assets(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            (raiz / "build").mkdir()
            (raiz / "assets" / "img").mkdir(parents=True)
            (raiz / "assets" / "plantillas").mkdir()
            (raiz / "build" / "libro.tex").write_text("libro", encoding="utf-8")
            (raiz / "refs.bib").write_text("refs", encoding="utf-8")
            (raiz / "assets" / "img" / "figura.png").write_bytes(b"png")
            (raiz / "assets" / "plantillas" / "signo.md").write_text(
                "plantilla", encoding="utf-8"
            )
            salida = raiz / "build" / "fuente.zip"

            archivos, _ = crear_paquete(raiz, salida)

            self.assertEqual(archivos, 4)
            with zipfile.ZipFile(salida) as zf:
                self.assertEqual(
                    set(zf.namelist()),
                    {
                        "biosemiotics-latex/build/libro.tex",
                        "biosemiotics-latex/refs.bib",
                        "biosemiotics-latex/assets/img/figura.png",
                        "biosemiotics-latex/assets/plantillas/signo.md",
                        "biosemiotics-latex/COMPILAR.md",
                    },
                )


if __name__ == "__main__":
    unittest.main()
