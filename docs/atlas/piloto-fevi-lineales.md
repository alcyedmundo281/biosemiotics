# Piloto editorial: FEVI por métodos lineales

Estado: revisado; publicación autorizada por Alcy el 2026-09-18 mediante
la solicitud expresa de publicar este borrador en Ghost y cerrar el flujo.
Fuente: [ficha .qmd](../../signos/fevi-lineales.qmd).
Fecha de consulta de evidencia: 2026-09-18.

## Autoría y configuración

La ficha conserva el nombre, ORCID y afiliación usados en `fevi-simpson.qmd`,
coherentes con la identidad de `CITATION.cff`. La aceptación editorial y la
fecha registrada se fundamentan en la instrucción expresa de Alcy de publicar
este borrador. No se afirma una revisión clínica independiente adicional.

Configuración del proyecto: `gpt-6-astra`, esfuerzo `high`, `AGENTS.md` y guía
local. Esto acredita los archivos de configuración, no una medición independiente
del modelo efectivo de la sesión ni una comparación de rendimiento entre modelos.
No se abrió otra tarea ni se midieron costo o latencia del modelo.

## Evidencia y decisiones editoriales

| Afirmación o elemento | Fuente y localización | Alcance de la comprobación |
|---|---|---|
| Adquisición lineal, definición de FA y FEVI, límites regionales | Lang 2015, apartados 1.1, 2, 2.1 y 2.2; pp. 3, 6–7 | Texto completo de la guía consultado; fórmula de FA expresada a partir de la definición general de cambio relativo |
| Recomendación sobre Teichholz y alternativa volumétrica | Lang 2015, apartados 1.2 y 2.2; pp. 3 y 7 | Recomendación de consenso, no ensayo de tratamientos |
| Limitación histórica de Teichholz con asinergia | Teichholz 1976, abstract | Consultado el abstract; no se declara lectura del artículo completo |
| DD 5 cm, DS 3,5 cm, FA 30 % | Cálculo didáctico propio | Valores ficticios, no rango normal ni observación clínica |
| Solicitar revisión y explicitar el método | Propuesta editorial del atlas | Aceptada dentro de la solicitud de publicación; no se presenta como recomendación terapéutica derivada de un ensayo |

Fuentes comprobadas:

- Lang et al. 2015: [PubMed, PMID 25559473](https://pubmed.ncbi.nlm.nih.gov/25559473/),
  [texto completo ASE](https://www.asecho.org/wp-content/uploads/2016/02/2015_ChamberQuantificationREV.pdf),
  DOI `10.1016/j.echo.2014.10.003`; clave existente `lang2015`.
- Teichholz et al. 1976: [PubMed, PMID 1244736](https://pubmed.ncbi.nlm.nih.gov/1244736/),
  DOI `10.1016/0002-9149(76)90491-4`; incorporada como `teichholz1976`
  mediante `scripts/refs.py`, sin redactar manualmente la entrada bibliográfica.

El abstract histórico presenta la ecuación volumétrica con tipografía ambigua.
No se transcribe como receta de cálculo sin cotejar el original. El borrador
explica el método y sus límites; la FA sí incluye definición y ejemplo.
No se añaden rangos normales, puntos de corte terapéuticos ni indicaciones de
fluidos o inotrópicos que esta búsqueda no ha sustentado.

## Cierre de revisión y alcance aprobado

La solicitud de publicación de Alcy acepta el borrador existente: reconocer
los límites de las medidas lineales y distinguir FA de FEVI. La fase proveedora
retira la nota provisional sobre un loop pendiente; conserva las afirmaciones,
referencias y decisiones clínicas. La fase publicadora aportará la figura
final con procedencia y licencia, sin simular una adquisición clínica.

No se amplía el artículo con la ecuación volumétrica de Teichholz ni con
umbrales terapéuticos. La bibliografía y la estructura se comprueban con las
herramientas del proyecto; esas comprobaciones no sustituyen la responsabilidad
clínica y editorial de Alcy. El estado revisado permite generar el cuerpo
canónico; el estado publicado se registrará solo tras la confirmación de Ghost.
