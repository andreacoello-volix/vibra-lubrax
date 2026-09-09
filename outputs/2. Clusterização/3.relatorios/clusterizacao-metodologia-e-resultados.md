# Segmentação de Clientes por Clusterização (K-Means) — Metodologia e Resultados

*Documento de apoio para apresentação ao cliente — descreve como a segmentação de clientes foi construída e o que ela encontrou.*

---

## Sumário Executivo

Para apoiar a diferenciação de preço por perfil de cliente (uma das oportunidades mapeadas no diagnóstico), agrupamos os **7.176 clientes ativos** da Vibra Lubrax em **5 segmentos**, usando um algoritmo de clusterização (K-Means) sobre 6 variáveis de comportamento de compra. Os segmentos foram depois cruzados com família de produto e frequência de compra, gerando **45 combinações práticas** que servem de base para uma tabela de preços diferenciada.

Este documento explica, em ordem: (1) o que é clusterização e como o método escolhido funciona; (2) quais dados entraram na conta e por quê; (3) o caminho até o resultado final; (4) os 5 segmentos encontrados e o que cada um representa; (5) limitações e próximos passos.

---

## 1. Objetivo

**Pergunta de negócio:** existem grupos de clientes suficientemente diferentes entre si para justificar uma política de preço diferenciada — em vez de uma régua única para todos os 7.176 clientes?

**Critério de sucesso:** um resultado que seja ao mesmo tempo **estatisticamente consistente** (grupos bem separados, não arbitrários) e **útil para o negócio** (tamanho de grupo operável, perfis interpretáveis por quem vai usar isso no dia a dia comercial).

---

## 2. O que é clusterização, e por que K-Means

**Clusterização** é a técnica de agrupar itens parecidos entre si automaticamente, a partir de várias características ao mesmo tempo — sem que ninguém defina os grupos manualmente de antemão. O algoritmo identifica os agrupamentos que emergem naturalmente dos dados.

Isso é diferente de segmentar clientes "na régua" (ex: faturamento alto/médio/baixo) porque considera múltiplas dimensões simultaneamente, encontrando combinações de comportamento que uma régua unidimensional não capturaria.

**K-Means** foi o método escolhido — um dos mais consolidados e interpretáveis para esse tipo de problema. Funciona em 5 passos, repetidos até estabilizar:

1. **Escolhe-se quantos grupos formar** (o parâmetro *k*).
2. O algoritmo parte de *k* "clientes médios" imaginários (centros iniciais).
3. Cada cliente real é atribuído ao centro mais parecido com ele, considerando todas as variáveis ao mesmo tempo.
4. Os centros são recalculados como a média real de quem foi atribuído a cada grupo.
5. Os passos 3 e 4 se repetem até os clientes pararem de trocar de grupo.

> **Importante:** o próprio algoritmo **não decide** quantos grupos (*k*) devem existir — isso é escolhido por quem está analisando, testando diferentes valores e avaliando qual resultado é mais consistente e mais útil (ver seção 4).

---

## 3. Dados e variáveis utilizadas

### 3.1 Base de dados

Fonte: exportação do dashboard Tableau "Sell in — Lubrificantes" (Azure Synapse), período de janeiro/2023 a setembro/2026, 253.624 registros de movimento. Cada linha foi classificada como venda, devolução provável, ajuste ou inconsistência, com base no sinal de volume e receita. Apenas as **245.456 vendas elegíveis** (96,8% da base) entram no cálculo das variáveis de comportamento — exceto a taxa de devolução, que por definição precisa olhar a base inteira.

Os dados foram agregados por cliente (`Código Cliente`), chegando a uma tabela de **7.176 clientes** (após remoção de outliers extremos — ver seção 4).

### 3.2 As 6 variáveis escolhidas

| Variável | O que representa | Como é calculada |
|---|---|---|
| **Volume** | Porte do cliente | Soma do volume (m³) de todas as vendas elegíveis |
| **Preço médio ponderado** | Quanto paga, em média, por m³ (todos os produtos misturados) | `receita líquida total ÷ volume total` — nunca a média simples de preços por venda |
| **Margem Bruta (%)** | Quão lucrativo é o cliente | `lucro de reposição total ÷ receita líquida total` |
| **Frequência** | Quantas vezes por mês compra, em média | `transações ÷ meses ativos` |
| **Taxa de devolução** | Com que frequência os pedidos voltam como devolução | `devoluções ÷ registros totais` (única variável que usa a base bruta inteira) |
| **Produtos** | Diversidade de produtos comprados | Nº de `Código Material` distintos por cliente |

**Por que essas 6 e não outras:** partimos de 13 métricas candidatas e medimos a correlação (Spearman) entre todas. Quando duas métricas correlacionam fortemente (≥ 0,90), elas carregam praticamente a mesma informação — usar as duas juntas só daria peso duplicado à mesma dimensão. Por isso:

- `receita_liquida_total` (correlação de 0,99 com volume) e `lucro_reposicao_total` (0,95) ficaram de fora — são "porte disfarçado" de outra forma.
- `transacoes` e `meses_ativos` ficaram de fora — a razão entre elas (frequência) já captura essa informação de forma normalizada.
- `taxa_ajuste` e `taxa_inconsistencia` ficaram de fora por serem quase constantes entre os clientes (médias de 0,52% e 0,013%) — não ajudam a diferenciar ninguém.

*Ver figura anexa: heatmap de correlação de Spearman entre as métricas candidatas.*

---

## 4. O caminho até o resultado final

Não acertamos de primeira — testamos 5 configurações antes de fechar no resultado final. Vale registrar o porquê, porque a primeira tentativa é um alerta importante sobre como uma métrica "boa no papel" pode ser inútil na prática.

| Teste | Configuração | O que aconteceu |
|---|---|---|
| 1 | k escolhido automaticamente pela maior silhueta, 5 features originais | Pareceu "perfeito" (silhueta 0,96), mas isolou uma dúzia de outliers extremos e jogou **99,8% dos clientes num único grupo** — estatisticamente "ótimo", inútil para negócio |
| 2 | k=4, 5 features do EDA, outliers cortados | Primeira segmentação comercialmente utilizável |
| 3 | k=5, 5 features do EDA, outliers cortados | Grupos mais granulares |
| 4 | k=4, 6 features (+ diversidade de produtos) | Adicionar diversidade de produtos melhorou a qualidade |
| **5** | **k=5, 6 features (+ diversidade de produtos)** | **Melhor resultado — adotado como final** |

**Resultado final (Teste 5):** 7.176 clientes (após corte de outliers pelos percentis 1%–99% de volume, preço e produtos), silhueta 0,30 (aceitável — não excelente, mas honesta: um k pequeno que isola só extremos teria silhueta artificialmente alta, como visto no Teste 1), Davies-Bouldin 1,14 (aceitável).

---

## 5. Resultado: os 5 segmentos de clientes

| # | Segmento | Clientes | % | Perfil |
|---|---|---|---|---|
| 0 | **Base Padrão** *("Pequeno")* | 4.071 | 56,7% | O grosso da carteira. Volume baixo, poucos produtos, compra rara. Preço e margem na média — sem traço que se destaque |
| 1 | **Estratégicos** *("Grande")* | 129 | 1,8% | Menor grupo, mas o mais valioso em volume — compram ~40× mais que o grupo Pequeno, com muito mais produtos e frequência alta. Preço na média — não é "premium", é grande e engajado |
| 2 | **Volume Médio Diversificado** *("Médio")* | 525 | 7,3% | Mesmo perfil dos Estratégicos, em escala menor — "estratégico em formação" |
| 3 | **Nicho Premium** *("Especial")* | 883 | 12,3% | O único grupo que não se diferencia por volume, e sim por **preço**: paga ~40% acima da média por m³. Compra pouco e raramente — vale investigar a causa do preço mais alto antes de qualquer ação |
| 4 | **Volume Médio Padrão** *("Padrão")* | 1.568 | 21,9% | Perfil intermediário em quase tudo — a "classe média" da segmentação |

*Nomes são sugestões baseadas nos perfis numéricos — precisam de validação com o time comercial antes de virarem rótulo oficial.*

### 5.1 Enriquecimento: família de produto e frequência

Os 5 segmentos dizem **quem se parece com quem** em termos gerais. Para virar referência prática de preço, cruzamos cada segmento com a **família de produto** que o cliente mais compra e o **nível de frequência** (Ocasionais / Regulares / Frequentes). O resultado são **45 combinações** (segmento × família), cobrindo 100% do volume (8 famílias nomeadas individualmente + bucket "Outras").

### 5.2 Onde focar primeiro

A receita não se distribui igualmente entre as 45 combinações — **16 delas já cobrem 80% da receita total**. Faz sentido validar e agir sobre essas primeiro, em vez de tentar cobrir as 45 de uma vez.

---

## 6. Limitações e próximos passos

- **Os nomes dos segmentos são hipóteses de trabalho**, não uma taxonomia validada — precisam de checagem com o time comercial.
- **Comportamento de compra muda com o tempo.** Recomenda-se reprocessar essa segmentação periodicamente (sugestão: trimestral) e comparar se os grupos continuam consistentes.
- **Testamos também remover o preço da conta** (ver anexo "Modelo A vs Modelo B") para checar se a segmentação dependia dele — o grupo Nicho Premium (definido pelo preço alto) se dissolve sem essa variável, confirmando que o preço é essencial para essa análise, não incidental.
- **Isso é um ponto de partida, não substitui o julgamento comercial.** Os dados mostram padrões; cabe ao time decidir o que fazer com eles.
- **Próximo passo natural:** testar elasticidade de preço por segmento (ver seção de Sensibilidade a Preços do diagnóstico).

---

## Anexo — arquivos de referência

| Arquivo | Conteúdo |
|---|---|
| `relatorio_tecnico_clusterizacao_vibra_lubrax.html` | Relatório técnico completo, com código, métricas e metodologia estatística detalhada |
| `relatorio_comercial_segmentacao_vibra_lubrax.html` | Versão em linguagem simples para o time comercial, com FAQ |
| `como-construimos-as-features.html` | Passo a passo visual de como cada uma das 6 variáveis foi calculada |
| `mapa_modelos_kmeans.html` | Comparação entre o modelo oficial (com preço) e um modelo de diagnóstico sem preço |
| `clusterizacao-vibra-lubrax.xlsx` | Todos os resultados em planilha (segmentação, perfis, matriz cluster×família, Pareto) |
| `5.Figures/05_correlacao_spearman_candidatas.png` | Heatmap de correlação das variáveis candidatas |
| `4.apresentacao/fig_antes_depois_clusterizacao.png` | Visualização antes/depois da clusterização (dados reais do projeto) |
