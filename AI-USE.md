# Declaración de uso de inteligencia artificial

**Obra:** biosemiotics — atlas de POCUS para el médico de primer contacto
**Autor responsable:** Alcy Edmundo Torres Guerrero — [ORCID 0000-0002-9742-375X](https://orcid.org/0000-0002-9742-375X)
**Editor:** Powersemiotics — Wellesley, Massachusetts, Estados Unidos
**DOI de la obra:** [10.5281/zenodo.21435362](https://doi.org/10.5281/zenodo.21435362)
**Alcance:** el sitio biosemiotics.net, este repositorio y las ediciones derivadas
(PDF, EPUB, LaTeX) que se publiquen a partir de él.
**Vigente desde:** 22 de octubre de 2026 · **Última revisión:** 22 de octubre de 2026

---

## Por qué existe este archivo

La pregunta «¿usó inteligencia artificial?» no tiene respuesta verificable: el uso
no se puede detectar, y los detectores disponibles clasifican falsamente como
generado por máquina más de la mitad de los textos escritos por autores cuya lengua
materna no es el inglés.¹ Es una vara que castiga al autor honesto.

La pregunta que sí tiene respuesta es otra: **¿se puede rastrear de dónde viene cada
afirmación?** Este archivo declara el uso, y el repositorio permite comprobarlo.

---

## Qué herramientas y en qué etapas

| Herramienta | Etapa | Qué hace |
|---|---|---|
| Codex (GPT-6 Astra) | Edición, investigación bibliográfica, mantenimiento del código | Asiste en redacción y revisión; propone, no decide. Configurado en `.codex/config.toml`. |
| Claude (Claude Code) | Edición del banco, operaciones de compilación y publicación | Trabaja bajo el manual `CLAUDE.md` y las skills de `.claude/skills/`. |

**El pipeline de compilación no usa inteligencia artificial.** Los scripts de
`scripts/` son Python determinista: el mismo banco produce siempre la misma salida.
La verificación de citas contra PubMed y Crossref es consulta a esas bases, no
inferencia de un modelo.

---

## Qué no hace la inteligencia artificial en esta obra

Estas prohibiciones no son promesas: están escritas en las instrucciones que
gobiernan cada sesión de trabajo (`CLAUDE.md`, `AGENTS.md`,
`.claude/skills/ghost/SKILL.md`) y varias las hace cumplir el compilador.

- **No genera imágenes.** Ninguna figura de este atlas fue generada, dibujada ni
  compuesta con IA. Todas provienen de Wikimedia Commons con archivo local, crédito,
  fuente, licencia y URL verificables. La ausencia de cualquiera de esos datos aborta
  la compilación.
- **No produce referencias.** Ninguna cita se escribe de memoria ni se acepta de un
  modelo sin verificar el PMID. Cada referencia se comprueba contra PubMed, y el DOI
  que PubMed devuelve debe coincidir con el declarado y con el que devuelve Crossref.
  Un DOI que Crossref no resuelve no se publica.
- **No aporta cifras clínicas.** Todo umbral, tasa o fórmula debe tener una fuente que
  lo diga exactamente. Si un modelo «recuerda» un dato, se trata como falso hasta
  probarlo en la fuente primaria.
- **No sustituye el consentimiento.** El consentimiento para escanear no es
  consentimiento para publicar: son dos «sí» distintos. Sin `consentimiento: obtenido`,
  un caso no se publica.
- **No autoriza publicaciones.** Preparar un borrador no equivale a aprobarlo. La
  validación estructural no demuestra revisión clínica.

---

## Qué decisiones no se delegan

La inteligencia artificial **no es autora** de esta obra y no puede serlo: no puede
asumir responsabilidad por lo que afirma.² No pierde una licencia profesional, no
responde ante un comité de ética y no comparece si una recomendación causa daño.

Quedan íntegramente a cargo del autor humano:

- La **tesis semiótica** del atlas y la estructura significante → significado → decisión.
- El **juicio clínico**: qué signo se enseña, con qué límites, y qué decisión se
  recomienda a partir de él.
- La **sección «dónde NO confiar»** de cada entrada, que es obligatoria.
- La **verificación final de cada cita** y la responsabilidad por el plagio.
- La **selección y revisión de cada imagen**, su atribución y su licencia.
- La **decisión de publicar**, y el consentimiento que la habilita.

---

## Confidencialidad

El procesamiento de contenido no publicado ocurre en la máquina del autor. Ningún
manuscrito confidencial de terceros se carga a servicios de inteligencia artificial.
Esto importa fuera de este proyecto: subir a un chatbot un manuscrito recibido para
arbitraje viola el acuerdo de confidencialidad en la mayoría de las revistas médicas.

---

## Cómo comprobarlo usted mismo

Esta declaración no pide que se le crea. El repositorio es público:

```bash
git clone https://github.com/alcyedmundo281/biosemiotics
cd biosemiotics
python -m pip install -r requirements.txt

python scripts/preflight.py          # integridad del banco
python scripts/verificar_citas.py    # cada PMID contra PubMed y Crossref
python scripts/verificar_publicacion.py
```

Una cita no declarada detiene la compilación. Las excepciones existen, pero exigen una
razón por escrito en `refs-sin-crossref.txt`; esa exención renuncia a la segunda
autoridad y obliga a confirmar el PMID a mano.

**Última corrida de verificación:** 22 de octubre de 2026 — **169 de 169**
referencias verificadas contra PubMed y Crossref, **cero exenciones declaradas**.
El banco contiene 52 entidades, de las cuales 49 están publicadas.

La corrida marcó además 32 variantes de título entre PubMed y Crossref con DOI
idéntico. Ninguna falla la verificación: el DOI coincidente es lo que prueba que se
trata del mismo artículo. Son subtítulos ausentes en uno de los registros, diferencias
de grafía y un caso con el título en inglés en PubMed y en polaco en Crossref. Se
revisan una por una; eso es criterio editorial, no automatización ciega.

Si encuentra un error, ábralo como *issue*. Es exactamente lo que esta declaración
pide.

---

## Qué ya falló

Este proyecto fue salvado de **tres referencias inventadas** por un modelo de
lenguaje. No las detectó una lectura atenta: las detectó la verificación automática
contra PubMed, que es la razón por la que esa verificación es obligatoria y bloquea
la compilación.

Se documenta aquí porque una declaración que solo enumera buenas prácticas no es
verificable. El modo de falla de estas herramientas no es razonar mal: es afirmar con
seguridad algo cuya procedencia no pueden sostener. El control existe porque el fallo
ocurrió.

---

## Notas

1. Liang W, Yuksekgonul M, Mao Y, Wu E, Zou J. GPT detectors are biased against
   non-native English writers. *Patterns*. 2023;4(7):100779.
   doi:10.1016/j.patter.2023.100779
2. ICMJE. *Recommendations for the Conduct, Reporting, Editing, and Publication of
   Scholarly Work in Medical Journals* — sección sobre inteligencia artificial.

---

*Este archivo se versiona con la obra. Su historial de cambios está en el repositorio.*
