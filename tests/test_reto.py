"""Recorrido artículo → Reto enfocado → artículo con el script real del Reto.

Ejecuta artefactos/reto.html en Node mediante tests/reto_harness.js, contra
el build/index.json versionado. Sin Node la prueba se omite en local y falla
en CI, donde el runner siempre lo trae.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import verificar_publicacion  # noqa: E402
from ghost import URL_RETO  # noqa: E402

RETO = RAIZ / "artefactos" / "reto.html"
ARNES = RAIZ / "tests" / "reto_harness.js"
INDICE = RAIZ / "build" / "index.json"
NODE = shutil.which("node")


def palabras(texto):
    plano = unicodedata.normalize("NFD", texto.lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return {w for w in "".join(c if c.isalnum() else " " for c in plano).split() if len(w) >= 6}


def legibles(ficha):
    return [f for f in ficha.get("falsos_positivos") or [] if f and "TODO" not in f and " " in f]


@unittest.skipUnless(NODE or os.environ.get("CI"), "Node no está instalado")
class RetoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not NODE:
            raise AssertionError("CI requiere Node para probar el Reto")
        cls.fichas = json.loads(INDICE.read_text(encoding="utf-8"))["fichas"]
        cls.signos = [f for f in cls.fichas if f["tipo"] == "signo"]

    def jugar(self, busqueda="", indice=INDICE, **extra):
        peticion = {"reto": str(RETO), "indice": str(indice), "busqueda": busqueda}
        peticion.update(extra)
        salida = subprocess.run(
            [NODE, str(ARNES)],
            input=json.dumps(peticion),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return json.loads(salida.stdout)

    def test_cada_signo_del_indice_tiene_reto_enfocado_que_devuelve_al_articulo(self):
        self.assertTrue(self.signos)
        for ficha in self.signos:
            with self.subTest(ficha["id"]):
                r = self.jugar("?signo=" + ficha["id"], responder="incorrecta")
                self.assertIn("Reto enfocado en", r["banner"] or "")
                preguntas = r["rondas"][0]["preguntas"]
                self.assertTrue(preguntas, "sin preguntas: el foco no sirve")
                for q in preguntas:
                    self.assertIn(q["correcto"], q["opciones"])
                    self.assertEqual(len(set(q["opciones"])), len(q["opciones"]))
                    if ficha.get("url"):
                        self.assertIn(f'href="{ficha["url"]}"', q["fuente"])
                    else:
                        self.assertIn("aún sin publicar", q["fuente"])
                repaso = r["rondas"][0]["fin"]["repaso"]
                if ficha.get("url"):
                    self.assertIn(f'href="{ficha["url"]}"', repaso)

    def test_distractores_de_limites_no_se_solapan_con_el_signo(self):
        por_limite = {}
        for s in self.signos:
            for fp in legibles(s):
                por_limite.setdefault(fp, []).append(s)
        for ficha in self.signos:
            propias = set().union(*(palabras(t) for t in legibles(ficha) + [ficha["titulo"]]))
            r = self.jugar("?signo=" + ficha["id"], semilla=len(ficha["id"]))
            for q in r["rondas"][0]["preguntas"]:
                if q["tipo"] != "Dónde NO confiar":
                    continue
                with self.subTest(ficha["id"]):
                    self.assertIn(q["correcto"], legibles(ficha))
                    for opcion in q["opciones"]:
                        if opcion == q["correcto"]:
                            continue
                        self.assertNotIn(opcion, ficha.get("falsos_positivos") or [])
                        self.assertFalse(palabras(opcion) & propias, opcion)
                        for origen in por_limite[opcion]:
                            self.assertNotEqual(origen.get("sistema"), ficha.get("sistema"))
                            self.assertNotEqual(origen.get("organo"), ficha.get("organo"))

    def test_id_ausente_del_indice_se_avisa_en_pantalla(self):
        r = self.jugar("?signo=signo-recien-publicado")
        self.assertIn("No se pudo enfocar", r["banner"])
        self.assertIn("signo-recien-publicado", r["banner"])
        self.assertIn("unos minutos", r["banner"])
        self.assertTrue(r["rondas"][0]["preguntas"], "debe seguir en modo general")

    def test_id_ausente_con_indice_de_respaldo_avisa_la_demora_de_cache(self):
        r = self.jugar("?signo=signo-recien-publicado", falla_primaria=True)
        self.assertEqual(len(r["pedidas"]), 2)
        self.assertIn("12 horas", r["banner"])

    def test_signo_sin_datos_para_preguntas_no_se_enfoca_en_silencio(self):
        fichas = [dict(f) for f in self.fichas]
        objetivo = fichas.index(next(f for f in fichas if f["tipo"] == "signo"))
        fichas[objetivo]["significado"] = ""
        fichas[objetivo]["decision"] = ""
        fichas[objetivo]["pregunta_clinica"] = ""
        fichas[objetivo]["falsos_positivos"] = []
        with tempfile.TemporaryDirectory() as tmp:
            indice = Path(tmp) / "index.json"
            indice.write_text(json.dumps({"fichas": fichas}), encoding="utf-8")
            r = self.jugar("?signo=" + fichas[objetivo]["id"], indice=indice)
        self.assertIn("No se pudo enfocar", r["banner"])

    def test_otra_ronda_reinicia_los_contadores_visibles(self):
        ficha = self.signos[0]
        r = self.jugar("?signo=" + ficha["id"], rondas=2, responder="correcta")
        primera, segunda = r["rondas"]
        self.assertTrue(all(q["acierto"] for q in primera["preguntas"]))
        self.assertGreater(len(primera["preguntas"]), 1)
        self.assertNotEqual(primera["preguntas"][-1]["contadores"]["aciertos"], "0")
        self.assertEqual(segunda["preguntas"][0]["contadores"]["aciertos"], "0")
        self.assertEqual(segunda["preguntas"][0]["contadores"]["racha"], "0")


class RecorridoLocalTest(unittest.TestCase):
    def setUp(self):
        self.signo = {
            "id": "signo-demo",
            "tipo": "signo",
            "titulo": "Signo demo",
            "cuerpo": "## El signo\n\nTexto.",
            "refs": [],
        }
        self.ficha = {"id": "signo-demo", "tipo": "signo", "titulo": "Signo demo",
                      "significado": "Algo"}

    def validar(self, fichas):
        errores = []
        verificar_publicacion.validar_recorrido_reto([self.signo], fichas, {}, errores)
        return errores

    def test_signo_en_el_indice_pasa(self):
        self.assertEqual(self.validar({"signo-demo": self.ficha}), [])

    def test_signo_ausente_del_indice_falla(self):
        errores = self.validar({})
        self.assertTrue(any("modo general" in e for e in errores))

    def test_signo_sin_datos_para_el_reto_falla(self):
        errores = self.validar({"signo-demo": dict(self.ficha, significado="")})
        self.assertTrue(any("no puede enfocarlo" in e for e in errores))

    def test_id_que_el_embed_descarta_falla(self):
        self.signo["id"] = self.ficha["id"] = "signo con espacio"
        errores = self.validar({"signo con espacio": self.ficha})
        self.assertTrue(any("embed" in e for e in errores))

    def test_enlace_del_cuerpo_usa_el_id(self):
        self.assertIn("{id}", URL_RETO)


if __name__ == "__main__":
    unittest.main()
