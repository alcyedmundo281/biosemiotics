"""La skill de Ghost y las tres compuertas que la motivaron.

Tres errores se repetían al publicar: imágenes generadas con IA en lugar de
Wikimedia Commons, el pie de la imagen destacada pegado dos veces y artículos
publicados solo en web, sin el email a los suscriptores. La skill anterior vivía
solo en .agents/ —Claude Code no la cargaba—, no decía nada del origen de la
imagen ni del pie, y pedía enviar el email solo si el usuario lo solicitaba.
"""
import copy
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
import ghost  # noqa: E402
import validacion  # noqa: E402
from auditar_pegado_ghost import auditar_pie, cabecera_canonica, cuerpo_markdown, huella  # noqa: E402
from banco import cargar  # noqa: E402
from bibliografia import cargar_bibliografia  # noqa: E402

CODEX = REPO / ".agents" / "skills" / "ghost" / "SKILL.md"
CLAUDE = REPO / ".claude" / "skills" / "ghost" / "SKILL.md"

# Pie de la imagen destacada tal como está publicado en Ghost (VExUS, #99).
PIE_VEXUS_PUBLICADO = (
    "Exploración ecográfica de tiroides en un paciente simulado; imagen "
    "ilustrativa de adquisición ecográfica, no de las ventanas VExUS. "
    "Christopher Hubenthal, U.S. Air Force, vía Wikimedia Commons. "
    "Dominio público en Estados Unidos."
)


def entidad(identificador):
    return copy.deepcopy(next(e for e in cargar(REPO) if e["id"] == identificador))


class SkillCargableTest(unittest.TestCase):
    def test_la_skill_existe_para_claude_code_y_para_codex(self):
        self.assertTrue(CLAUDE.is_file(), "Claude Code solo carga .claude/skills/")
        self.assertTrue(CODEX.is_file(), "Codex la busca en .agents/skills/")

    def test_las_dos_copias_son_identicas(self):
        """Una sola fuente: si divergen, un agente publica con reglas viejas."""
        self.assertEqual(CLAUDE.read_text(encoding="utf-8"),
                         CODEX.read_text(encoding="utf-8"),
                         "copia .agents/skills/ghost/SKILL.md en .claude/skills/ghost/")

    def test_la_cabecera_declara_nombre_y_descripcion(self):
        cabecera = CLAUDE.read_text(encoding="utf-8").split("---")[1]
        self.assertIn("name: ghost", cabecera)
        self.assertIn("description:", cabecera)

    def test_la_skill_sigue_versionada_y_la_config_local_no(self):
        if not (REPO / ".git").exists():
            self.skipTest("no es un checkout de git")

        def ignorado(ruta):
            return subprocess.run(["git", "check-ignore", "-q", ruta], cwd=REPO).returncode == 0

        self.assertFalse(ignorado(".claude/skills/ghost/SKILL.md"))
        self.assertTrue(ignorado(".claude/settings.local.json"))


class ContenidoDeLaSkillTest(unittest.TestCase):
    def setUp(self):
        self.texto = CLAUDE.read_text(encoding="utf-8")

    def test_compuerta_imagen_solo_commons_nunca_ia(self):
        self.assertIn("SOLO Wikimedia Commons", self.texto)
        self.assertIn("NUNCA generada con IA", self.texto)
        self.assertIn("auditar_medios.py", self.texto)

    def test_compuerta_pie_canonico_y_auditado(self):
        self.assertIn("pie_esperado", self.texto)
        self.assertIn("--pie", self.texto)

    def test_compuerta_email_a_los_suscriptores(self):
        self.assertIn("Publish and email", self.texto)
        self.assertIn("Published and sent", self.texto)
        # La instrucción que provocaba el error: email solo si se pedía.
        self.assertNotIn("Only choose this if the user explicitly requested", self.texto)

    def test_no_propone_fijar_el_slug(self):
        self.assertNotIn("Ensure the slug matches", self.texto)


class PieCanonicoTest(unittest.TestCase):
    def test_reproduce_exactamente_el_pie_publicado_de_vexus(self):
        medio = ghost.imagen_destacada(entidad("vexus"))
        self.assertEqual(ghost.pie_ghost(medio), PIE_VEXUS_PUBLICADO)

    def test_no_duplica_puntos_cuando_los_campos_ya_terminan_en_punto(self):
        pie = ghost.pie_ghost({"descripcion": "Uno.", "credito": "Dos.",
                               "fuente": "Tres", "licencia_img": "CC BY 4.0"})
        self.assertEqual(pie, "Uno. Dos, vía Tres. CC BY 4.0.")

    def test_la_cabecera_ghost_lleva_lo_que_se_pega_sin_tocar_la_huella(self):
        e = entidad("vexus")
        bibliografia = cargar_bibliografia(REPO / "refs.bib")
        markdown = ghost.markdown_ghost(e, bibliografia)
        cabecera = cabecera_canonica(markdown)
        self.assertEqual(cabecera["pie"], PIE_VEXUS_PUBLICADO)
        self.assertEqual(cabecera["imagen"], "assets/img/vexus-wikimedia.jpg")
        self.assertEqual(cabecera["tags"], e["tags"])
        self.assertTrue(cabecera["alt"])
        # La huella registrada en el índice solo cubre el cuerpo.
        self.assertEqual(huella(cuerpo_markdown(markdown))["sha256"],
                         ghost.huella_cuerpo_ghost(e, bibliografia))

    def test_sin_imagen_destacada_no_hay_campos_de_imagen(self):
        e = entidad("vexus")
        e["medios"] = []
        cabecera = cabecera_canonica(ghost.markdown_ghost(
            e, cargar_bibliografia(REPO / "refs.bib")))
        self.assertNotIn("pie", cabecera)


class AuditoriaDelPieTest(unittest.TestCase):
    def test_el_pie_exacto_pasa(self):
        self.assertEqual(auditar_pie(PIE_VEXUS_PUBLICADO, PIE_VEXUS_PUBLICADO), [])

    def test_el_pie_pegado_dos_veces_se_detecta(self):
        errores = auditar_pie(f"{PIE_VEXUS_PUBLICADO} {PIE_VEXUS_PUBLICADO}",
                              PIE_VEXUS_PUBLICADO)
        self.assertIn("la atribución del pie está duplicada", errores)

    def test_el_cli_toma_el_pie_esperado_del_canonico(self):
        canon = REPO / "build" / "ghost" / "conceptos" / "vexus.qmd"
        if not canon.is_file():
            self.skipTest("falta build/ghost; corre build.py")
        base = [sys.executable, str(SCRIPTS / "auditar_pegado_ghost.py"),
                "--canon", str(canon), "--pie"]
        bien = subprocess.run(base + [PIE_VEXUS_PUBLICADO], capture_output=True)
        doble = subprocess.run(base + [PIE_VEXUS_PUBLICADO * 2], capture_output=True)
        self.assertEqual(bien.returncode, 0, bien.stderr)
        self.assertEqual(doble.returncode, 1)


class OrigenDeImagenTest(unittest.TestCase):
    def con_fuente(self, identificador, url):
        e = entidad(identificador)
        ghost.imagen_destacada(e)["fuente_url"] = url
        return e

    def test_commons_file_es_valido(self):
        self.assertEqual(validacion.errores_origen_imagen(entidad("vexus")), [])

    def test_otro_origen_bloquea_la_compilacion(self):
        e = self.con_fuente("vexus", "https://example.org/generada-con-ia.png")
        errores, _ = validacion.validar([e], [], REPO)
        self.assertTrue(any("Wikimedia Commons" in m for m in errores), errores)

    def test_sin_fuente_url_tambien_bloquea(self):
        e = self.con_fuente("vexus", "")
        self.assertTrue(validacion.errores_origen_imagen(e))

    def test_commons_fuera_de_una_pagina_file_no_basta(self):
        e = self.con_fuente("vexus", "https://commons.wikimedia.org/wiki/Category:Ultrasound")
        self.assertTrue(validacion.errores_origen_imagen(e))

    def test_en_un_borrador_es_alerta_no_error(self):
        e = self.con_fuente("vexus", "https://example.org/x.png")
        e.update(estado="borrador", url="")
        errores, alertas = validacion.validar([e], [], REPO, permitir_borradores=True)
        self.assertFalse(any("Wikimedia Commons" in m for m in errores))
        self.assertTrue(any("Wikimedia Commons" in m for m in alertas))

    def test_la_excepcion_historica_de_vti_se_respeta(self):
        self.assertEqual(validacion.errores_origen_imagen(entidad("signo-vti")), [])

    def test_el_banco_actual_cumple(self):
        for e in cargar(REPO):
            with self.subTest(entidad=e["id"]):
                self.assertEqual(validacion.errores_origen_imagen(e), [])


if __name__ == "__main__":
    unittest.main()
