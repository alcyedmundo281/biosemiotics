"""Taxonomías y orden editorial compartidos por los generadores."""

RELS = (
    "relacionado_con",
    "prerequisito_de",
    "se_basa_en",
    "contrasta_con",
    "signos",
    "conceptos",
)

NIVELES = {"principiante", "intermedio", "avanzado"}

CAPITULOS = {
    2: "Física del ultrasonido",
    3: "El lenguaje de la imagen",
    4: "Técnica, sondas y ventanas",
    5: "Artefactos",
    6: "Instrumentación y medición",
}

ORGANOS = {
    "aorta-abdominal": "Aorta abdominal",
    "apendice": "Apéndice",
    "corazon": "Corazón",
    "higado": "Hígado",
    "intestino": "Intestino",
    "pared": "Pared",
    "pericardio": "Pericardio",
    "pleura": "Pleura",
    "pulmon": "Pulmón",
    "riñon": "Riñón",
    "utero": "Útero",
    "vejiga": "Vejiga",
    "vena-profunda": "Vena profunda",
    "vesicula": "Vesícula",
    "via-biliar": "Vía biliar",
}


def nombre_organo(clave: str) -> str:
    """Devuelve el nombre legible y tolera slugs nuevos."""
    if not clave:
        return "Otros"
    return ORGANOS.get(clave) or clave.replace("-", " ").capitalize()


SISTEMAS = [
    ("respiratorio", "Sistema respiratorio"),
    ("cardiovascular", "Sistema cardiovascular"),
    ("digestivo", "Sistema digestivo"),
    ("genitourinario", "Sistema genitourinario"),
    ("vascular", "Sistema vascular"),
    ("musculoesqueletico", "Musculoesquelético y pared"),
    ("endocrino", "Sistema endocrino"),
    ("nervioso", "Sistema nervioso"),
    ("multiorgano", "Multiórgano y protocolos"),
]
