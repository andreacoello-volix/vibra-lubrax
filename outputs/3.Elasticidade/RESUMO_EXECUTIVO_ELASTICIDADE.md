# 🎯 RESUMO EXECUTIVO — Elasticidade Preço-Demanda VIBRA LUBRAX

**Data:** Setembro 2026  
**Projeto:** Vibra Lubrax — Segmentação de Clientes para Pricing  
**Contexto:** Lubrificantes | Base SELL IN (jan/2023 – set/2026)  

---

## 🚀 Missão

Quantificar **elasticidade preço-demanda** por segmento (cluster × família de produto) para:
- 📈 Informar decisões de pricing diferenciado
- 💰 Otimizar margem por segmento
- 🎯 Identificar oportunidades de aumento de receita

---

## 📊 O Que é Elasticidade?

```
Elasticidade = (% mudança no volume) / (% mudança no preço)

EXEMPLO:
  Aumentar preço em 10% → volume cai 5%?
  Elasticidade = -5% / +10% = -0.5
  
  Interpretação: "inelástico" → subir preço aumenta receita
```

| Elasticidade | Tipo | Reação | Recomendação |
|---|---|---|---|
| **EPD < -1** | Elástica | Volume muito sensível a preço | ↓ Preço (demanda sobe mais%) |
| **-1 < EPD < 0** | Inelástica | Volume pouco sensível a preço | ↑ Preço (receita sobe) |
| **EPD ≈ 0** | Fixa | Demanda não reage a preço | Maximize preço |

---

## 📋 Estratégia em 2 Fases

### **Fase 1: EDA_elasticidade** (Exploração)
**Duração:** 1-2 dias

✅ Validar se há **variação de preço** suficiente  
✅ Inspecionar **relação bruta** preço-volume  
✅ Identificar **sazonalidade** e **tendências**  
✅ Catalogar por **segmento** (cluster, família)  
✅ **Decisão GO/NO-GO** para Fase 2  

**Outputs:**
- 7-10 gráficos exploratórios
- Tabela de variância por segmento
- Relatório de síntese

---

### **Fase 2: elasticidade.ipynb** (Modelagem)
**Duração:** 2-3 dias

#### Modelo 1️⃣ — **Agregado**
- Elasticidade em nível total
- Valida existência de relação
- Base para comparação

#### Modelo 2️⃣ — **Por Cluster (K-Means)**
- Elasticidade para cada cluster (0–4)
- Espera-se heterogeidade: premium inelástico, volume elástico

#### Modelo 3️⃣ — **Por Cluster × Família**
- Até 44 segmentos (cluster × família)
- Máxima granularidade
- Algumas células pequenas (<10 clientes) — agregadas

#### Modelo 4️⃣ — **Painel com Efeitos Fixos**
- Controla heterogeneidade não observada (lealdade, estoque)
- Elasticidade "pura" (mais robusta)

#### Modelo 5️⃣ — **Robustez**
- Sem outliers
- Diferentes períodos de agregação
- Com lags (preço t-1, t-2)

**Outputs:**
- Tabela: elasticidades + IC 95% (significância)
- Gráficos de coeficientes
- Simulação: cenários de preço
- Recomendações comerciais

---

## 🎲 3 Cenários de Resultado Esperado

### Cenário A: Demanda Inelástica (Esperado)
```
EPD agregado ≈ -0.5 a -0.8
Interpretação: Lubrificantes são suprimento obrigatório
                Clientes não trocam fácil (switching cost)

Recomendação: ↑ Preço (receita sobe)
              Tomar cuidado: perda de cliente
```

### Cenário B: Heterogeidade entre Clusters
```
Cluster Premium (EPD ≈ -0.3): Inelástico
  → Aumentar preço (margem sobe)

Cluster Volume (EPD ≈ -1.5): Elástico
  → Cuidado ao aumentar; oportunidade de reduzir preço se margem permite

Cluster Ocasional (EPD ≈ -0.9): Unitário
  → Equilibrado; qualquer mudança tem efeito compensado
```

### Cenário C: Endogeneidade (Risco)
```
Se a empresa sobe preço quando demanda está forte
(em vez do contrário):
  Regressão pode capturar correlação, não causalidade

Sinais: β > 0 (positivo, contrar intuição)
Solução: Usar instrumentos ou regressão com lags
```

---

## 📐 Metodologia Resumida

### Forma Funcional (Log-Log)

```
ln(Volume) = α + β × ln(Preço) + Controles + Erro

β = elasticidade (interpretação direta)
Controles = sazonalidade, tendência, efeitos fixos
```

**Vantagens:**
- β é diretamente a elasticidade (fácil de comunicar)
- Reduz heterocedasticidade
- Robusto a outliers

### Dados
- **Base:** 253.624 registros (jan/2023 – set/2026)
- **Período de análise:** 45 meses
- **Filtro:** Apenas vendas (245.456 registros)
- **Agregação:** Cliente-mês (N clientes × N meses)

### Pressupostos Testados
✅ Linearidade (escala log-log)  
✅ Normalidade dos resíduos (Shapiro-Wilk)  
✅ Homocedasticidade (Breusch-Pagan)  
✅ Não colinearidade (VIF)  
✅ Autocorrelação (Durbin-Watson)  

---

## 🎯 Saídas Esperadas (Por Fase)

### **Fase 1 — Pasta: `outputs/3.Elasticidade/`**

```
01_eda_preco_volume.png          # Scatter + histogramas
02_eda_serie_temporal.png        # Time series
03_decomposicao_stl.png          # Sazonalidade
04_eda_por_cluster.png           # 5 scatter plots
05_correlacao_features.png       # Heatmap

EDA_ELASTICIDADE_RELATORIO.csv   # Síntese de variâncias
```

### **Fase 2 — Pasta: `outputs/3.Elasticidade/`**

```
10_elasticidade_por_cluster.png  # Coef. + IC (Modelo 2)
11_modelo_1_diagnostics.png      # Resíduos (Modelo 1)
12_modelo_painel_diagnostics.png # Resíduos (Modelo 4)

elasticidade_coeficientes.csv    # Tabela: β, SE, p-value
elasticidade_ic.csv              # Intervalos de confiança
elasticidade_robustez.csv        # Testes alternativos

simulacao_cenarios_*.csv         # Cenários de pricing
impacto_simulado.png             # Gráficos de impacto
recomendacoes_pricing.csv        # Ações comerciais

elasticidade_resultados_final.xlsx  # CONSOLIDADO (6 abas)
  ├─ Resumo Executivo
  ├─ Por Cluster
  ├─ Por Cluster × Família
  ├─ Simulação
  ├─ Recomendações Comerciais
  └─ Metodologia & Limitações
```

---

## ⚠️ Limitações Conhecidas

### 1. **Variância de Preço Limitada**
   - B2B lubrificantes: contatos de longo prazo, reajustes contratuais
   - Se CV(preço) < 5%, estimativa será fraca
   - **Ação:** Fase 1 valida isso; se fraco, considerar período maior

### 2. **Endogeneidade (Simultaneidade)**
   - Se a empresa sobe preço quando demanda está alta (não baixa):
     Regressão captura correlação, não causalidade
   - **Ação:** Usar lags (preço t-1 explica volume t) ou instrumentos

### 3. **Fatores Não Capturados**
   - Competição, suprimento, mudanças de contrato
   - Podem confounder a relação preço-demanda
   - **Ação:** Incluir controles (tendência, sazonalidade); testar robustez

### 4. **Tamanho da Amostra por Segmento**
   - Alguns clusters × famílias podem ter <10 clientes/mês
   - Estimativa instável → agregar segmentos pequenos
   - **Ação:** Filtro de viabilidade (≥10 clientes)

### 5. **Lag Temporal**
   - Demanda pode reagir lentamente (meses de atraso)
   - Regressão contemp. pode perder dinâmica
   - **Ação:** Testar preço t-1, t-2 em robustez

---

## 💡 Como Usar Os Resultados

### Decisão 1️⃣ — **Aumentar Preço?**

```
IF Elasticidade < -1 (elástica):
  NÃO ↑ preço (receita cai — volume sai mais que preço sobe)
  
ELSE IF -1 < Elasticidade < 0 (inelástica):
  ✓ ↑ preço (receita sobe — volume cai pouco)
  ⚠️ Risco: perda de cliente se muito agressivo
  
ELSE IF Elasticidade ≈ 0 (inelástica demais):
  ✓✓ ↑ preço agressivo (demanda não reage)
  ⚠️ Pode haver substitutos não capturados
```

### Decisão 2️⃣ — **Competir em Preço?**

```
IF Elasticidade < -1 (elástica):
  ✓ ↓ preço (volume sobe mais % que preço desce)
  📈 Receita pode subir com volume maior
  ⚠️ Margem cai — viável só se custos permitirem
  
ELSE:
  ⚠️ ↓ preço não compensa (volume não aumenta suficiente)
  Estratégia melhor: diferenciação (qualidade, serviço)
```

### Decisão 3️⃣ — **Priorizar Segmentos?**

```
Matriz (Elasticidade vs. Tamanho de Receita):

Alto    │ [Ocasional]  │ [Premium]      │ ← Manter estratégia
Receita │              │ (inelástico,   │
        │ (pequeno)    │  ↑ preço)      │
        ├──────────────┼────────────────┤
Baixo   │ [Ocasional]  │ [Volume]       │
Receita │ (pequeno,    │ (elástico,     │
        │  negligível) │ ↑ volume?)     │
        └──────────────┴────────────────┘
                Elasticidade
```

---

## 🗂️ Documentos de Referência

| Documento | Conteúdo | Para Quem |
|---|---|---|
| **ESTRATEGIA_ELASTICIDADE_PRECO_DEMANDA.md** | Estratégia completa, métodos, exemplos de código | Data Scientist, PM |
| **ARQUITETURA_ELASTICIDADE.md** | Fluxo de dados, specs, pressupostos, troubleshooting | Dev, Analyst |
| **RESUMO_EXECUTIVO_ELASTICIDADE.md** | Este! Visão rápida | Executivo, PM, Comercial |

---

## ✅ Checklist Rápido

- [ ] Fase 1: EDA_elasticidade concluído
- [ ] Variância de preço validada (CV > 5%?)
- [ ] GO/NO-GO decidido
- [ ] Fase 2: elasticidade.ipynb concluído
- [ ] Elasticidades por segmento estimadas
- [ ] Pressupostos testados (residuos normais?)
- [ ] Tabela de recomendações gerada
- [ ] Apresentação para comercial pronta

---

## 📞 Próximas Ações

1. **Confirmar com PM/Comercial:**
   - Qual é a **decisão de pricing** que elasticidade vai orientar?
   - Há dados de **competidor/custo** para usar como instrumentos?
   - Qual **granularidade** é operacional? (cluster? família? cliente-mês?)

2. **Iniciar Fase 1** (`5.EDA_elasticidade.ipynb`)
   - Carregar base
   - Validar variância de preço
   - Gerar gráficos

3. **Fase 2** (após validação Fase 1)
   - Ajustar modelos
   - Testar pressupostos
   - Gerar recomendações

---

**Status:** 🟢 Pronto para iniciar  
**Estimado:** 3-5 dias (Fase 1 + 2)  
**Responsável:** Data Science  

