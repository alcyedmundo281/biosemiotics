#!/usr/bin/env python3
"""Lo que el banco permite y Ghost NO: exploración estructurada del atlas."""
import sqlite3
from pathlib import Path

con = sqlite3.connect(Path(__file__).parent / "build" / "atlas.db")
con.row_factory = sqlite3.Row
q = lambda s, *a: con.execute(s, a).fetchall()


def titulo(t):
    print(f"\n{'─'*66}\n{t}\n{'─'*66}")


# 1. RUTA DE APRENDIZAJE — ¿qué debo saber ANTES de leer líneas B?
titulo("1. PREREQUISITOS de 'signo-lineas-b'  (ruta de aprendizaje)")
for r in q("""
    SELECT e.titulo, e.dominio, r.clase
    FROM relacion r JOIN entidad e ON e.id = r.origen
    WHERE r.destino = 'signo-lineas-b'
      AND r.clase IN ('prerequisito_de','se_basa_en')
"""):
    print(f"  ← {r['titulo']:<38} [{r['dominio'] or '—'}]")
for r in q("""
    SELECT e.titulo FROM relacion r JOIN entidad e ON e.id = r.destino
    WHERE r.origen='signo-lineas-b' AND r.clase='se_basa_en'
"""):
    print(f"  ← {r['titulo']:<38} [se basa en]")

# 2. DE LA DECISIÓN AL SIGNO — entrada clínica, no alfabética
titulo("2. TODOS los signos que cambian una decisión (entrada clínica)")
for r in q("""SELECT titulo, organo, decision FROM entidad
              WHERE tipo='signo' AND decision IS NOT NULL ORDER BY organo"""):
    print(f"  [{r['organo']:<7}] {r['titulo']}")
    print(f"            → {r['decision']}")

# 3. EL GRAFO SEMIÓTICO — un artefacto físico genera N signos clínicos
titulo("3. GRAFO: qué signos nacen del artefacto 'reverberación'")
for r in q("""
    SELECT e.titulo, e.significado FROM relacion r JOIN entidad e ON e.id=r.origen
    WHERE r.destino='artefacto-reverberacion' AND r.clase='se_basa_en'
"""):
    print(f"  → {r['titulo']}")
    print(f"    {r['significado']}")

# 4. SEGURIDAD — todos los falsos positivos del banco, de golpe
titulo("4. AUDITORÍA CLÍNICA: falsos positivos declarados (tu firewall)")
for r in q("""SELECT e.titulo, f.texto FROM falso_positivo f
              JOIN entidad e ON e.id=f.entidad ORDER BY e.titulo"""):
    print(f"  {r['titulo']:<26} ✗ {r['texto']}")

# 5. CURRÍCULO DEL TALLER — filtrar por órgano + nivel
titulo("5. TALLER DE PULMÓN: todo el material, nivel principiante")
for r in q("""SELECT tipo, titulo FROM entidad
              WHERE organo='pulmon' AND nivel='principiante'
              ORDER BY tipo DESC"""):
    print(f"  [{r['tipo']:<8}] {r['titulo']}")

# 6. CONTRASTE — la bifurcación semiótica
titulo("6. PARES EN CONTRASTE (las bifurcaciones que enseñas)")
for r in q("""
    SELECT a.titulo AS uno, b.titulo AS otro, a.decision AS d1, b.decision AS d2
    FROM relacion r
    JOIN entidad a ON a.id=r.origen JOIN entidad b ON b.id=r.destino
    WHERE r.clase='contrasta_con' AND a.id < b.id
"""):
    print(f"  {r['uno']}\n     ⇄ {r['otro']}")
    print(f"     · {r['d1']}\n     · {r['d2']}")

# 7. BÚSQUEDA FULL-TEXT
titulo("7. BÚSQUEDA FTS: 'líquido'")
for r in q("SELECT titulo FROM busqueda WHERE busqueda MATCH 'líquido'"):
    print(f"  · {r['titulo']}")

# 8. HUÉRFANOS — control de calidad editorial
titulo("8. CONTROL EDITORIAL: entidades sin referencias bibliográficas")
for r in q("""SELECT titulo, tipo FROM entidad
              WHERE id NOT IN (SELECT entidad FROM ref) AND tipo='signo'"""):
    print(f"  ⚠ {r['titulo']} ({r['tipo']}) — sin BibLaTeX")

print()
