"""Datos de catalogación de la primera edición con ISBN y hueco del prólogo.

Sello, ISBN y DOI llegan a Books In Print y a los catálogos de bibliotecas: una
cadena equivocada no rompe el render, así que se fija aquí y en los validadores
de `libro.py` y `epub.py`.
"""

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import epub  # noqa: E402
import libro  # noqa: E402
import qmd  # noqa: E402

DECLARACION = "## DECLARACIÓN {.unnumbered}\n\nTexto."


class CreditosTest(unittest.TestCase):
    def setUp(self):
        self.texto = qmd.portadilla("abc1234", DECLARACION)

    def test_cada_identificador_va_en_su_linea(self):
        # En un párrafo corrido LaTeX partía el ISBN por sus guiones.
        lineas = qmd.creditos_identificadores().split("\\\n")
        self.assertEqual(lineas, [
            f"DOI de la obra: [{qmd.DOI_CONCEPTO}]({qmd.DOI_URL}).",
            "ISBN EPUB: 979-8-953844-01-7.",
            "ISBN tapa blanda: 979-8-953844-00-0.",
        ])

    def test_declara_el_sello_y_los_dos_isbn(self):
        self.assertIn("Editorial: Powersemiotics.", self.texto)
        self.assertIn("ISBN EPUB: 979-8-953844-01-7.", self.texto)
        self.assertIn("ISBN tapa blanda: 979-8-953844-00-0.", self.texto)
        self.assertNotIn("pendiente", self.texto)

    def test_la_filiacion_no_lleva_issn(self):
        self.assertIn("Edición impresa derivada del atlas en línea "
                      f"*{qmd.OBRA_EN_LINEA}*.", self.texto)
        self.assertNotIn("ISSN", self.texto)

    def test_sin_deposito_de_edicion_cita_el_doi_de_la_obra(self):
        self.assertIn(f"DOI de la obra: [{qmd.DOI_CONCEPTO}]", self.texto)
        self.assertNotIn("DOI de esta edición", self.texto)

    def test_con_deposito_de_edicion_lo_cita_y_conserva_el_de_la_obra(self):
        with patch.object(qmd, "DOI_EDICION", "10.5281/zenodo.1"):
            texto = qmd.portadilla("abc1234", DECLARACION)
        self.assertIn("DOI de esta edición: [10.5281/zenodo.1]", texto)
        self.assertIn(f"DOI de la obra: [{qmd.DOI_CONCEPTO}]", texto)

    def test_declara_la_edicion_sobre_la_linea_de_compilacion(self):
        edicion = ("Primera edición. Contiene las entradas publicadas hasta el "
                   "13 de noviembre de 2026.")
        self.assertIn(edicion, self.texto)
        self.assertLess(self.texto.index(edicion), self.texto.index("Compilación"))
        self.assertIn("versión `abc1234`", self.texto)

    def test_el_quiebre_de_portada_reproduce_el_subtitulo(self):
        # Si cambia el subtítulo y nadie toca la portada, la CI lo para.
        self.assertEqual(" ".join(qmd.SUBTITULO_PORTADA), qmd.SUBTITULO)
        self.assertEqual(qmd.SUBTITULO_PORTADA[1], "para el médico de primer contacto")

    def test_la_portada_svg_usa_las_constantes(self):
        svg = qmd.portada_svg()
        for linea in qmd.SUBTITULO_PORTADA:
            self.assertIn(f">{linea}</text>", svg)
        self.assertLess(svg.index(qmd.SUBTITULO_PORTADA[0]),
                        svg.index(qmd.SUBTITULO_PORTADA[1]))
        self.assertIn(f">{qmd.EDITORIAL}</text>", svg)
        self.assertNotIn("BioSemiotics", svg)

    def test_la_portada_pdf_parte_el_subtitulo_igual(self):
        macro = "\\newcommand{\\subtitulolibro}{%s}" % "\\\\".join(qmd.SUBTITULO_PORTADA)
        self.assertIn(macro, qmd.preambulo_libro())

    def test_el_opf_declara_el_sello(self):
        self.assertIn("<dc:publisher>Powersemiotics</dc:publisher>",
                      qmd.metadatos_epub([], "v1"))


class DeclaracionTest(unittest.TestCase):
    def test_el_nombre_de_archivo_no_se_parte_en_su_guion(self):
        # U+2011: LuaTeX corta tras un guion normal aun en monoespaciada, y el
        # PDF mostraba «AI-» / «USE.md».
        texto = (RAIZ / qmd.DECLARACION_IA).read_text(encoding="utf-8")
        self.assertIn("`AI‑USE.md`", texto)
        self.assertNotIn("AI-USE.md", texto)


class PrologoTest(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        (self.raiz / "paratextos").mkdir()

    def test_sin_archivo_no_hay_prologo(self):
        self.assertIsNone(qmd.prologo(self.raiz))
        yml = qmd.quarto_yml([], {}, "v1", "portada.svg")
        self.assertNotIn("prologo.qmd", yml)
        plano = qmd.manuscrito_plano([], {}, [], "v1", DECLARACION)
        self.assertNotIn("Prólogo", plano)

    def test_con_archivo_va_detras_del_indice_y_antes_del_primer_capitulo(self):
        (self.raiz / qmd.PROLOGO).write_text(
            "Texto del prólogo.\n\nDr. Edison Espinosa — ORCID 0000-0003-1342-9669\n",
            encoding="utf-8")
        texto = qmd.prologo(self.raiz)
        self.assertTrue(texto.startswith("# Prólogo {.unnumbered}\n"))
        self.assertIn("Dr. Edison Espinosa", texto)

        yml = qmd.quarto_yml([("Fundamentos", [])], {"Fundamentos": "fundamentos.qmd"},
                             "v1", "portada.svg", con_prologo=True)
        self.assertLess(yml.index("- index.qmd"), yml.index("- prologo.qmd"))
        self.assertLess(yml.index("- prologo.qmd"), yml.index("- fundamentos.qmd"))

        plano = qmd.manuscrito_plano([], {}, [], "v1", DECLARACION, texto)
        self.assertLess(plano.index("\\tableofcontents"), plano.index("# Prólogo"))

    def test_aborta_si_esta_vacio_o_trae_un_marcador(self):
        for contenido, motivo in (("  \n", "vacío"), ("Texto {FIRMA}\n", r"\{FIRMA\}")):
            with self.subTest(motivo=motivo):
                (self.raiz / qmd.PROLOGO).write_text(contenido, encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, motivo):
                    qmd.prologo(self.raiz)


class ValidadoresTest(unittest.TestCase):
    """Los validadores exigen los ISBN reales, no la palabra «pendiente»."""

    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.dir = Path(temporal.name)

    def contenido(self, portadilla):
        return "\n".join([
            portadilla, "Material educativo.", "Bibliografía", "Créditos de imágenes",
            "≥ → ±", qmd.FUENTE_LIBRO, qmd.PANDOCBOUNDED_CON_TOPE,
        ])

    def validar_libro(self, portadilla):
        tex, pdf = self.dir / "libro.tex", self.dir / "libro.pdf"
        tex.write_text(self.contenido(portadilla), encoding="utf-8")
        pdf.write_bytes(b"%PDF-" + b"0" * (600 * 1024))
        return libro.validar_libro(tex, pdf, [], 0)

    def validar_epub(self, portadilla):
        ruta = self.dir / "atlas.epub"
        opf = (f"<package><metadata><dc:identifier>{qmd.DOI_URL}</dc:identifier>"
               f"<dc:rights>{qmd.LICENCIA_URL}</dc:rights><dc:publisher>x</dc:publisher>"
               "<dc:description>x</dc:description></metadata>"
               '<item properties="cover-image"/></package>')
        with zipfile.ZipFile(ruta, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            zf.writestr("META-INF/container.xml", "<container/>")
            zf.writestr("EPUB/text/libro.xhtml", self.contenido(portadilla))
            zf.writestr("EPUB/content.opf", opf)
            zf.writestr("EPUB/nav.xhtml", "<nav/>")
            zf.writestr("EPUB/media/portada.png", b"\x89PNG" + bytes(60 * 1024))
        return epub.validar_epub(ruta, 1, 0, 0)

    def test_pasan_con_los_isbn_de_la_portadilla(self):
        portadilla = qmd.portadilla("abc1234", DECLARACION)
        self.assertIn("coherentes", self.validar_libro(portadilla))
        self.assertIn("válido", self.validar_epub(portadilla))

    def test_fallan_si_la_edicion_vuelve_a_decir_pendiente(self):
        portadilla = qmd.portadilla("abc1234", DECLARACION).replace(
            qmd.creditos_identificadores(), "ISBN EPUB: pendiente.")
        with self.assertRaisesRegex(RuntimeError, "ISBN EPUB y tapa blanda"):
            self.validar_libro(portadilla)
        with self.assertRaisesRegex(RuntimeError, "ISBN EPUB y tapa blanda"):
            self.validar_epub(portadilla)


if __name__ == "__main__":
    unittest.main()
