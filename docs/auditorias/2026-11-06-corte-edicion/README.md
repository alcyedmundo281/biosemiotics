# Corte de la primera edición: 13 de noviembre de 2026

El libro usa `banco.seleccionar_edicion(entidades, fecha_corte)`. Solo incluye
fichas publicadas cuyo `fecha_publicacion` sea anterior a la medianoche UTC
del 14 de noviembre de 2026: el día 13 es inclusivo. La falta de fecha en una
publicada y la falta o invalidez de `FECHA_CORTE` abortan la compilación.

`seleccionar_publicables` no cambió: el seriado y su índice siguen siendo
continuos. PDF, EPUB y el ensamblador Quarto pasan el corte explícitamente;
la verificación de derivados también distingue las salidas del seriado de las
imágenes exigidas a la edición.

El colofón solo imprime fichas y referencias de esa edición y su corte. Los
conteos globales permanecen en la instantánea fechada de `AI-USE.md`. Se retiraron
los antiguos marcadores globales de la plantilla y del sustituidor.

## Auditoría Linux

La comparación usa la misma redacción autorizada del colofón en ambos lados.
Así se aísla el filtro de fecha del cambio editorial del párrafo:

- Base anterior al filtro, con colofón limitado a la edición:
  `852236f78b04b6a16ee0b4b9b65ff8378a63595d`.
- Head del PR con filtro y auditoría: `11c9250a712110f735d70f848f2e271bb09250a9`.
- SHA exacto ejecutado por Actions (merge de prueba):
  `5f41e2995f0ea7c8fbb375e28c5bf48a990c07f0`.
- [Ejecución 42291932141](https://github.com/alcyedmundo281/biosemiotics/actions/runs/42291932141),
  artifact `auditoria-corte-edicion`; el informe y hashes de cada página se
  conservan en `resultado.json` junto a este archivo.

| Escenario | Fichas en el libro | Páginas | Publicadas en el seriado | Páginas distintas respecto a la base |
|---|---:|---:|---:|---:|
| Antes del filtro | 56 | 264 | 56 | — |
| Después del filtro | 56 | 264 | 56 | 0 |
| Después, con artículo 57 ficticio del 20 de noviembre | 56 | 264 | 57 | 0 |

El texto extraído de los tres PDF es idéntico. Todas las páginas renderizadas a
150 dpi tienen hashes SHA-256 idénticos. Se controlaron la etiqueta impresa de
versión Git (`auditoria-corte`) y la fecha reproducible para que no confundieran
la comparación. No se afirma igualdad binaria de metadatos internos del PDF.
La ficha ficticia solo existió en el banco temporal de la auditoría; nunca se
escribió en el banco del repositorio ni se publicó.

El recuento para Bowker permanece en **264 páginas**.

## Reproducción

En un checkout con el código auditado, Python 3.13, dependencias editoriales de
Linux del workflow (Quarto 1.5.57, LuaLaTeX, Libertinus 7.051) y Poppler:

```sh
git fetch origin 852236f78b04b6a16ee0b4b9b65ff8378a63595d
python docs/auditorias/2026-11-06-corte-edicion/comparar_pdf.py 852236f78b04b6a16ee0b4b9b65ff8378a63595d
```

El script compila las tres variantes, exige 56 fichas y 264 páginas, compara
texto y páginas y se detiene ante cualquier diferencia. Si falla, conserva un
informe y las páginas diferentes para inspección.

Los dos pasos temporales de auditoría y conservación del artifact, junto con
la dependencia temporal `poppler-utils`, se retiraron del workflow final.
El script y este registro quedan disponibles; el workflow no queda apuntando
a una rama temporal. La limpieza no modifica entradas, lógica de selección ni texto generado del libro.
