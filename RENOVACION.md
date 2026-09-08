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

**Estado:** cerrado. [PR #69](https://github.com/alcyedmundo281/biosemiotics/pull/69)
fusionado con CI correcta; merge `3e9af32`.

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

**Estado:** cerrado. [PR #70](https://github.com/alcyedmundo281/biosemiotics/pull/70)
fusionado con CI correcta; merge `bfe3957`.

- **Problema:** un fallo de red puede producir una CI verde sin verificación.
- **Cambio:** usar verificación estricta como requisito de integración;
  reintentos acotados y diferenciar error bibliográfico de servicio no disponible.
- **Loop:** simular timeout, 429, 5xx, DOI inexistente y duplicados → comprobar
  estados de salida → integrar el bloqueo en CI.
- **Cierre:** verde solo con verificación completa o exención explícita ya
  revisada; un servicio caído deja el PR pendiente/fallido, nunca aprobado.
- **Nota:** la identidad PMID/DOI no demuestra que una cifra esté en el artículo;
  se mantiene la revisión humana de la evidencia clínica.
- **Implementación:** modo estricto por defecto, alias `--estricto` compatible;
  máximo de tres intentos por consulta, esperas de 1 y 2 segundos y parada al
  agotarse Crossref. Código 1 para datos/discrepancias y 2 para servicio no
  disponible; ninguno se presenta como éxito. Bibliografía vacía, incompleta o
  con claves duplicadas se rechaza antes de consultar la red.
- **Exenciones:** razón obligatoria, claves existentes o prefijo de registrador
  acotado; solo 404 y solo con PubMed coherente. No se añaden exenciones al banco.
- **Integración:** el control obligatorio existente depende también de citas en
  PR/manual/semanal y falla si se cancela u omite un requisito. Push a `main`
  conserva la comprobación local sin repetir la red. Citas tiene timeout de 10 min.
- **Evidencia:** 73 pruebas, incluidas simulaciones sin red de timeout, 429, 503,
  recuperación, 403, 404, JSON inválido, claves duplicadas y exenciones.
  Verificación real: 137/137 referencias correctas en PubMed y Crossref, sin exenciones.

## Ciclo 5 — Corregir rutas y comandos de uso diario

**Estado:** cerrado. [PR #72](https://github.com/alcyedmundo281/biosemiotics/pull/72)
fusionado con CI correcta; merge `af9b752`.

- **Problema:** `consultas.py` busca la base bajo `scripts/build/`.
- **Cambio:** centralizar raíz, salidas y argumentos; revisar `--raiz`,
  `--destino`, `--proyecto` y `--salida` sin ampliar permisos de borrado.
- **Loop:** ejecutar comandos desde distintos directorios → reproducir fallos →
  unificar rutas → comprobar errores claros cuando falta una compilación.
- **Cierre:** comandos documentados funcionales en Windows y Linux; base única.
- **Implementación:** `rutas.py` fija la raíz por ubicación del repositorio y
  resuelve artefactos relativos desde ella. `--raiz` queda disponible en los
  comandos diarios; `indice.py` y `atlas.py` conservan la raíz posicional como
  transición. `consultas.py` y `senuelo.py` comparten `build/atlas.db` y aceptan
  `--db`; `nuevo.py` deja de escribir según el directorio actual.
- **Contrato:** una raíz explícita relativa se interpreta desde el directorio
  actual; destino/proyecto/salida/db relativos, desde la raíz. Las rutas absolutas
  se respetan. Falta de raíz o base produce un error con ruta y acción sugerida.
- **Seguridad:** no cambia `validar_destino()` ni se amplía el área reemplazable
  de Quarto. La compatibilidad posicional no puede combinarse con `--raiz`.
- **Evidencia:** 82 pruebas en Windows, incluidas las 15 interfaces diarias y
  ejecuciones desde la raíz,
  `scripts/` y un directorio externo; los mismos casos son portables a Linux.

## Ciclo 6 — Separar responsabilidades del código

**Estado:** cerrado mediante el
[PR #73](https://github.com/alcyedmundo281/biosemiotics/pull/73), con CI correcta.

- **Cambio:** extraer carga, esquema/validación, bibliografía y configuración
  a módulos comunes; dejar los scripts como interfaces de comandos.
- **Loop:** fijar salidas de referencia → extraer un módulo por PR → comparar
  contenido y metadatos → conservar interfaces existentes.
- **Cierre:** menos duplicación sin cambios editoriales; citas y orden de fichas
  idénticos. No introducir una base remota ni otro framework sin necesidad demostrada.
- **Implementación:** `banco.py` concentra carga y estados; `validacion.py`, el
  contrato editorial y la trazabilidad; `bibliografia.py`, la resolución de
  citas; `configuracion.py`, las taxonomías y el orden canónico. `build.py`
  queda como orquestador de SQLite, grafo y Ghost y reexporta su API histórica.
  Los demás comandos importan directamente el módulo que necesitan.
- **Evidencia local:** 84 pruebas; `build.py` pasa de 663 a 172 líneas. Las
  huellas de `atlas-inject.html`, `grafo.json` y los 42 artículos Ghost-ready
  son idénticas a las previas; `index.json` coincide con el blob versionado.

## Ciclo 7 — Hacer verificable todo el flujo editorial

**Estado:** cerrado mediante el
[PR #74](https://github.com/alcyedmundo281/biosemiotics/pull/74), con CI correcta.

- **Cambio:** alinear README, LEEME y CLAUDE con `.qmd`, Quarto y rutas reales;
  documentar dependencias reproducibles y un comando de preflight.
- **Loop:** seguir el instructivo desde un entorno limpio → resolver cada
  divergencia → verificar todos los formatos y errores de entrada.
- **Cierre:** onboarding reproducible, huella del cuerpo Ghost y registro de
  publicación, índices coherentes y pruebas de regresión de los ciclos 1–6.
- **Revisión adicional:** comprobar si el JATS generado cumple el uso de depósito
  que se anuncia; completar referencias y formato o documentar su alcance real.
- **Implementación:** README, LEEME y CLAUDE describen las fuentes `.qmd`, las
  rutas y comandos actuales. `requirements.txt` fija PyYAML y
  `preflight.py` comprueba entorno, contrato editorial, índice y publicación;
  el perfil `--publicacion` exige también toda la toolchain de EPUB/PDF.
- **Trazabilidad:** cada ficha del índice registra `ghost_sha256`, calculado
  por el mismo render puro que genera el cuerpo Ghost. La verificación de
  publicación vuelve a calcularlo y bloquea cualquier deriva.
- **JATS:** la revisión mostró que el XML no declara DTD, no expande las
  referencias y no valida un perfil de repositorio. Se conserva como XML
  experimental de intercambio, marcado como material educativo, y se retira
  toda afirmación de que esté listo para depósito.
- **Evidencia local:** 92 pruebas; preflight correcto para 43 entidades y 186
  relaciones; índice coherente con 41 URLs; huella global de los 42 cuerpos
  Ghost idéntica a la del ciclo 6.

## Registro de ejecución

| Ciclo | Rama / PR | Evidencia | Estado |
|---|---|---|---|
| 1 | [PR #67](https://github.com/alcyedmundo281/biosemiotics/pull/67), `codex/renovacion-ciclo-1` | 44 pruebas; CI correcta | Cerrado, merge `9164198` |
| 2 | [PR #68](https://github.com/alcyedmundo281/biosemiotics/pull/68), `codex/renovacion-ciclo-2` | 52 pruebas; CI correcta | Cerrado, merge `913e09e` |
| 3 | [PR #69](https://github.com/alcyedmundo281/biosemiotics/pull/69), `codex/renovacion-ciclo-3` | 59 pruebas; CI correcta | Cerrado, merge `3e9af32` |
| 4 | [PR #70](https://github.com/alcyedmundo281/biosemiotics/pull/70), `codex/renovacion-ciclo-4` | 73 pruebas; CI correcta | Cerrado, merge `bfe3957` |
| 5 | [PR #72](https://github.com/alcyedmundo281/biosemiotics/pull/72), `codex/renovacion-ciclo-5` | 82 pruebas; comandos desde raíz, scripts y directorio externo | Cerrado, merge `af9b752` |
| 6 | [PR #73](https://github.com/alcyedmundo281/biosemiotics/pull/73), `codex/renovacion-ciclo-6` | 84 pruebas; derivados y API histórica sin cambios | Cerrado; integración registrada en el PR |
| 7 | [PR #74](https://github.com/alcyedmundo281/biosemiotics/pull/74), `codex/renovacion-ciclo-7` | 92 pruebas; preflight, huellas Ghost y documentación verificadas | Cerrado; integración registrada en el PR |

## Trabajo editorial conservado

La imagen y metadatos de disfunción diastólica se guardaron en
`codex/publicacion-diastolica`, commit `c021feb`. El cierre de esa publicación
(URL definitiva, derivados y PR apilados) sigue siendo una tarea separada y
no debe perderse al renovar el código.
