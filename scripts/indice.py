#!/usr/bin/env python3
"""
ÍNDICE v2 — modelo PubMed/PMC.

  ÍNDICE (index.json) = PubMed. Fichas de metadatos. NUNCA el cuerpo.
  GHOST (campo url)   = PMC. Texto completo, loops, imágenes, referencias.

  python3 indice.py . <URL_DEL_INDEX_JSON>

Produce en build/:
  index.json          fichas ricas → el buscador con facetas
  atlas-inject.html   code injection de la página /atlas de Ghost
  jsonld/*.json       schema.org por post (Google + sistemas de IA)
  jats/*.xml          JATS para DEPÓSITO y archivo (NO se sube a Ghost)
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import cargar  # noqa: E402

# DOI de la obra completa (Zenodo). Se muestra bajo el buscador del atlas.
DOI_OBRA = "10.5281/zenodo.21435362"


# ══════════════════ 1. LA FICHA (el registro tipo PubMed) ══════════════════
def ficha(e: dict) -> dict:
    f = {"id": e["id"], "tipo": e["tipo"], "titulo": e["titulo"]}

    for k in ("titulo_en", "url", "doi", "version", "abstract",
              "sistema", "organo", "nivel", "ventana", "pregunta_clinica",
              "significante", "significado", "umbral",
              "licencia", "composite", "revisado_por"):
        if e.get(k):
            f[k] = e[k]
    for k in ("fecha", "actualizado"):
        if e.get(k):
            f[k] = str(e[k])

    dec = e.get("decision") or e.get("decision_semiotica")
    if dec:
        f["decision"] = dec

    for k in ("sonda", "escenario", "descriptores", "mesh", "tags",
              "falsos_positivos", "se_basa_en", "contrasta_con",
              "signos", "conceptos"):
        if e.get(k):
            f[k] = e[k]

    f["autores"] = e.get("autores") or [{"nombre": "Alcy Torres"}]

    # Inventario de medios — NO los archivos. Esa es la diferencia PubMed/PMC.
    med = e.get("medios") or []
    if med:
        f["medios"] = med
        f["n_loops"] = sum(1 for m in med if m.get("tipo") == "loop")
        f["n_imagenes"] = sum(1 for m in med if m.get("tipo") == "imagen")

    if e.get("refs"):
        f["refs"] = e["refs"]
        f["n_refs"] = len(e["refs"])
    return f


# ══════════════════ 2. JSON-LD (Google + sistemas de IA) ══════════════════
def jsonld(e: dict) -> dict:
    autores = e.get("autores") or [{"nombre": "Alcy Torres"}]
    ld = {
        "@context": "https://schema.org",
        "@type": "MedicalScholarlyArticle",
        "headline": e["titulo"],
        "inLanguage": "es",
        "author": [
            {k: v for k, v in {
                "@type": "Person",
                "name": a.get("nombre"),
                "identifier": (f"https://orcid.org/{a['orcid']}"
                               if a.get("orcid") else None),
                "affiliation": ({"@type": "Organization", "name": a["afiliacion"]}
                                if a.get("afiliacion") else None),
            }.items() if v} for a in autores
        ],
        "publisher": {"@type": "Organization", "name": "biosemiotics"},
        "isAccessibleForFree": True,
        "audience": {"@type": "MedicalAudience", "audienceType": "Physician"},
        "learningResourceType": "Clinical education",
    }
    if e.get("abstract"):
        ld["abstract"] = ld["description"] = " ".join(e["abstract"].split())
    if e.get("url"):
        ld["url"] = ld["mainEntityOfPage"] = e["url"]
    if e.get("doi"):
        ld["identifier"] = {"@type": "PropertyValue",
                            "propertyID": "DOI", "value": e["doi"]}
    if e.get("fecha"):
        ld["datePublished"] = str(e["fecha"])
    if e.get("actualizado"):
        ld["dateModified"] = str(e["actualizado"])
    if e.get("licencia"):
        ld["license"] = "https://creativecommons.org/licenses/by-nc/4.0/"
    if e.get("version"):
        ld["version"] = e["version"]

    kw = (e.get("descriptores") or []) + (e.get("mesh") or []) + (e.get("tags") or [])
    if kw:
        ld["keywords"] = ", ".join(dict.fromkeys(kw))

    if e["tipo"] == "signo":
        about = {
            "@type": "MedicalSignOrSymptom",
            "name": e["titulo"],
            "identifyingTest": {
                "@type": "MedicalTest",
                "name": "Point-of-care ultrasound",
                "usedToDiagnose": e.get("significado", ""),
            },
        }
        if e.get("significante"):
            about["signDetected"] = e["significante"]
        ld["about"] = about

    vids = [{"@type": "VideoObject", "name": m.get("descripcion", "")}
            for m in (e.get("medios") or []) if m.get("tipo") == "loop"]
    if vids:
        ld["video"] = vids
    return {k: v for k, v in ld.items() if v}


# Mapeo instructivo → JATS. El núcleo archivable; la envoltura NO se deposita.
SEC_MAP = {
    "la pregunta clínica": "clinical-question",
    "viñeta clínica": "case-presentation",
    "el fenómeno": "intro",
    "por qué el examen físico no basta": "rationale",
    "lo que hubiera hecho sin la sonda": "rationale",
    "por qué importa para leer la imagen": "rationale",
    "cómo se obtiene la ventana": "acquisition",
    "el escaneo": "acquisition",
    "el signo": "sign",
    "lo que mostró": "sign",
    "cómo se ve en pantalla": "sign",
    "la bifurcación": "decision",
    "la bifurcación y el desenlace": "decision",
    "dónde no confiar": "limitations",
}
# Envoltura comunitaria: se queda en Ghost, nunca se deposita.
NO_ARCHIVAR = {"practica esto", "discusión abierta", "evidencia"}


def secciones(cuerpo: str):
    """Parte el cuerpo por '## ' y devuelve [(sec_type, titulo, texto)] del núcleo."""
    out, actual, buf = [], None, []
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            if actual:
                out.append((*actual, "\n".join(buf).strip()))
            t = linea[3:].strip()
            k = t.lower().rstrip(".:")
            actual = (SEC_MAP.get(k), t) if k not in NO_ARCHIVAR else None
            buf = []
        elif actual:
            buf.append(linea)
    if actual:
        out.append((*actual, "\n".join(buf).strip()))
    return [s for s in out if s[0]]


# ══════════════════ 3. JATS (depósito y archivo — NO Ghost) ══════════════════
def jats(e: dict) -> str:
    a = ET.Element("article", {"article-type": "research-article"})
    meta = ET.SubElement(ET.SubElement(a, "front"), "article-meta")

    if e.get("doi"):
        ET.SubElement(meta, "article-id", {"pub-id-type": "doi"}).text = e["doi"]
    ET.SubElement(meta, "article-id",
                  {"pub-id-type": "publisher-id"}).text = e["id"]

    tg = ET.SubElement(meta, "title-group")
    ET.SubElement(tg, "article-title").text = e["titulo"]
    if e.get("titulo_en"):
        ET.SubElement(tg, "trans-title").text = e["titulo_en"]

    cg = ET.SubElement(meta, "contrib-group")
    for au in (e.get("autores") or []):
        c = ET.SubElement(cg, "contrib", {"contrib-type": "author"})
        if au.get("orcid"):
            ET.SubElement(c, "contrib-id",
                          {"contrib-id-type": "orcid"}).text = au["orcid"]
        n = ET.SubElement(c, "name")
        p = (au.get("nombre") or "").split()
        ET.SubElement(n, "surname").text = " ".join(p[-2:]) if len(p) > 2 else (p[-1] if p else "")
        ET.SubElement(n, "given-names").text = " ".join(p[:-2]) if len(p) > 2 else " ".join(p[:-1])
        if au.get("afiliacion"):
            ET.SubElement(c, "aff").text = au["afiliacion"]
        for rol in (au.get("credit") or []):
            ET.SubElement(c, "role", {"vocab": "CRediT"}).text = rol

    if e.get("fecha"):
        parts = (str(e["fecha"]).split("-") + ["", ""])[:3]
        pd = ET.SubElement(meta, "pub-date", {"date-type": "pub"})
        for tag, val in zip(("year", "month", "day"), parts):
            if val:
                ET.SubElement(pd, tag).text = val

    if e.get("abstract"):
        ET.SubElement(ET.SubElement(meta, "abstract"), "p").text = \
            " ".join(e["abstract"].split())

    kws = (e.get("descriptores") or []) + (e.get("tags") or [])
    if kws:
        kg = ET.SubElement(meta, "kwd-group", {"kwd-group-type": "author"})
        for k in kws:
            ET.SubElement(kg, "kwd").text = k
    if e.get("mesh"):
        kg = ET.SubElement(meta, "kwd-group", {"kwd-group-type": "MeSH"})
        for k in e["mesh"]:
            ET.SubElement(kg, "kwd").text = k

    if e.get("licencia"):
        lic = ET.SubElement(ET.SubElement(meta, "permissions"), "license")
        ET.SubElement(lic, "license-p").text = e["licencia"]

    # BODY: secciones del núcleo archivable, con su sec-type del instructivo.
    body = ET.SubElement(a, "body")
    secs = secciones(e["cuerpo"])
    if secs:
        for sec_type, titulo, texto in secs:
            s = ET.SubElement(body, "sec", {"sec-type": sec_type})
            ET.SubElement(s, "title").text = titulo
            for parr in [p for p in texto.split("\n\n") if p.strip()]:
                ET.SubElement(s, "p").text = " ".join(parr.split())
        # Los medios se declaran como figuras del cuerpo.
        for m in (e.get("medios") or []):
            fig = ET.SubElement(body, "fig")
            ET.SubElement(ET.SubElement(fig, "caption"), "p").text = \
                m.get("descripcion", "")
            ET.SubElement(fig, "media", {
                "mimetype": "video" if m.get("tipo") == "loop" else "image",
                "content-type": m.get("tipo", ""),
            })
    else:
        # Entidad sin artículo estructurado todavía: solo el cuerpo crudo.
        ET.SubElement(ET.SubElement(body, "sec"), "p").text = e["cuerpo"][:2000]

    rl = ET.SubElement(ET.SubElement(a, "back"), "ref-list")
    for r in (e.get("refs") or []):
        ET.SubElement(rl, "ref", {"id": r})

    ET.indent(a, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(a, encoding="unicode")


# ══════════════════ 4. LA PÁGINA /atlas ══════════════════
CSS = """
#bs{max-width:840px;margin:0 auto;font-family:'Literata',Georgia,serif;color:#14181B}
#bs *{box-sizing:border-box}
.bsdoi{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#8A9199;
margin:0 0 14px;letter-spacing:.03em}
.bsdoi a{color:#A8322F;text-decoration:none}
.bsdoi a:hover{text-decoration:underline}
#bsq{width:100%;padding:14px 16px;font-size:16px;font-family:inherit;
border:1px solid #DFE3E6;border-radius:6px;background:#fff}
#bsq:focus{outline:none;border-color:#A8322F}
.bsfg{margin:14px 0}
.bsfl{font-family:'IBM Plex Mono',monospace;font-size:10px;text-transform:uppercase;
letter-spacing:.08em;color:#8A9199;margin-bottom:6px}
.bsf{display:flex;gap:5px;flex-wrap:wrap}
.bsf button{font-family:'IBM Plex Mono',monospace;font-size:11px;text-transform:uppercase;
letter-spacing:.05em;padding:5px 11px;border:1px solid #DFE3E6;border-radius:20px;
background:none;color:#5F676E;cursor:pointer}
.bsf button:hover{border-color:#8A9199}
.bsf button.on{background:#A8322F;border-color:#A8322F;color:#fff}
#bsn{font-family:'IBM Plex Mono',monospace;font-size:11px;text-transform:uppercase;
letter-spacing:.08em;color:#5F676E;margin:22px 0 4px;padding-top:16px;
border-top:1px solid #E3E7EA}
.bsr{border-top:1px solid #E3E7EA;padding:20px 0}
.bsr:first-child{border-top:none}
.bsk{font-family:'IBM Plex Mono',monospace;font-size:10px;text-transform:uppercase;
letter-spacing:.08em;color:#8A9199;margin-bottom:5px}
.bst{font-family:'Archivo',system-ui,sans-serif;font-weight:600;font-size:19px;
margin:0 0 3px;letter-spacing:-.01em;line-height:1.3}
.bst a{color:#A8322F;text-decoration:none}
.bst a:hover{text-decoration:underline}
.bsp{font-size:14px;color:#5F676E;font-style:italic;margin:2px 0 9px}
.bsa{font-size:14.5px;line-height:1.6;color:#333;margin:0 0 10px}
.bsd{font-size:14px;color:#A8322F;font-weight:600;margin:8px 0}
.bsw{font-size:13px;color:#8A4B00;margin:6px 0}
.bsm{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#8A9199;
margin-top:10px;display:flex;gap:14px;flex-wrap:wrap}
.bsm a{color:#2E5A87}
.bsg{font-size:13px;color:#5F676E;margin-top:7px}
.bsg b{font-family:'IBM Plex Mono',monospace;font-size:10px;text-transform:uppercase;
letter-spacing:.06em;font-weight:400;color:#8A9199;margin-right:5px}
.bsg span{color:#2E5A87;cursor:pointer}
.bsg span:hover{text-decoration:underline}
.bsx{color:#8A9199;padding:44px 0;text-align:center}
"""

JS = r"""
(function(){
var IDX="%%URL%%",IDX2="%%URL2%%",el=document.getElementById('bs');if(!el)return;
var D=[],F={},BY={};
var nm=function(s){return(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();};
var es=function(s){return String(s).replace(/[&<>]/g,function(c){
  return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});};

function facets(){
  return [['tipo','Tipo'],['sistema','Sistema'],['organo','Órgano'],
          ['nivel','Nivel'],['escenario','Escenario']].map(function(d){
    var v={};
    D.forEach(function(n){
      var x=n[d[0]];
      (Array.isArray(x)?x:[x]).forEach(function(y){if(y)v[y]=1;});
    });
    var ks=Object.keys(v).sort();
    if(!ks.length)return'';
    return '<div class="bsfg"><div class="bsfl">'+d[1]+'</div><div class="bsf">'+
      ks.map(function(k){return '<button data-f="'+d[0]+'" data-v="'+es(k)+'">'+
        es(k)+'</button>';}).join('')+'</div></div>';
  }).join('');
}

function ok(n){
  for(var k in F){
    if(!F[k])continue;
    var v=n[k];
    if(!(Array.isArray(v)?v.indexOf(F[k])>-1:v===F[k]))return false;
  }
  return true;
}

function render(){
  var q=nm(document.getElementById('bsq').value);
  var h=D.filter(function(n){
    if(!ok(n))return false;
    if(!q)return true;
    return nm([n.titulo,n.titulo_en,n.abstract,n.pregunta_clinica,n.organo,
      n.sistema,n.decision,n.significante,n.significado,
      (n.descriptores||[]).join(' '),(n.mesh||[]).join(' ')].join(' ')).indexOf(q)>-1;
  });
  var o={signo:0,caso:1,concepto:2};
  h.sort(function(a,b){return(o[a.tipo]-o[b.tipo])||a.titulo.localeCompare(b.titulo);});
  document.getElementById('bsn').textContent=h.length+
    (h.length===1?' resultado':' resultados');
  var out=document.getElementById('bso');
  if(!h.length){out.innerHTML='<p class="bsx">Sin resultados.</p>';return;}

  out.innerHTML=h.map(function(n){
    var t=n.url?'<a href="'+n.url+'">'+es(n.titulo)+'</a>'
      :es(n.titulo)+' <span style="font-size:12px;color:#8A9199">(sin publicar)</span>';
    var s='<div class="bsr"><div class="bsk">'+n.tipo+
      (n.sistema?' · '+n.sistema:'')+(n.organo?' · '+n.organo:'')+
      (n.nivel?' · '+n.nivel:'')+'</div><h3 class="bst">'+t+'</h3>';
    if(n.pregunta_clinica)s+='<p class="bsp">'+es(n.pregunta_clinica)+'</p>';
    if(n.abstract)s+='<p class="bsa">'+es(n.abstract)+'</p>';
    if(n.decision)s+='<p class="bsd">→ '+es(n.decision)+'</p>';
    if(n.falsos_positivos&&n.falsos_positivos.length)
      s+='<p class="bsw">No confiar si: '+n.falsos_positivos.map(es).join(' · ')+'</p>';

    ['se_basa_en','contrasta_con','signos','conceptos'].forEach(function(r){
      if(!n[r]||!n[r].length)return;
      var lb={se_basa_en:'Se basa en',contrasta_con:'Contrasta con',
              signos:'Signos',conceptos:'Conceptos'}[r];
      var lk=n[r].map(function(id){
        var x=BY[id];
        return x?'<span data-go="'+id+'">'+es(x.titulo)+'</span>':'';
      }).filter(Boolean).join(' · ');
      if(lk)s+='<div class="bsg"><b>'+lb+'</b>'+lk+'</div>';
    });

    var m=[];
    if(n.autores)m.push(n.autores.map(function(a){return es(a.nombre);}).join(', '));
    if(n.fecha)m.push(n.fecha);
    if(n.n_loops)m.push(n.n_loops+(n.n_loops===1?' loop':' loops'));
    if(n.n_refs)m.push(n.n_refs+' refs');
    if(n.doi)m.push('<a href="https://doi.org/'+n.doi+'">doi</a>');
    if(m.length)s+='<div class="bsm">'+m.map(function(x){
      return'<span>'+x+'</span>';}).join('')+'</div>';
    return s+'</div>';
  }).join('');

  out.querySelectorAll('[data-go]').forEach(function(b){
    b.onclick=function(){
      F={};
      document.querySelectorAll('.bsf button').forEach(function(x){x.classList.remove('on');});
      var x=BY[b.dataset.go];
      document.getElementById('bsq').value=x?x.titulo:'';
      render();
      window.scrollTo(0,el.offsetTop-20);
    };
  });
}

// El índice se pide primero a raw.githubusercontent (cache 5 min) y, si falla
// —rate-limit, corte—, se reintenta contra jsDelivr (cache 12 h en ramas).
// Ambos sirven el MISMO archivo del repo. Nunca se lee desde biosemiotics.net.
function cargar(u){
  return fetch(u,{cache:'no-cache'}).then(function(r){
    if(!r.ok)throw new Error('HTTP '+r.status);
    return r.json();
  });
}

cargar(IDX).catch(function(){return cargar(IDX2);}).then(function(j){
  D=j.fichas||j;
  D.forEach(function(n){BY[n.id]=n;});
  document.getElementById('bsfw').innerHTML=facets();
  document.getElementById('bsq').addEventListener('input',render);
  document.querySelectorAll('.bsf button').forEach(function(b){
    b.onclick=function(){
      var f=b.dataset.f,v=b.dataset.v;
      if(F[f]===v){delete F[f];b.classList.remove('on');}
      else{
        F[f]=v;
        document.querySelectorAll('.bsf button[data-f="'+f+'"]').forEach(
          function(x){x.classList.remove('on');});
        b.classList.add('on');
      }
      render();
    };
  });
  render();
}).catch(function(){
  document.getElementById('bso').innerHTML=
    '<p class="bsx">No se pudo cargar el índice.</p>';
});
})();
"""


def raw_desde_jsdelivr(url: str) -> str:
    """https://cdn.jsdelivr.net/gh/USER/REPO@RAMA/ruta
       → https://raw.githubusercontent.com/USER/REPO/RAMA/ruta

    raw se cachea 5 min; jsDelivr cachea las rutas de RAMA 12 h y ni la purga
    ni un query string la esquivan. Por eso raw va de primario y jsDelivr de
    respaldo. Si la URL no es de jsDelivr, se devuelve tal cual.
    """
    m = re.match(r"https://cdn\.jsdelivr\.net/gh/([^/]+)/([^@/]+)@([^/]+)/(.+)", url)
    if not m:
        return url
    usuario, repo, rama, ruta = m.groups()
    return f"https://raw.githubusercontent.com/{usuario}/{repo}/{rama}/{ruta}"


def main():
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    url = sys.argv[2] if len(sys.argv) > 2 else "/content/index.json"
    # Primario: raw (fresco). Respaldo: lo que se pasó por argumento (jsDelivr).
    url_primaria = sys.argv[3] if len(sys.argv) > 3 else raw_desde_jsdelivr(url)
    ent = cargar(raiz)
    b = raiz / "build"
    b.mkdir(exist_ok=True)

    fichas = [ficha(e) for e in ent]
    (b / "index.json").write_text(
        json.dumps({"fichas": fichas}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    (b / "jsonld").mkdir(exist_ok=True)
    (b / "jats").mkdir(exist_ok=True)
    for e in ent:
        (b / "jsonld" / f"{e['id']}.json").write_text(
            json.dumps(jsonld(e), ensure_ascii=False, indent=2), encoding="utf-8")
        (b / "jats" / f"{e['id']}.xml").write_text(jats(e), encoding="utf-8")

    (b / "atlas-inject.html").write_text(
        f"<style>{CSS}</style>\n\n"
        '<div id="bs">\n'
        f'  <p class="bsdoi">Obra citable · <a href="https://doi.org/{DOI_OBRA}">DOI: {DOI_OBRA}</a></p>\n'
        '  <input id="bsq" placeholder="Buscar signo, órgano, pregunta clínica…" autocomplete="off">\n'
        '  <div id="bsfw"></div>\n'
        '  <p id="bsn"></p>\n'
        '  <div id="bso"></div>\n'
        '</div>\n\n'
        f"<script>{JS.replace('%%URL%%', url_primaria).replace('%%URL2%%', url)}</script>\n",
        encoding="utf-8")

    kb = (b / "index.json").stat().st_size / 1024
    sin_ab = [f["id"] for f in fichas if not f.get("abstract")]
    sin_url = [f["id"] for f in fichas if not f.get("url")]

    print(f"→ index.json        {len(fichas)} fichas · {kb:.1f} KB · sin cuerpos")
    print(f"→ atlas-inject.html facetas + navegación de grafo")
    print(f"   primario  {url_primaria}")
    print(f"   respaldo  {url}")
    print(f"→ jsonld/           {len(ent)} · schema.org (Google + IA)")
    print(f"→ jats/             {len(ent)} · XML para DEPÓSITO (no para Ghost)")
    print(f"\n   proyección: 1.000 fichas ≈ {kb / len(fichas) * 1000:.0f} KB")
    if sin_ab:
        print(f"\n⚠ {len(sin_ab)} sin abstract — no se pueden evaluar desde el índice")
    if sin_url:
        print(f"⚠ {len(sin_url)} sin url — no enlazan a Ghost")


if __name__ == "__main__":
    main()
