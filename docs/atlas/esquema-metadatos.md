# Metadatos de la ficha

El índice permite encontrar y evaluar una entrada antes de abrir el artículo
completo en Ghost. Guarda metadatos, enlaces y conteos, no el cuerpo.
Los campos se escriben en el YAML de la fuente `.qmd`.

## Identificación y estado

`id`, `tipo`, `titulo`, `nivel`, `abstract` y `refs` describen la ficha.
`titulo_en` es opcional. `url` es la URL pública real de Ghost, nunca la del
editor ni un slug supuesto. `doi` y `version` se registran cuando existan;
no se inventa un DOI individual a partir del DOI general del atlas.

`estado` gobierna inclusión pública: `borrador` excluido, `revisado` disponible
para edición completa y `publicado` incluido también en `--solo-publicados`.
`fecha_revision` registra la aprobación real, no la fecha del commit.
`ghost_id` guarda el identificador real del post. `ghost_sha256` es derivado:
permite contrastar el cuerpo canónico con fuente, bibliografía y registro.

## Abstract

Debe contener 40–80 palabras y seguir la lógica de la entidad:

- Signo: qué se ve → qué significa → qué decisión cambia → dónde falla.
- Caso: duda clínica → hallazgo → bifurcación → desenlace.
- Concepto: fenómeno → importancia para interpretar la imagen.

El excerpt de Ghost refleja este resumen. No se introducen en él conclusiones
más fuertes que la evidencia del cuerpo.

## Descriptores

| Campo | Uso |
|---|---|
| `sistema` | Taxonomía del mapa: respiratorio, cardiovascular, digestivo, genitourinario, vascular, musculoesqueletico, endocrino, nervioso, multiorgano |
| `organo` | Órgano según mapa maestro |
| `nivel` | principiante, intermedio, avanzado |
| `ventana`, `sonda` | Adquisición y sondas requeridas |
| `descriptores` | Términos libres en español |
| `mesh` | Descriptores MeSH comprobados |
| `escenario` | urgencias, consulta, hospitalizacion, uci, preoperatorio |
| `pregunta_clinica` | Duda concreta que permite entrar al atlas por una decisión |

Las relaciones del [esquema](esquema.md) permiten pasar del signo al concepto,
al contraste y al caso. Las facetas y el abstract ayudan a decidir qué abrir.

## Autoría y contribución

`autores` es una lista de personas con `nombre`, `orcid`, `afiliacion` y,
cuando proceda, `credit`. Solo se declaran identificadores y afiliaciones
verificados; no se dejan ORCID de relleno ni se implica aval institucional.

El material original propone etiquetas de contribución en español:
`conceptualizacion`, `adquisicion-imagenes`, `redaccion`, `revision`, `edicion`,
`curacion-datos`, `supervision`. Su uso local no certifica una correspondencia
automática con CRediT; un depósito que lo exija necesita mapearlas y validarlas.

## Medios

`medios` inventaría imágenes, loops y clips. `tipo`, `id`, `descripcion` y,
si corresponde, `duracion_s` describen el recurso. Los archivos utilizados en
las ediciones se conservan localmente; un enlace externo no los sustituye.

Para imágenes registra `archivo_local`, `credito`, `fuente`, `fuente_url`,
`licencia_img` y `licencia_url`; marca `destacada: true` cuando corresponda.
Comprueba archivo, atribución y licencia según el manual. Las adaptaciones
también requieren `adaptacion` y `original_local`; los fotogramas de video
requieren `referencia` incluida en las `refs` de la ficha.

La misma imagen publicada debe llegar a las ediciones EPUB y LaTeX.
No se inventan licencias ni se hereda automáticamente la licencia del texto.

## Evidencia, procedencia y licencia

`refs` guarda claves; los datos bibliográficos están en `refs.bib` y se
incorporan mediante `scripts/refs.py` desde PubMed. Crossref proporciona la
segunda comprobación según el manual. Las fuentes terciarias pueden ayudar
a localizar literatura primaria, pero no sustituyen la evidencia verificada.

`fecha`, `actualizado` y `revisado_por` describen hechos reales, si constan.
El texto del atlas usa CC BY 4.0; las imágenes conservan sus propias licencias.
Los casos necesitan además consentimiento y desidentificación.

JSON-LD y XML son derivados. El XML usa vocabulario JATS experimental; no
garantiza conformidad con un perfil de depósito ni expande por sí solo toda
la bibliografía. Consulta el instructivo antes de atribuirle ese alcance.
