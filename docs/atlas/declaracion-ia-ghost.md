---
tipo: pagina_ghost
titulo: Uso de inteligencia artificial
slug: ia
url: https://www.biosemiotics.net/ia/
ghost_id: 6ada9401a45f8b0001223b62
fecha_revision: 2026-10-30
---

En la preparación de este atlas se usó asistencia de inteligencia artificial. Esta página declara qué herramientas, en qué etapas, y qué decisiones no se delegaron.

La pregunta «¿usó IA?» no tiene respuesta verificable: el uso no se puede detectar, y los detectores disponibles clasifican falsamente como generado por máquina más de la mitad de los textos escritos por autores cuya lengua materna no es el inglés. La pregunta que sí se puede responder es si cada afirmación es rastreable hasta su fuente. Eso es lo que este proyecto se compromete a sostener.

## Qué se usó, y dónde

**Codex (GPT-6 Astra)** y **Claude** asisten en la redacción, la búsqueda bibliográfica y el mantenimiento del código. Proponen; no deciden.

El pipeline que compila el atlas **no usa inteligencia artificial**: es Python determinista, y la verificación de citas es una consulta a PubMed y Crossref, no la inferencia de un modelo.

## Qué no hace la inteligencia artificial aquí

- **Ninguna imagen fue generada con IA.** Todas vienen de Wikimedia Commons, con crédito, fuente y licencia verificables. Si falta cualquiera de esos datos, la compilación se detiene.
- **Ninguna referencia procede de un modelo.** Cada PMID se verifica contra PubMed, y su DOI debe coincidir con el que devuelve Crossref. Un DOI que Crossref no resuelve no se publica.
- **Ninguna cifra clínica se acepta sin fuente** que la diga exactamente.
- **Los casos son sintéticos.** No se usan historias clínicas ni datos de personas reales. Se declaran como viñetas docentes; las imágenes de Commons son ilustraciones independientes, no estudios del paciente ficticio. El consentimiento se exigirá si se incorpora un caso real.

## Qué no se delega

La inteligencia artificial no es autora de esta obra y no puede serlo: no puede asumir responsabilidad. El juicio clínico, los límites de cada signo, la sección «dónde no confiar», la verificación final de cada cita y la decisión de publicar son del autor.

## Cómo comprobarlo

El repositorio es público y la verificación se puede ejecutar: [github.com/alcyedmundo281/biosemiotics](https://github.com/alcyedmundo281/biosemiotics)

La declaración completa, con los comandos y el historial de cambios, está en el archivo [AI-USE.md](https://github.com/alcyedmundo281/biosemiotics/blob/main/AI-USE.md).

Si encuentra un error, ábralo como *issue*. Es exactamente lo que esta declaración pide.

---

Alcy Edmundo Torres Guerrero · [ORCID 0000-0002-9742-375X](https://orcid.org/0000-0002-9742-375X)
