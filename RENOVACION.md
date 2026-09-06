# Renovación gradual de biosemiotics

Plan iniciado el 6 de septiembre de 2026, a partir de la revisión de `fa48911`.
Se conserva el banco `.qmd`, Quarto y Ghost. Cada ciclo resuelve un riesgo
concreto y deja un resultado verificable antes de comenzar el siguiente.

## Loop común de cada ciclo

1. **Observar:** actualizar desde GitHub, comprobar rama, estado y worktree;
   identificar el fallo con una reproducción pequeña y guardar el trabajo ajeno.
2. **Delimitar:** fijar alcance, contrato esperado y criterio de cierre.
3. **Reproducir:** añadir una prueba que detecte el comportamiento incorrecto.
4. **Corregir:** implementar el cambio mínimo en una rama propia y un PR pequeño.
5. **Verificar:** ejecutar las pruebas relevantes, integridad y derivados afectados.
   Revisar el diff; no cambiar datos clínicos para hacer pasar una prueba.
6. **Integrar:** esperar toda la CI, fusionar con merge real, volver a `main`,
   actualizar y podar referencias. Registrar evidencia y pendientes aquí.
7. **Evaluar:** si el contrato no se cumple, volver al paso 3. Si se cumple,
   cerrar el ciclo; comenzar el siguiente cuando Alcy lo indique.

La reversión de código se hace con un PR de revert. Los archivos de `build/`
se regeneran desde fuentes; nunca se reparan a mano. La publicación en Ghost
mantiene su flujo separado de proveedor/publicador en `CLAUDE.md`.

## Ciclo 1 — Proteger la generación Quarto

**Estado:** cerrado. [PR #67](https://github.com/alcyedmundo281/biosemiotics/pull/67)
fusionado con CI correcta; merge `9164198`.

- **Problema:** `qmd.generar()` elimina el destino sin delimitar su alcance.
  Un destino erróneo puede ser la raíz o una carpeta de fuentes.
- **Cambio:** permitir únicamente subdirectorios del `build/` real; rechazar
  enlaces y junctions; no reemplazar directorios ajenos. Reconocer proyectos
  por marcador, con transición para el proyecto histórico `build/quarto/`.
- **Loop:** probar destinos peligrosos → bloquearlos antes de escribir →
  ensamblar en temporal → intercambiar directorios → restaurar ante fallo.
- **Pruebas:** raíz, fuentes, escapes con `..`, enlaces, archivo como destino,
  directorio ajeno, regeneración válida, migración y fallos durante el intercambio.
- **Cierre:** fuentes intactas, proyecto anterior recuperable ante error,
  pruebas Python 3.9/3.13 y CI editorial correctas.
- **Límite:** protege la fase de ensamblado, no convierte el render posterior
  en una transacción ni coordina procesos concurrentes o cortes eléctricos.
- **Recuperación:** si falla también la restauración, conservar el directorio
  `.quarto-*/anterior` en el padre del destino y recuperarlo tras resolver el bloqueo.

## Ciclo 2 — Hacer obligatorias las reglas editoriales

**Estado:** cerrado. [PR #68](https://github.com/alcyedmundo281/biosemiotics/pull/68)
fusionado con CI correcta; merge `913e09e`.

- **Problema:** faltas clínicas/semióticas solo generan alertas; no se exige
  consistentemente abstract ni secciones obligatorias.
- **Cambio:** contrato por tipo de entidad; distinguir borrador incompleto de
  contenido publicable. Validar antes de generar cualquier salida pública.
- **Loop:** inventariar incumplimientos actuales → probar fichas inválidas →
  aplicar bloqueo → corregir datos solo con fuentes y revisión clínica.
- **Cierre:** ninguna ficha publicable sin referencias, abstract, límites y
  campos obligatorios; errores accionables con archivo y campo.
- **Reversión:** revertir el cambio de código; nunca relajar reglas silenciosamente.
- **Implementación:** contrato común en `build.py`, aplicado también a Ghost,
  índice/JSON-LD/JATS, atlas HTML y Quarto antes de escribir. `--solo db|grafo`
  permite trabajar fichas incompletas sin URL ni marca de publicación, con alertas.
- **Inventario:** 43 fichas. Se añade a ecogenicidad una referencia ya existente
  (`hangiandreou2003`), se separa un párrafo existente bajo el encabezado faltante
  en derrame pericárdico y se añaden preguntas de discusión en neumotórax y riñón
  crónico. No cambian umbrales ni decisiones clínicas; índice regenerado.
- **Evidencia:** 52 pruebas; generación Quarto de las 41 fichas con URL;
  137/137 referencias verificadas en PubMed y Crossref con `--estricto`.
- **Límite:** validación estructural, no revisión clínica automatizada. El caso
  pendiente conserva su estado; la elegibilidad y consentimiento se unifican
  en el ciclo 3. Los conceptos conservan estructura libre de encabezados.

## Ciclo 3 — Unificar publicación y consentimiento

**Estado:** implementado. CI e integración registradas en el
[PR #69](https://github.com/alcyedmundo281/biosemiotics/pull/69).
El ciclo queda cerrado cuando ese PR se fusione con todos sus checks correctos.

- **Problema:** el libro selecciona por `url`; SQLite y consentimiento usan
  `publicado`. El mismo caso puede tener estados contradictorios.
- **Cambio:** definir una función común de elegibilidad y estados explícitos
  de borrador, revisado y publicado; migración compatible del banco.
- **Loop:** probar contradicciones → decidir autoridad del estado → migrar →
  comprobar SQLite, índice, libro y casos con consentimiento pendiente.
- **Cierre:** selección coherente en todas las salidas; ningún caso público
  sin consentimiento obtenido. Fecha de revisión y Ghost ID quedan trazables.
- **Migración:** 41 fichas con URL → `publicado`; disfunción diastólica →
  `revisado`, por la aprobación editorial previa de Alcy; caso de disnea →
  `borrador`, con consentimiento pendiente. No se modifican cuerpos ni citas.
- **Contrato:** `estado_publicacion()` valida estado, URL, booleano legado,
  consentimiento y formato de trazabilidad. `seleccionar_publicables()` decide
  el alcance de Ghost, índice, atlas y Quarto (incluidos EPUB/PDF). Un caso
  revisado/publicado sin consentimiento falla antes de escribir, incluso cuando
  el filtro de edición podría excluirlo.
- **Trazabilidad:** se añaden `fecha_revision` y `ghost_id` a fuente, SQLite e
  índice. En la migración quedan `null`: no constan en las fuentes históricas.
  Completar con evidencia en futuras revisiones/publicaciones; no inventar fechas
  ni mezclar aquí el cierre pendiente de Ghost de disfunción diastólica.
- **Evidencia:** 59 pruebas; SQLite conserva 43 fichas y deriva 41 publicadas;
  índice/Ghost contienen 42; Quarto publicado contiene 41. El caso pendiente
  queda fuera del índice, Ghost-ready, atlas y libro. JSON-LD/JATS anteriores
  se retiran al devolver una ficha a borrador.
- **Límites:** SQLite y grafo son salidas locales de trabajo y conservan borradores.
  Regenerar no retira artículos de Ghost ni ediciones ya archivadas. La aprobación
  clínica y el consentimiento real siguen siendo responsabilidad editorial.

## Ciclo 4 — No aprobar citas sin verificar

**Estado:** pendiente.

- **Problema:** un fallo de red puede producir una CI verde sin verificación.
- **Cambio:** usar verificación estricta como requisito de integración;
  reintentos acotados y diferenciar error bibliográfico de servicio no disponible.
- **Loop:** simular timeout, 429, 5xx, DOI inexistente y duplicados → comprobar
  estados de salida → integrar el bloqueo en CI.
- **Cierre:** verde solo con verificación completa o exención explícita ya
  revisada; un servicio caído deja el PR pendiente/fallido, nunca aprobado.
- **Nota:** la identidad PMID/DOI no demuestra que una cifra esté en el artículo;
  se mantiene la revisión humana de la evidencia clínica.

## Ciclo 5 — Corregir rutas y comandos de uso diario

**Estado:** pendiente.

- **Problema:** `consultas.py` busca la base bajo `scripts/build/`.
- **Cambio:** centralizar raíz, salidas y argumentos; revisar `--raiz`,
  `--destino`, `--proyecto` y `--salida` sin ampliar permisos de borrado.
- **Loop:** ejecutar comandos desde distintos directorios → reproducir fallos →
  unificar rutas → comprobar errores claros cuando falta una compilación.
- **Cierre:** comandos documentados funcionales en Windows y Linux; base única.

## Ciclo 6 — Separar responsabilidades del código

**Estado:** pendiente.

- **Cambio:** extraer carga, esquema/validación, bibliografía y configuración
  a módulos comunes; dejar los scripts como interfaces de comandos.
- **Loop:** fijar salidas de referencia → extraer un módulo por PR → comparar
  contenido y metadatos → conservar interfaces existentes.
- **Cierre:** menos duplicación sin cambios editoriales; citas y orden de fichas
  idénticos. No introducir una base remota ni otro framework sin necesidad demostrada.

## Ciclo 7 — Hacer verificable todo el flujo editorial

**Estado:** pendiente.

- **Cambio:** alinear README, LEEME y CLAUDE con `.qmd`, Quarto y rutas reales;
  documentar dependencias reproducibles y un comando de preflight.
- **Loop:** seguir el instructivo desde un entorno limpio → resolver cada
  divergencia → verificar todos los formatos y errores de entrada.
- **Cierre:** onboarding reproducible, huella del cuerpo Ghost y registro de
  publicación, índices coherentes y pruebas de regresión de los ciclos 1–6.
- **Revisión adicional:** comprobar si el JATS generado cumple el uso de depósito
  que se anuncia; completar referencias y formato o documentar su alcance real.

## Registro de ejecución

| Ciclo | Rama / PR | Evidencia | Estado |
|---|---|---|---|
| 1 | [PR #67](https://github.com/alcyedmundo281/biosemiotics/pull/67), `codex/renovacion-ciclo-1` | 44 pruebas; CI correcta | Cerrado, merge `9164198` |
| 2 | [PR #68](https://github.com/alcyedmundo281/biosemiotics/pull/68), `codex/renovacion-ciclo-2` | 52 pruebas; CI correcta | Cerrado, merge `913e09e` |
| 3 | [PR #69](https://github.com/alcyedmundo281/biosemiotics/pull/69), `codex/renovacion-ciclo-3` | 59 pruebas; 43 fichas locales, 42 elegibles, 41 publicadas | Implementado; cierre por merge del PR con CI correcta |

## Trabajo editorial conservado

La imagen y metadatos de disfunción diastólica se guardaron en
`codex/publicacion-diastolica`, commit `c021feb`. El cierre de esa publicación
(URL definitiva, derivados y PR apilados) sigue siendo una tarea separada y
no debe perderse al renovar el código.
