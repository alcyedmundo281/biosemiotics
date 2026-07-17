#!/usr/bin/env python3
"""
Genera el ATLAS: una sola página HTML con buscador, estilo UpToDate.

  python3 atlas.py            → build/atlas.html

No tiene hubs, ni menús, ni arquitectura de navegación que mantener.
Tiene una caja de búsqueda y resultados jerárquicos. Agregar neurología o
gastroenterología = agregar archivos al banco y recompilar. Cero diseño nuevo.

El banco se embebe como JSON en el HTML: sin servidor, sin API, sin base de
datos remota. Un archivo, se abre en cualquier parte.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import cargar, RELS  # noqa: E402

CSS = """
:root{--ink:#14181B;--mute:#5F676E;--line:#E3E7EA;--paper:#FBFCFC;
--doppler:#A8322F;--surface:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font-family:'Literata',Georgia,serif;line-height:1.65}
header{background:var(--surface);border-bottom:1px solid var(--line);
padding:20px 0;position:sticky;top:0;z-index:10}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}
.brand{font-family:'Archivo',system-ui,sans-serif;font-weight:600;
font-size:15px;letter-spacing:-.01em;margin:0 0 14px}
.brand span{color:var(--doppler)}
#q{width:100%;padding:13px 16px;font-size:16px;font-family:inherit;
border:1px solid var(--line);border-radius:6px;background:var(--paper);color:var(--ink)}
#q:focus{outline:none;border-color:var(--doppler)}
.filters{display:flex;gap:6px;margin-top:12px;flex-wrap:wrap}
.f{font-family:'IBM Plex Mono',monospace;font-size:11px;text-transform:uppercase;
letter-spacing:.06em;padding:5px 11px;border:1px solid var(--line);border-radius:20px;
background:none;color:var(--mute);cursor:pointer}
.f:hover{border-color:var(--mute)}
.f.on{background:var(--doppler);border-color:var(--doppler);color:#fff}
main{padding:28px 0 80px}
.count{font-family:'IBM Plex Mono',monospace;font-size:11px;text-transform:uppercase;
letter-spacing:.08em;color:var(--mute);margin-bottom:20px}
.r{border-top:1px solid var(--line);padding:20px 0}
.r:first-of-type{border-top:none}
.rt{font-family:'Archivo',system-ui,sans-serif;font-weight:600;font-size:19px;
color:var(--doppler);margin:0 0 3px;cursor:pointer;letter-spacing:-.01em}
.rt:hover{text-decoration:underline}
.rk{font-family:'IBM Plex Mono',monospace;font-size:10px;text-transform:uppercase;
letter-spacing:.08em;color:var(--mute);margin-bottom:8px}
.sub{margin:9px 0 0 22px;font-size:14.5px;color:#2E5A87;cursor:pointer}
.sub:hover{text-decoration:underline}
.det{margin:14px 0 0 22px;padding-left:14px;border-left:2px solid var(--line);display:none}
.det.open{display:block}
.row{display:flex;gap:14px;margin:7px 0;font-size:14.5px}
.lbl{font-family:'IBM Plex Mono',monospace;font-size:10px;text-transform:uppercase;
letter-spacing:.06em;color:var(--mute);min-width:96px;padding-top:3px;flex-shrink:0}
.dec{color:var(--doppler);font-weight:600}
.warn{color:#8A4B00}
.lnk{color:#2E5A87;cursor:pointer}.lnk:hover{text-decoration:underline}
.body{margin-top:10px;font-size:15px;color:#333}
.empty{color:var(--mute);padding:40px 0;text-align:center}
"""

JS = """
const nodes = DATA.nodos, edges = DATA.aristas;
const byId = Object.fromEntries(nodes.map(n=>[n.id,n]));
const norm = s => (s||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
let filt = null;

const rel = (id,clase,dir) => edges
  .filter(e => e.clase===clase && (dir==='out' ? e.origen===id : e.destino===id))
  .map(e => byId[dir==='out' ? e.destino : e.origen]).filter(Boolean);

function render(){
  const q = norm(document.getElementById('q').value);
  let hits = nodes.filter(n => {
    if (filt && n.tipo !== filt) return false;
    if (!q) return true;
    return norm(n.titulo+' '+(n.organo||'')+' '+(n.dominio||'')+' '+
      (n.significante||'')+' '+(n.significado||'')+' '+(n.decision||'')+' '+
      (n.cuerpo||'')).includes(q);
  });
  hits.sort((a,b)=>{ const o={signo:0,caso:1,concepto:2};
    return (o[a.tipo]-o[b.tipo]) || a.titulo.localeCompare(b.titulo); });

  document.getElementById('count').textContent =
    hits.length + (hits.length===1?' resultado':' resultados');
  const out = document.getElementById('out');

  if(!hits.length){ out.innerHTML =
    '<p class="empty">Nada en el banco todavía. Escríbelo.</p>'; return; }

  out.innerHTML = hits.map(n=>{
    const base = rel(n.id,'se_basa_en','out');
    const contr = rel(n.id,'contrasta_con','out');
    const casos = rel(n.id,'signos','in');
    let d = '';
    if(n.significante) d += row('Significante', esc(n.significante));
    if(n.significado)  d += row('Significado',  esc(n.significado));
    if(n.decision)     d += row('Decisión','<span class="dec">'+esc(n.decision)+'</span>');
    if(n.umbral)       d += row('Umbral', esc(n.umbral));
    if(n.fp && n.fp.length)
      d += row('No confiar si','<span class="warn">'+n.fp.map(esc).join(' · ')+'</span>');
    if(base.length) d += row('Se basa en', links(base));
    if(contr.length) d += row('Contrasta con', links(contr));
    if(casos.length) d += row('Casos', links(casos));
    if(n.cuerpo) d += '<div class="body">'+esc(n.cuerpo.slice(0,320))+
      (n.cuerpo.length>320?'…':'')+'</div>';

    const subs = [];
    if(n.decision) subs.push(['La decisión clínica', n.id]);
    if(base.length) subs.push(['Fundamento físico', n.id]);
    if(n.fp && n.fp.length) subs.push(['Límites y falsos positivos', n.id]);
    if(casos.length) subs.push(['Casos donde aparece', n.id]);

    return '<div class="r">'+
      '<div class="rk">'+n.tipo+(n.organo?' · '+n.organo:'')+
        (n.dominio?' · '+n.dominio:'')+(n.nivel?' · '+n.nivel:'')+'</div>'+
      '<h2 class="rt" onclick="tog(\\''+n.id+'\\')">'+esc(n.titulo)+'</h2>'+
      subs.map(s=>'<div class="sub" onclick="tog(\\''+s[1]+'\\')">'+s[0]+'</div>').join('')+
      '<div class="det" id="d-'+n.id+'">'+d+'</div>'+
    '</div>';
  }).join('');
}

const row=(l,v)=>'<div class="row"><span class="lbl">'+l+'</span><span>'+v+'</span></div>';
const links=a=>a.map(x=>'<span class="lnk" onclick="go(\\''+x.id+
  '\\')">'+esc(x.titulo)+'</span>').join(' · ');
const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));

function tog(id){ const e=document.getElementById('d-'+id); if(e) e.classList.toggle('open'); }
function go(id){ const n=byId[id]; if(!n) return;
  filt=null; document.querySelectorAll('.f').forEach(b=>b.classList.remove('on'));
  document.getElementById('q').value=n.titulo; render();
  setTimeout(()=>tog(id),30); window.scrollTo(0,0); }

document.getElementById('q').addEventListener('input',render);
document.querySelectorAll('.f').forEach(b=>b.addEventListener('click',()=>{
  const t=b.dataset.t;
  if(filt===t){ filt=null; b.classList.remove('on'); }
  else { filt=t; document.querySelectorAll('.f').forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); }
  render();
}));
render();
"""


def main():
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    ent = cargar(raiz)

    nodos = []
    for e in ent:
        nodos.append({
            "id": e["id"], "tipo": e["tipo"], "titulo": e["titulo"],
            "organo": e.get("organo"), "dominio": e.get("dominio"),
            "nivel": e.get("nivel"),
            "significante": e.get("significante"),
            "significado": e.get("significado"),
            "decision": e.get("decision") or e.get("decision_semiotica"),
            "umbral": e.get("umbral"),
            "fp": e.get("falsos_positivos") or [],
            "cuerpo": e["cuerpo"],
        })
    aristas = [{"origen": e["id"], "destino": d, "clase": c}
               for e in ent for c in RELS for d in (e.get(c) or [])]

    data = json.dumps({"nodos": nodos, "aristas": aristas}, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atlas — biosemiotics</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600&family=Literata:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="wrap">
<p class="brand">bio<span>semiotics</span> · atlas</p>
<input id="q" placeholder="Buscar signo, órgano, decisión clínica…" autocomplete="off">
<div class="filters">
  <button class="f" data-t="signo">Signos</button>
  <button class="f" data-t="concepto">Conceptos</button>
  <button class="f" data-t="caso">Casos</button>
</div>
</div></header>
<main><div class="wrap">
<p class="count" id="count"></p>
<div id="out"></div>
</div></main>
<script>const DATA={data};</script>
<script>{JS}</script>
</body></html>"""

    out = raiz / "build" / "atlas.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"→ {out}  ({len(nodos)} entidades, {kb:.0f} KB, sin servidor)")


if __name__ == "__main__":
    main()
