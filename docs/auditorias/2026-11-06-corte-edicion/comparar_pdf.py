"""Auditoría Linux: antes/después del filtro y banco con publicación futura."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

root=Path.cwd()
base=sys.argv[1]
out=root/'build/auditoria-corte'
out.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,SOURCE_DATE_EPOCH='1793923200',FORCE_SOURCE_DATE='1')
report={'base_colofon':base,'head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
        'version_controlada':'auditoria-corte','dpi':150,'escenarios':{}}

with tempfile.TemporaryDirectory() as tmp:
    manifests={}
    texts={}
    for name,ref in [('antes',base),('despues','HEAD'),('con_futura','HEAD')]:
        bank=Path(tmp)/name
        bank.mkdir()
        data=subprocess.check_output(['git','archive',ref])
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            archive.extractall(bank,filter='data')
        if name=='con_futura':
            # Solo el banco temporal de esta prueba. No hay edición del banco real.
            (bank/'conceptos/auditoria-futura.qmd').write_text(
                '---\nid: auditoria-futura\ntipo: concepto\ntitulo: FICHA FICTICIA POSTERIOR\n'
                'estado: publicado\nnumero: 57\nvolumen: 1\n'
                'ghost_id: abcdef0123456789abcdef01\n'
                'url: "https://example.org/auditoria-futura/"\n'
                'fecha_publicacion: "2026-11-20T12:00:00.000+00:00"\n'
                '---\nEsta ficha ficticia no puede entrar en el libro.\n',encoding='utf-8')
        code="""import sys; from pathlib import Path
sys.path.insert(0,'scripts')
import banco,qmd,libro
es=banco.cargar(Path('.').resolve())
seleccion=banco.seleccionar_edicion(es,qmd.FECHA_CORTE) if hasattr(banco,'seleccionar_edicion') else banco.seleccionar_publicables(es,True)
assert len(seleccion)==56, len(seleccion)
if any(e['id']=='auditoria-futura' for e in es):
    assert len(banco.seleccionar_publicables(es,True))==57
    assert not any(e['id']=='auditoria-futura' for e in seleccion)
qmd.version_git=lambda raiz:'auditoria-corte'
sys.argv=['libro.py','--salida','build/libro.pdf','--solo-publicados']
raise SystemExit(libro.main())
"""
        subprocess.run([sys.executable,'-c',code],cwd=bank,env=env,check=True)
        pdf=bank/'build/libro.pdf'
        info=subprocess.check_output(['pdfinfo',str(pdf)]).decode()
        pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
        report['escenarios'][name]={'fichas':56,'paginas':pages,'publicadas_seriado':57 if name=='con_futura' else 56}
        if pages!=264:
            (out/'resultado.json').write_text(json.dumps(report,indent=2)+'\n')
            raise SystemExit(f'FALLO: {name} tiene {pages} páginas, no 264. Detener.')
        txt=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'])
        texts[name]=txt
        pngdir=Path(tmp)/('paginas-'+name);pngdir.mkdir()
        subprocess.run(['pdftoppm','-r','150','-png',str(pdf),str(pngdir/'pagina')],check=True)
        manifests[name]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pngdir.glob('*.png'))}
        if len(manifests[name])!=pages:
            raise SystemExit('FALLO: faltan páginas renderizadas')
        report['escenarios'][name]['hashes_paginas']=manifests[name]
        if name!='antes':
            diffs=sorted(k for k in manifests['antes'].keys()|manifests[name].keys()
                         if manifests['antes'].get(k)!=manifests[name].get(k))
            report['escenarios'][name]['paginas_distintas']=diffs
            report['escenarios'][name]['texto_identico']=txt==texts['antes']
            if diffs or txt!=texts['antes']:
                for page in diffs:
                    for scenario in ('antes',name):
                        src=Path(tmp)/('paginas-'+scenario)/page
                        if src.exists():shutil.copy2(src,out/(scenario+'-'+page))
                (out/'resultado.json').write_text(json.dumps(report,indent=2)+'\n')
                raise SystemExit('FALLO: cambia el PDF en '+name+': '+str(diffs)+'. Detener.')
    (out/'resultado.json').write_text(json.dumps(report,indent=2)+'\n')
    print('OK: antes, después y con ficha del 20 de noviembre: 56 fichas, 264 páginas; texto y todas las páginas idénticos a 150 dpi.')
