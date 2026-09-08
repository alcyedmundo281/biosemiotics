"""Un único estado gobierna SQLite y la selección de todos los derivados."""
import copy
from contextlib import closing
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import build
import qmd


class EstadosPublicacionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name).resolve()
        self.caso = copy.deepcopy(next(e for e in build.cargar(REPO) if e["tipo"] == "caso"))
        self.caso.update(estado="borrador", url="", fecha_revision=None, ghost_id=None)
        self.caso.pop("publicado", None)
        (self.raiz / "refs.bib").write_text((REPO / "refs.bib").read_text(encoding="utf-8"), encoding="utf-8")

    def guardar(self, caso):
        carpeta = self.raiz / "casos"
        carpeta.mkdir(exist_ok=True)
        meta = {k: v for k, v in caso.items() if k not in ("cuerpo", "_archivo")}
        (carpeta / "caso.qmd").write_text(
            "---\n" + yaml.safe_dump(meta, allow_unicode=True) + "---\n" + caso["cuerpo"], encoding="utf-8")

    def ejecutar(self, script, *args):
        return subprocess.run([sys.executable, str(REPO / "scripts" / script),
                               "--raiz", str(self.raiz), *args],
                              cwd=self.raiz, capture_output=True, encoding="utf-8")

    def test_matriz_estados_y_consentimiento(self):
        for estado in ("borrador", "revisado", "publicado"):
            for consentimiento in (None, "pendiente", "obtenido"):
                with self.subTest(estado=estado, consentimiento=consentimiento):
                    e = dict(self.caso, estado=estado, consentimiento=consentimiento,
                             url="https://www.biosemiotics.net/caso/" if estado == "publicado" else "")
                    if estado != "borrador" and consentimiento != "obtenido":
                        with self.assertRaisesRegex(RuntimeError, "consentimiento"):
                            build.seleccionar_publicables([e])
                    else:
                        self.assertEqual(bool(build.seleccionar_publicables([e])), estado != "borrador")
                        self.assertEqual(bool(build.seleccionar_publicables([e], True)), estado == "publicado")

    def test_contradicciones_no_se_ocultan_al_filtrar(self):
        for cambios in ({"estado": "publicado"}, {"url": "https://example.org/"},
                        {"publicado": True}, {"publicado": "false"}, {"estado": "otro"},
                        {"estado": []}, {"fecha_revision": "ayer"}, {"ghost_id": "inventado"}):
            with self.subTest(cambios=cambios):
                with self.assertRaisesRegex(RuntimeError, "PUBLICACIÓN"):
                    build.seleccionar_publicables([dict(self.caso, **cambios)], True)

    def test_compatibilidad_legada_sin_inventar_revision(self):
        e = dict(self.caso, tipo="signo")
        e.pop("estado")
        self.assertEqual(build.estado_publicacion(e), "borrador")
        e["url"] = "https://www.biosemiotics.net/demo/"
        self.assertEqual(build.estado_publicacion(e), "publicado")
        self.assertIsNone(e["fecha_revision"])
        e["publicado"] = False
        with self.assertRaisesRegex(RuntimeError, "contradice"):
            build.estado_publicacion(e)

    def test_sqlite_conserva_borradores_y_deriva_booleano(self):
        ent = build.cargar(REPO)
        self.raiz.joinpath("build").mkdir()
        ruta = build.build_sqlite(ent, self.raiz / "build")
        with closing(sqlite3.connect(ruta)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM entidad").fetchone()[0], len(ent))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM entidad WHERE publicado=1").fetchone()[0],
                             len(build.seleccionar_publicables(ent, True)))
            self.assertEqual(db.execute("SELECT estado,publicado FROM entidad WHERE tipo='caso'").fetchone(),
                             ("borrador", 0))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM entidad WHERE fecha_revision IS NOT NULL").fetchone()[0],
                             sum(bool(e.get("fecha_revision")) for e in ent))

    def test_indice_retira_caso_y_derivados_tras_volver_a_borrador(self):
        revisado = dict(self.caso, estado="revisado", consentimiento="obtenido",
                        fecha_revision="2026-09-06", ghost_id="6a9d7015cb99d50001dc7569")
        self.guardar(revisado)
        resultado = self.ejecutar("indice.py")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        ficha = json.loads((self.raiz / "build/index.json").read_text())["fichas"][0]
        self.assertEqual(ficha["estado"], "revisado")
        self.assertEqual(ficha["fecha_revision"], "2026-09-06")
        self.assertEqual(ficha["ghost_id"], revisado["ghost_id"])
        self.guardar(self.caso)
        resultado = self.ejecutar("indice.py")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(json.loads((self.raiz / "build/index.json").read_text())["fichas"], [])
        self.assertEqual(list((self.raiz / "build/jats").glob("*.xml")), [])
        self.assertEqual(list((self.raiz / "build/jsonld").glob("*.json")), [])

    def test_ghost_atlas_y_quarto_excluyen_caso_pendiente(self):
        self.guardar(self.caso)
        destino = self.raiz / "build"
        ghost = build.build_ghost([self.caso], destino, self.raiz / "refs.bib")
        self.assertEqual(list(ghost.iterdir()), [])
        resultado = self.ejecutar("atlas.py")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertNotIn(self.caso["titulo"], (destino / "atlas.html").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(RuntimeError, "ninguna entidad"):
            qmd.generar([self.caso], self.raiz, destino / "quarto")
        self.assertFalse((destino / "quarto").exists())

    def test_caso_con_url_sin_consentimiento_bloquea_antes_de_escribir(self):
        e = dict(self.caso, estado="publicado", url="https://www.biosemiotics.net/caso/")
        self.guardar(e)
        destino = self.raiz / "build"
        destino.mkdir()
        anterior = destino / "index.json"
        anterior.write_text("conservar")
        resultado = self.ejecutar("indice.py")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("consentimiento", resultado.stderr)
        self.assertEqual(anterior.read_text(), "conservar")
        with self.assertRaisesRegex(RuntimeError, "consentimiento"):
            build.build_ghost([e], destino, self.raiz / "refs.bib")
        with self.assertRaisesRegex(RuntimeError, "consentimiento"):
            qmd.generar([e], self.raiz, destino / "quarto")
        with self.assertRaisesRegex(RuntimeError, "consentimiento"):
            build.build_sqlite([e], destino)


if __name__ == "__main__":
    unittest.main()
