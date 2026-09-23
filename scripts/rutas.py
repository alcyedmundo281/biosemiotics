"""Rutas y salida comunes de las interfaces de comando del repositorio."""
import sys
from pathlib import Path


RAIZ_REPO = Path(__file__).resolve().parents[1]


def blindar_salida() -> None:
    """UTF-8 en stdout y stderr, explícito y desde main(), nunca al importar.

    El banco escribe ✓, ✗, → y ≥ en los mensajes normales y también en los de
    error. En Windows la consola es cp1252: sin esto, `print("✓ …")` aborta con
    UnicodeEncodeError y el error real nunca se ve. stderr importa tanto como
    stdout —ahí sale lo que hay que leer cuando algo falla— y antes quedaba sin
    blindar en indice.py, atlas.py, refs.py, auditar_medios.py y
    verificar_citas.py, que emitían sus errores en cp1252 hacia un pipeline que
    los lee como UTF-8.

    Se llama desde cada main(). Cuando esto vivía a nivel de módulo,
    verificar_publicacion.py funcionaba solo por importar indice.py de rebote,
    y preflight.py —que no importa ninguno— fallaba en el primer comando de
    cada sesión.
    """
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")


def escribir_texto(ruta: Path, texto: str) -> None:
    """Escribe UTF-8 con LF en cualquier plataforma.

    Path.write_text solo acepta newline desde 3.10 y el piso del repositorio es
    3.9, así que el salto se fija con open(). Sin esto, en Windows todo derivado
    sale con CRLF: index.json aparece modificado tras cada indice.py aunque no
    haya cambiado nada, y .gitattributes tiene que normalizarlo al commitear.
    """
    with ruta.open("w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(texto)


def resolver_raiz(valor=None) -> Path:
    """La raíz explícita es relativa al cwd; por defecto usa este repositorio."""
    raiz = RAIZ_REPO if valor is None else Path(valor).expanduser()
    raiz = raiz.resolve()
    if not raiz.is_dir():
        raise RuntimeError(f"la raíz del banco no existe o no es un directorio: {raiz}")
    return raiz


def desde_raiz(raiz: Path, valor) -> Path:
    """Las rutas relativas de artefactos pertenecen a la raíz, no al cwd."""
    ruta = Path(valor).expanduser()
    return ruta if ruta.is_absolute() else raiz / ruta


def raiz_argumentos(parser, *, legado=False):
    parser.add_argument(
        "--raiz", type=Path, help="raíz del banco (por defecto, la del repositorio)"
    )
    if legado:
        parser.add_argument("raiz_legacy", nargs="?", type=Path, help="raíz posicional obsoleta")


def raiz_desde_argumentos(parser, args) -> Path:
    legado = getattr(args, "raiz_legacy", None)
    if getattr(args, "raiz", None) is not None and legado is not None:
        parser.error("usa --raiz o la raíz posicional obsoleta, no ambas")
    try:
        return resolver_raiz(getattr(args, "raiz", None) or legado)
    except RuntimeError as exc:
        parser.error(str(exc))
