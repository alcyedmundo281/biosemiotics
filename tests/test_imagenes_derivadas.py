"""La figura del libro sale de `archivo_local`, nunca de un nombre inferido.

Este invariante existía contra `build.figura_latex()`, que jubiló el proyecto
Quarto. Sigue importando igual: `archivo_local` es el mismo campo que se sube a
Ghost, así que deducir la ruta del `id` de la ficha publicaría una imagen
distinta a la que se acreditó.
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import qmd  # noqa: E402


class ImagenDerivadaTest(unittest.TestCase):
    MEDIO = {
        "tipo": "imagen",
        "archivo_local": "assets/img/nombre-elegido-en-ghost.png",
        "credito": "Autora",
        "fuente": "Fuente",
        "fuente_url": "https://example.org/origen",
        "licencia_img": "CC BY 4.0",
        "licencia_url": "https://creativecommons.org/licenses/by/4.0/",
        "descripcion": "Descripción",
    }

    def test_usa_archivo_local_sin_inferir_nombre_desde_id(self):
        entidad = {
            "id": "signo-un-id-distinto",
            "tipo": "signo",
            "titulo": "Un signo",
            "cuerpo": "",
            "refs": [],
            "medios": [self.MEDIO],
        }
        salida = qmd.ficha_markdown(entidad, {}, [])
        self.assertIn("(assets/img/nombre-elegido-en-ghost.png)", salida)
        self.assertNotIn("assets/img/signo-un-id-distinto", salida)

    def test_el_pie_acredita_la_imagen_que_se_declara(self):
        pie = qmd.figura_markdown(self.MEDIO)
        for dato in ("Descripción", "Autora", "Fuente", "CC BY 4.0"):
            self.assertIn(dato, pie)


if __name__ == "__main__":
    unittest.main()
