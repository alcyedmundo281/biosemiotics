#!/usr/bin/env python3
"""
Mina un caso del banco y arma los esqueletos de señuelo (TikTok/Reels/Shorts).

  python3 senuelo.py caso-01-disnea

El caso (trabajo profundo) se escribe PRIMERO; los señuelos son virutas de ese
bloque — baratos, porque el pensamiento ya está hecho. Nunca al revés.

Regla de oro: el señuelo NO resuelve. Es la primera mitad de una frase que el
archivo completa. Si el clip satisface, nadie hace clic.
"""
import sqlite3
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    caso_id = sys.argv[1]

    db = Path.cwd() / "build" / "atlas.db"
    if not db.exists():
        sys.exit("Falta build/atlas.db — corre primero: python3 scripts/build.py")

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    caso = con.execute(
        "SELECT * FROM entidad WHERE id=? AND tipo='caso'", (caso_id,)
    ).fetchone()
    if not caso:
        sys.exit(f"No existe el caso '{caso_id}'")

    signos = con.execute("""
        SELECT e.* FROM relacion r JOIN entidad e ON e.id = r.destino
        WHERE r.origen = ? AND r.clase = 'signos'
    """, (caso_id,)).fetchall()

    print(f"\n{'='*68}\nSEÑUELOS — {caso['titulo']}\n{'='*68}")
    print(f"\nBifurcación: {caso['decision'] or '(ver decision_semiotica)'}")
    print(f"Signos: {', '.join(s['titulo'] for s in signos) or '—'}")

    print(f"\n{'─'*68}\n1. LA BIFURCACIÓN SIN RESPUESTA  (el señuelo canónico)\n{'─'*68}")
    print("[0:00-0:03] GANCHO — credencial + amenaza")
    print('  "Soy médico internista. Este paciente tenía [síntoma] y el')
    print('   examen físico me estaba mintiendo."')
    print("\n[0:03-0:10] LA IMAGEN — corte directo entre los dos patrones, SIN explicar")
    for s in signos:
        print(f'  → {s["titulo"]}')
        if s["significante"]:
            print(f'    ({s["significante"][:60]}...)')
    print("\n[0:10-0:15] LA BIFURCACIÓN — el corte sin respuesta")
    for s in signos:
        if s["decision"]:
            print(f'  · {s["decision"]}')
    print('  "Y son el mismo paciente en la puerta de tu consultorio."')
    print("\n[0:15-0:18] PERMISO + PUENTE")
    print('  "No necesitas 40 ventanas. Necesitas esta. Caso completo en el enlace."')
    print("\n  → CORTE. Sin resolución, sin tutorial.")

    print(f"\n{'─'*68}\n2. VARIANTES A MINAR DEL MISMO CASO\n{'─'*68}")
    print("  a) Provocación institucional:")
    print('     "El estetoscopio tiene 200 años. Tu facultad no te enseñó')
    print('      lo que lo reemplaza."')
    print("  b) Desafío al colega (alimenta el parlamento):")
    print('     "Mira el loop. ¿Cuál es? Comenta antes de ver el caso."')
    print("  c) Permiso puro (desactiva la intimidación):")
    print('     "Lo que necesitas para empezar: una sonda de bolsillo y')
    print('      dos patrones. Eso es todo. Hoy."')
    print("  d) El error que todos cometen:")
    print('     "Auscultaste limpio y trataste otra cosa. El ultrasonido')
    print('      decía lo contrario."')

    print(f"\n{'─'*68}\nPRODUCCIÓN\n{'─'*68}")
    print("  · Vertical, subtítulos quemados (se ve sin audio).")
    print("  · Plano sonda-en-mano = mitad del gancho. Sin rostro ni identificadores.")
    print("  · Registro: RUIDOSO. El archivo es sobrio; el señuelo puede ser filoso.")
    print("  · Mismo clip → TikTok + Reels + Shorts. Nunca una sola plataforma.")
    print(f"  · Consentimiento del caso: {caso['consentimiento']!r}", end="")
    if caso["consentimiento"] != "obtenido":
        print("  ⚠ NO PUBLICAR")
    else:
        print()
    print()


if __name__ == "__main__":
    main()
