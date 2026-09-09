# Vibra Lubrax — Segmentação de Clientes para Pricing

Documentação consolidada do projeto. Este é o único arquivo em `docs/` — reúne o que antes estava
espalhado em 5 documentos (linhagem, dicionário de dados, plano de EDA, estratégia de clusterização e
guia de métricas), atualizado para refletir o estado real do projeto em setembro de 2026.

> **Para o passo a passo completo da análise** (metodologia, os 5 testes de clusterização, resultado
> final, segmentação híbrida), leia `relatorios/relatorio_tecnico_clusterizacao_vibra_lubrax.html`
> (gerado a partir de `notebooks/7.Relatorio-Tecnico.ipynb`). Este README foca em **dados**: de onde
> vêm, o que significam, como foram preparados.

## Estrutura de pastas

```text
.
├── docs/README.md              # este arquivo
├── inputs/raw/                 # base principal, sem edição
├── notebooks/                  # 1.EDA_Kmeans, 2.Kmeans, 4.Segmentacao-Hibrida, 7.Relatorio-Tecnico
├── outputs/                    # organizado por etapa da análise
│   ├── cache/                  # cache da base bruta
│   ├── 1. EDA/                 # dataset agregado por cliente, reconciliação
│   ├── 2. Clusterização/       # resultados do K-Means + segmentação híbrida (ver seção 7)
│   └── 3.Elasticidade/         # próxima etapa (ainda não iniciada)
└── Script/                     # tema visual Volix (matplotlib/Jupyter)
```

## 1. Fonte e linhagem dos dados

### Arquivo atual (usado em toda a análise)

- Caminho: `inputs/raw/base_Lubrax_origem.xlsx`, aba `Base Exportavel (1)`
- **253.624 registros, 110 colunas físicas (108 nomes únicos)**
- **Período: 01/01/2023 a 01/09/2026** (confirmado diretamente na coluna `Data Venda`, sem nulos)
- Duplicidades no cabeçalho: `Index`/`Index.1` e `prod_categoria_3`/`prod_categoria_3.1` — o pandas
  materializa as segundas ocorrências com sufixo `.1`
- Contém CNPJ e nome de cliente — tratar como informação corporativa sensível

> **Nota histórica:** versões anteriores da documentação deste projeto (e um README duplicado, já
> removido) descreviam um arquivo diferente — `inputs/raw/sell_in_lubrificantes_base.csv`
> (160.676 registros, período "agosto/2025 a agosto/2026"). Esse arquivo **não existe mais** no
> projeto; foi substituído pelo Excel acima antes da análise de clusterização começar. Todos os
> números deste projeto (EDA, K-Means, segmentação híbrida) usam o Excel.

### De onde vêm os dados (Tableau → Synapse)

```text
Azure Synapse Analytics
  → view LDW.VW_SELLIN
  → SQL personalizado do Tableau (107 campos, sem WHERE)
  → extração publicada "Sell in - Lubrificantes"
  → cálculos, agregações e filtros das planilhas
  → planilha "Base Export Excel (Filtrar antes)"
  → inputs/raw/base_Lubrax_origem.xlsx
```

- Plataforma: Azure Synapse Analytics, servidor `syn-dtan-pdados-ondemand.sql.azuresynapse.net`
- Objeto consultado: `LDW.VW_SELLIN` (schema `LDW`, view `VW_SELLIN`), modo extração
- O SQL do Tableau não filtra registros (sem `WHERE`/`JOIN`), mas a definição interna da view não é
  visível — ela pode conter filtros/regras não documentados aqui
- **Limitações de acesso:** a conta usada permite visualizar e exportar, mas não editar a conexão,
  consultar o Synapse diretamente, ver a definição da view, ou baixar a extração `.hyper`/`.tdsx`
- Por isso os dados **não devem ser descritos como cópia do banco** — são uma exportação de planilha
  Tableau já pós-processada

**Pendências para o negócio confirmar** (nenhuma resposta ainda):
nome do banco na conexão · definição SQL de `LDW.VW_SELLIN` · fontes que alimentam essa view ·
processo/periodicidade de carga · disponibilidade do `.hyper`/`.tdsx` original.

## 2. Dicionário de dados

Inferido pelos nomes dos campos, pelo SQL visível no Tableau e pelo perfil da planilha — descrições de
negócio ainda precisam de validação com o responsável pelos dados.

### Perfil de qualidade observado

- Tipos após `pandas.read_excel`: 51 `float64`, 29 `int64`, 28 textos, 1 data, 1 coluna mista
  (`CPV Rep por M³`, requer coerção explícita)
- `Index` é único e preenchido em todas as linhas (rastreabilidade de exportação, **não** chave de
  negócio); `Index.1` é constante (`1`)
- `prod_categoria_3` e `prod_categoria_3.1` são idênticas linha a linha — a segunda pode ser removida
  da camada analítica (mantendo ambas no arquivo bruto)
- Nulos relevantes: `incoterms` (~0,95%), `% Dif CPV Contab vs Rep` / `CPV Contab vs Rep` (~3,79%),
  `CPV Contábil por M³` / `Receita Liquida por m³` (~2,38%), `Margem Reposição + CTLM` (~2,39%),
  `Margem Contábil + CTLM` (~2,45%)
- 26 colunas constantes no recorte atual (`Canal Owner`, `Canal`, `DIR`, `GE`, `CT`, `LM`, `Nexus`,
  `Total CT LM`, `Qtd de Clientes` e várias medidas auxiliares iniciadas por ponto) — sem variância
  útil para clusterização, devem ser excluídas dos modelos

### Tipos recomendados na camada analítica

| Grupo | Tipo recomendado | Observação |
|---|---|---|
| `Data Venda` | `datetime64` | Competência mensal da venda |
| CNPJ e códigos (cliente/material/base/município/produto) | `string` | Identificadores, não grandezas numéricas |
| Hierarquias, canal, localização, produto, segmentação | `category`/`string` | `category` reduz memória com baixa cardinalidade |
| Valores financeiros, custos, margens, preços, volume | `float64` | Validar unidade, sinal e regra de agregação antes do uso |
| Contagens e indicadores inteiros | `Int64` | Tipo anulável quando houver ausências |
| `Index` | `Int64` | Controle de exportação, não chave de negócio |

### Como interpretar a coluna "Origem" nas tabelas abaixo

- **SQL direto:** aparece explicitamente na consulta da view `LDW.VW_SELLIN`, mesmo renomeado no Tableau
- **Tableau:** campo criado ou calculado depois da consulta SQL
- **Não confirmado:** sem evidência suficiente sem acesso ao workbook

### Identificação e tempo

| Campo | Descrição | Origem SQL | Origem |
|---|---|---|---|
| `Index` / `Index.1` | Índices da exportação; `Index` único, `Index.1` constante | não aparece | Tableau |
| `Data Venda` | Data de referência da venda | `TRY_CAST(DATA_VENDA AS DATE)` → `Dt Venda` | SQL, renomeado |
| `Código Cliente` | Identificador do cliente | `COD_CLIENTE` | SQL direto |
| `Nome Cliente` | Razão social/nome do cliente | `NOME_CLIENTE_` | SQL direto |
| `CNPJ Cliente` | CNPJ do cliente (ler como texto) | `CNPJ_CLIENTE` | SQL direto |
| `Código Material` | Identificador do material/produto | `COD_MATERIAL` | SQL direto |
| `Material` | Descrição do material/produto | `ISNULL(PRODUTO, DSC_MATERIAL)` | Expressão SQL |
| `Prod - Código` | Código do produto | `CODIGO` | SQL direto |

### Estrutura comercial e cliente

| Campo | Descrição | Origem SQL | Origem |
|---|---|---|---|
| `Canal Owner` | Agrupamento responsável pelo canal | `CANAL_OWNER` | SQL direto |
| `Canal` | Canal comercial | `CANAL` | SQL direto |
| `DIR` | Nível organizacional de diretoria | `VP` | SQL, renomeado |
| `GE` | Nível organizacional de gerência | `DIR` | SQL, renomeado |
| `2º Nivel` | 2º nível da hierarquia comercial | `GER` | SQL, renomeado |
| `3º Nível` | 3º nível da hierarquia comercial | `ZV` | SQL, renomeado |
| `nome_atividade` | Setor/atividade do cliente | `SETOR_ATIVIDADE` | SQL, renomeado |
| `setor_industrial_cliente` | Grupo/setor industrial do cliente | `GRUPO_CLIENTE` | SQL, renomeado |
| `País Cliente` | País do cliente | `PAIS_CLIENTE_` | SQL, renomeado |
| `Estado Cliente` | Estado do cliente | `REGIAO_CLIENTE` | SQL, renomeado |
| `Município Cliente` | Município do cliente | `MUNICIPIO_CLIENTE` | SQL, renomeado |
| `incoterms` | Condição logística/comercial Incoterm | `DSC_INCOTERMS` | SQL, renomeado |
| `Segmentação B2B` | Segmentação comercial B2B | `SEGMENTO_B2B` | SQL, renomeado |
| `Clientes Risel?` | Indicador exibido pelo Tableau (coluna própria) | não aparece com esse nome | Tableau/não confirmado |
| `cliente_risel` | Indicador de cliente Risel (outra coluna) | `CLIENTES_RISEL` | SQL direto |

### Base e produto

| Campo | Descrição | Origem SQL | Origem |
|---|---|---|---|
| `Código Base` | Identificador da base operacional | `COD_BASE` | SQL direto |
| `Nome Base` | Nome da base operacional | `NOME_BASE` | SQL direto |
| `Estado Base` | Estado da base | `REGIAO_BASE` | SQL direto |
| `Municipio Base` | Município/código municipal da base | `COD_MUNICIPIO_BASE` | SQL direto |
| `Prod - Tipo de Base` | Tipo de base do produto | `TIPO_BASE` | SQL direto |
| `Tipo de Produtos (Básicos)` | Classificação básica | `TIPO_PRODUTO_BASICO` | SQL, renomeado |
| `PRODUTO_NVL4` | 4º nível da hierarquia de produto | `PRODUTO_NVL4` | SQL direto |
| `Prod - Embalagem` | Tipo/descrição da embalagem | `EMBALAGEM` | SQL direto |
| `Prod - Categoria simples` | Categoria simplificada | `CATEGORIA_SIMPLES` | SQL direto |
| `Prod - Família de Produtos` | Família do produto | `FAMILIA_PRODUTO` | SQL direto |
| `prod_categoria_1` | 1º nível de categoria | `CATEGORIA_1` | SQL direto |
| `prod_categoria_3` / `.1` | 3º nível de categoria (duplicado no Excel) | `CATEGORIA_3` | SQL direto |
| `Aplicação` | Aplicação do produto | não aparece com esse nome | Tableau/não confirmado |
| `prod_litragem` | Litragem do produto | `LITRAGEM` | SQL direto |

### Valores financeiros e de volume (origem direta ou derivada)

| Campo | Descrição |
|---|---|
| `Volume` | Volume de venda, **em m³** (confirmado cruzando `Receita líquida ÷ 'Receita Liquida por m³'` contra `Volume`: mediana da razão 1,00, 94% das linhas dentro de ±5% — ver `1.EDA_Kmeans.ipynb`, seção 5) — **feature `volume_total` do K-Means vem daqui** |
| `Receita Bruta` / `Receita líquida` | Receita bruta e líquida — **`preco_liquido_ponderado` = receita líquida ÷ volume** |
| `CPV Fechamento` / `CPV Parc` / `CPV Rep` | Custo dos produtos vendidos (fechamento, parcial, reposição) |
| `LB Contábil` / `LB Reposição` | Lucro bruto contábil e de reposição — **`margem_pct_ponderada` = LB Reposição ÷ Receita líquida** |
| `Frete` / `encargos` / `desconto` | Frete, encargos e desconto concedido |
| `CT` / `LM` / `Total CT LM` / `nx` | Componentes CT, LM e Nexus — significado de negócio a validar |
| `Preço MedNF` | Preço médio de nota fiscal |
| `Repasse ICMS` / `Repasse ICMS Total` / `repasse_pis_confis` | Repasses de impostos |
| `faturamento_real` / `percen_receita_bruta` / `receita_bruta_total` | Medidas de faturamento derivadas |
| Campos prefixados com `.` (ex: `.Receita Liquida`, `.CPV Reposição`, `.Efeito Estoque`) | Medidas auxiliares/calculadas do Tableau — o Excel traz o resultado materializado, não a fórmula original |

**Identidades verificadas em 100% das 253.624 linhas** (tolerância R$ 0,01): `.Volume = Volume`,
`.Receita Liquida = Receita líquida`, `.CPV Reposição = -CPV Rep`, `.LB Reposição = LB Reposição`,
`.Receita de Frete = Frete`, `.Receita de Encargos = encargos`,
`.Receita Liquida = .Receita Bruta + .Total Impostos`,
`.Receita Liquida sem Encargos e Frete = .Receita Liquida - encargos - Frete`,
`.LB Contábil = .Receita Liquida + .CPV Contábil`,
`.LB Reposição = .Receita Liquida sem Encargos e Frete + .CPV Reposição`,
`.Efeito Estoque = .CPV Contábil + CPV Rep`, `.LB Rep + Efeito Estoque = .LB Reposição + .Efeito Estoque`,
`LB Rep + Efeito Estoque + Encargos = .LB Rep + Efeito Estoque + encargos`.

**Atenção — nomes parecidos que NÃO são equivalentes:** `Receita Bruta` e `.Receita Bruta` coincidem em
apenas 82,41% das linhas; `CPV Fechamento` e o inverso de `.CPV Contábil` coincidem em 98,43%. Não usar
como sinônimos sem entender a regra do Tableau por trás da diferença.

### Regras para qualquer análise nesta base

1. Preservar o Excel bruto sem edição; gravar limpezas/transformações em `outputs/`.
2. Remover `Index.1` e `prod_categoria_3.1` só na camada analítica (preservar ambas no arquivo bruto).
3. Converter CNPJ e códigos (cliente/material/base/produto) para texto, mesmo vindo como inteiro.
4. Converter `Data Venda` explicitamente (`pd.to_datetime(..., dayfirst=True, errors='coerce')`).
5. Excluir colunas constantes e identificadores das features de clusterização.
6. Validar unidade, sinal e agregação antes de criar indicadores de preço/margem.
7. Não assumir que uma medida é coluna física do Synapse sem validar origem/fórmula.
8. Preço e margem agregados são **sempre ponderados** (`soma(receita) / soma(volume)`), nunca média
   simples de preços por linha.

## 3. Pipeline de preparação (implementado em `notebooks/1.EDA_Kmeans.ipynb`)

### Classificação dos movimentos (`tipo_movimento_eda`)

Regra conservadora — só classifica como venda ou devolução quando os sinais são coerentes:

| Classe | Regra | Registros | % |
|---|---|---:|---:|
| `VENDA` | Volume > 0 e receita líquida > 0 | 245.456 | 96,78% |
| `DEVOLUCAO_PROVAVEL` | Volume < 0, receita líquida < 0 e CPV de reposição < 0 | 2.068 | 0,82% |
| `AJUSTE_SEM_VOLUME` | Volume = 0 e alguma métrica financeira ≠ 0 | 1.292 | 0,51% |
| `SEM_MOVIMENTO` | Volume e métricas financeiras = 0 | 4.767 | 1,88% |
| `SINAL_INCONSISTENTE` | Combinações de sinal não cobertas acima | 41 | 0,02% |

Essa separação impede que devoluções e ajustes distorçam preços unitários. "Devolução provável" ainda
depende de confirmação por tipo de documento/natureza da operação (não disponível na base atual).

### Reconciliação financeira

13 identidades financeiras testadas com tolerância de R$ 0,01 — **todas fecharam em 100%** das
253.624 linhas (ver tabela de identidades na seção 2 acima).

### Dataset agregado por cliente

- Unidade: **cliente** (`Código Cliente`) — preços ponderados; devoluções/ajustes entram como
  taxas/valores agregados, não como preços de venda
- Resultado: **7.507 clientes, 22 colunas** (`outputs/1. EDA/kmeans_clientes_features.pkl`)
- Concentração de receita: maior cliente = 5,63% da receita; top 20 clientes = 21,67% — concentração
  relevante, mas não dependência de cliente único

## 4. Metodologia de clusterização — resumo

Documentado em detalhe em `notebooks/2.Kmeans.ipynb` e no relatório técnico. Resumo:

- **5 testes** rodados, de k=2 (5 features originais, agregação manual) até o resultado final
- **Resultado adotado: Teste 5 — K-Means, k=5, 6 features**, silhueta 0,3014 (aceitável),
  Davies-Bouldin 1,1413 (aceitável), 7.176 clientes finais (após corte de outliers 1%-99%)
- **6 features:** `volume_total` (porte), `preco_liquido_ponderado` (preço),
  `margem_pct_ponderada` (margem, **percentual**, não lucro absoluto — evita redundância com porte),
  `frequencia_mensal` (frequência), `taxa_devolucao` (comportamento), `produtos` (diversidade)
- Seleção de features guiada por correlação de Spearman entre 13 candidatas — grupos com
  correlação ≥0,90 mantiveram só 1 representante cada (ver relatório técnico, seção 5)

### Glossário rápido — silhueta e Davies-Bouldin

| Métrica | Mede | Faixa | Ideal |
|---|---|---|---|
| Silhueta | Quão mais perto um cliente está do seu cluster do que do vizinho mais próximo | -1 a +1 | > 0,5 excelente · 0,3–0,5 aceitável · < 0,3 fraco |
| Davies-Bouldin | Razão entre dispersão interna e distância entre clusters | 0 a +∞ | < 1,0 excelente · 1,0–1,5 aceitável · > 1,5 fraco |

**Armadilha a evitar:** um k pequeno que isola só os clientes mais extremos pode gerar silhueta
*altíssima* sem ser uma segmentação útil — sempre olhar também a distribuição de tamanho dos
clusters (ver Teste 1 no relatório técnico, seção 4).

## 5. Segmentação híbrida (implementado em `notebooks/4.Segmentacao-Hibrida.ipynb`)

Cruza os 5 clusters com **família de produto** (8 nomeadas + `Outras`, 100% de cobertura) e
**frequência de compra** (Ocasionais < 1,5/mês · Regulares 1,5–3,5/mês · Frequentes > 3,5/mês) para
virar uma tabela de preços operacional — 45 segmentos (cluster × família), 44 viáveis (≥10 clientes),
16 cobrem 80% da receita. Detalhes de metodologia (família por transação vs. família principal do
cliente, consolidação de células pequenas) estão no relatório técnico, seção 6.

## 6. Ideias de segmentação não implementadas (backlog)

Levantadas durante o planejamento, mas fora do escopo desta rodada — ainda não têm código associado:

- **Segmentação de produtos** por margem/demanda (volume total, margem média, preço médio,
  variabilidade de preço, concentração de vendas por produto) — apoiaria decisões de reposicionamento
  de preço e bundles/promoções.
- **Segmentação de transações** por perfil de venda (volume, margem, frete, Incoterm, sazonalidade,
  desconto por transação) — apoiaria detecção de transações anômalas e otimização de mix de pedido.
- **Segmentação geográfica + comercial** (estado do cliente × estado da base, canal, custo de frete
  típico) — apoiaria decisões logísticas e de cobertura comercial.

## 7. Onde encontrar cada coisa

| Arquivo/pasta | Conteúdo |
|---|---|
| `notebooks/1.EDA_Kmeans.ipynb` | Exploração, classificação de movimentos, reconciliação financeira, dataset agregado |
| `notebooks/2.Kmeans.ipynb` | Os 5 testes de clusterização até o resultado final |
| `notebooks/4.Segmentacao-Hibrida.ipynb` | Cruzamento cluster × família × frequência |
| `notebooks/7.Relatorio-Tecnico.ipynb` | Relatório técnico completo (fonte) |
| `outputs/1. EDA/` | Dataset agregado por cliente e artefatos de reconciliação |
| `outputs/2. Clusterização/clusterizacao-vibra-lubrax.xlsx` | Todos os resultados consolidados em 9 abas de dados |
| `outputs/2. Clusterização/segmentacao_clientes_kmeans.csv` | Segmentação final (cliente → cluster) |
| `outputs/2. Clusterização/1.Kmeans_testes/` | Artefatos de cada um dos 5 testes (auditoria/comparação) |
| `outputs/2. Clusterização/2.segmentacao_hibrida/` | Matriz cluster×família, Pareto |
| `outputs/2. Clusterização/3.relatorios/` | Relatório técnico completo (HTML) e relatório em linguagem simples para o time comercial |
| `outputs/2. Clusterização/4.apresentacao/` | Figuras em alta definição (300 DPI) usadas no relatório e no `slides/` a seguir |
| `outputs/2. Clusterização/4.apresentacao/slides/Segmentacao-Clientes-Vibra-Lubrax.html` | Apresentação para consultor comercial e cliente |
| `outputs/2. Clusterização/5.Figures/` | Figuras de diagnóstico do modelo final (silhueta, PCA, boxplot) |
