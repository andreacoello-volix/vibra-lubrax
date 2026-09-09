# Prompt pronto: aplicar o estilo visual Volix neste projeto

Cole o texto abaixo no Codex ou no Claude (junto com esta pasta `volix-visual-style-kit/` anexada ou já copiada para o repositório) para que a IA aplique o padrão visual Volix automaticamente.

---

Aplique o padrão visual Volix neste projeto, usando os arquivos da pasta `volix-visual-style-kit/` como referência (não invente cores ou componentes novos, use exatamente o que está documentado ali):

1. Leia `volix-visual-style-kit/STYLE_GUIDE.md` para entender a paleta, tipografia e regras de gráfico.
2. Se o projeto tiver notebooks Jupyter ou scripts Python que gerem gráficos (matplotlib):
   - Copie `volix-visual-style-kit/Script/` (com `tema_visual.py` e `__init__.py`) para a raiz deste projeto, se ainda não existir uma pasta `Script/` equivalente.
   - No topo de cada notebook/script relevante, importe e chame `configurar_tema()` de `Script.tema_visual`.
   - Depois de montar cada gráfico matplotlib, chame `aplicar_estilo_grafico(ax)` antes de salvar/mostrar.
   - Use `painel_kpis_terminal`, `tabela_terminal`, `cabecalho_secao` e `nota_aviso` para qualquer output formatado em HTML dentro do notebook (KPIs, tabelas destacadas, cabeçalhos de seção, avisos).
3. Se o projeto tiver dashboards ou relatórios em HTML (fora do Jupyter):
   - Use `volix-visual-style-kit/volix-theme.css` como base de estilo (import ou copie o conteúdo para dentro do `<style>` do arquivo).
   - Siga as classes já definidas (`.volix-panel`, `.volix-kpi-card`, `.volix-table`, `.volix-warning`, `.volix-section-header`) em vez de criar CSS novo.
4. Regras de cor a respeitar em qualquer novo componente que precise ser criado:
   - Fundo escuro (`#111111` / `#171717`), nunca fundo claro.
   - Um único acento verde-menta (`#7EF3C4` / `#06D6A0`) para destaque; amarelo (`#FFD166`) reservado só para avisos e outliers.
   - Texto principal quase branco (`#F7FFF9`), texto secundário em cinza-esverdeado (`#A7B8B2`).
   - Títulos/labels em caixa alta, negrito forte, letter-spacing largo (`.12em` a `.18em`).
5. Não altere as cores/valores do `tema_visual.py` — se precisar de uma variação, crie uma constante nova ao lado das existentes, mantendo a mesma paleta.
6. Ao final, gere um exemplo visual (um gráfico ou um trecho de HTML) mostrando o tema aplicado, para eu conferir antes de aplicar em todo o projeto.

---
