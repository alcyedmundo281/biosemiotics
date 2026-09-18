# Codex con GPT-6 Astra

Este repositorio no integra una API de modelos. Astra asiste en edición,
investigación y mantenimiento; el pipeline Python sigue siendo determinista.

## Configuración

`.codex/config.toml` fija `model = "gpt-6-astra"` para este proyecto de confianza.
No fija esfuerzo de razonamiento: conserva la elección del usuario o de la app.
Si la selección anterior es `none` o `minimal`, selecciona `low` para Astra.
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
- No se encontró `biosemiotics-atlas` en las skills de Codex; el directorio
  personal de skills de Claude no existe en este equipo. Su material exclusivo
  sigue pendiente de localizar.

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

## Reversión

Retira solo la línea `model` de `.codex/config.toml` para volver al modelo
heredado y abre una sesión nueva. Conserva `AGENTS.md` si deseas seguir usando
Codex con otro modelo. Para retirar toda la integración, revierte el commit de
migración mediante un PR normal, sin reset destructivo ni cambios al contenido.

## Documentación oficial consultada

- [GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model)
- [Instrucciones AGENTS.md](https://developers.openai.com/es-419/docs/agent-configuration/agents-md)
- [Configuración de Codex](https://developers.openai.com/es-419/docs/config-file/config-reference)
