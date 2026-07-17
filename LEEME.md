# Banco biosemiotics — cómo arrancar

## Estructura
```
proyecto-biosemiotics/
├── conceptos/     ← física, artefactos, técnica (el "por qué")
├── signos/        ← significante → significado → decisión (el "qué hago")
├── casos/         ← el paciente real
├── scripts/       ← build.py, indice.py, refs.py, nuevo.py, senuelo.py, atlas.py, consultas.py
├── refs.bib       ← bibliografía (se llena desde PubMed)
└── build/         ← generado (no se versiona)
```

## Requisitos (una sola vez)
```bash
pip install pyyaml
```

## Uso diario
```bash
python3 scripts/nuevo.py signo nervio-optico "Vaina del nervio óptico"  # crear
python3 scripts/build.py            # compila SQLite + LaTeX + grafo + valida
python3 scripts/indice.py . <URL>   # genera index.json + atlas + jsonld + jats
python3 scripts/refs.py             # audita qué referencias faltan
python3 scripts/refs.py --buscar    # las busca en PubMed
python3 scripts/consultas.py        # explora el atlas en SQL
```

## Regla de oro
Escribe en los .md. Todo lo de build/ es derivado: se regenera con un comando.
El banco es la única fuente de verdad. Versiona con Git; build/ va en .gitignore.
