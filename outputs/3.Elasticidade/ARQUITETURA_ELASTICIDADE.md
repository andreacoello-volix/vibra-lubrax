# ARQUITETURA TÉCNICA — Modelagem de Elasticidade Preço-Demanda

---

## Fluxo de Dados & Processamento

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: base_Lubrax_origem.xlsx (outputs/1. EDA/)                │
│ ├─ 253.624 registros (jan/2023 – set/2026)                      │
│ ├─ Colunas: Data Venda, Código Cliente, Volume, Preço, etc.     │
│ └─ Estado: venda, devolução, ajuste classificados               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: EDA_elasticidade (5.EDA_elasticidade.ipynb)             │
│                                                                   │
│ Passos:                                                           │
│ ├─ 1.1 Carga & Limpeza                                           │
│ │   └─ Filtro: apenas VENDA (245.456 registros)                 │
│ │                                                                 │
│ ├─ 1.2 Agregação por Cliente-Mês                                │
│ │   └─ Shape: (N_clientes × N_meses) → volume, preço, margem   │
│ │                                                                 │
│ ├─ 1.3 Análise Exploratória                                      │
│ │   ├─ Distribuição de preço e volume                           │
│ │   ├─ Correlação bruta (ln(P), ln(Q))                          │
│ │   ├─ Série temporal (sazonalidade, tendência)                 │
│ │   ├─ Análise por cluster (usar segmentação K-Means)           │
│ │   └─ Análise por família de produto                           │
│ │                                                                 │
│ └─ 1.4 Decisão: "Há variança suficiente?"                       │
│     ├─ YES → Prosseguir para Fase 2                            │
│     └─ NO  → Revisar abordagem (menos segmentos? períodos?)     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
           ┌─────────────────────────────────┐
           │ OUTPUTS FASE 1:                  │
           ├─────────────────────────────────┤
           │ 01_eda_preco_volume.png         │ (scatter, histogramas)
           │ 02_eda_serie_temporal.png       │ (time series)
           │ 03_decomposicao_stl.png         │ (sazonalidade)
           │ 04_eda_por_cluster.png          │ (5 scatter plots)
           │ 05_correlacao_features.png      │ (heatmap)
           │ EDA_ELASTICIDADE_RELATORIO.csv  │ (resumo síntese)
           └─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 2A: Modelagem — Regressões (6.elasticidade.ipynb)          │
│                                                                   │
│ Modelo 1: Agregado (Baseline)                                   │
│ ├─ ln(Q_total) = α + β₁ × ln(P_total) + ... + ε                │
│ ├─ Agregação: mensal (todos clientes)                           │
│ ├─ N obs: ~45 (meses)                                           │
│ └─ Output: β₁ (elasticidade agregada)                           │
│                                                                   │
│ Modelo 2: Por Cluster (K-Means)                                 │
│ ├─ Para k=0..4:                                                 │
│ │   ln(Q_k,t) = α_k + β_k × ln(P_k,t) + γ_k × t + ε_k,t        │
│ ├─ Agregação: mensal por cluster                                │
│ ├─ N obs: ~40-45 por cluster                                    │
│ └─ Output: β_0, β_1, β_2, β_3, β_4 (5 elasticidades)           │
│                                                                   │
│ Modelo 3: Por Cluster × Família                                 │
│ ├─ Para cada (k, f) viável (≥10 clientes):                      │
│ │   ln(Q_kf,t) = α_kf + β_kf × ln(P_kf,t) + ... + ε_kf,t       │
│ ├─ Agregação: mensal por (cluster, família)                     │
│ ├─ N obs: variável (média ~20-30)                               │
│ └─ Output: até 44 elasticidades (segmentos viáveis)             │
│                                                                   │
│ Modelo 4: Painel com Efeitos Fixos                              │
│ ├─ ln(Q_c,t) = α_c + β × ln(P_c,t) + γ × trend + ε_c,t         │
│ ├─ Dados: cliente-mês (painel não balanceado)                   │
│ ├─ Controle: efeito fixo por cliente (heterogeneidade)          │
│ └─ Output: β (elasticidade comum, robusta)                      │
│                                                                   │
│ Modelo 5: Análise de Robustez                                   │
│ ├─ Sem outliers (1%-99%)                                        │
│ ├─ Diferentes freqs. temporais (trim., semestre)                │
│ ├─ Com lags: preço t-1, t-2                                     │
│ └─ Output: validação da estabilidade de β                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
           ┌─────────────────────────────────┐
           │ OUTPUTS FASE 2A:                 │
           ├─────────────────────────────────┤
           │ 10_elasticidade_por_cluster.png │ (coefs + IC)
           │ 11_modelo_1_diagnostics.png     │ (resíduos)
           │ elasticidade_coeficientes.csv   │ (tabela)
           │ elasticidade_ic.csv             │ (intervalos)
           └─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 2B: Simulação & Recomendações de Pricing                   │
│                                                                   │
│ Simulação: Impacto de Mudança de Preço                          │
│ ├─ Para cada segmento (c, f):                                   │
│ │   Δ% Volume = β_cf × Δ% Preço                                 │
│ │   Novo Volume = Volume_atual × (1 + Δ% Volume)                │
│ │   Nova Receita = Novo Volume × Novo Preço                     │
│ │   Impacto em Margem = ?                                       │
│ │                                                                 │
│ ├─ Cenários: -10%, -5%, +5%, +10% de preço                     │
│ └─ Output: matriz de simulação (Volume, Receita, Margem)        │
│                                                                   │
│ Recomendações Comerciais                                        │
│ ├─ Se EPD < -1 (elástica):                                      │
│ │   ✓ Reduzir preço → volume sobe mais → receita sobe          │
│ │   ✗ Aumentar preço → volume cai mais → receita cai           │
│ │                                                                 │
│ ├─ Se -1 < EPD < 0 (inelástica):                                │
│ │   ✓ Aumentar preço → volume cai pouco → receita sobe         │
│ │   ✗ Reduzir preço → volume sobe pouco → receita cai          │
│ │                                                                 │
│ └─ Matriz: Segmento → Recomendação + Impacto Esperado           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
           ┌─────────────────────────────────┐
           │ OUTPUTS FASE 2B:                 │
           ├─────────────────────────────────┤
           │ simulacao_cenarios.xlsx         │ (6 abas)
           │ recomendacoes_pricing.csv       │ (ações)
           │ impacto_simulado.png            │ (gráficos)
           └─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ CONSOLIDAÇÃO: elasticidade_resultados_final.xlsx                │
│                                                                   │
│ Aba 1: Resumo Executivo                                         │
│ ├─ Elasticidade agregada + IC                                   │
│ ├─ Heterogeidade por cluster                                    │
│ └─ Top 5 oportunidades de pricing                               │
│                                                                   │
│ Aba 2: Elasticidades por Cluster                                │
│ ├─ Coluna: Cluster, Elasticidade, IC 95%, p-value, R²          │
│ └─ Interpretação: inelástico vs. elástico                       │
│                                                                   │
│ Aba 3: Elasticidades por Cluster × Família                      │
│ ├─ Coluna: Cluster, Família, Elasticidade, N Clientes, Viável? │
│ └─ Filtro: apenas segmentos com ≥10 clientes                    │
│                                                                   │
│ Aba 4: Simulação de Pricing                                     │
│ ├─ Segmento, Preço Atual, Cenários (-10% a +10%)                │
│ └─ Novo Volume, Nova Receita, Δ Receita Esperada                │
│                                                                   │
│ Aba 5: Recomendações Comerciais                                 │
│ ├─ Segmento, Elasticidade, Ação, Impacto Esperado, Risco        │
│ └─ Prioridade: alto, médio, baixo                               │
│                                                                   │
│ Aba 6: Metodologia & Limitações                                 │
│ ├─ Descrição de modelos                                         │
│ ├─ Pressupostos e testes                                        │
│ └─ Limitações e recomendações de uso                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Pastas (Outputs)

```
outputs/
├── 3.Elasticidade/
│   ├── 01_eda_preco_volume.png
│   ├── 02_eda_serie_temporal.png
│   ├── 03_decomposicao_stl.png
│   ├── 04_eda_por_cluster.png
│   ├── 05_correlacao_features.png
│   │
│   ├── 10_elasticidade_por_cluster.png
│   ├── 11_modelo_1_diagnostics.png
│   ├── 12_modelo_painel_diagnostics.png
│   │
│   ├── EDA_ELASTICIDADE_RELATORIO.csv  # síntese Fase 1
│   ├── elasticidade_coeficientes.csv   # β por segmento
│   ├── elasticidade_ic.csv              # intervalos de confiança
│   ├── elasticidade_robustez.csv        # testes alternativos
│   │
│   ├── simulacao_cenarios_cluster_0.csv
│   ├── simulacao_cenarios_cluster_1.csv
│   ├── ... (1 por cluster)
│   │
│   ├── impacto_simulado.png  # gráfico de cenários
│   ├── recomendacoes_pricing.csv
│   │
│   └── elasticidade_resultados_final.xlsx  # consolidado (6 abas)
│
└── 2. Clusterização/
    └── (manter segmentacao_clientes_kmeans.csv, familias_principais.csv)
```

---

## Especificação de Dados & Formatos

### INPUT (Fase 1)

**Arquivo:** `outputs/1. EDA/kmeans_clientes_features.pkl` ou reconstruir de base bruta

**Colunas principais:**
```python
{
    'Código Cliente': str,           # ID cliente
    'Data Venda': datetime64,        # período (agregar para mês)
    'Volume': float,                 # volume (litros)
    'Receita líquida': float,        # receita após desconto/frete
    'Material': str,                 # material/SKU
    'Prod - Família de Produtos': str,  # família
}
```

### INTERMEDIATE (Fase 1 → Fase 2)

**Aggregated client-month dataset:**
```python
df_monthly_agg = {
    'Código Cliente': str,
    'Data Venda': datetime64[M],  # month-end
    'Volume': float,               # soma do mês
    'Receita líquida': float,      # soma do mês
    'preco_medio': float,          # receita / volume (ponderado)
    'Cluster': int,                # do K-Means (0-4)
    'Familia_Principal': str,      # família mais freq.
    'frequencia': int,             # contagem de transações no mês
    'taxa_devolucao': float,       # devoluções / vendas
}
```

**Time-series aggregated dataset (monthly):**
```python
df_ts_agg = {
    'Data Venda': datetime64[M],
    'Volume': float,               # agregado de todos clientes
    'Receita líquida': float,
    'preco_medio': float,
    'ln_volume': float,            # log(Volume)
    'ln_preco': float,             # log(preco_medio)
    'trend': int,                  # 0, 1, 2, ... (linear trend)
    'mes': int,                    # 1-12 (sazonalidade)
}
```

### OUTPUT (Fase 2)

**elasticidade_coeficientes.csv:**
```
Modelo,Segmento,Elasticidade (β),SE,p-value,R²,N_obs,Intervalo_IC_95_Inferior,Intervalo_IC_95_Superior
Agregado,Total,-0.850,0.124,0.002,0.52,45,-1.051,-0.649
Cluster,0,-0.420,0.132,0.045,0.38,36,-0.688,-0.152
Cluster,1,-1.280,0.171,0.001,0.55,40,-1.618,-0.942
...
```

**recomendacoes_pricing.csv:**
```
Segmento,Cluster,Familia,Elasticidade,Acao,Impacto_Receita_Esperado_%,Risco,Prioridade
0,0,Motores,-0.42,Aumentar preço 10%,+5.8%,Baixo (inelástico),Alta
1,1,Motores,-1.28,Reduzir preço 5%,+1.2%,Médio (demanda sensível),Alta
...
```

---

## Tecnologia Stack

### Linguagem & Versões
- **Python 3.10+**
- **Pandas 2.0+** — manipulação de dados, agregações
- **NumPy 1.24+** — operações numéricas
- **Statsmodels 0.14+** — regressões OLS, FE, diagnósticos
- **Matplotlib 3.7+ / Seaborn 0.12+** — visualizações
- **Scipy 1.10+** — testes estatísticos

### Notebook Environment
- **Jupyter Lab / VSCode + Jupyter**
- **Tema visual Volix** (usar `Script/tema_visual.py`)

### Armazenamento
- **Inputs:** Pickle (`.pkl`), Excel (`.xlsx`)
- **Outputs:** CSV (tabelas), PNG (gráficos), Excel (consolidado)

---

## Pressupostos Estatísticos & Testes

### Regressão OLS (Modelo 1, 2, 3)

**Pressupostos a validar:**

1. **Linearidade na escala log-log**
   ```python
   # Scatter plot ln(P) vs ln(Q)
   plt.scatter(np.log(df['preco']), np.log(df['volume']))
   # Aparência: nuvem linear?
   ```

2. **Normalidade dos resíduos**
   ```python
   from scipy.stats import shapiro
   _, p = shapiro(model.resid)
   print(f"Shapiro-Wilk p-value: {p:.4f}")  # p > 0.05 → normal
   
   # Gráfico: Q-Q plot
   sm.qqplot(model.resid, line='45')
   ```

3. **Homocedasticidade** (variância constante)
   ```python
   from statsmodels.stats.diagnostic import het_breuschpagan
   _, p_bp, _, _ = het_breuschpagan(model.resid, model.model.exog)
   print(f"Breusch-Pagan p-value: {p_bp:.4f}")  # p > 0.05 → homocedástico
   
   # Gráfico: resíduos vs valores ajustados
   plt.scatter(model.fittedvalues, model.resid)
   plt.axhline(0)
   ```

4. **Não colinearidade** (entre variáveis independentes)
   ```python
   from statsmodels.stats.outliers_influence import variance_inflation_factor
   vif = pd.DataFrame({
       'Var': X.columns,
       'VIF': [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
   })
   # VIF < 5 para cada variável (preferível < 2)
   ```

5. **Autocorrelação** (em série temporal)
   ```python
   from statsmodels.stats.diagnostic import durbin_watson
   dw = durbin_watson(model.resid)
   print(f"Durbin-Watson: {dw:.4f}")  # ~2 → sem autocorrelação; <2 → positiva; >2 → negativa
   ```

### Painel com Efeitos Fixos (Modelo 4)

**Teste de especificação (FE vs. OLS):**
```python
# F-test: todos efeitos fixos são zero?
from statsmodels.regression.linear_model import PanelOLS
model_fe = PanelOLS(y, X, entity_effects=True).fit()
# p-value < 0.05 → FE significativo (use FE em vez de OLS)
```

---

## Exemplos de Código (Snippets)

### Carregamento & Agregação

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import STL
import statsmodels.api as sm

# Carregar base
df = pd.read_pickle('outputs/1. EDA/kmeans_clientes_features.pkl')

# Filtro: apenas vendas
df = df[df['tipo_movimento_eda'] == 'VENDA'].copy()

# Carregar segmentação K-Means
seg = pd.read_csv('outputs/2. Clusterização/segmentacao_clientes_kmeans.csv')
df = df.merge(seg[['Código Cliente', 'Cluster']], on='Código Cliente')

# Agregar por cliente-mês
df['YearMonth'] = df['Data Venda'].dt.to_period('M')
df_monthly = df.groupby(['Código Cliente', 'YearMonth', 'Cluster']).agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
}).reset_index()

df_monthly['Data Venda'] = df_monthly['YearMonth'].dt.to_timestamp()
df_monthly['preco_medio'] = df_monthly['Receita líquida'] / df_monthly['Volume']

# Agregar por mês (todos os clientes)
df_ts = df_monthly.groupby('Data Venda').agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
}).reset_index()
df_ts['preco_medio'] = df_ts['Receita líquida'] / df_ts['Volume']
df_ts = df_ts.sort_values('Data Venda')

print(f"Time series: {len(df_ts)} meses")
print(df_ts.head())
```

### Regressão Log-Log (Modelo 1)

```python
# Preparar dados
df_reg = df_ts.dropna()
df_reg['ln_volume'] = np.log(df_reg['Volume'])
df_reg['ln_preco'] = np.log(df_reg['preco_medio'])
df_reg['trend'] = np.arange(len(df_reg))

# Dummies de sazonalidade
df_reg['mes'] = df_reg['Data Venda'].dt.month
sazonalidade = pd.get_dummies(df_reg['mes'], prefix='mes', drop_first=True)

# Regressão
X = df_reg[['ln_preco', 'trend']].join(sazonalidade)
X = sm.add_constant(X)
y = df_reg['ln_volume']

model = sm.OLS(y, X).fit()

# Resultados
print(model.summary())
print(f"\nElasticidade = {model.params['ln_preco']:.4f}")
print(f"IC 95% = [{model.conf_int(alpha=0.05).loc['ln_preco', 0]:.4f}, {model.conf_int(alpha=0.05).loc['ln_preco', 1]:.4f}]")
print(f"p-value = {model.pvalues['ln_preco']:.4f}")
```

### Regressão por Cluster (Modelo 2)

```python
elasticidades = {}

for cluster in df_monthly['Cluster'].unique():
    df_c = df_monthly[df_monthly['Cluster'] == cluster].copy()
    
    # Agregar por mês
    df_c_ts = df_c.groupby('Data Venda').agg({
        'Volume': 'sum',
        'Receita líquida': 'sum',
    }).reset_index()
    df_c_ts['preco_medio'] = df_c_ts['Receita líquida'] / df_c_ts['Volume']
    df_c_ts = df_c_ts.sort_values('Data Venda').dropna()
    
    if len(df_c_ts) < 12:
        print(f"Cluster {cluster}: apenas {len(df_c_ts)} obs — pulando")
        continue
    
    # Regressão
    df_c_ts['ln_volume'] = np.log(df_c_ts['Volume'])
    df_c_ts['ln_preco'] = np.log(df_c_ts['preco_medio'])
    df_c_ts['trend'] = np.arange(len(df_c_ts))
    
    X = df_c_ts[['ln_preco', 'trend']]
    X = sm.add_constant(X)
    y = df_c_ts['ln_volume']
    
    model_c = sm.OLS(y, X).fit()
    
    elasticidades[f'Cluster {cluster}'] = {
        'beta': model_c.params['ln_preco'],
        'se': model_c.bse['ln_preco'],
        'pvalue': model_c.pvalues['ln_preco'],
        'r2': model_c.rsquared,
        'n_obs': len(df_c_ts)
    }

df_elas = pd.DataFrame(elasticidades).T
print(df_elas)

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
ax.errorbar(
    np.arange(len(df_elas)),
    df_elas['beta'],
    yerr=1.96 * df_elas['se'],
    fmt='o',
    capsize=5,
    markersize=8
)
ax.axhline(0, color='k', linestyle='--', alpha=0.3)
ax.set_ylabel('Elasticidade (β)')
ax.set_xlabel('Cluster')
ax.set_xticks(np.arange(len(df_elas)))
ax.set_xticklabels(df_elas.index)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/3.Elasticidade/10_elasticidade_por_cluster.png', dpi=300)
plt.close()
```

---

## Checklist de Validação

### Fase 1 (EDA)

- [ ] Base carregada e filtrada (apenas VENDA)
- [ ] Agregação cliente-mês validada
- [ ] Distribuições de preço e volume visualizadas
- [ ] Série temporal inspecionada
- [ ] Sazonalidade identificada (STL)
- [ ] Outliers mapeados
- [ ] Correlação bruta calculada
- [ ] Por cluster: variança de preço quantificada
- [ ] Por família: padrões identificados
- [ ] Relatório de síntese gerado
- [ ] Decision: GO/NO-GO

### Fase 2 (Modelagem)

- [ ] Modelo 1 ajustado (agregado)
- [ ] Pressupostos testados (normalidade, homocedasticidade)
- [ ] Modelo 2 ajustado (por cluster)
- [ ] Heterogeneidade entre clusters validada
- [ ] Modelo 3 ajustado (por cluster × família)
- [ ] Modelo 4 ajustado (painel com FE)
- [ ] Análise de robustez executada
- [ ] Tabela de coeficientes + IC gerada
- [ ] Gráficos de diagnostics inclusos
- [ ] Simulação de cenários calculada
- [ ] Recomendações de pricing redigidas
- [ ] Excel consolidado gerado

---

## Troubleshooting

| Problema | Causa Provável | Solução |
|---|---|---|
| Correlação bruta é zero | Preço varia muito pouco | Aumentar período de agregação? Remover clientes com preço fixo? |
| R² muito baixo (<0.2) | Ruído alto; variáveis não-capturadas | Adicionar controles (sazonalidade, concorrência)? |
| Coeficiente β = +0.3 (positivo) | Endogeneidade: empresa sobe preço qdo demanda sobe | Usar instrumentos ou regressão com lag |
| Outliers extremos | Clientes atípicos | Remover 1%-99%; usar robust regression |
| p-value > 0.05 | Amostra pequena ou efeito fraco | Aumentar período? Agregar segmentos menores? |

