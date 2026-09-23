---
name: ghost
description: Publica o actualiza un artículo del atlas biosemiotics en Ghost (www.biosemiotics.net) mediante el navegador. Úsala siempre que la tarea toque Ghost — "publica X en Ghost", "sube el artículo", "pon la imagen destacada", "pega el cuerpo en Ghost", "configura tags/excerpt/pie", "envía a los suscriptores", "obtén el ghost_id", "revisa el post en Ghost" — y también en inglés ("publish on Ghost", "Ghost admin", "featured image"). Contiene las tres compuertas que se incumplían una y otra vez: imagen solo de Wikimedia Commons (nunca generada con IA), pie pegado una sola vez y publicación con envío por email a los suscriptores.
---

# Publicar en Ghost — biosemiotics

`CLAUDE.md` es la autoridad: esta skill es su lista de ejecución para el rol
**publicador**. Si algo aquí contradice a `CLAUDE.md`, gana `CLAUDE.md`. Lee sus
secciones «Ciclo de publicación en Ghost» y «Traspaso atómico del índice» antes
de empezar; no se repiten aquí.

## Las tres compuertas — no se negocian

Estos tres errores ya ocurrieron varias veces. Cada compuerta tiene una
comprobación que la cierra; sin esa comprobación en verde, no avances.

### 1. Imagen: SOLO Wikimedia Commons. NUNCA generada con IA.

- La imagen destacada sale de una página `https://commons.wikimedia.org/wiki/File:…`.
  No generes imágenes con ninguna herramienta de IA, no las dibujes, no las
  compongas, y no las tomes de otro sitio aunque parezcan libres.
- Si no encuentras en Commons una imagen adecuada con licencia compatible,
  **detente y pregúntale a Alcy**. No la sustituyas por una generada.
- Descarga el original, guárdalo en `assets/img/` y decláralo en `medios` con
  `tipo: imagen`, `destacada: true`, `descripcion`, `credito`, `fuente`
  (`Wikimedia Commons`), `fuente_url` (la página `File:`), `licencia_img`,
  `licencia_url` y `archivo_local`.
- **Comprobación:** `python scripts/auditar_medios.py` (verifica el archivo
  contra la API de Commons por SHA-1) y luego `python scripts/build.py`.
  `build.py` **falla** si la `fuente_url` de una imagen no es una página `File:`
  de Commons. No se arregla con una exención: las exenciones son solo
  históricas y las decide Alcy.

### 2. Pie de la imagen: el canónico, pegado UNA sola vez.

- No compongas el pie ni el alt a mano. Sácalos del canónico:

  ```bash
  python scripts/auditar_pegado_ghost.py --canon build/ghost/<carpeta>/<archivo>.qmd
  ```

  Copia `pie_esperado` y `alt_esperado` tal cual. El pie tiene el formato
  «descripción. crédito, vía fuente. licencia.».
- Pégalo de forma idempotente: abre el campo de pie desde la interfaz (nunca
  hagas clic por coordenadas: puede caer dentro del primer encabezado del
  cuerpo), selecciona todo, borra, **confirma que quedó vacío**, inserta una
  vez. No encadenes `fill()` y `type()`: así se duplicaba.
- **Comprobación:** lee el pie visible en Ghost y pásalo al auditor. Debe salir
  con código 0:

  ```bash
  python scripts/auditar_pegado_ghost.py --canon build/ghost/<carpeta>/<archivo>.qmd \
    --pie "<pie observado en Ghost>"
  ```

  Si reporta «duplicada» o «no coincide», vuelve a vaciar el campo y repite.
  Haz lo mismo con el cuerpo usando `--captura` (ver `CLAUDE.md` §1.4).

### 3. Publicación: web **y email a los suscriptores**.

- Toda publicación **nueva** sale como «Publish and email» / «Publicar y enviar
  por email» a los suscriptores. «Publish only» / solo web **no** es la opción
  del atlas. (Actualizar un post ya publicado no reenvía email; eso es normal.)
- En el diálogo de publicación, lee el **número exacto** de destinatarios que
  muestra Ghost. Justo antes del último botón, díselo al usuario y pide su
  confirmación: «Publicaré en web y enviaré por email a N suscriptores.
  ¿Confirmas?». Publicar requiere ese sí explícito.
- Si Ghost no ofrece el envío por email (newsletter desactivada, 0
  destinatarios), **detente y repórtalo**: no publiques solo en web en silencio.
- **Comprobación:** después de publicar, Ghost debe mostrar
  `Published and sent` (no solo `Published`). Registra ese estado y el número
  de destinatarios en el informe y en el PR.

## Flujo

### 0. Antes de abrir Ghost

1. `git status` limpio y `git worktree list` con un solo worktree. Crea la rama
   de publicación desde `main`.
2. La ficha ya existe, está `revisado` y validada en la fase proveedora. Si
   falta la ficha o el cuerpo canónico, o fallan sus referencias, detente
   (`CLAUDE.md`, «Límite de responsabilidad»).
3. Compuerta 1 (imagen) y `python scripts/build.py` en verde.
4. `python scripts/auditar_pegado_ghost.py --canon build/ghost/<carpeta>/<archivo>.qmd`:
   anota la huella y todos los campos `*_esperado`.

### 1. En Ghost

Usa el navegador donde ya está abierta la sesión de Ghost del usuario
(normalmente Claude in Chrome). Si aparece `/ghost/#/signin`, **detente**: nunca
introduzcas credenciales ni resuelvas 2FA.

1. **Busca duplicados primero:** busca el título entre borradores y publicados.
   Si ya existe, ábrelo; nunca crees un segundo post.
2. **Título:** el `title` del canónico.
3. **Cuerpo:** el de `build/ghost/<carpeta>/<archivo>.qmd`, sin la cabecera,
   pegado una sola vez. Si el editor ya tiene texto: `Ctrl/Cmd+A`, `Backspace`,
   confirma longitud cero y pega una vez. Si ya coincide con el canónico, no lo
   toques. No regeneres el canónico.
4. **Ajustes del post** (panel lateral):
   - **Slug:** no lo edites. Ghost lo genera del título y así se hizo en todos
     los artículos; nunca lo adivines ni lo cambies por el `id` de la ficha.
   - **Tags:** `tags_esperado`, en ese orden.
   - **Excerpt:** `excerpt_esperado` (ya recortado al límite de 300 caracteres
     de Ghost). No pegues el abstract completo.
   - **Autor:** Alcy Edmundo Torres Guerrero. **Acceso:** público.
   - **Imagen destacada:** sube `imagen_esperado` con la carga de archivos de
     la herramienta del navegador sobre el `<input type="file">`; no abras el
     diálogo nativo del sistema. Alt: `alt_esperado`. Pie: compuerta 2.
   - Meta title/description y tarjetas sociales: vacíos, para heredar título,
     excerpt e imagen como en los artículos anteriores.
5. **Vistas previas web y email:** título, excerpt, imagen, atribución,
   evidencia y enlace al Reto. El contador de palabras no debe haber aumentado
   al doble y cada encabezado canónico aparece una vez. Tras cualquier edición,
   repite esta revisión.
6. **Publicar:** compuerta 3.

### 2. Después de publicar

1. Copia la URL pública definitiva (nunca `/ghost/#/…` ni una vista previa
   `/p/…`) y el `ghost_id`: los 24 caracteres hexadecimales del final de
   `/ghost/#/editor/post/<ghost_id>`.
2. En la ficha, cambia **solo** `estado: publicado`, `url` y `ghost_id` (y
   `medios` si hizo falta). Nada del cuerpo, `refs`, PMID ni DOI.
3. `python scripts/build.py` y `python scripts/libro.py --salida build/libro.pdf --solo-publicados`.
   **No** ejecutes `indice.py` ni toques `build/index.json` en este rol.
4. Abre el **PR padre en borrador** y luego cambia al rol proveedor para el PR
   hijo de regeneración, según `CLAUDE.md` §2–3.

## Informe final

`id`, título, URL pública, `ghost_id`, estado de Ghost (`Published and sent`),
fecha/hora, **audiencia y número de destinatarios del email**, tags, excerpt,
autor, acceso, imagen (`archivo_local` y `fuente_url` de Commons), alt, pie
(con la salida en verde de `auditar_pegado_ghost.py --pie`), crédito, fuente,
licencia, archivos cambiados y PR.

## Nunca

- Generar, dibujar o componer imágenes con IA, ni usar imágenes que no vengan de Commons.
- Escribir el pie o el alt a mano, o pegarlos dos veces.
- Publicar solo en web una publicación nueva.
- Inventar o editar el slug, o usar URLs del editor o de vista previa como `url`.
- Repetir `fill`/`type`/pegar sobre un campo que ya contiene texto.
- Introducir credenciales, o publicar sin el sí explícito del usuario.
