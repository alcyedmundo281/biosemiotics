// Ejecuta el script real de artefactos/reto.html con un DOM mínimo y juega
// rondas completas. Lee una petición JSON por stdin y escribe la transcripción
// en stdout. Lo invoca tests/test_reto.py; no depende de paquetes de npm.
//
// Petición: {reto, indice, busqueda, falla_primaria, rondas, responder}
//   responder: "correcta" | "incorrecta"
"use strict";

const fs = require("fs");

function semilla(n) {
  // mulberry32: rondas reproducibles sin depender de Math.random real.
  return function () {
    n |= 0; n = (n + 0x6d2b79f5) | 0;
    let t = Math.imul(n ^ (n >>> 15), 1 | n);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

class Elemento {
  constructor(id) {
    this.id = id;
    this.style = {};
    this.textContent = "";
    this.children = [];
    this.className = "";
    this.disabled = false;
    this.onclick = null;
    this.dataset = {};
    this._html = "";
    const clases = new Set();
    this.classList = {
      add: (c) => clases.add(c),
      remove: (c) => clases.delete(c),
      contains: (c) => clases.has(c),
    };
  }
  get innerHTML() { return this._html; }
  set innerHTML(v) { this._html = String(v); this.children = []; }
  appendChild(hijo) { this.children.push(hijo); return hijo; }
}

function crearDocumento() {
  const porId = new Map();
  return {
    getElementById(id) {
      if (!porId.has(id)) porId.set(id, new Elemento(id));
      return porId.get(id);
    },
    createElement() { return new Elemento(null); },
    querySelectorAll() { return []; },
    documentElement: { scrollHeight: 800 },
  };
}

async function esperar() {
  for (let k = 0; k < 5; k++) await new Promise((r) => setTimeout(r, 0));
}

async function main() {
  const peticion = JSON.parse(fs.readFileSync(0, "utf8"));
  const html = fs.readFileSync(peticion.reto, "utf8");
  const m = /<script>\s*(\(function\(\)\{[\s\S]*?)<\/script>/.exec(html);
  if (!m) throw new Error("reto.html sin script principal");
  const indice = JSON.parse(fs.readFileSync(peticion.indice, "utf8"));
  const idFoco = /[?&]signo=([^&]+)/.exec(peticion.busqueda || "");
  const foco = (indice.fichas || indice).find(
    (f) => idFoco && f.id === decodeURIComponent(idFoco[1]),
  ) || {};

  const document = crearDocumento();
  const window = { location: { search: peticion.busqueda || "" } };
  window.parent = window;
  const pedidas = [];
  const fetch = (url) => {
    pedidas.push(url);
    const falla = peticion.falla_primaria && pedidas.length === 1;
    return Promise.resolve({
      ok: !falla,
      status: falla ? 503 : 200,
      json: () => Promise.resolve(JSON.parse(JSON.stringify(indice))),
    });
  };
  const consola = { warn() {}, log() {}, error() {} };
  const matematica = Object.create(Math);
  matematica.random = semilla(peticion.semilla || 7);

  new Function("window", "document", "fetch", "console", "Math", m[1])(
    window, document, fetch, consola, matematica,
  );
  await esperar();

  const $ = (id) => document.getElementById(id);
  const salida = {
    banner: $("focoBanner").style.display === "block" ? $("focoBanner").innerHTML : null,
    inicio: $("inicio").innerHTML,
    pedidas,
    rondas: [],
  };

  for (let r = 0; r < (peticion.rondas || 1); r++) {
    if (!/id="empezar"/.test($("inicio").innerHTML)) break;
    $("empezar").onclick();
    const ronda = { preguntas: [], fin: null };
    for (let guardia = 0; guardia < 200 && $("juego").style.display === "block"; guardia++) {
      const opciones = $("opts").children;
      const pregunta = {
        tipo: $("tipo").textContent,
        enunciado: $("enunciado").textContent,
        cita: $("cita").style.display === "block" ? $("cita").textContent : null,
        opciones: opciones.map((b) => b.textContent),
        contadores: {
          aciertos: String($("eAciertos").textContent),
          racha: String($("eRacha").textContent),
          pregunta: String($("ePreg").textContent),
        },
      };
      // En modo enfocado la respuesta correcta es un campo de la ficha foco;
      // así el arnés puede acertar o fallar a propósito. El Reto marca "bien"
      // la correcta después de responder, y eso es lo que se registra.
      const propios = new Set([foco.titulo, foco.significado, foco.decision]
        .concat(foco.falsos_positivos || []));
      let elegida = opciones.findIndex((b) => propios.has(b.textContent));
      if (peticion.responder === "incorrecta") {
        elegida = opciones.findIndex((b) => !propios.has(b.textContent));
      }
      opciones[elegida < 0 ? 0 : elegida].onclick();
      const correcta = opciones.find((b) => b.classList.contains("bien"));
      pregunta.correcto = correcta ? correcta.textContent : null;
      pregunta.acierto = $("veredicto").textContent === "Correcto";
      pregunta.fuente = $("fuente").innerHTML;
      pregunta.explica = $("explica").textContent;
      ronda.preguntas.push(pregunta);
      $("siguiente").onclick();
    }
    ronda.fin = { cifra: $("finCifra").textContent, repaso: $("repaso").innerHTML };
    salida.rondas.push(ronda);
    $("otra").onclick();
  }
  process.stdout.write(JSON.stringify(salida));
}

main().catch((e) => { process.stderr.write(String(e && e.stack || e)); process.exit(1); });
