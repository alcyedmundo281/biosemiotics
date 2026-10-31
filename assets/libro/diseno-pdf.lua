--[[
Diseño del libro impreso: filtro de Quarto que solo actúa en la salida LaTeX.

`qmd.py` lo declara únicamente bajo `format: pdf`, y además cada función sale
sin tocar nada si el formato no es LaTeX. El EPUB y el manuscrito plano siguen
recibiendo exactamente el mismo Markdown: aquí no se añade ni se quita texto,
solo se envuelven bloques en los entornos que define `preambulo.tex`.

  - Portadilla: el encabezado «Portadilla» se convierte en la página de
    título, y créditos + declaración de uso de IA en una página de créditos
    fuera del índice.
  - Cada ficha abre página; el capítulo temático u órgano la antecede en la
    misma página.
  - Significante / significado / decisión / umbral van en un recuadro.
  - «Dónde NO confiar» va en un recuadro de aviso; «Evidencia», en letra menor.
  - El código en línea no se parte por sus guiones.
]]

local ETIQUETAS_SIGNO = {
  ["Significante."] = true,
  ["Significado."] = true,
  ["Decisión."] = true,
  ["Umbral."] = true,
  ["Decisión semiótica."] = true,
}

local function latex(texto)
  return pandoc.RawBlock("latex", texto)
end

local function es_latex()
  return FORMAT:match("latex") ~= nil
end

-- Nombres de archivo e id de ficha: LuaTeX corta tras un «-» explícito aun en
-- monoespaciada, y «AI-» / «USE.md» parecía una palabra dividida. Dentro de
-- \mbox el guion no admite corte; los espacios del código sí.
function Code(el)
  if not es_latex() or not el.text:find("-", 1, true) then
    return nil
  end
  local texto = pandoc.write(pandoc.Pandoc({pandoc.Plain({el})}), "latex")
  texto = texto:gsub("%s+$", ""):gsub("%-", "\\mbox{-}")
  return pandoc.RawInline("latex", texto)
end

-- Encabezado no numerado y fuera del índice, con su texto en LaTeX.
local function encabezado_oculto(h)
  local texto = pandoc.write(pandoc.Pandoc({pandoc.Plain(h.content)}), "latex")
  texto = texto:gsub("%s+$", "")
  local orden = h.level <= 1 and "chapter" or "section"
  return latex("\\" .. orden .. "*{" .. texto .. "}")
end

local function etiqueta_signo(bloque)
  if bloque.t ~= "Para" or #bloque.content == 0 then
    return nil
  end
  local primero = bloque.content[1]
  if primero.t ~= "Strong" then
    return nil
  end
  local texto = pandoc.utils.stringify(primero)
  if ETIQUETAS_SIGNO[texto] then
    return texto
  end
  return nil
end

local function es_enlace_ficha(bloque)
  if bloque.t ~= "Para" or #bloque.content == 0 then
    return false
  end
  local primero = bloque.content[1]
  return primero.t == "Emph" and pandoc.utils.stringify(primero) == "Edición en línea:"
end

local function contiene_indice(bloque)
  return bloque.t == "RawBlock" and bloque.text:find("\\tableofcontents", 1, true) ~= nil
end

-- Copia los bloques desde `i` hasta el siguiente encabezado de nivel <= `nivel`
-- (o el final) dentro de `entorno`. Devuelve el índice siguiente.
local function envolver_seccion(bloques, i, nivel, entorno, salida)
  salida:insert(latex("\\begin{" .. entorno .. "}"))
  while i <= #bloques do
    local b = bloques[i]
    if b.t == "Header" and b.level <= nivel then
      break
    end
    salida:insert(b)
    i = i + 1
  end
  salida:insert(latex("\\end{" .. entorno .. "}"))
  return i
end

function Pandoc(doc)
  if not es_latex() then
    return nil
  end
  local bloques = doc.blocks
  local salida = pandoc.List()
  local anterior = nil
  local i = 1
  while i <= #bloques do
    local b = bloques[i]

    if b.t == "Header" and b.identifier == "portadilla" then
      -- Página de título: los párrafos que siguen (subtítulo, autor, versión).
      salida:insert(latex("\\begin{portadillapdf}"))
      i = i + 1
      while i <= #bloques and bloques[i].t ~= "Header" do
        salida:insert(bloques[i])
        i = i + 1
      end
      salida:insert(latex("\\end{portadillapdf}"))
      -- Créditos y declaración de uso de IA, hasta el índice.
      salida:insert(latex("\\begin{creditospdf}"))
      while i <= #bloques and not contiene_indice(bloques[i]) do
        local c = bloques[i]
        if c.t == "Header" then
          salida:insert(encabezado_oculto(c))
        else
          salida:insert(c)
        end
        i = i + 1
      end
      salida:insert(latex("\\end{creditospdf}"))
      anterior = nil

    elseif b.t == "Header" then
      local texto = pandoc.utils.stringify(b.content)
      -- La parte ocupa su propia página. El capítulo temático u órgano abre
      -- página y la ficha también, salvo la primera, que va bajo su órgano.
      local tras_organo = anterior ~= nil and anterior.t == "Header"
        and anterior.level == 2
      if b.level == 2 or (b.level == 3 and not tras_organo) then
        salida:insert(latex("\\clearpage"))
      end
      salida:insert(b)
      anterior = b
      i = i + 1
      if texto == "Dónde NO confiar" then
        i = envolver_seccion(bloques, i, b.level, "alertaficha", salida)
      elseif texto == "Evidencia" then
        i = envolver_seccion(bloques, i, b.level, "evidencia", salida)
      end

    elseif etiqueta_signo(b) then
      salida:insert(latex("\\begin{triadasigno}"))
      while i <= #bloques and etiqueta_signo(bloques[i]) do
        local p = bloques[i]
        local resto = pandoc.List()
        resto:insert(pandoc.RawInline("latex", "\\etiquetasigno{"))
        resto:extend(p.content[1].content)
        resto:insert(pandoc.RawInline("latex", "}"))
        for k = 2, #p.content do
          resto:insert(p.content[k])
        end
        salida:insert(pandoc.Para(resto))
        i = i + 1
      end
      salida:insert(latex("\\end{triadasigno}"))
      anterior = salida[#salida]

    elseif es_enlace_ficha(b) then
      salida:insert(latex("\\begin{enlaceficha}"))
      salida:insert(b)
      salida:insert(latex("\\end{enlaceficha}"))
      anterior = b
      i = i + 1

    else
      salida:insert(b)
      anterior = b
      i = i + 1
    end
  end
  doc.blocks = salida
  return doc
end
