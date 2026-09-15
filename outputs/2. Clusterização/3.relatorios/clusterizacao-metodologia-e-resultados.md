# Segmentação de Clientes por Clusterização (K-Means) — Metodologia e Resultados

*Documento de apoio para apresentação ao cliente — descreve como a segmentação de clientes foi construída e o que ela encontrou.*

---

## Sumário Executivo

Para apoiar a diferenciação de preço por perfil de cliente (uma das oportunidades mapeadas no diagnóstico), agrupamos os **7.050 clientes ativos** da Vibra Lubrax em **4 segmentos**, usando um algoritmo de clusterização (K-Means) sobre 5 variáveis de comportamento de compra. Os segmentos foram depois cruzados com família de produto e frequência de compra, gerando **40 combinações práticas** que servem de base para uma tabela de preços diferenciada.

Este documento explica, em ordem: (1) o que é clusterização e como o método escolhido funciona; (2) quais dados entraram na conta e por quê; (3) o caminho até o resultado final; (4) os 4 segmentos encontrados e o que cada um representa; (5) limitações e próximos passos.

---

## 1. Objetivo

**Pergunta de negócio:** existem grupos de clientes suficientemente diferentes entre si para justificar uma política de preço diferenciada — em vez de uma régua única para todos os 7.050 clientes?

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

Fonte: exportação do dashboard Tableau "Sell in — Lubrificantes" (Azure Synapse), período de janeiro/2023 a setembro/2026, 253.624 registros de movimento. Cada linha foi classificada como venda, devolução provável, ajuste ou inconsistência, com base no sinal de volume e receita. Apenas as **vendas elegíveis** (volume e receita líquida positivos) entram no cálculo das variáveis de comportamento.

A pedido do cliente, a **família de produto AV foi excluída da análise** (tratada à parte, fora do escopo desta segmentação) — isso remove ~24% do volume total da base e 175 clientes que só compravam produtos AV (sem mais nenhuma transação elegível para o modelo).

Os dados foram agregados por cliente (`Código Cliente`), chegando a uma tabela de **7.050 clientes** (após excluir AV e cortar outliers extremos de volume e preço, percentis 1%–99%).

### 3.2 As 5 variáveis escolhidas

| Variável | O que representa | Como é calculada |
|---|---|---|
| **Volume** | Porte do cliente | Soma do volume (m³) de todas as vendas elegíveis (sem AV) |
| **Preço médio ponderado** | Quanto paga, em média, por m³ (todos os produtos misturados) | `receita líquida total ÷ volume total` — nunca a média simples de preços por venda |
| **Margem Bruta (%)** | Quão lucrativo é o cliente | `lucro de reposição total ÷ receita líquida total` |
| **Produtos** | Diversidade de produtos comprados | Nº de `Código Material` distintos por cliente |
| **Recência** | Há quantos dias o cliente não compra | Prioriza a base de pedidos (mais recente); usa a última compra da base de vendas como alternativa quando não há pedido |

**Variáveis testadas e descartadas, com o motivo de cada uma:**

| Variável | Por que ficou fora |
|---|---|
| `frequencia_mensal` | Versão original (transações ÷ meses ativos) inflada por pedidos faturados em várias remessas/dias. Corrigida depois (`frequencia_mensal_corrigida`, via `pedidos.csv`) e retestada por ablação: melhora silhueta e Davies-Bouldin, mas dissolve o cluster Especial dentro do Pequeno — mantida como enriquecimento, não como feature (ver seção 4.1) |
| `taxa_devolucao` | Removida a pedido do cliente |
| `receita_liquida_total`, `lucro_reposicao_total` | Correlação de 0,99 e 0,96 com volume — "porte disfarçado" de outra forma |
| `transacoes`, `meses_ativos` | Quase constantes/redundantes entre si (correlação 0,94) |
| `intensidade_desconto` (desconto ÷ receita bruta) | Testada por ablação: piorava a separação dos clusters (silhueta 0,295 vs. 0,335) e quase não reorganizava os clientes (98% ficavam no mesmo grupo) — não trazia informação nova de segmentação |
| `concentracao_familia` (% do volume na família principal) | Fortemente anti-correlacionada com `produtos` (-0,75). Testes mostraram que manter as duas juntas piorava o resultado; optamos por manter `produtos` (mais simples de explicar ao time comercial) |
| `setor_industrial_cliente` | 93% dos clientes numa única categoria ("Consumidor") — não discrimina nada |

Nenhuma das 5 variáveis finais tem correlação (Spearman) ≥ 0,90 entre si — não há redundância no conjunto usado.

*Ver figura anexa: `5.Figures/01_correlacao_spearman_modelo.png`.*

---

## 4. O caminho até o resultado final

Processo iterativo, sempre testando por evidência (mesma população, mesmo *k*, variando uma coisa por vez) em vez de assumir que "mais variáveis é melhor":

| Etapa | O que foi testado | O que aconteceu |
|---|---|---|
| 1ª rodada | *k* escolhido automaticamente pela maior silhueta, features originais sem tratamento de outlier | Pareceu "perfeito" (silhueta ~0,98), mas isolou uma dúzia de clientes extremos e jogou quase todo mundo num único grupo — estatisticamente "ótimo", inútil para negócio |
| Rodadas seguintes | Cortamos outliers (percentis 1%–99% de volume e preço); testamos *k*=4 e *k*=5 com 5 e depois 6 features (incluindo diversidade de produtos) | Segmentações comercialmente utilizáveis; adicionar diversidade de produtos ajudou |
| Revisão de qualidade de dado | Identificamos que `frequencia_mensal` estava inflada por pedidos fraturados em várias remessas — removida | Modelo ficou mais confiável, mesmo com uma variável a menos (revisitada depois — ver seção 4.1) |
| Fase 2 — novas candidatas | Testamos recência, concentração de família e intensidade de desconto (todas passaram no filtro de correlação) | Recência entrou; concentração e intensidade de desconto foram descartadas por ablação (ver seção 3.2) |
| Exclusão da família AV | Pedido do cliente — removida da base usada no modelo | 175 clientes "só AV" saíram do modelo |
| Remoção de `taxa_devolucao` | Pedido do cliente | Modelo passou a ter 5 features |
| Escolha de *k* | Comparamos *k*=3 e *k*=4 na população final | *k*=4 tem silhueta um pouco menor que *k*=3 (0,32 vs. 0,36), mas revela um segmento de negócio real — ver seção 5 |

**Resultado final:** 7.050 clientes, *k*=4, silhueta 0,3186 (aceitável), Davies-Bouldin 1,1048 (aceitável).

### 4.1 Frequência de compra corrigida: revisitada e ainda descartada como feature

O problema que tirou `frequencia_mensal` do modelo (pedidos faturados em várias remessas inflando a contagem) foi corrigido depois — `frequencia_mensal_corrigida` conta pedidos únicos (`DOC_VENDA`) via `pedidos.csv`, e é o que usamos como enriquecimento (seção 5.1, nível de frequência). Mas essa versão corrigida nunca tinha sido retestada como feature do K-Means. Mesmo critério de sempre: mesma população, mesmo *k*, com/sem.

| | Silhueta | Davies-Bouldin | ARI vs. atual |
|---|---|---|---|
| Atual (5 features) | 0,3186 | 1,1048 | — |
| + `frequencia_mensal_corrigida` (6 features) | **0,3436** (melhor) | **1,0787** (melhor) | 0,554 |

Diferente de todas as outras candidatas testadas neste documento, essa **melhora as duas métricas ao mesmo tempo**, com realocação real de clientes (ARI=0,554). Olhando para onde os clientes vão parar, porém: **93,8% do cluster Especial** — o achado central desta segmentação — e **95,7% do cluster Pequeno** são absorvidos pelo mesmo cluster maior, cujo preço médio (R$ 13.391/m³) fica perto do Pequeno, não do Especial. O sinal de preço que define o Especial se dilui dentro de um grupo genérico.

**Decisão:** mantido o modelo de 5 features. Métricas agregadas um pouco melhores não compensam perder o segmento de negócio mais acionável do projeto. `frequencia_mensal_corrigida` segue como enriquecimento, não como feature de treino.

*Ver `2.Kmeans.ipynb`, seção 14, para o teste completo (correlação, ablação e o cruzamento cluster atual × cluster candidato).*

---

## 5. Resultado: os 4 segmentos de clientes

| # | Segmento | Clientes | % | Volume médio | Preço médio | Margem | Produtos | Recência (dias) |
|---|---|---|---|---|---|---|---|---|
| 0 | **Pequeno** | 4.656 | 66,0% | 3,6 | 12.326 | 16,4% | 5,4 | 421 |
| 1 | **Grande** | 265 | 3,8% | 87,8 | 12.464 | 15,1% | 23,9 | 110 |
| 2 | **Especial** | 998 | 14,2% | 2,9 | **18.514** | **14,3%** | 5,2 | 249 |
| 3 | **Médio** | 1.131 | 16,0% | 27,4 | 13.037 | 16,0% | 17,7 | 117 |

**Leitura de cada grupo:**

- **Pequeno** (grosso da carteira): volume baixo, poucos produtos, muito tempo sem comprar (recência ~14 meses). Preço e margem na média.
- **Grande**: menor grupo, mas o mais valioso em volume — compram ~25× mais que o Pequeno, com muito mais produtos e recência baixa (compram com frequência).
- **Médio**: mesmo perfil do Grande, em escala intermediária.
- **Especial** *(achado do modelo, não um rótulo de tamanho)*: mesmo volume baixo do Pequeno, mas paga **~50% mais caro por m³** e tem a **menor margem de todos os grupos** — não estão recebendo os descontos que o resto da base pequena recebe, apesar de comprarem um pouco mais recentemente que o grupo Pequeno. É o segmento mais acionável para revisão de política de desconto por volume: ou o preço deles está desalinhado, ou há uma razão de produto/canal que precisa ser investigada antes de qualquer ação.

*Nomes são sugestões baseadas nos perfis numéricos — precisam de validação com o time comercial antes de virarem rótulo oficial.*

### 5.1 Enriquecimento: família de produto, frequência (corrigida), margem e CNAE

Os 4 segmentos dizem **quem se parece com quem** em termos gerais. Para virar referência prática de preço, cruzamos cada segmento com quatro dimensões que o modelo não usa diretamente (ou usa só como número, não como categoria fácil de comunicar):

- **Família de produto** que o cliente mais compra.
- **Nível de frequência** (Ocasionais / Regulares / Frequentes) — mas agora a partir de `frequencia_mensal_corrigida`, que conta **pedidos únicos** (`DOC_VENDA` de `pedidos.csv`) em vez de linhas de remessa da base de vendas. Isso corrige o mesmo problema que tirou a frequência do modelo como feature: um pedido faturado em 3 remessas contava como 3 compras, não 1. Depois da correção, a distribuição de níveis mudou bastante (Ocasionais subiu de 38,8% para 68,3%, Frequentes caiu de 16,9% para 5,1%).
- **Nível de margem** (Baixa / Média / Alta) — classificação de `margem_pct_ponderada` (uma das 5 features do modelo) em tercis da população: Baixa < 13%, Média 13%–18%, Alta ≥ 18% (cada faixa com ~1/3 da base). Serve para comunicar a margem de forma mais direta que o percentual bruto.
- **CNAE** (via cruzamento CNPJ → Receita Federal) — substitui `segmento_b2b` como leitura de setor. Cobertura de 96,8% dos clientes (o restante é pessoa física). Mais granular e sem o "buraco negro" das categorias OUTROS/OUTRAS INDÚSTRIAS (juntas, quase 1.500 clientes que o `segmento_b2b` não discriminava). Para não ficar granular demais, usamos o CNAE por **divisão** (nível oficial da estrutura CNAE 2.0, entre subclasse e seção — 2 primeiros dígitos do código): "Transporte rodoviário de carga", "...de passageiros" e "...de produtos perigosos" (3 subclasses) viram uma só linha, "Transporte terrestre". O código completo (7 dígitos) continua disponível na base para quem precisar do detalhe.

A tabela de preço por segmento usa as mesmas **10 famílias** de maior volume das visões exploratórias acima, sem bucket "Outras" — aceitando cobertura parcial (69,6% do volume total). Isso dá **40 combinações viáveis** (4 clusters × 10 famílias, todas com 10 clientes ou mais — nenhuma célula precisou ser descartada).

**Top 10 famílias — quanto pesam no volume e na receita de cada grupo:** o Especial tem menos concentração nas famílias líderes — TOP TURBO (a família líder da base) cai para ~15% do volume e ~12% da receita do Especial, contra ~30% nos outros três grupos — e a **cobertura do top 10** (soma das % dessas 10 famílias) cai para **~52% do volume e ~45% da receita** no Especial, contra **~65%–73%** nos outros três grupos. Quase metade do volume/receita do Especial vem de fora das 10 famílias mais vendidas da base. O mix de produtos do Especial já é um pouco mais disperso, mas isso sozinho não explica a diferença de preço/margem: o achado de margem unitária (abaixo) mostra que a queda de margem acontece em toda família, dispersa ou não.

*Ver figura anexa: `2.segmentacao_hibrida/top10_familias_volume_receita_cluster.png`.*

**Top 10 famílias — só dentro do cluster Especial:** o top 10 acima é o mesmo para os 4 clusters. Recalculando o top 10 usando só as transações do Especial, aparece um conjunto parcialmente diferente: 4 das 10 famílias (**TOP TURBO AVANTE**, **LITHPLUS EP**, **TRM 5 PLUS**, **LITH EP**) não aparecem no top 10 da base toda, e 4 famílias do top 10 geral (FLUIDO PARA RADIADOR, HYDRA, UNITRACTOR, UTILE) nem entram no top 10 do Especial. O Especial não compra só menos concentrado — compra produtos parcialmente diferentes. Esse top 10 próprio cobre 60,4% do volume e 56,8% da receita do Especial (mais que os 52,0%/44,8% do top 10 geral aplicado a ele).

*Ver figura anexa: `2.segmentacao_hibrida/top10_familias_especial.png`.*

**Achado do nível de margem:** o cluster **Especial** tem 48,5% dos seus clientes na faixa **Baixa** (contra 29%–35% nos outros três grupos) e só 23,4% na faixa **Alta** — a menor proporção dos quatro. Confirma, cliente a cliente (não só na média do grupo), que a margem apertada do Especial é um padrão consistente na maioria dos clientes, não puxada por poucos casos extremos.

*Ver figura anexa: `2.segmentacao_hibrida/nivel_margem_por_cluster.png`.*

**Onde esses clientes estão concentrados?** Dentro do Especial, clientes de Mato Grosso/MS estão mais concentrados na faixa de margem Baixa (57,7% deles, contra 46,8% do resto do grupo), e o frete médio já é o mais alto justamente nessa faixa (R$ 655/m³ contra R$ 558/m³ na faixa Alta). Reforça que vale investigar o custo logístico desses clientes específicos antes de tratar isso como desconto comercial mal aplicado.

**Margem unitária — top 10 específico do Especial:** as duas famílias mais caras do top 10 do Especial — **TOP TURBO AVANTE** e **LITHPLUS EP** — estão na faixa de margem **Baixa** (11%–12%), não na Alta. Já GEAR e HYDRA XP, com preço no meio da tabela, são as únicas com margem **Alta** (19,5%–20,5%). Das 4 famílias exclusivas do Especial, 3 (TOP TURBO AVANTE, LITHPLUS EP, TRM 5 PLUS) estão na faixa Baixa — por quê? Investigamos a seguir.

*Ver figura anexa: `2.segmentacao_hibrida/margem_unitaria_top10_especial.png`.*

**Margem vs. custo (top 10 do Especial):** cada produto como uma bolha (eixo = margem % e custo % do preço, tamanho = margem unitária em R$/m³, cor = nível de margem). As bolhas vermelhas (margem Baixa) ficam concentradas no canto de maior custo relativo — exatamente onde estão as famílias exclusivas mais caras do Especial.

*Ver figura anexa: `2.segmentacao_hibrida/bolha_margem_custo_especial.png`.*

**O frete explica a margem baixa desses produtos?** Testamos: qual o frete médio dos clientes que compram os produtos de margem Baixa (LITHPLUS EP, TRM 5 PLUS, TOP TURBO AVANTE, TRM 5), dentro do próprio Especial, comparado aos que compram os outros produtos do top 10? **Não é frete.** O frete médio de quem compra os produtos de margem Baixa (R$ 559/m³, n=440) é, na verdade, **menor** que o de quem compra os outros produtos do top 10 (R$ 678/m³, n=411) — o frete não explica a margem apertada desses 4 produtos especificamente. O achado de frete/UF segue válido no nível agregado do cluster (parágrafo acima), mas não é a causa da margem baixa desses produtos em particular.

*Ver figura anexa: `2.segmentacao_hibrida/frete_produtos_margem_baixa.png`.*

**Produtos com margem Baixa no Especial: quantos são, e onde são vendidos.** 4 dos 10 produtos do top 10 do Especial caem na faixa de margem Baixa. 440 clientes (44,1% do Especial) compram pelo menos um desses 4 produtos, espalhados pelas mesmas UFs que já vimos antes (SP, MG, CE e MT concentram a maior parte) — não é um problema geográfico isolado.

*Ver figura anexa: `2.segmentacao_hibrida/clientes_uf_produtos_margem_baixa.png`.*

**Por que a margem desses 4 produtos é baixa?** Testamos a hipótese comercial (desconto mal calibrado no Especial): comparamos a margem desses mesmos 4 produtos nos outros 3 clusters.

| Produto | Pequeno | Grande | Especial | Médio |
|---|---|---|---|---|
| LITHPLUS EP | 10,0% | 8,6% | **11,0%** | 9,4% |
| TRM 5 PLUS | 10,1% | 9,9% | **11,1%** | 10,9% |
| TOP TURBO AVANTE | 9,7% | 12,9% | 12,0% | 11,3% |
| TRM 5 | 14,4% | 15,7% | 12,9% | 15,4% |

**Achado: não é (só) o Especial.** Esses 4 produtos têm margem apertada em **todos os 4 clusters** (8,6% a 15,7%) — não é uma questão de logística, região ou desconto mal aplicado no Especial. Em 2 dos 4 produtos (LITHPLUS EP e TRM 5 PLUS) a margem do Especial é a **melhor** entre os 4 clusters; em TOP TURBO AVANTE fica no meio; só TRM 5 é consistentemente pior no Especial. A causa mais provável é o **custo de aquisição do próprio produto** (as formulações "PLUS"/"AVANTE" sugerem insumos mais caros), não algo específico do Especial. O que arrasta a média de margem do Especial para baixo é o **mix**: o grupo compra proporcionalmente mais desses produtos inerentemente de margem apertada do que os outros três clusters — não porque recebe um preço ou desconto piores nesses produtos especificamente.

### 5.2 Onde focar primeiro

A receita não se distribui igualmente entre as 40 combinações — **16 delas já cobrem 80% da receita total**. Faz sentido validar e agir sobre essas primeiro, em vez de tentar cobrir as 40 de uma vez.

### 5.3 Quanto da base é agro de verdade (preparação para análise de safra)

`segmento_b2b` tagueava 3,9% da base como AGRONEGOCIO — categoria que misturava agricultura de verdade (soja, café, laranja...) com pecuária, pesca, madeira e transporte ligado ao agro. Usando CNAE seção A (divisões 01 agricultura/pecuária, 02 produção florestal, 03 pesca/aquicultura), isolamos quem é agro de verdade: **4,2% da base** (295 clientes), distribuídos de forma parecida entre os 4 segmentos (não concentrados em nenhum específico). Esse recorte é a base para o próximo passo de análise de safra (seção 6).

**O que os clientes AGRO compram, por segmento:** os clientes AGRO não compram todos igual — em `4.Segmentacao-Hibrida.ipynb` cruzamos, para o subconjunto de clientes AGRO, a família de produto por segmento:

| Segmento | Padrão de compra AGRO (dentro do top 10, cobertura 68%–80% do volume AGRO) |
|---|---|
| Pequeno | 45% TOP TURBO + 21% UNITRACTOR — mix parecido com a média geral |
| Grande | 43% TOP TURBO, mas **26% HYDRA XP** — bem acima dos outros segmentos |
| Especial | Diferente dos demais: **36% UNITRACTOR** (o maior de todos) e só 17% TOP TURBO (os outros ficam em 43%–45%) |
| Médio | 44% TOP TURBO + 17% UNITRACTOR — parecido com o Pequeno |

*Ver figura anexa: `2.segmentacao_hibrida/produtos_agro_por_cluster.png`.*

### 5.4 Maiores segmentos de CNAE por receita (não só por nº de clientes)

As visões de CNAE acima são por **contagem de clientes** — um CNAE pode ter poucos clientes mas concentrar muita receita. Olhando por receita, cluster a cluster, e já na visão simplificada por divisão, "Transporte terrestre" é a maior divisão em **todos os 4 segmentos**, com concentração ainda mais forte do que no nível de subclasse: 39,2% da receita do Pequeno, 41,7% do Grande, 40,5% do Médio e **48,8% do Especial** — quase metade de toda a receita desse grupo vem de uma única divisão de CNAE, a maior concentração entre os quatro.

Também vale notar, olhando o heatmap de preço por cluster × top 10 famílias (anexo, sem bucket "Outras"): o grupo Especial paga mais em **todas as 10 famílias, sem exceção** (chega a R$ 18.057/m³ em UTILE, quase 50% mais caro que a média dos outros três grupos nessa mesma família) — reforça que o achado é um padrão de preço do cliente, não um efeito de mix de produto.

**Preço no top 10 específico do Especial:** olhando o preço só nas famílias que o próprio Especial mais compra (incluindo as 4 exclusivas), as 2 famílias exclusivas com maior volume são também as mais caras de toda a lista — **TOP TURBO AVANTE** (R$ 22.903/m³) e **LITHPLUS EP** (R$ 22.436/m³), acima até do pico visto no top 10 geral (R$ 18.057/m³ em UTILE). O mix específico do Especial não é só diferente — é mais caro ainda.

*Ver figura anexa: `2.segmentacao_hibrida/preco_top10_familias_especial.png`.*

**Preço por UF, top 10 do Especial:** abrindo o achado de UF por produto (células com menos de 10 clientes ficam em branco), Mato Grosso é a UF mais cara em praticamente todo produto do Especial onde há amostra suficiente — chegando a **R$ 29.761/m³ em TOP TURBO AVANTE** e **R$ 26.869/m³ em LITHPLUS EP**. O achado de frete/UF não é só um efeito de composição de cluster — aparece produto a produto.

*Ver figura anexa: `2.segmentacao_hibrida/preco_uf_top10_especial.png`.*

**Preço por UF, comparando os 4 clusters:** o mesmo recorte para os 4 clusters lado a lado (top 10 geral, mesma escala de cor). O painel do Especial é visivelmente mais escuro (mais caro) que Pequeno, Grande e Médio em praticamente toda combinação produto × UF — não é efeito de uma UF ou produto isolado, é o cluster inteiro que paga mais.

*Ver figura anexa: `2.segmentacao_hibrida/preco_uf_4clusters.png`.*

*Ver figura anexa: `2.segmentacao_hibrida/receita_transporte_por_cluster.png`.*

### 5.5 UF do cliente por segmento — o Especial está concentrado nalguma região?

Testamos a UF do cliente (`Estado Cliente` na base bruta, 0 nulos — não precisou do cruzamento com a Receita Federal) como enriquecimento, especificamente para checar se o preço mais alto do Especial tem componente geográfico (frete):

- **Mato Grosso: 11,2% dos clientes do Especial, contra 2,6% na base toda — 4,4x mais representado.**
- **Mato Grosso do Sul: 4,4% contra 1,6% na base toda — 2,7x mais representado.**

Os dois estados são do Centro-Oeste, longe das refinarias e centros de distribuição do litoral. Isso é uma pista concreta de que parte do preço mais alto do Especial pode ser **frete**, não só política comercial — vale confirmar com o time de logística antes de qualquer ajuste de preço nesse grupo.

*Ver figura anexa: `2.segmentacao_hibrida/uf_por_cluster.png`.*

*Ver também: `2.segmentacao_hibrida/uf_sobrerrepresentacao_especial.png` (ranking de sobrerrepresentação por UF, com linha de referência 1,0x).*

### 5.6 Frete: testado como feature, mantido como enriquecimento

Testamos `frete_por_m3` (frete ÷ volume, limpa de outliers p01–p99) diretamente como 6ª feature do K-Means, mesma população e mesmo *k*:

| | Silhueta | Davies-Bouldin | ARI vs. atual |
|---|---|---|---|
| Atual (5 features) | 0,3186 | 1,1048 | — |
| + `frete_por_m3` (6 features) | 0,2462 (pior) | 1,3742 (pior) | 0,694 |

**Descartada como feature** — piora as duas métricas de qualidade ao mesmo tempo, mesmo com realocação real de clientes (mesmo padrão de `intensidade_desconto`, seção 3.2). Mantida como enriquecimento, onde já mostrou valor:

| Segmento | Frete médio (R$/m³) |
|---|---|
| Pequeno | 522 |
| Grande | 465 |
| **Especial** | **609** |
| Médio | 516 |

E, dentro do próprio Especial, o padrão de UF se confirma: clientes de Mato Grosso/MS pagam **R$ 919/m³** de frete contra R$ 552/m³ do resto do grupo (+66%) — a maior diferença entre os 4 segmentos (no Médio, só 3%). Não é só "o Especial tem mais gente de MT/MS": dentro do próprio grupo, MT/MS paga desproporcionalmente mais frete.

*Ver figura anexa: `2.segmentacao_hibrida/frete_por_cluster.png`.*

*Ver também: `2.segmentacao_hibrida/frete_mtms_vs_resto_por_cluster.png` (frete médio, Mato Grosso/MS vs. resto da base, dentro de cada segmento).*

---

## 6. Limitações e próximos passos

- **Os nomes dos segmentos são hipóteses de trabalho**, não uma taxonomia validada — precisam de checagem com o time comercial.
- **O grupo Especial precisa de investigação qualitativa**: os dados mostram *que* esses clientes pagam mais e têm menos margem, e a análise de UF (seção 5.5) já dá uma pista — Mato Grosso e Mato Grosso do Sul são 4,4x e 2,7x mais representados no grupo, sugerindo frete/logística como parte da causa. Mas ainda não mostram a causa completa (canal, mix de produto específico, política comercial regional, etc.) — importante confirmar antes de qualquer ajuste de preço.
- **Comportamento de compra muda com o tempo.** Recomenda-se reprocessar essa segmentação periodicamente (sugestão: trimestral) e comparar se os grupos continuam consistentes.
- **A família AV está fora desta análise** por decisão do cliente — se algum dia fizer sentido reincorporá-la, o modelo precisa ser retreinado do zero (a composição de carteira muda).
- **Isso é um ponto de partida, não substitui o julgamento comercial.** Os dados mostram padrões; cabe ao time decidir o que fazer com eles.
- **Próximo passo natural:** testar elasticidade de preço por segmento (ver seção de Sensibilidade a Preços do diagnóstico).
- ~~Avaliar o cruzamento externo CNPJ → CNAE~~ — **feito** (seção 5.1/5.3): 96,8% de cobertura, substituiu `segmento_b2b` como enriquecimento (`outputs/4.CNAE/build_cnae_lookup.py`).
- **Próximo passo (não implementado ainda):** cruzar o CNAE dos clientes agro (4,2% da base, seção 5.3) com o calendário de safra da cultura correspondente, para testar uma feature de sazonalidade específica desse recorte.

---

## Anexo — arquivos de referência

**Atualizados com o modelo atual (k=4, 5 features):**

| Arquivo | Conteúdo |
|---|---|
| `5.Figures/01_correlacao_spearman_modelo.png` | Heatmap de correlação das 5 features do modelo final |
| `5.Figures/02_comparativo_k.png` | Varredura de k=2 a 10 (silhueta, Davies-Bouldin, elbow) |
| `5.Figures/03_silhouette_by_cluster.png` | Silhueta detalhada por cliente, agrupada por cluster |
| `5.Figures/04_kmeans_pca_2d.png` | Projeção PCA 2D dos 4 clusters com centroides |
| `5.Figures/05_features_boxplot.png` | Distribuição de cada feature por cluster |
| `2.segmentacao_hibrida/` | Matriz cluster × família, Pareto, top famílias, frequência/CNAE/agro/UF por cluster, heatmaps de margem e preço (todos recalculados com k=4) |
| `segmentacao_clientes_kmeans.csv`, `resumo_clusters.csv`, `recomendacoes_pricing.csv` | Segmentação final por cliente e resumos, na raiz de `outputs/2. Clusterização/` |
| `relatorio_tecnico_clusterizacao_vibra_lubrax.html` | Relatório técnico completo (gerado pelo `notebooks/7.Relatorio-Tecnico.ipynb`), reescrito com o modelo final |
| `relatorio_comercial_segmentacao_vibra_lubrax.html` | Versão em linguagem simples para o time comercial, reescrita com o modelo final |

**Pendentes de atualização** (ainda refletem o modelo anterior — Teste 5, k=5, 6 features, com AV incluída):

| Arquivo | Conteúdo |
|---|---|
| `como-construimos-as-features.html` | Passo a passo de como as variáveis foram calculadas |
| `mapa_modelos_kmeans.html` | Comparação entre modelo oficial e um modelo sem preço — o experimento em si não existe mais no `2.Kmeans.ipynb` atual; precisa decisão sobre recriá-lo ou arquivar a página |
| `clusterizacao-k=5-5f.xlsx`, `clusterizacao-k=5-6f.xlsx` | Planilhas com os resultados do modelo anterior |
| `4.apresentacao/*.png`, `4.apresentacao/*.pptx` | Figuras e slides de apresentação ao cliente |
