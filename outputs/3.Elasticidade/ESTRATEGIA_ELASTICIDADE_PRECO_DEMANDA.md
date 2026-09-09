# VIBRA LUBRAX — Estratégia de Modelagem de Elasticidade Preço-Demanda

**Data:** Setembro 2026  
**Projeto:** Vibra Lubrax — Segmentação de Clientes para Pricing  
**Contexto:** Lubrificantes — Base SELL IN  
**Objetivo:** Quantificar a sensibilidade da demanda a variações de preço por segmento de cliente e família de produto

---

## 📋 Índice

1. [Definição do Problema](#1-definição-do-problema)
2. [Fundamentação Teórica](#2-fundamentação-teórica)
3. [Estratégia Geral](#3-estratégia-geral)
4. [Fase 1: EDA_elasticidade (Exploração)](#4-fase-1-eda_elasticidade-exploração)
5. [Fase 2: Modelagem de Elasticidade](#5-fase-2-modelagem-de-elasticidade)
6. [Implementação & Roadmap](#6-implementação--roadmap)
7. [Métricas de Sucesso](#7-métricas-de-sucesso)
8. [Limitações e Considerações](#8-limitações-e-considerações)

---

## 1. Definição do Problema

### Por que medir elasticidade?

Na indústria de lubrificantes (B2B), o pricing diferenciado por segmento de cliente e família de produto depende de saber:

- **Se reduzir preço atrai volume?** (elasticidade > 1, demanda elástica)
- **Quanto volume aumenta para cada % de queda de preço?** (coeficiente de elasticidade)
- **Há diferenças entre segmentos?** (clusters, famílias, frequência de compra)

### Escopo

- **O quê:** elasticidade preço-demanda por **cluster + família de produto** (segmentação híbrida)
- **Quando:** análise histórica (jan/2023 – set/2026) com variação natural de preços
- **Como:** regressão log-log + testes de robustez
- **Saídas:** coeficientes de elasticidade + limites de confiança + recomendações de pricing

---

## 2. Fundamentação Teórica

### Elasticidade Preço-Demanda (EPD)

**Definição:**

```
EPD = (% mudança na quantidade demandada) / (% mudança no preço)
    = (ΔQ/Q) / (ΔP/P)
    = (dQ/dP) × (P/Q)
```

### Interpretação

| EPD | Comportamento | Recomendação de Preço |
|-----|-----|-----|
| **EPD < -1** | **Elástica:** quantidade cai mais que preço sobe | ↓ Preço → receita ↑ (demanda sensível) |
| **-1 < EPD < 0** | **Inelástica:** quantidade cai menos que preço sobe | ↑ Preço → receita ↑ (demanda robusta) |
| **EPD = -1** | **Unitária:** mudança % igual em P e Q | Equilibrada |
| **EPD ≈ 0** | **Perfeitamente inelástica:** Q não reage a P | Max preço (cautela: pode haver substitutos) |

### Forma Funcional: Regressão Log-Log

Para evitar heterocedasticidade e tornar o coeficiente interpretável diretamente:

```
ln(Q) = α + β × ln(P) + γ₁ × X₁ + γ₂ × X₂ + ... + ε

onde:
  - Q = volume de venda (litros ou unidades)
  - P = preço (preço_liquido_ponderado)
  - X₁, X₂, ... = variáveis de controle (temporal, sazonalidade, estoque, cliente, etc.)
  - β = elasticidade (interpretação direta: EPD ≈ β)
  - ε = erro idiossincrático
```

**Vantagens:**
- Coeficiente β é a elasticidade — fácil interpretação
- Reduz heterocedasticidade (escala de variância mais homogênea)
- Robusto a outliers em unidades absolutas

### Considerações B2B (Lubrificantes)

1. **Variabilidade no preço é baixa** — contatos de longo prazo, reajustes contratuais, não há pricing dinâmico diário
2. **Demanda é derivada** — volume segue consumo do cliente (máquinas industriais), não é resposta rápida a preço
3. **Houve variações de preço?** — análise dos dados deve validar se há variância de preço suficiente para identificar elasticidade
4. **Lag temporal** — efeito de preço pode levar meses para aparecer em volume (reação lenta)

---

## 3. Estratégia Geral

### Três Camadas de Análise

#### **Camada 1: Agregado (Baseline)**
- Elasticidade no **agregado total** (todos os clientes, todas as famílias)
- Valida se há relação preço-volume no período
- Base para comparação

#### **Camada 2: Por Segmento Híbrido**
- Elasticidade por **cluster × família de produto**
- Usa matriz de segmentação híbrida (45 segmentos, 44 viáveis)
- Espera-se heterogeneidade: clientes premium vs. volume, produtos commodity vs. especiais

#### **Camada 3: Efeitos Dinâmicos & Contexto**
- Controla por **fatores temporais** (sazonalidade, tendência, crise de supply)
- Controla por **proxy de oferta** (preço do competidor, índice de custo de insumos)
- Detecta **não-linearidades** (elasticidade muda com nível de preço?)

---

## 4. Fase 1: EDA_elasticidade (Exploração)

### Objetivo

Identificar:
1. **Variação de preço** — há suficiente variância para estimar elasticidade?
2. **Variação de volume** — há resposta da demanda?
3. **Estrutura temporal** — há sazonalidade, tendência?
4. **Outliers** — quais clientes/períodos quebram o padrão?
5. **Relação bruta** — existe correlação preço-volume?

### Seções Propostas (Notebook `5.EDA_elasticidade.ipynb`)

#### **5.1 — Carga e Preparação**
```python
# Carregar base bruta
df = pd.read_excel(..., sheet_name='Base Exportavel (1)')

# Aplicar pipeline de limpeza (usar outputs/1. EDA/)
# - Classificar movimento (venda, devolução, ajuste)
# - Manter só VENDA (tipo_movimento_eda == 'VENDA')
# - Validar reconciliação financeira

# Agregar por cliente-mês (série temporal)
# Saída: (cliente, data_venda) → volume, preço_liquido_ponderado, receita, etc.
df_monthly = df.groupby(['Código Cliente', pd.Grouper(key='Data Venda', freq='MS')]).agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
    'Material': lambda x: x.nunique(),  # diversidade de produtos
    # ...
}).reset_index()

# Calcular preço ponderado por período
df_monthly['preco_medio'] = df_monthly['Receita líquida'] / df_monthly['Volume']
```

#### **5.2 — Variação de Preço e Volume**

Visualizar e quantificar:

```python
# Distribuição cross-sectional (client-level, agregado anual/trimestral)
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# (a) Distribuição de preços
df_annual['preco_medio'].describe()  # media, desvio, quartis
axes[0, 0].hist(df_annual['preco_medio'], bins=50, alpha=0.7)

# (b) Distribuição de volume
axes[0, 1].hist(np.log(df_annual['volume_total']), bins=50, alpha=0.7)

# (c) Correlação bruta preço-volume (por cliente-ano)
axes[1, 0].scatter(df_annual['preco_medio'], df_annual['volume_total'], alpha=0.3)
axes[1, 0].set_xlabel('Preço médio')
axes[1, 0].set_ylabel('Volume total')

# (d) Scatter em escala log-log (a forma funcional da regressão)
axes[1, 1].scatter(
    np.log(df_annual['preco_medio']),
    np.log(df_annual['volume_total']),
    alpha=0.3
)
axes[1, 1].set_xlabel('ln(Preço)')
axes[1, 1].set_ylabel('ln(Volume)')

plt.tight_layout()
plt.savefig(outputs/3.Elasticidade/01_eda_preco_volume.png')
```

**Métricas calculadas:**
- Coeficiente de variação (CV) do preço: `σ(P) / μ(P)` — se CV < 5%, variação é fraca
- Coeficiente de variação do volume
- Correlação de Pearson e Spearman: `corr(ln(P), ln(Q))`

#### **5.3 — Série Temporal**

Validar presença de **sazonalidade** e **tendência**:

```python
# Agregar por mês (todos os clientes)
df_ts = df_monthly.groupby('Data Venda').agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
}).reset_index()
df_ts['preco_medio'] = df_ts['Receita líquida'] / df_ts['Volume']

# Visualizar série
fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)

axes[0].plot(df_ts['Data Venda'], df_ts['preco_medio'], marker='o', markersize=3)
axes[0].set_ylabel('Preço médio (R$/litro)')
axes[0].grid(alpha=0.3)

axes[1].plot(df_ts['Data Venda'], df_ts['Volume'], marker='o', markersize=3)
axes[1].set_ylabel('Volume (litros)')
axes[1].grid(alpha=0.3)

axes[2].plot(df_ts['Data Venda'], df_ts['Receita líquida'], marker='o', markersize=3)
axes[2].set_ylabel('Receita líquida (R$)')
axes[2].grid(alpha=0.3)
axes[2].set_xlabel('Data')

plt.tight_layout()
plt.savefig('outputs/3.Elasticidade/02_eda_serie_temporal.png')

# Decomposição de série temporal (STL)
from statsmodels.tsa.seasonal import STL
result = STL(df_ts['Volume']).fit()
result.plot()
plt.savefig('outputs/3.Elasticidade/03_decomposicao_stl.png')
```

#### **5.4 — Análise por Segmento**

Repetir para **cada cluster** (K-Means final) e **cada família de produto**:

```python
# Carregar segmentação final
seg_kmeans = pd.read_csv('outputs/2. Clusterização/segmentacao_clientes_kmeans.csv')
df_eda = df_monthly.merge(seg_kmeans[['Código Cliente', 'Cluster']], on='Código Cliente')

# Agregar por cluster-mês
df_cluster_ts = df_eda.groupby(['Cluster', 'Data Venda']).agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
}).reset_index()

df_cluster_ts['preco_medio'] = df_cluster_ts['Receita líquida'] / df_cluster_ts['Volume']

# Gráfico: 5 clusters em subplots
fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
axes = axes.flatten()

for i, cluster in enumerate(sorted(df_cluster_ts['Cluster'].unique())):
    data = df_cluster_ts[df_cluster_ts['Cluster'] == cluster]
    axes[i].scatter(data['preco_medio'], data['Volume'], alpha=0.5)
    axes[i].set_title(f'Cluster {cluster}')
    axes[i].set_xlabel('Preço médio')
    axes[i].set_ylabel('Volume')
    axes[i].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/3.Elasticidade/04_eda_por_cluster.png')
```

#### **5.5 — Análise por Família de Produto**

```python
# Classificar por família (usar segmentação híbrida)
familias = pd.read_csv('outputs/2. Clusterização/2.segmentacao_hibrida/familias_principais.csv')
df_familia = df_monthly.merge(
    df[['Código Cliente', 'Prod - Família de Produtos']].drop_duplicates(),
    on='Código Cliente'
)

# Idem: scatter + série temporal por família
```

#### **5.6 — Matriz de Correlação & Outliers**

```python
# Correlação entre volume, preço, margem, frequência
df_annual_corr = df_annual[['volume_total', 'preco_liquido_ponderado', 'margem_pct_ponderada', 'frequencia_mensal']]
corr_matrix = df_annual_corr.corr()

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
plt.savefig('outputs/3.Elasticidade/05_correlacao_features.png')

# Detectar outliers (IQR, Z-score)
Q1 = df_annual['volume_total'].quantile(0.25)
Q3 = df_annual['volume_total'].quantile(0.75)
IQR = Q3 - Q1
outliers = df_annual[(df_annual['volume_total'] < Q1 - 1.5*IQR) | (df_annual['volume_total'] > Q3 + 1.5*IQR)]
print(f"Outliers detectados: {len(outliers)} clientes ({100*len(outliers)/len(df_annual):.1f}%)")
```

#### **5.7 — Relatório de Síntese**

- Tabela: variância de preço por cluster/família
- Tabela: correlação bruta (ln(P), ln(Q)) — antecipando elasticidade
- Gráfico: distribuição de correlações
- Checklist: "Há variança suficiente para estimar elasticidade?"

---

## 5. Fase 2: Modelagem de Elasticidade

### Objetivo

Estimar **coeficientes de elasticidade** via regressão, com testes de robustez.

### Arquitetura de Modelos

#### **Modelo 1: Agregado (Baseline)**

```
ln(Volume_total) = α + β × ln(Preço) + γ × Tendência + δ × Sazonalidade + ε

Amostra: todas as transações (ou agregado mensal)
Métrica: β = elasticidade-preço agregada
Esperado: -0.5 a -1.5 (demanda inelástica a unitária — lubrificantes são suprimentos)
```

**Implementação:**
```python
import statsmodels.api as sm
from scipy import stats

# Preparar dados
df_model = df_ts.dropna()
df_model['ln_volume'] = np.log(df_model['Volume'])
df_model['ln_preco'] = np.log(df_model['preco_medio'])
df_model['trend'] = np.arange(len(df_model))

# Adicionar dummies de mês (sazonalidade)
df_model['mes'] = df_model['Data Venda'].dt.month
sazonalidade = pd.get_dummies(df_model['mes'], prefix='mes', drop_first=True)

# Regressão OLS
X = df_model[['ln_preco', 'trend']].join(sazonalidade)
X = sm.add_constant(X)
y = df_model['ln_volume']

model_1 = sm.OLS(y, X).fit()
print(model_1.summary())

# Extrair elasticidade
beta = model_1.params['ln_preco']
se_beta = model_1.bse['ln_preco']
ic_95 = model_1.conf_int(alpha=0.05).loc['ln_preco']

print(f"Elasticidade = {beta:.4f}")
print(f"IC 95% = [{ic_95[0]:.4f}, {ic_95[1]:.4f}]")
print(f"Sig.: {model_1.pvalues['ln_preco']:.4f}")
```

#### **Modelo 2: Por Cluster**

```
Para cada cluster k:
  ln(Volume_k,t) = α_k + β_k × ln(Preço_k,t) + ... + ε_k,t

Amostra: agregado mensal por cluster
Métrica: β_k — elasticidade do cluster k
Esperado: heterogeidade — clusters premium (inelástico) vs. volume (mais elástico?)
```

**Implementação:**
```python
# Preparar dados por cluster
elasticidades = {}

for cluster in df_cluster_ts['Cluster'].unique():
    df_c = df_cluster_ts[df_cluster_ts['Cluster'] == cluster].copy()
    df_c = df_c.sort_values('Data Venda').dropna()
    
    if len(df_c) < 12:  # requer mínimo de obs.
        print(f"Cluster {cluster}: apenas {len(df_c)} obs. — pulando")
        continue
    
    df_c['ln_volume'] = np.log(df_c['Volume'])
    df_c['ln_preco'] = np.log(df_c['preco_medio'])
    df_c['trend'] = np.arange(len(df_c))
    
    X = df_c[['ln_preco', 'trend']]
    X = sm.add_constant(X)
    y = df_c['ln_volume']
    
    model_c = sm.OLS(y, X).fit()
    
    elasticidades[f'Cluster {cluster}'] = {
        'beta': model_c.params['ln_preco'],
        'se': model_c.bse['ln_preco'],
        'pvalue': model_c.pvalues['ln_preco'],
        'r2': model_c.rsquared,
        'n_obs': len(df_c)
    }

# Visualizar
df_elasticidades = pd.DataFrame(elasticidades).T
print(df_elasticidades)

# Gráfico de coeficientes com barras de erro
fig, ax = plt.subplots(figsize=(10, 5))
x_pos = np.arange(len(df_elasticidades))
ax.errorbar(
    x_pos,
    df_elasticidades['beta'],
    yerr=1.96 * df_elasticidades['se'],
    fmt='o',
    capsize=5
)
ax.axhline(0, color='k', linestyle='--', alpha=0.3)
ax.set_ylabel('Elasticidade (β)')
ax.set_xticks(x_pos)
ax.set_xticklabels(df_elasticidades.index, rotation=45)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/3.Elasticidade/10_elasticidade_por_cluster.png')
```

#### **Modelo 3: Por Cluster × Família**

```
Para cada segmento (cluster, família):
  ln(Volume_i,t) = α_i + β_i × ln(Preço_i,t) + ... + ε_i,t

Amostra: agregado mensal por (cluster, família)
Métrica: β_i — elasticidade do segmento i
Esperado: máxima heterogeneidade — 44 estimativas
```

**Implementação similar a Modelo 2, mas com dupla chave (Cluster, Família).**

#### **Modelo 4: Painel com Efeitos Fixos (FE)**

Para explorar dinâmica entre clientes:

```
ln(Volume_c,t) = α_c + β × ln(Preço_c,t) + γ × X_c,t + ε_c,t

α_c = efeito fixo de cliente (captura heterogeneidade não observada)
β = elasticidade comum (mais robusta)
X_c,t = variáveis de controle (estoque, taxa de câmbio?, índice de confiança)
```

**Implementação:**
```python
# Preparar dados em painel
df_painel = df_monthly.copy()
df_painel['ln_volume'] = np.log(df_painel['Volume'])
df_painel['ln_preco'] = np.log(df_painel['preco_medio'])

# Remover nulos e outliers extremos
df_painel = df_painel[
    (df_painel['ln_volume'].notna()) &
    (df_painel['ln_preco'].notna()) &
    (df_painel['Volume'] > 0) &
    (df_painel['preco_medio'] > 0)
]

# Fixed Effects usando sklearn/statsmodels
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import PanelOLS

# Simplificado: regressão com dummies de cliente
cliente_dummies = pd.get_dummies(df_painel['Código Cliente'], drop_first=True)
X = df_painel[['ln_preco']].join(cliente_dummies)
X = sm.add_constant(X)
y = df_painel['ln_volume']

model_fe = sm.OLS(y, X).fit()
print(f"Elasticidade (FE): {model_fe.params['ln_preco']:.4f}")
```

#### **Modelo 5: Análise de Robustez**

Testar alternativas:

| Variação | Objetivo | Esperado |
|---|---|---|
| **Without outliers** | Remover top 1% e bottom 1% | β deve estabilizar |
| **Log volume vs. log quantity** | Usar unidades físicas vs. litros | Comparação de magnitude |
| **Lag estruturas** | Volume t vs. preço t-1, t-2 | Detectar delays de reação |
| **Diferentes freq. temporais** | Trimestral, semestral vs. mensal | Robustez a agregação |
| **Com controles** | Adicionar tendência, sazonalidade | Isolamento de elasticidade "pura" |

---

## 6. Implementação & Roadmap

### Notebook `5.EDA_elasticidade.ipynb`

**Duração estimada:** 1-2 dias

**Seções:**
1. Carregamento e limpeza
2. Variação de preço/volume
3. Série temporal
4. Análise por segmento
5. Análise por família
6. Matriz de correlação
7. Relatório de síntese

**Outputs:**
- Gráficos exploratórios (7-10 PNG)
- CSV com resumo de correlações
- Checklist: "Procedemos para modelagem?"

### Notebook `6.elasticidade.ipynb`

**Duração estimada:** 2-3 dias

**Seções:**
1. Modelo 1: Agregado
2. Modelo 2: Por Cluster
3. Modelo 3: Por Cluster × Família
4. Modelo 4: Painel com FE
5. Análise de robustez
6. Tabela resumida: elasticidades + IC 95%
7. Recomendações de pricing

**Outputs:**
- Tabela Excel: elasticidades por segmento
- Gráficos de coeficientes
- Simulação: "Se preço sobe X%, volume cai Y%?"
- Recomendações (bundle, promoção, estratégia de entrada)

---

## 7. Métricas de Sucesso

### Fase 1 (EDA)

- ✅ Variância de preço identificada e quantificada
- ✅ Relação bruta preço-volume visualizada
- ✅ Sazonalidade e tendência documentadas
- ✅ Outliers catalogados

### Fase 2 (Modelagem)

- ✅ Elasticidade agregada estimada com IC
- ✅ Elasticidades por cluster heterogêneas e significativas
- ✅ Modelos satisfazem pressupostos (normalidade, homocedasticidade)
- ✅ R² adequado (≥ 0.4 — aceitável para dados macroeconômicos)
- ✅ Recomendações de pricing viáveis

---

## 8. Limitações e Considerações

### Limitações Metodológicas

1. **Variação de preço é endógena?** 
   - Se a empresa ajusta preço em resposta a variações de demanda (em vez do contrário), a regressão sofre **viés de simultaneidade**.
   - **Solução:** instrumentos (custos de insumo, taxa de câmbio) ou regressão com lags.

2. **Correlação vs. Causalidade**
   - A regressão identifica correlação. Outros fatores (concorrência, sazonalidade, alterações de contrato) podem confounder.
   - **Solução:** incluir controles (sazonalidade, tendência, proxy de oferta).

3. **Heterogeneidade não observada**
   - Clientes variam em preferências, lealdade, acesso a substitutos (não observados).
   - **Solução:** Modelo 4 com efeitos fixos.

4. **Lag temporal**
   - Demanda pode reagir lentamente a preço (meses de atraso).
   - **Solução:** Testar estruturas de lag (preço t-1, t-2) na análise de robustez.

5. **Tamanho da amostra por segmento**
   - Alguns clusters × famílias podem ter <10 clientes/mês — estimativa instável.
   - **Solução:** filtro mínimo, pooling (agregar segmentos pequenos).

### Considerações de Negócio

1. **Contração vs. Expansão** — elasticidade pode diferir:
   - Subir preço (testado na história: queda de volume) vs. descer preço (raro — não testado)
   - **Recomendação:** cuidado em extrapolações para redução de preço.

2. **Competição** — falta preço do concorrente:
   - Se houve movimentos concorrenciais no período, elasticidade pode estar confundida.
   - **Recomendação:** incorporar índice de preço do concorrente (se disponível).

3. **Mix de produtos** — família varia por cliente:
   - Elasticidade pode mudar se mix muda (mesmo preço médio, composição diferente).
   - **Recomendação:** analisar também por SKU quando dados permitirem.

4. **Decisão de pricing** — usar elasticidade para:
   - **Limite de margem:** se elástica (EPD < -1), aumentar volume beneficia margem.
   - **Limite de volume:** se inelástica, aceitar menor volume com margem maior.

---

## 9. Template de Saídas

### Arquivo: `outputs/3.Elasticidade/elasticidade_resultados.xlsx`

**Aba 1: Resumo Executivo**
| Métrica | Valor | Interpretação |
|---|---|---|
| Elasticidade agregada | -0.85 | Demanda inelástica (típico de commodity B2B) |
| Intervalo de confiança 95% | [-1.05, -0.65] | Estimativa robusta |
| p-value | 0.002 | Significante a 1% |
| R² | 0.52 | Modelo explica 52% da variância |

**Aba 2: Por Cluster**
| Cluster | Elasticidade | IC 95% | Sig. | N (obs) | Interpretação |
|---|---|---|---|---|---|
| 0 (Premium) | -0.42 | [-0.68, -0.16] | ✓ 5% | 36 | Inelástico — preço sobe, volume não cai |
| 1 (Volume) | -1.28 | [-1.62, -0.94] | ✓ 1% | 40 | Elástico — sensível a preço |
| 2 (Ocasional) | -0.91 | [-1.18, -0.64] | ✓ 1% | 28 | Unitário — resposta proporcional |
| ... | ... | ... | ... | ... | ... |

**Aba 3: Por Cluster × Família**
| Cluster | Família | Elasticidade | N Clientes | Viável? | Recomendação |
|---|---|---|---|---|---|
| 0 | Motores | -0.35 | 45 | Sim | Aumentar preço (inelástico) |
| 0 | Compressores | -0.58 | 18 | Sim | Moderado aumento |
| 1 | Motores | -1.65 | 52 | Sim | Reduzir preço (elástico) |
| ... | ... | ... | ... | ... | ... |

**Aba 4: Recomendações Comerciais**
| Segmento | Ação | Impacto Esperado | Risco |
|---|---|---|---|
| Cluster 0 × Motores | Aumentar 10% | Receita +6% (inelástico) | Perda de cliente |
| Cluster 1 × Motores | Reduzir 5% | Volume +7%, Receita +1% | Margem unitária cai |
| ... | ... | ... | ... |

---

## 10. Referências Teóricas

- **Elasticidade Preço-Demanda:** Wooldridge, J. M. (2019). *Introductory Econometrics* (7th ed.).
- **Log-log models:** Greene, W. H. (2018). *Econometric Analysis* (8th ed.).
- **Panel methods:** Cameron & Trivedi (2005). *Microeconometrics: Methods and Applications*.
- **Causalidade em preço-demanda:** Angrist & Pischke (2009). *Mostly Harmless Econometrics*.

---

## 11. Checklist de Implementação

- [ ] Fase 1: `5.EDA_elasticidade.ipynb` completo
- [ ] Variância de preço quantificada por segmento
- [ ] Série temporal inspecionada
- [ ] Outliers identificados
- [ ] Relatório de síntese gerado
- [ ] **GO/NO-GO Decision:** Há suficiente variança para Fase 2?
- [ ] Fase 2: `6.elasticidade.ipynb` — Modelo 1 (agregado)
- [ ] Modelo 1: resultados validados (pressupostos testados)
- [ ] Modelo 2: elasticidades por cluster
- [ ] Modelo 3: elasticidades por cluster × família
- [ ] Modelo 4: painel com efeitos fixos
- [ ] Análise de robustez concluída
- [ ] Tabela de resultados e recomendações gerada
- [ ] Revisão final e aprovação

---

**Próximos passos:**
1. Validar com PM/comercial: "Qual é a decisão que elasticidade vai orientar?"
2. Confirmar se há dados de competidor/custo de insumo para instrumentos
3. Iniciar Fase 1 (EDA)
