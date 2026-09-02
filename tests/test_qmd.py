"""Salvaguardas del generador del proyecto Quarto (`scripts/qmd.py`).

Cubren las tres cosas que, si se rompen, no se notan hasta tener el EPUB en la
mano: la jerarquía de encabezados, el orden canónico del atlas y el contrato de
atribución de las figuras.
"""

import sys
import unittest
from pathlib import Path

# `qmd.py` y `epub.py` se ejecutan como scripts (`python scripts/qmd.py`), así
# que importan `build` a secas. Para poder probarlos hay que poner `scripts/`
# en la ruta igual que lo haría el intérprete al lanzarlos.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import qmd  # noqa: E402


class DegradarTest(unittest.TestCase):
    def test_baja_los_encabezados_del_cuerpo_bajo_su_ficha(self):
        cuerpo = "## La pregunta clínica\n\nTexto.\n\n### Detalle\n"
        self.assertEqual(
            qmd.degradar(cuerpo, 1),
            "### La pregunta clínica\n\nTexto.\n\n#### Detalle\n",
        )

    def test_se_topa_en_cinco_niveles(self):
        self.assertEqual(qmd.degradar("##### Hondo\n", 2), "##### Hondo\n")

    def test_no_toca_almohadillas_que_no_son_encabezado(self):
        cuerpo = "Ver el canal #pocus del equipo.\n"
        self.assertEqual(qmd.degradar(cuerpo, 1), cuerpo)


class SlugTest(unittest.TestCase):
    def test_produce_nombres_ascii_estables(self):
        self.assertEqual(qmd.slug("Sistema genitourinario"), "sistema-genitourinario")
        self.assertEqual(qmd.slug("Riñón"), "rinon")
        self.assertEqual(qmd.slug("Multiórgano y protocolos"), "multiorgano-y-protocolos")

    def test_nunca_devuelve_cadena_vacia(self):
        self.assertEqual(qmd.slug("··"), "seccion")


class EstructuraTest(unittest.TestCase):
    def entidad(self, **campos):
        base = {"id": "x", "tipo": "signo", "titulo": "T", "cuerpo": "", "refs": []}
        base.update(campos)
        return base

    def test_respeta_el_orden_canonico_de_sistemas_no_el_alfabetico(self):
        entidades = [
            self.entidad(id="a", titulo="A", sistema="digestivo", organo="higado"),
            self.entidad(id="b", titulo="B", sistema="respiratorio", organo="pleura"),
        ]
        partes = [nombre for nombre, _ in qmd.estructura(entidades)]
        self.assertEqual(partes, ["Sistema respiratorio", "Sistema digestivo"])

    def test_un_sistema_desconocido_cae_en_otros_signos_y_no_se_pierde(self):
        entidades = [self.entidad(id="a", titulo="A", sistema="inventado")]
        partes = qmd.estructura(entidades)
        self.assertEqual([nombre for nombre, _ in partes], ["Otros signos"])
        _, capitulos = partes[0]
        self.assertEqual([e["id"] for e in capitulos[0][1]], ["a"])

    def test_agrupa_los_signos_por_organo_dentro_del_sistema(self):
        entidades = [
            self.entidad(id="a", titulo="A", sistema="respiratorio", organo="pulmon"),
            self.entidad(id="b", titulo="B", sistema="respiratorio", organo="pleura"),
        ]
        _, capitulos = qmd.estructura(entidades)[0]
        self.assertEqual([titulo for titulo, _ in capitulos], ["Pleura", "Pulmon"])


class FichaTest(unittest.TestCase):
    def test_la_ficha_manda_sobre_su_cuerpo(self):
        entidad = {
            "id": "signo-demo",
            "tipo": "signo",
            "titulo": "Demo",
            "cuerpo": "## La pregunta clínica\n\nTexto.",
            "refs": [],
            "significante": "Lo que se ve.",
        }
        salida = qmd.ficha_markdown(entidad, {}, [])
        self.assertIn("## Demo {#sec-signo-demo}", salida)
        # El defecto que motivó la migración: el cuerpo quedaba en `##`, por
        # encima del título de su propia ficha, y partía el EPUB por dentro.
        self.assertIn("### La pregunta clínica", salida)
        self.assertNotIn("\n## La pregunta clínica", salida)


class FigurasTest(unittest.TestCase):
    def entidad_con_medio(self, medio):
        return {
            "id": "signo-demo",
            "tipo": "signo",
            "titulo": "Demo",
            "cuerpo": "",
            "_archivo": "signos/demo.qmd",
            "medios": [medio],
        }

    def test_aborta_si_a_una_figura_le_falta_la_atribucion(self):
        medio = {"tipo": "imagen", "descripcion": "Algo", "archivo_local": "assets/img/x.jpg"}
        with self.assertRaises(RuntimeError) as caso:
            qmd.figuras_validadas([self.entidad_con_medio(medio)], RAIZ)
        mensaje = str(caso.exception)
        self.assertIn("credito", mensaje)
        self.assertIn("licencia_img", mensaje)

    def test_aborta_si_archivo_local_apunta_fuera_del_repositorio(self):
        medio = {
            "tipo": "imagen",
            "descripcion": "Algo",
            "credito": "Alguien",
            "fuente": "Commons",
            "fuente_url": "https://example.org",
            "licencia_img": "CC BY 4.0",
            "licencia_url": "https://creativecommons.org/licenses/by/4.0/",
            "archivo_local": "../fuera.jpg",
        }
        with self.assertRaises(RuntimeError) as caso:
            qmd.figuras_validadas([self.entidad_con_medio(medio)], RAIZ)
        self.assertIn("fuera del repositorio", str(caso.exception))

    def test_los_loops_no_cuentan_como_figuras(self):
        medio = {"tipo": "loop", "id": "yt:x", "descripcion": "Clip"}
        self.assertEqual(qmd.figuras_validadas([self.entidad_con_medio(medio)], RAIZ), [])


if __name__ == "__main__":
    unittest.main()
