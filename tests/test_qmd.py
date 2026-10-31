"""Salvaguardas del generador del proyecto Quarto (`scripts/qmd.py`).

Cubren las tres cosas que, si se rompen, no se notan hasta tener el EPUB en la
mano: la jerarquía de encabezados, el orden canónico del atlas y el contrato de
atribución de las figuras.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# `qmd.py` y `epub.py` se ejecutan como scripts (`python scripts/qmd.py`), así
# que importan módulos hermanos. Para poder probarlos hay que poner `scripts/`
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
        # El nombre del capítulo es el del órgano escrito en español, no el
        # slug de la taxonomía: antes salía "Pulmon", sin tilde.
        self.assertEqual([titulo for titulo, _ in capitulos], ["Pleura", "Pulmón"])


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


class EnlacesTest(unittest.TestCase):
    def test_la_ficha_publicada_enlaza_a_su_articulo_en_ghost(self):
        entidad = {
            "id": "signo-demo", "tipo": "signo", "titulo": "Demo",
            "cuerpo": "## Sección\n\nTexto.", "refs": [],
            "url": "https://www.biosemiotics.net/demo/",
        }
        self.assertIn("<https://www.biosemiotics.net/demo/>",
                      qmd.ficha_markdown(entidad, {}, []))

    def test_la_ficha_sin_publicar_no_inventa_enlace(self):
        entidad = {"id": "signo-demo", "tipo": "signo", "titulo": "Demo",
                   "cuerpo": "Texto.", "refs": [], "url": ""}
        self.assertNotIn("biosemiotics.net", qmd.ficha_markdown(entidad, {}, []))

    def test_el_pie_de_figura_conserva_fuente_y_licencia_como_enlaces(self):
        medio = {
            "descripcion": "Una vista", "credito": "Alguien",
            "fuente": "Wikimedia Commons", "fuente_url": "https://commons.example/x",
            "licencia_img": "CC BY 4.0",
            "licencia_url": "https://creativecommons.org/licenses/by/4.0/",
            "archivo_local": "assets/img/x.jpg",
        }
        pie = qmd.figura_markdown(medio)
        self.assertIn("[Wikimedia Commons](https://commons.example/x)", pie)
        self.assertIn("[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)", pie)


class MetadatosTest(unittest.TestCase):
    def test_declara_doi_dereferenciable_y_licencia_con_url(self):
        xml = qmd.metadatos_epub([], "v1")
        self.assertIn("https://doi.org/" + qmd.DOI_CONCEPTO, xml)
        self.assertIn(qmd.LICENCIA_URL, xml)
        self.assertIn("<dc:rights>", xml)
        # El título y el autor los aporta pandoc: duplicarlos deja dos
        # `dc:title` y dos `dc:identifier` en el OPF.
        self.assertNotIn("<dc:title>", xml)

    def test_arrastra_los_terminos_mesh_del_banco_como_materias(self):
        entidades = [{"mesh": ["Ultrasonography", "Lung"]}, {"mesh": ["Lung"]}]
        xml = qmd.metadatos_epub(entidades, "v1")
        self.assertEqual(xml.count("<dc:subject>"), 2)
        self.assertIn("<dc:subject>Ultrasonography</dc:subject>", xml)

    def test_declara_la_editorial(self):
        # Quarto no lleva `book: publisher:` al OPF: si no está aquí, por la
        # ruta Quarto el contenedor sale sin `dc:publisher`.
        self.assertIn("<dc:publisher>", qmd.metadatos_epub([], "v1"))

    def test_escapa_los_caracteres_que_romperian_el_xml(self):
        xml = qmd.metadatos_epub([{"mesh": ["A & B <x>"]}], "v1")
        self.assertIn("A &amp; B &lt;x&gt;", xml)


class BibliografiaTest(unittest.TestCase):
    def test_escapa_el_asterisco_literal_de_un_titulo_publicado(self):
        bib = {"x": {"title": "evaluation of proficiency*", "journal": "Crit Care Med"}}
        self.assertEqual(
            qmd.bibliografia_para_libro(bib)["x"]["title"],
            r"evaluation of proficiency\*",
        )


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


class DeclaracionIATest(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        (self.raiz / "paratextos").mkdir()

    def paratexto(self, texto):
        (self.raiz / qmd.DECLARACION_IA).write_text(texto, encoding="utf-8")

    def test_el_paratexto_del_banco_resuelve_las_citas_de_la_edicion(self):
        texto = qmd.declaracion_ia(RAIZ, 151)
        self.assertIn("las 151 citas", " ".join(texto.split()))
        self.assertNotIn(qmd.MARCADOR_CITAS, texto)
        self.assertEqual(qmd.titulo_declaracion(texto),
                         "DECLARACIÓN DE USO DE INTELIGENCIA ARTIFICIAL")

    def test_aborta_si_falta_el_paratexto(self):
        with self.assertRaisesRegex(RuntimeError, "declaracion-ia.md"):
            qmd.declaracion_ia(self.raiz, 3)

    def test_aborta_si_el_marcador_no_aparece_una_sola_vez(self):
        for texto in ("## T\n\nlas 151 citas\n", "## T\n\n{N} y {N}\n"):
            with self.subTest(texto=texto):
                self.paratexto(texto)
                with self.assertRaisesRegex(RuntimeError, "exactamente una vez"):
                    qmd.declaracion_ia(self.raiz, 3)

    def test_aborta_ante_otro_marcador_sin_sustituir(self):
        self.paratexto("## T {.unnumbered}\n\nlas {N} citas, edición {FECHA}\n")
        with self.assertRaisesRegex(RuntimeError, r"\{FECHA\}"):
            qmd.declaracion_ia(self.raiz, 3)


class CitasVerificablesTest(unittest.TestCase):
    ARTICULO = "@article{{{0},\n title={{T}},\n pmid={{{1}}},\n doi={{{2}}},\n}}\n"

    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)

    def bib(self, texto):
        (self.raiz / "refs.bib").write_text(texto, encoding="utf-8")

    def test_cuenta_las_citas_de_la_edicion_no_las_de_refs_bib(self):
        self.bib(self.ARTICULO.format("a", "1", "10.1000/a")
                 + self.ARTICULO.format("b", "2", "10.1000/b"))
        self.assertEqual(qmd.citas_verificables(["a"], self.raiz), 1)

    def test_aborta_si_una_cita_no_es_articulo_verificable(self):
        casos = {
            "@book{a,\n title={T},\n}\n": "no es una entrada @article",
            self.ARTICULO.format("a", "1", ""): "PMID o DOI",
        }
        for texto, motivo in casos.items():
            with self.subTest(motivo=motivo):
                self.bib(texto)
                with self.assertRaisesRegex(RuntimeError, motivo):
                    qmd.citas_verificables(["a"], self.raiz)

    def test_aborta_si_una_cita_esta_exenta_de_crossref(self):
        # La frase dice «contra PubMed y Crossref»: una exención la haría falsa.
        self.bib(self.ARTICULO.format("a", "1", "10.1000/a"))
        (self.raiz / "refs-sin-crossref.txt").write_text(
            "a  # revista que no deposita\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "exenta de Crossref"):
            qmd.citas_verificables(["a"], self.raiz)


class PortadillaTest(unittest.TestCase):
    def test_en_pdf_creditos_y_declaracion_preceden_al_indice(self):
        texto = qmd.portadilla("v1", "## DECLARACIÓN {.unnumbered}\n\nTexto.")
        self.assertLess(texto.index("Créditos, licencia y uso"), texto.index("DECLARACIÓN"))
        self.assertLess(texto.index("DECLARACIÓN"), texto.index("\\tableofcontents"))
        # En `book` el capítulo es el nivel 0: `tocdepth` 2 lista las fichas.
        self.assertIn(f"\\setcounter{{tocdepth}}{{{qmd.TOC_PROFUNDIDAD}}}", texto)

    def test_el_pdf_limita_la_altura_de_las_figuras(self):
        yml = qmd.quarto_yml([], {}, "v1", "portada.svg")
        pdf = yml.split("  pdf:\n", 1)[1].split("  html:\n", 1)[0]
        self.assertIn(f"include-in-header: {qmd.PREAMBULO_LIBRO}", pdf)
        preambulo = qmd.preambulo_libro()
        self.assertIn(f"={qmd.ALTURA_MAXIMA_FIGURA}\\textheight", preambulo)
        # Las dos plantillas de Quarto: la reciente y la que fija la CI. Un
        # \renewcommand directo rompía la CI con «\pandocbounded undefined».
        self.assertIn("\\ifdefined\\pandocbounded", preambulo)
        self.assertIn("\\ifdefined\\maxheight", preambulo)
        self.assertNotIn("\\renewcommand*\\pandocbounded", preambulo)
        # El EPUB no hereda la regla: es LaTeX.
        self.assertNotIn("pandocbounded", yml.split("  pdf:\n", 1)[0])

    def test_el_pdf_no_emite_un_segundo_indice_automatico(self):
        yml = qmd.quarto_yml([], {}, "v1", "portada.svg")
        pdf = yml.split("  pdf:\n", 1)[1].split("  html:\n", 1)[0]
        self.assertIn("toc: false", pdf)
        self.assertIn("toc: true", yml.split("  epub:\n", 1)[1].split("  pdf:\n", 1)[0])

    def test_el_diseno_del_libro_solo_toca_el_pdf(self):
        yml = qmd.quarto_yml([], {}, "v1", "portada.svg")
        antes, pdf = yml.split("  pdf:\n", 1)
        pdf, html = pdf.split("  html:\n", 1)
        for clave in (qmd.FILTRO_LIBRO, qmd.PREAMBULO_LIBRO, qmd.FUENTE_LIBRO):
            self.assertIn(clave, pdf)
            self.assertNotIn(clave, antes + html)

    def test_el_preambulo_trae_los_datos_de_la_portada(self):
        texto = qmd.preambulo_libro()
        # La versión va en la portadilla, no en la portada.
        self.assertNotIn("versionlibro", texto)
        self.assertIn("\\newcommand{\\titulolineas}{", texto)
        self.assertIn("\\portadaatlas", texto)


if __name__ == "__main__":
    unittest.main()
