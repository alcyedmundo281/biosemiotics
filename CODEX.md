# Codex con GPT-6 Astra

Este repositorio no integra una API de modelos. Astra asiste en edición,
investigación y mantenimiento; el pipeline Python sigue siendo determinista.

## Configuración

`.codex/config.toml` fija `model = "gpt-6-astra"` para este proyecto de confianza.
Fija `model_reasoning_effort = "high"` como elección del proyecto para el trabajo
de investigación y revisión editorial. Es una configuración de trabajo, no una
garantía de exactitud clínica. Puedes elegir un esfuerzo menor para tareas simples.
No modifica credenciales, proveedor, sandbox ni permisos globales.

Abre una sesión nueva en este repositorio y comprueba el modelo efectivo en el
selector de la app. Un override explícito de la sesión puede prevalecer sobre
el archivo. En CLI se puede seleccionar expresamente con
`codex -m gpt-6-astra`. La existencia del archivo no demuestra que una sesión
anterior cambió de modelo ni que la cuenta tiene acceso.

`AGENTS.md` es la entrada breve; requiere leer el manual compartido `CLAUDE.md`.
No se copia el manual entero a las instrucciones automáticas: supera los 32 KiB
del presupuesto predeterminado de descubrimiento de Codex.

## Entorno y comprobaciones

En PowerShell:

```powershell
. ./activar-entorno.ps1
python scripts/preflight.py
python -m unittest discover -s tests
python scripts/verificar_publicacion.py
```

El modo UTF-8 también se hereda en los subprocesos. Sin él, Windows puede usar
CP1252 y provocar errores de impresión y decodificación ajenos a Astra.

Para contenido y publicación, ejecuta los comandos del manual en su rol
correspondiente. Antes de producir EPUB/PDF/LaTeX, usa
`python scripts/preflight.py --publicacion`. El entorno reproducible completo
está en `.github/workflows/epub.yml`.

## Registro de migración (2026-09-18)

Base local: `4d9a582e4feed814456da32b0b6d8d90e7e4fca8`.
No existía configuración Codex en el proyecto ni un modelo anterior fijado aquí.

- Línea base con UTF-8: 92 pruebas correctas, preflight correcto y publicación
  coherente (46 entidades, 45 URLs).
- Tras integrar `origin/main`: 103 pruebas correctas, preflight y compilación
  del banco correctos. El TOML se analiza correctamente y
  `codex debug prompt-input` confirma que se descubre el nuevo `AGENTS.md`.
- Sin UTF-8: preflight falla por CP1252 y la suite registra un fallo y cinco
  errores. Se usa el activador existente; no requiere cambios del pipeline.
- Herramientas disponibles en PATH: GitHub CLI, Codex, Python del venv,
  Quarto y Java.
- Preflight editorial bloqueado localmente: faltan LuaLaTeX, rsvg-convert y
  EPUBCheck. La validación completa debe quedar acreditada en CI antes del uso
  editorial de la migración.
- El material de `biosemiotics-atlas`, aportado posteriormente por el usuario,
  está incorporado y actualizado en [docs/atlas/README.md](docs/atlas/README.md).
  No hace falta instalar una skill ni conservar el paquete externo.

## Piloto y criterios de adopción

La configuración y las pruebas del repositorio no sustituyen un piloto del
modelo efectivo. En una sesión confirmada como Astra, evaluar secuencialmente:

1. Corrección documental: mantener el contrato y producir un diff limitado.
2. Mantenimiento Python: resolver una incidencia real y pasar sus pruebas,
   conservando compatibilidad 3.9. No introducir una modificación artificial
   solo para tener un piloto.
3. Borrador basado en fuentes: respetar la oleada, citar evidencia comprobada,
   mantenerlo como borrador y someterlo a revisión clínica.

Registrar tarea, modelo/esfuerzo efectivos, tiempo, correcciones del revisor y
resultado de las comprobaciones. Si hay una sesión de referencia disponible,
comparar las mismas tareas. No se ha medido todavía una mejora de calidad,
costo o latencia. Para adoptar el flujo editorial se requieren las pruebas
aplicables en verde, ninguna referencia ni metadato inventado y revisión clínica.

## Trabajo del próximo tema

Según el mapa al 2026-09-18, sigue FEVI por métodos lineales (Teichholz y FA),
cardiovascular/corazon, nivel intermedio, dentro de la oleada 3. Comprueba de
nuevo el mapa al comenzar: este párrafo no es una segunda cola de prioridades.

1. Abrir una sesión en el proyecto, confirmar Astra y leer AGENTS, el manual,
   el mapa y la guía incorporada. Activar UTF-8 y ejecutar preflight.
2. Revisar las fichas existentes de eyeball y Simpson, Modo M y cuantificación.
   Delimitar qué pregunta educativa resolverá la nueva ficha, sin duplicarlas.
3. Buscar fuentes primarias en PubMed; comprobar DOI/Crossref y preparar una
   tabla afirmación → fuente → pasaje o dato comprobado. Marcar las lagunas;
   no completar fórmulas, umbrales o decisiones clínicas de memoria.
4. Preparar el `.qmd` en `estado: borrador`, URL vacía, con abstract, ocho
   secciones del signo, relaciones, límites y medios con licencia comprobada.
5. Validar estructura y referencias, y entregar a Alcy el borrador junto con
   la tabla de evidencia y las decisiones clínicas que requieren su revisión.
   La condición de borrador permite incompletitud: un build correcto no basta;
   revisar también las alertas de la ficha antes de presentarla como completa.
6. Tras aprobación editorial, aplicar el cambio de estado y el flujo proveedor.
   Publicar en Ghost solo cuando esté autorizado, registrar sus datos reales y
   completar el traspaso publicador/proveedor y los derivados del manual.

Solicitud de arranque sugerida:

> Prepara el borrador del siguiente tema del mapa: FEVI por métodos lineales
> (Teichholz y fracción de acortamiento). Sigue la guía incorporada, verifica
> fuentes y presenta la tabla de evidencia junto al artículo para mi revisión.
> Mantén el estado borrador y no publiques en Ghost.

## Reversión

Retira las líneas `model` y `model_reasoning_effort` de `.codex/config.toml`
para volver a la configuración heredada y abre una sesión nueva. Conserva
`AGENTS.md` si deseas seguir usando
Codex con otro modelo. Para retirar toda la integración, revierte el commit de
migración mediante un PR normal, sin reset destructivo ni cambios al contenido.

## Documentación oficial consultada

- [GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model)
- [Instrucciones AGENTS.md](https://developers.openai.com/es-419/docs/agent-configuration/agents-md)
- [Configuración de Codex](https://developers.openai.com/es-419/docs/config-file/config-reference)
