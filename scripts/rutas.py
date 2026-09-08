"""Rutas comunes de las interfaces de comando del repositorio."""
from pathlib import Path


RAIZ_REPO = Path(__file__).resolve().parents[1]


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
