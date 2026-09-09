# Guia de Estilo Visual Volix

Este é o padrão visual usado nos notebooks e relatórios de pricing (dark mode, acentos em verde-menta). Extraído de `Script/tema_visual.py` do projeto Comolatti para reuso em qualquer outro projeto.

## Paleta de cores

| Nome           | Hex       | Uso                                                          |
|----------------|-----------|---------------------------------------------------------------|
| Fundo          | `#111111` | Fundo principal (notebook, painéis, gráficos)                 |
| Painel         | `#171717` | Fundo de cards/painéis sobre o fundo principal                |
| Painel suave   | `#1F1F1F` | Fundo de painéis secundários                                   |
| Texto          | `#F7FFF9` | Texto principal, quase branco                                  |
| Muted          | `#A7B8B2` | Texto secundário, labels, eixos de gráfico                     |
| Acento         | `#7EF3C4` | Cor de marca — bordas, títulos de seção, séries principais     |
| Acento (fundo) | `#06D6A0` | Verde mais saturado, usado em `rgba(6,214,160,.20)` como fundo de cabeçalho de tabela |
| Primária       | `#1B9AAA` | Azul petróleo (variável CSS disponível, uso pontual)           |
| Aviso          | `#FFD166` | Alertas, mediana em destaque, outliers                          |
| Borda          | `#7EF3C4` | Mesma cor do acento, usada em bordas de cards e painéis         |
| Grade/grid     | `#222222` a `#2A2A2A` | Linhas de grade tracejadas nos gráficos            |
| Spine (eixo)   | `#333333` | Linhas dos eixos esquerdo/inferior nos gráficos                 |

Regra geral: fundo escuro quase preto, texto quase branco, um único acento (verde-menta) para tudo que precisa chamar atenção, amarelo reservado só para avisos/outliers.

## Tipografia

- Família: `sans-serif` (padrão do sistema; sem fonte customizada).
- Títulos de seção e labels: **caixa alta**, `font-weight: 850-900`, `letter-spacing: .12em` a `.18em`.
- Texto corrido: `15px`, `line-height: 1.58`.
- Valores numéricos em destaque (KPIs): fonte monoespaçada (`font-family: monospace`), peso 900.
- Código inline: fundo `#1B1B1B`, texto no acento claro.

## Componentes (HTML, para notebooks/dashboards)

Todos com fundo escuro, borda de 2px na cor de acento, `border-radius: 8px`:

1. **Cabeçalho de seção** — texto uppercase no acento, com badge opcional (pill verde com texto escuro).
2. **Painel de KPIs** — cards lado a lado, cada um com borda na cor do próprio KPI, label muted em cima, valor grande monoespaçado embaixo.
3. **Tabela estilizada** — cabeçalho com fundo verde translúcido (`rgba(6,214,160,.20)`) e borda inferior grossa no acento; linhas com texto claro e separador sutil.
4. **Nota de aviso** — borda e título na cor de aviso (amarelo), fundo amarelo bem translúcido.
5. **Injeção de CSS no notebook** (Jupyter) — reestiliza `.dataframe`, células de código/output e headers markdown para o tema escuro.

## Gráficos (matplotlib)

- Fundo da figura e dos eixos: `#111111`.
- Sem bordas (spines) no topo/direita; esquerda/baixo em `#333333`.
- Grid tracejado (`--`), fino, em `#222222`/`#2A2A2A`, atrás dos dados (`set_axisbelow(True)`).
- Ticks e labels dos eixos: cor muted (`#A7B8B2`).
- Série principal/destaque: acento (`#7EF3C4`); segunda camada ou outlier: aviso (`#FFD166`); linhas de referência/neutras: muted.
- `figure.dpi: 110`.
- Legenda: fundo igual ao da figura, borda muted, texto na cor do texto principal.

## Como aplicar em um projeto novo

1. Copie a pasta `Script/` (contém `tema_visual.py` e `__init__.py`) para a raiz do projeto (ou onde os notebooks conseguam importar).
2. No topo do notebook:
   ```python
   from Script.tema_visual import (
       configurar_tema, aplicar_estilo_grafico,
       painel_kpis_terminal, tabela_terminal, cabecalho_secao, nota_aviso,
       COR_ACENTO, COR_AVISO, COR_FUNDO, COR_TEXTO, COR_MUTED,
   )
   configurar_tema()
   ```
3. Em cada gráfico matplotlib, ao final, chame `aplicar_estilo_grafico(ax)`.
4. Para relatórios HTML/dashboards standalone (fora do Jupyter), use `volix-theme.css` (nesta mesma pasta) e siga os mesmos nomes de variável (`--volix-*`).

## Arquivos desta pasta

- `Script/tema_visual.py` — módulo Python original, pronto para copiar e importar.
- `Script/__init__.py` — expõe as funções/constantes do módulo.
- `volix-theme.css` — as mesmas cores em CSS puro, para dashboards HTML/artifacts fora do Jupyter.
- `exemplos/exemplo_notebook.py` — trecho de código mostrando o uso completo (tema + gráfico + KPIs + tabela).
- `PROMPT_PARA_IA.md` — texto pronto para colar no Codex/Claude em outro projeto, pedindo para aplicar esse estilo.
