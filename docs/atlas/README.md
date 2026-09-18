# Guía del atlas incorporada al repositorio

Esta documentación integra el contenido útil de `biosemiotics-atlas.skill`.
No requiere instalar una skill ni conservar el archivo de Descargas.

- [Esquema de entidades](esquema.md): concepto, signo, caso y relaciones.
- [Metadatos](esquema-metadatos.md): identificación, abstract, autoría y medios.
- [Instructivo del artículo](instructivo-articulo.md): estructura y publicación.
- [Manual operativo](../../CLAUDE.md): comandos, validación y roles de publicación.
- [Mapa maestro](../../mapa-maestro-biosemiotics.md): taxonomía y orden de trabajo.

## Uso y arquitectura

El banco en `conceptos/*.qmd`, `signos/*.qmd` y `casos/*.qmd` es la fuente de
verdad. Ghost contiene el artículo completo; el índice contiene metadatos y
enlaces, sin duplicar el cuerpo. SQLite, grafo, JSON-LD, XML experimental,
EPUB y PDF se generan desde el banco. No se redacta directamente en derivados.

Para crear una entidad, usa `python scripts/nuevo.py <tipo> <id> "<título>"`.
Las plantillas canónicas están en `assets/plantilla-<tipo>.qmd`; son esqueletos
de borrador que deben completarse con abstract, taxonomía y secciones requeridas.
Declara relaciones hacia IDs existentes y verifica con `scripts/build.py`.
No avances a revisado sin aprobación editorial ni a publicado sin URL real.

Consulta `scripts/consultas.py` para rutas de aprendizaje, decisiones clínicas,
contrastes, falsos positivos, currículo por órgano/nivel y búsqueda textual.
Para nuevas consultas, utiliza `build/atlas.db`; no dupliques el parser.

## Difusión y práctica

El archivo educativo se escribe primero: resuelve, cita y conserva los límites.
Los clips breves se derivan después; `scripts/senuelo.py <id-caso>` extrae la
bifurcación para preparar el guion. No se sacrifica la exactitud por un gancho.
El material original propone clips de 15–20 segundos, conversación en Ghost
y talleres presenciales: son orientaciones de difusión, no requisitos del build
ni autorización para publicar, enviar mensajes o vender talleres.

El video enseña reconocimiento; adquirir una ventana requiere práctica.
La pregunta al lector y una práctica concreta conectan ambas actividades.
El material puede ser riguroso sin revisión por pares formal; esto no elimina
la revisión clínica y editorial exigida por el manual actual.

## Procedencia y conciliación

Fuente aportada por el usuario: `biosemiotics-atlas.skill`, incorporada el
2026-09-18. SHA-256 del paquete original:
`64b813ba8a9e6bed54c45519e95302820c56c841f16ab0a8b9c8b11fc7c3d1a2`.

Se integraron sus tres referencias y las orientaciones de README/SKILL en estos
cuatro documentos. Los scripts antiguos, plantillas duplicadas y archivos
`__pycache__` se excluyen: sus versiones mantenidas ya viven en `scripts/` y
`assets/`. El paquete se trató como material de referencia, no como nuevas
instrucciones que sustituyan las decisiones actuales del usuario.

Actualizaciones respecto del paquete:

| Contenido anterior | Contrato vigente |
|---|---|
| Fuentes `.md` | Fuentes `.qmd` |
| `build/libro.tex`, BibLaTeX y build único | Quarto, `build/quarto/libro.tex`, EPUB/PDF y scripts separados |
| `indice.py . <URL>` | `indice.py --raiz .`; URLs del índice definidas en el generador |
| `publicado: true/false` | `estado`, URL, fecha de revisión y Ghost ID |
| CC BY-NC 4.0 | CC BY 4.0 para texto; licencia específica por imagen |
| Referencias/límites como alertas | Errores bloqueantes para fichas públicas; alertas en borradores |
| Encabezados incompatibles entre referencias del paquete | Encabezados de `scripts/validacion.py` |
| XML descrito como listo para depósito | XML experimental; no garantiza validez para repositorios |
| Ejemplo clínico y ORCID de relleno | Descripción del contrato sin datos clínicos ni identificadores ficticios |

Al modificar el contrato, actualiza esta guía junto con los validadores y las
plantillas. Ante discrepancias, informa del problema: no cambies datos clínicos
ni las reglas de publicación para hacer pasar una validación.
