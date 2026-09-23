# Instrucciones para Codex — biosemiotics

Este atlas educativo de POCUS se escribe en español para el médico de primer
contacto. Alcy conserva la responsabilidad clínica y editorial.

## Antes de trabajar

- Lee completo `CLAUDE.md`: es el manual compartido, también para Codex.
- Lee `mapa-maestro-biosemiotics.md` para el orden y la taxonomía del contenido.
- Comprueba `git status` y `git worktree list`; conserva el trabajo ajeno.
- En PowerShell, ejecuta `. ./activar-entorno.ps1` para activar Python y UTF-8.
- Ejecuta `python scripts/preflight.py` y comunica fallos previos al cambio.
- Para configurar Astra, validar la migración o revertirla, lee `CODEX.md`.

## Contrato que debe conservarse

- Los `.qmd` son la fuente de verdad. Corrige la fuente y regenera los derivados;
  no edites `build/` a mano. Solo se versionan `build/index.json` y
  `build/atlas-inject.html`.
- No inventes cifras, PMID, DOI, URLs, fechas de revisión ni identificadores de
  Ghost. Verifica las referencias con PubMed y Crossref según el manual.
- Conserva significante → significado → decisión, los encabezados obligatorios,
  abstract de 40–80 palabras y límites/falsos positivos. Escribe en español claro.
- Conserva `borrador`, `revisado` y `publicado` con sus requisitos. La validación
  estructural no demuestra revisión clínica ni consentimiento para publicar.
- Las imágenes requieren archivo local, fuente, crédito y licencia verificables,
  y vienen SOLO de Wikimedia Commons: nunca generadas con IA.
- Para publicar en Ghost usa la skill `.agents/skills/ghost/`: publicación nueva
  en web y por email a los suscriptores, y pie canónico pegado una sola vez.
- Mantén Python 3.9+, Quarto y LuaLaTeX, y las verificaciones existentes.
- Usa el worktree principal y una rama por unidad de trabajo. Para publicación,
  respeta los roles secuenciales y PR apilados del manual: el publicador no
  regenera el índice; el proveedor lo hace tras congelar el PR padre.

## Alcance, permisos y verificación

Completa el trabajo autorizado y reversible sin repetir preguntas ya resueltas.
Prepara un resultado revisable antes de solicitar una decisión que realmente
falte. Una solicitud de plan no autoriza editar, publicar ni fusionar.
La publicación requiere la autorización aplicable del usuario; preparar un
borrador no equivale a aprobarlo. No amplíes permisos ni copies las reglas de
`.claude/settings.local.json` a Codex.

Prueba lo que corresponda al cambio. Para Python usa
`python -m unittest discover -s tests`; para contenido sigue las comprobaciones
del manual. No repitas pruebas correctas sin cambios o evidencia nueva. Distingue
pruebas ejecutadas, fallos previos y verificaciones pendientes por herramientas.

La guía de `biosemiotics-atlas` está incorporada en `docs/atlas/README.md` y sus
referencias locales. Consúltalas al crear o revisar entidades. No depende de
una skill instalada ni de archivos en Descargas. Usa las plantillas actuales
de `assets/` y `scripts/validacion.py` para comprobar el contrato; la guía
documenta las diferencias del paquete antiguo y los límites del XML.
