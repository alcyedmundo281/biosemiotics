import tempfile
import unittest
from pathlib import Path

from scripts.build import figura_latex


class ImagenLatexTest(unittest.TestCase):
    def test_usa_archivo_local_sin_inferir_nombre_desde_id(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            imagen = raiz / "assets" / "img" / "nombre-elegido-en-ghost.png"
            imagen.parent.mkdir(parents=True)
            imagen.write_bytes(b"imagen-de-prueba")
            entidad = {
                "id": "signo-un-id-distinto",
                "medios": [{
                    "tipo": "imagen",
                    "archivo_local": "assets/img/nombre-elegido-en-ghost.png",
                    "credito": "Autora",
                    "fuente": "Fuente",
                    "licencia_img": "CC BY 4.0",
                    "descripcion": "Descripción",
                }],
            }

            latex = figura_latex(entidad, raiz)

            self.assertIn(
                r"\includegraphics[width=0.85\textwidth,height=0.45\textheight,keepaspectratio]{../assets/img/nombre-elegido-en-ghost.png}",
                latex,
            )
            self.assertNotIn("signo-un-id-distinto", latex)


if __name__ == "__main__":
    unittest.main()
