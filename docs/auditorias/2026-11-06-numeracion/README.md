# Congelación de numeración 1–56

La única entrada de asignación fue `propuesta-numeracion.csv`, aprobado por Alcy e incluido byte por byte en este directorio. Se añadieron los números 1–56 y se repararon 40 `ghost_id: null`; los otros 16 coincidían. No se volvió a consultar Ghost ni se derivaron números nuevos.

Antes de escribir se validaron 56 IDs publicados existentes y únicos, ausencia total de `numero`, rango exacto sin huecos ni duplicados, slug de URL y coincidencia de los 16 IDs existentes. El RSS público se recuperó de nuevo: 15/15 coincidencias exactas de fecha/hora y orden contra el CSV, registradas en `rss-comparacion.json`.

En las fichas solo se añadió `numero` y se reemplazaron los 40 IDs nulos. Una auditoría inversa del commit reprodujo byte por byte las fichas base. Se regeneró `build/index.json` únicamente por las reparaciones de IDs. No se modificaron generadores ni plantillas del libro.

## Comprobación del libro terminada en Linux

- Base anterior: `c3c278966fe0d4497cdfd36d4591fe3eda050071`.
- Head del PR verificado: `f3aaac87a4e183790ab96bd60119b9a048d5349f`.
- SHA exacto ejecutado por Actions (merge de prueba del PR): `aa7ee5200d6f57233e0a0efafb8dece4258c6aeb`.
- [Ejecución editorial 42265491211](https://github.com/alcyedmundo281/biosemiotics/actions/runs/42265491211): **success**. El job específico **Generar EPUB, PDF y fuente LuaLaTeX** terminó verde, incluidos preflight de publicación, EPUBCheck, PDF, paquete LaTeX y coherencia de publicación.
- Comparación: **264 páginas antes, 264 después y cero páginas diferentes**. Los SHA-256 de las imágenes de todas las páginas a 150 dpi coinciden. Evidencia: artifact `comparacion-numeracion-pdf`, con PNG y `resultado.json` (retención original de 30 días).

`comparar_libro.py` conserva el procedimiento reproducible: compila ambas revisiones con Quarto/LuaLaTeX, fija `SOURCE_DATE_EPOCH` y usa la misma etiqueta impresa de versión Git (`auditoria-numeracion`). Esta última es una variable de control: el SHA impreso cambia necesariamente entre commits y no mide cambios del contenido. El resultado demuestra igualdad de las páginas renderizadas a 150 dpi, no identidad binaria de PDFs con metadatos distintos.

Para reproducir en un checkout del SHA ejecutado, con sus dependencias editoriales de Linux y `poppler-utils` instaladas:

```sh
python docs/auditorias/2026-11-06-numeracion/comparar_libro.py c3c278966fe0d4497cdfd36d4591fe3eda050071
```

## Separación del pin y conservación de la evidencia

El pin de los tres jobs de `ci.yml` en Ubuntu 24.04 se separó al [PR #152](https://github.com/alcyedmundo281/biosemiotics/pull/152), para fusionarlo antes del #151. Resuelve un fallo ajeno al banco: `setup-python` no encontraba Python 3.9 para Ubuntu 26.04, imagen a la que pasó a resolver `ubuntu-latest`.

El #151 se actualiza sobre ese pin mediante rebase. El pin solo modifica `ci.yml`; no cambia fichas, recursos, bibliografía, generadores ni plantillas del libro. La limpieza posterior elimina los dos pasos temporales y `poppler-utils` de `epub.yml`, sin alterar entradas del libro. La comparación anterior conserva su validez porque esas entradas se mantienen idénticas; el script de auditoría queda disponible y el workflow editorial habitual vuelve a comprobar la edición. Los pasos ligados a la rama temporal no entran en `main`.

## Validación y deuda de formato

Preflight del banco, `build.py`, `verificar_publicacion.py` y 182 pruebas locales correctas; 176 alertas previas de borradores. El perfil de publicación local no pudo completarse por ausencia de `rsvg-convert` y EPUBCheck: el resultado editorial autorizado es el del CI Linux citado. También pasaron integridad Python 3.9/3.13 y citas PubMed/Crossref en la ejecución 42265491465.

El cargador YAML y los validadores no imponen orden alfabético de claves ni rechazan el campo adicional `numero`. Se conserva `numero` inmediatamente después de `estado`, tal como fue revisado. Su reubicación por criterio alfabético queda como deuda de formato; no se rehacen 56 hunks por estética.

Sin `--admin`, sin omitir protección de rama. Las ramas se conservan hasta confirmación de Alcy.
