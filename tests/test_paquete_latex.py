"""El paquete LaTeX debe poder compilarse fuera del repositorio.

Empaqueta el proyecto Quarto entero, que es donde conviven `libro.tex` y las
imágenes que referencia por ruta relativa. La versión anterior mezclaba el
`build/libro.tex` del generador propio con el árbol `assets/` del repositorio,
y el .tex traía rutas `../assets/...` que solo resolvían desde `build/`.
"""

import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.paquete_latex import crear_paquete


class PaqueteLatexTest(unittest.TestCase):
    def proyecto(self, raiz: Path) -> Path:
        proyecto = raiz / "build" / "quarto"
        (proyecto / "assets" / "img").mkdir(parents=True)
        (proyecto / "_salida").mkdir()
        (proyecto / "libro.tex").write_text("libro", encoding="utf-8")
        (proyecto / "refs.bib").write_text("refs", encoding="utf-8")
        (proyecto / "_quarto.yml").write_text("project:", encoding="utf-8")
        (proyecto / "assets" / "img" / "figura.png").write_bytes(b"png")
        return proyecto

    def test_empaqueta_el_proyecto_con_sus_imagenes(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            self.proyecto(raiz)
            salida = raiz / "build" / "fuente.zip"

            archivos, _ = crear_paquete(raiz, salida)

            self.assertEqual(archivos, 4)
            with zipfile.ZipFile(salida) as zf:
                self.assertEqual(
                    set(zf.namelist()),
                    {
                        "biosemiotics-latex/libro.tex",
                        "biosemiotics-latex/refs.bib",
                        "biosemiotics-latex/_quarto.yml",
                        "biosemiotics-latex/assets/img/figura.png",
                        "biosemiotics-latex/COMPILAR.md",
                    },
                )

    def test_excluye_la_salida_de_quarto(self):
        # `_salida/` guarda el PDF renderizado: pesa y no es fuente.
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            proyecto = self.proyecto(raiz)
            (proyecto / "_salida" / "libro.pdf").write_bytes(b"%PDF-1.7")
            salida = raiz / "build" / "fuente.zip"

            crear_paquete(raiz, salida)

            with zipfile.ZipFile(salida) as zf:
                self.assertNotIn("biosemiotics-latex/_salida/libro.pdf", zf.namelist())

    def test_falla_con_un_mensaje_accionable_si_no_se_generó_el_libro(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            (raiz / "build").mkdir()
            with self.assertRaises(RuntimeError) as caso:
                crear_paquete(raiz, raiz / "build" / "fuente.zip")
            self.assertIn("scripts/libro.py", str(caso.exception))


if __name__ == "__main__":
    unittest.main()
