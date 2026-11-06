"""CI Linux: compara todas las páginas renderizadas de base y propuesta."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

root = Path.cwd()
base = sys.argv[1]
out = root / 'build/comparacion-numeracion'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, SOURCE_DATE_EPOCH='1793923200', FORCE_SOURCE_DATE='1')
with tempfile.TemporaryDirectory() as tmp:
    banks = []
    for name, ref in [('antes', base), ('despues', 'HEAD')]:
        target = Path(tmp) / name
        target.mkdir()
        data = subprocess.check_output(['git', 'archive', ref])
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            archive.extractall(target, filter='data')
        # The only controlled variable is the printed Git version. Both builds
        # still execute the actual libro.py and its internal validators.
        code = "import sys; sys.path.insert(0,'scripts'); import qmd,libro; qmd.version_git=lambda raiz:'auditoria-numeracion'; sys.argv=['libro.py','--salida','build/libro.pdf','--solo-publicados']; raise SystemExit(libro.main())"
        subprocess.run([sys.executable, '-c', code], cwd=target, env=env, check=True)
        pages = out / name
        pages.mkdir(exist_ok=True)
        subprocess.run(['pdftoppm', '-r', '150', '-png', str(target/'build/libro.pdf'),str(pages/'pagina')],check=True)
        rendered = sorted(pages.glob('pagina-*.png'))
        if not rendered:
            raise RuntimeError('PDF sin páginas renderizadas')
        banks.append({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in rendered})
    changed = sorted(k for k in banks[0].keys() | banks[1].keys() if banks[0].get(k)!=banks[1].get(k))
    report = dict(base=base, paginas_antes=len(banks[0]),paginas_despues=len(banks[1]),paginas_distintas=changed, resolucion_dpi=150, version_controlada='auditoria-numeracion', hashes_antes=banks[0],hashes_despues=banks[1])
    (out/'resultado.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if changed:
        raise SystemExit('FALLO: cambian páginas del PDF; detener revisión')
