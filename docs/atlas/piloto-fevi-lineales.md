# Piloto editorial: FEVI por métodos lineales

Estado: borrador para revisión de Alcy; no aprobado ni publicado.
Fuente: [ficha .qmd](../../signos/fevi-lineales.qmd).
Fecha de consulta de evidencia: 2026-09-18.

## Autoría y configuración

La ficha conserva el nombre, ORCID y afiliación usados en `fevi-simpson.qmd`,
coherentes con la identidad de `CITATION.cff`. No atribuye una revisión clínica
ya realizada ni registra una fecha de aprobación. Alcy decide la aceptación
y atribución final del borrador asistido.

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
| Solicitar revisión y explicitar el método | Propuesta editorial del atlas | Pendiente de valoración de Alcy; no se presenta como recomendación terapéutica derivada de un ensayo |

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

## Revisión pendiente

1. Aprobar o corregir el enfoque: reconocer límites de medidas lineales, sin
   enseñar Teichholz como sustituto clínico de la cuantificación volumétrica.
2. Revisar la propuesta de decisión para primer contacto y su redacción.
3. Seleccionar un loop docente o figura con procedencia/licencia verificable.
   `medios: []` declara que esta versión no los tiene; no se ha fabricado evidencia.
4. Si se desea desarrollar la ecuación de Teichholz, cotejar su escritura y
   unidades en el texto original antes de ampliar el artículo.

La bibliografía y la estructura se comprueban con las herramientas del proyecto;
eso no sustituye esta revisión clínica. La ficha permanece excluida de Ghost,
índice público y libro mientras esté en `estado: borrador`.
