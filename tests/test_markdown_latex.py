import unittest

from scripts.build import markdown_a_latex


class MarkdownLatexTest(unittest.TestCase):
    def test_renderiza_estructura_editorial_sin_marcadores_crudos(self):
        markdown = """## Sección clínica

Texto con **negrita**, *énfasis*, `código` y cita [paper2026].

- Primer punto
- Segundo punto con **fuerza**

1. Medir
2. Decidir

> **Tip.** Confirmar en dos planos.

| Vista | Hallazgo |
|---|---|
| Pulmón | Sliding |

```text
profundidad = velocidad * tiempo / 2
```
"""

        latex = markdown_a_latex(markdown)

        self.assertIn(r"\subsection*{Sección clínica}", latex)
        self.assertIn(r"\textbf{negrita}", latex)
        self.assertIn(r"\emph{énfasis}", latex)
        self.assertIn(r"\texttt{código}", latex)
        self.assertIn(r"\cite{paper2026}", latex)
        self.assertIn(r"\begin{itemize}", latex)
        self.assertIn(r"\begin{enumerate}", latex)
        self.assertIn(r"\begin{quote}", latex)
        self.assertIn(r"\begin{tabularx}", latex)
        self.assertIn(r"\begin{verbatim}", latex)
        for marcador in ("## ", "**", "```", "|---"):
            self.assertNotIn(marcador, latex)


if __name__ == "__main__":
    unittest.main()
