# 🗺️ ROADMAP DE IMPLEMENTAÇÃO — Elasticidade Preço-Demanda VIBRA LUBRAX

**Status:** 🟢 Pronto para iniciar  
**Duração Total:** 3-5 dias  
**Equipe:** Data Science (1 pessoa)  
**Data:** Setembro 2026  

---

## 📅 Cronograma Detalhado

### **DIA 1-2: Fase 1 — EDA_elasticidade**

#### Manhã (4-5h)
- [ ] **Setup ambiente**
  - Validar Jupyter + Python 3.10+
  - Verificar pacotes: pandas, numpy, matplotlib, seaborn, statsmodels
  - Validar acesso aos dados: `inputs/raw/` e `outputs/`

- [ ] **Seção 1: Carregamento & Limpeza**
  - Carregar `base_Lubrax_origem.xlsx` (ou `.pkl`)
  - Converter `Data Venda` para datetime
  - Filtrar apenas VENDA (245.456 registros esperados)
  - ✅ Checkpoint: verificar tipos e nulos

#### Tarde (3-4h)
- [ ] **Seção 2: Variação de Preço & Volume**
  - Agregar por cliente (acumulado)
  - Calcular preço_médio = receita / volume
  - Calcular Coef. Variação: CV(preço), CV(volume)
  - ⚠️ **Decision point:** CV(preço) > 5%?
    - SIM → prosseguir
    - NÃO → considerar período maior, remover clientes com preço fixo

- [ ] **Seção 3: Série Temporal**
  - Agregar por mês (todos os clientes)
  - Visualizar preço, volume, receita ao longo do tempo
  - STL decomposition (sazonalidade + tendência)
  - ✅ Salvar gráficos: `01_*`, `02_*`, `03_*`

#### Noite/Home (1-2h)
- [ ] **Seção 4: Análise por Cluster**
  - Carregar segmentação K-Means: `segmentacao_clientes_kmeans.csv`
  - Agrupar clientes por cluster
  - Visualizar preço vs volume por cluster
  - ✅ Salvar gráfico: `04_eda_por_cluster.png`

---

### **DIA 2-3: Fase 1 (cont.) & Síntese**

#### Manhã (3-4h)
- [ ] **Seção 5: Correlação & Outliers**
  - Matriz de correlação (preço, volume, diversidade)
  - Detectar outliers (IQR method, Z-score)
  - Visualizar: heatmap, boxplots
  - ✅ Salvar gráficos: `05_correlacao_features.png`

#### Tarde (2-3h)
- [ ] **Seção 6: Relatório de Síntese**
  - Compilar tabela: métricas chave (CV, correlação, n clusters, etc.)
  - Checklist GO/NO-GO (6 critérios)
  - ✅ Salvar: `EDA_ELASTICIDADE_RELATORIO.csv`

#### **🔴 DECISION GATE: Há variância suficiente?**

| Cenário | Ação |
|---|---|
| **GO** (CV > 5%, corr > 0.2, ≥12 meses) | → Fase 2 |
| **NO-GO** (variância fraca) | → Revisar período, remover clientes fixos, ou postergar |

---

### **DIA 3-4: Fase 2 — elasticidade.ipynb (Modelagem)**

#### Manhã (4-5h)
- [ ] **Modelo 1: Agregado (Baseline)**
  ```python
  ln(Volume) = α + β × ln(Preço) + Tendência + Sazonalidade + ε
  ```
  - OLS com série temporal agregada (45 meses)
  - Testar pressupostos: normalidade, homocedasticidade
  - ✅ Output: elasticidade agregada + IC 95%

- [ ] **Modelo 2: Por Cluster**
  ```python
  Para cada cluster k:
    ln(Volume_k) = α_k + β_k × ln(Preço_k) + ... + ε_k
  ```
  - 5 regressões (1 por cluster)
  - Comparar β_0, β_1, β_2, β_3, β_4
  - Visualizar coeficientes com barras de erro
  - ✅ Output: tabela `elasticidade_coeficientes_cluster.csv`

#### Afternoon (3-4h)
- [ ] **Modelo 3: Por Cluster × Família**
  ```python
  Para cada segmento (cluster, família) viável (≥10 clientes):
    ln(Volume_i) = α_i + β_i × ln(Preço_i) + ... + ε_i
  ```
  - Agregar por (cluster, família) — esperado: ~40 segmentos viáveis
  - Regressões paralelas
  - ✅ Output: tabela `elasticidade_coeficientes_segmento.csv`

#### Noite (2-3h)
- [ ] **Modelo 4: Painel com Efeitos Fixos**
  ```python
  ln(Volume_c,t) = α_c + β × ln(Preço_c,t) + Tendência + ε_c,t
  ```
  - Dados: cliente-mês (painel não balanceado)
  - Regressão com dummies de cliente (efeitos fixos)
  - β comum = elasticidade "pura" (mais robusta)
  - ✅ Output: coeficiente β com IC

---

### **DIA 4-5: Fase 2 (cont.) — Robustez & Recomendações**

#### Manhã (3-4h)
- [ ] **Modelo 5: Análise de Robustez**
  - **Teste A:** Sem outliers (1%-99%)
    - Remover top 1% e bottom 1%
    - Regressão Modelo 1 sem outliers
    - Comparar β antes/depois

  - **Teste B:** Diferentes períodos de agregação
    - Trimestral (em vez de mensal)
    - Semestral
    - Comparar estabilidade de β

  - **Teste C:** Com lags
    - Volume_t vs. Preço_t (contemporâneo)
    - Volume_t vs. Preço_{t-1} (lag 1 mês)
    - Volume_t vs. Preço_{t-2} (lag 2 meses)
    - Verificar se há delay na reação

- [ ] **Consolidar Tabela de Resultados**
  - Coluna: Modelo, Segmento, β (Elasticidade), SE, p-value, R², n_obs
  - Adicionar IC 95%
  - Adicionar interpretação (elástico/inelástico)
  - ✅ Output: `elasticidade_resultados_consolidado.csv`

#### Afternoon (3-4h)
- [ ] **Simulação de Cenários**
  ```python
  Para cada segmento viável:
    Cenários: -10%, -5%, +5%, +10% de preço
    
    Novo_Volume = Volume_atual × (1 + β × Δ% Preço)
    Novo_Preço = Preço_atual × (1 + Δ% Preço)
    Nova_Receita = Novo_Volume × Novo_Preço
    Δ Receita (%) = (Nova_Receita - Receita_atual) / Receita_atual
    
    Δ Margem (%) = ?  [se tiver info de custo]
  ```
  - Criar matriz: segmento × cenário → impacto em receita/margem
  - Visualizar top 10 oportunidades
  - ✅ Output: `simulacao_cenarios_*.csv` + gráfico

#### Noite (2-3h)
- [ ] **Recomendações Comerciais**
  - **Regra 1:** EPD < -1 → Reduzir preço (elástico, demanda sensível)
  - **Regra 2:** -1 < EPD < 0 → Aumentar preço (inelástico, demanda robusta)
  - **Regra 3:** EPD ≈ 0 → Maximize preço (demanda fixa)
  - **Exceções:** Risco de perda de cliente, concorrência
  - ✅ Output: `recomendacoes_pricing.csv`

---

### **DIA 5: Consolidação & Apresentação**

#### Manhã (2-3h)
- [ ] **Consolidar Excel Final**
  - Aba 1: Resumo Executivo
    - Elasticidade agregada + IC
    - Top 5 oportunidades
  - Aba 2: Por Cluster (elasticidades + interpretação)
  - Aba 3: Por Cluster × Família (viáveis)
  - Aba 4: Simulação de cenários
  - Aba 5: Recomendações comerciais (com risco/prioridade)
  - Aba 6: Metodologia & Limitações
  - ✅ Output: `elasticidade_resultados_final.xlsx`

#### Afternoon (2-3h)
- [ ] **Documentação & Limpeza**
  - Revisar todos os notebooks (5.EDA, 6.elasticidade)
  - Adicionar comentários e interpretações
  - Salvar figuras de alta qualidade (dpi=300)
  - Criar sumário de outputs

- [ ] **Preparar Apresentação para Comercial**
  - Slide 1: Metodologia (log-log regression)
  - Slide 2: Elasticidades por cluster + IC
  - Slide 3: Matriz de simulação
  - Slide 4: Top 5 recomendações
  - Slide 5: Limitações & próximos passos
  - ✅ Output: Apresentação PowerPoint/HTML

#### Final Check (30min)
- [ ] Todos os outputs em `outputs/3.Elasticidade/`?
- [ ] Notebooks sem erros?
- [ ] Documentação atualizada?
- [ ] Excel consolidado pronto?

---

## 📊 Matriz de Decisão (Por Dia)

```
DIA 1 ───────────────────────────────────────────────────────────
├─ Manhã: Setup + Carregamento
├─ Tarde: Variação de preço/volume (DECISION: CV > 5%?)
├─ Noite: Série temporal + Clusters
└─ Status: ✅ (Fase 1: 50%)

DIA 2 ───────────────────────────────────────────────────────────
├─ Manhã: Correlação + Outliers
├─ Tarde: Síntese + Checklist GO/NO-GO
└─ Status: ✅ (Fase 1: 100%)
          ⚠️ GATE: Prosseguir?

DIA 3 ───────────────────────────────────────────────────────────
├─ Manhã: Modelo 1 (agregado) + Modelo 2 (cluster)
├─ Afternoon: Modelo 3 (segmento)
├─ Noite: Modelo 4 (painel)
└─ Status: ✅ (Fase 2: 50%)

DIA 4 ───────────────────────────────────────────────────────────
├─ Manhã: Robustez + Consolidação de tabela
├─ Afternoon: Simulação de cenários
├─ Noite: Recomendações
└─ Status: ✅ (Fase 2: 80%)

DIA 5 ───────────────────────────────────────────────────────────
├─ Manhã: Excel consolidado
├─ Afternoon: Apresentação
├─ Final: QA
└─ Status: ✅ (100% — Pronto para entrega)
```

---

## 📁 Arquivos Entregáveis

### Fase 1 (DIA 2)
```
outputs/3.Elasticidade/
├── 01_eda_preco_volume.png              # Scatter + histogramas
├── 02_eda_serie_temporal.png            # Time series
├── 03_decomposicao_stl.png              # Sazonalidade
├── 04_eda_por_cluster.png               # 5 scatter (clusters)
├── 05_correlacao_features.png           # Heatmap
└── EDA_ELASTICIDADE_RELATORIO.csv       # Síntese
```

### Fase 2 (DIA 5)
```
outputs/3.Elasticidade/
├── 10_elasticidade_por_cluster.png      # Coef. + IC
├── 11_modelo_1_diagnostics.png          # Resíduos, Q-Q plot
├── 12_modelo_painel_diagnostics.png     # FE residuals
│
├── elasticidade_coeficientes.csv        # Tabela: β, SE, p-value
├── elasticidade_ic.csv                  # Intervalos de confiança
├── elasticidade_robustez.csv            # Testes alternativos
│
├── simulacao_cenarios_cluster_0.csv     # Cenários por cluster
├── simulacao_cenarios_cluster_*.csv     # (1 por cluster)
├── impacto_simulado.png                 # Gráfico de impacto
├── recomendacoes_pricing.csv            # Ações comerciais
│
└── elasticidade_resultados_final.xlsx   # 📊 CONSOLIDADO (6 abas)
```

### Documentação
```
outputs/
├── ESTRATEGIA_ELASTICIDADE_PRECO_DEMANDA.md   # Estratégia completa
├── ARQUITETURA_ELASTICIDADE.md                # Arquitetura técnica
├── RESUMO_EXECUTIVO_ELASTICIDADE.md           # Visão executiva
├── ROADMAP_IMPLEMENTACAO.md                   # Este documento
└── template_5_EDA_elasticidade_skeleton.py    # Template Python
```

---

## ⚠️ Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Variação de preço insuficiente | 🟡 Média | 🔴 Alto | Validar em Dia 1; se fraco, expandir período |
| Correlação fraca (r < 0.2) | 🟡 Média | 🟠 Médio | Adicionar controles (sazonalidade, lags) |
| Amostra pequena por segmento | 🟢 Baixa | 🟠 Médio | Filtro ≥10 clientes; agregar segmentos pequenos |
| Endogeneidade (preço sobe qdo demanda sobe) | 🟡 Média | 🔴 Alto | Testar com lags; usar instrumentos se necessário |
| Pressupostos violados (resíduos não-normais) | 🟢 Baixa | 🟠 Médio | Usar robust regression ou transformações |

---

## 🎯 Critérios de Sucesso

### ✅ Fase 1 (GO/NO-GO)
- [ ] Coef. Variação de preço > 5%
- [ ] Correlação log-log significativa (r > 0.2, p < 0.05)
- [ ] Série temporal ≥ 12 meses
- [ ] Sazonalidade identificada
- [ ] Decisão clara: GO ou NO-GO

### ✅ Fase 2 (Modelagem)
- [ ] Elasticidade agregada estimada com p < 0.05
- [ ] Elasticidades por cluster heterogêneas (β_i significativamente diferentes)
- [ ] R² ≥ 0.3 (aceitável para macro data)
- [ ] Pressupostos testados e validados
- [ ] Recomendações acionáveis geradas

### ✅ Entrega Final
- [ ] Excel consolidado com 6 abas
- [ ] Apresentação para comercial pronta
- [ ] Documentação completa
- [ ] Notebooks funcionais (sem erros)

---

## 🚀 Próximos Passos (Pós-Entrega)

1. **Apresentar para PM/Comercial**
   - Validar elasticidades com intuição de negócio
   - Coletar feedback sobre recomendações

2. **Refinamento**
   - Se houve feedback: reajustar modelos/interpretações
   - Adicionar dados de concorrente (se disponível)

3. **Implementação**
   - Integrar elasticidades em tabela de preços
   - Testar pricing diferenciado em piloto
   - Medir impacto real (lift de receita/volume)

4. **Iteração**
   - Atualizar elasticidades trimestralmente (novos dados)
   - Validar impacto das mudanças de preço

---

## 📞 Contatos & Suporte

| Função | Responsável | Contato |
|---|---|---|
| **Data Science** | Você | ... |
| **PM** | ... | ... |
| **Comercial** | ... | ... |
| **Dados** (Synapse) | ... | ... |

---

## 📋 Checklist Final (DIA 5)

- [ ] Todos os 7+ gráficos salvos em `outputs/3.Elasticidade/`
- [ ] Todas as tabelas CSV geradas
- [ ] Excel consolidado com 6 abas concluído
- [ ] Notebooks 5.EDA e 6.elasticidade sem erros
- [ ] Documentação atualizada e validada
- [ ] Apresentação pronta
- [ ] QA: nenhum output vazio ou com erro
- [ ] Pronto para entrega ✅

---

**Status Final:** 🟢 Pronto para iniciar  
**Data de Início Recomendada:** Segunda-feira da semana que vem  
**Data de Entrega Esperada:** Sexta-feira (fim do dia)  

