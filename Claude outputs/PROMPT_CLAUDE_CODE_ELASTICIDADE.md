# 🎯 PROMPT PARA CLAUDE CODE — Análise Completa de Elasticidade Preço-Demanda

**Copie este prompt e execute no Claude Code CLI:**

```
claude_code run --task "Executar análise completa de elasticidade preço-demanda VIBRA LUBRAX"
```

---

## 📋 PROMPT COMPLETO (Cole no Claude Code)

```
Projeto: VIBRA LUBRAX — Elasticidade Preço-Demanda (Análise Completa)
Duração: 3-5 dias
Data: Setembro 2026

OBJETIVO:
Executar análise completa de elasticidade preço-demanda em duas fases:
- Fase 1 (EDA): Validar variação de preço e gerar exploratória
- Fase 2 (Modelagem): Estimar 5 modelos de regressão + simulação + recomendações

CONTEXTO:
- Base de dados: base_Lubrax_origem.xlsx (253.624 registros, jan/2023-set/2026)
- Filtro: Apenas vendas (VENDA type)
- Segmentação: 5 clusters K-Means × 8-9 famílias de produto
- Metodologia: Log-log regression (ln(Volume) = α + β×ln(Preço) + controles + ε)
- Granularidade: Agregado → Cluster → Cluster×Família → Painel com efeitos fixos

═══════════════════════════════════════════════════════════════════════════════

FASE 1: EXPLORAÇÃO (Dias 1-2) — EDA_ELASTICIDADE
─────────────────────────────────────────────────────────────────────────────

[ ] 1. SETUP
  • Validar Jupyter + Python 3.10+
  • Verificar: pandas, numpy, matplotlib, seaborn, statsmodels, scikit-learn
  • Criar pasta: outputs/3.Elasticidade/
  • Carregar template: template_5_EDA_elasticidade_skeleton.py

[ ] 2. CARREGAMENTO & LIMPEZA
  • Carregar base_Lubrax_origem.xlsx (ou .pkl)
  • Converter Data Venda para datetime
  • Filtrar apenas VENDA (espera-se: 245.456 registros)
  • Validar tipos de dados, nulos
  • CHECKPOINT: Nenhum valor nulo em preço/volume/cliente/data?

[ ] 3. VARIAÇÃO DE PREÇO & VOLUME (Decision Point 1)
  • Agregar por cliente (acumulado)
  • Calcular: preço_médio = receita / volume
  • Calcular Coef. Variação: CV(preço), CV(volume)
  ⚠️ DECISÃO: CV(preço) > 5%?
    ✅ SIM → prosseguir para Fase 2
    ❌ NÃO → expandir período ou remover clientes com preço fixo
  • Salvar: EDA_ELASTICIDADE_RELATORIO.csv (métricas resumidas)

[ ] 4. SÉRIE TEMPORAL (Agregação Mensal)
  • Agregar por mês (todos os clientes)
  • Calcular: Preço_médio_mês, Volume_total_mês, Receita_mês
  • Visualizar: Série temporal (45 meses)
  • STL decomposition: Sazonalidade + Tendência + Resíduos
  • Salvar gráficos: 01_eda_preco_volume.png, 02_eda_serie_temporal.png, 03_decomposicao_stl.png

[ ] 5. ANÁLISE POR CLUSTER
  • Carregar segmentação: segmentacao_clientes_kmeans.csv
  • Agrupar clientes por cluster (clusters 0-4)
  • Para cada cluster: calcular preço_médio, volume, correlação ln-ln
  • Visualizar: 5 scatter plots (preço vs volume) com regressão linear
  • Salvar: 04_eda_por_cluster.png

[ ] 6. CORRELAÇÃO & OUTLIERS
  • Matriz de correlação: [preço, volume, diversidade_produto, tendência]
  • Detectar outliers: IQR method (Q1-1.5×IQR, Q3+1.5×IQR)
  • Heatmap de correlação
  • Boxplots de preço/volume por cluster
  • Salvar: 05_correlacao_features.png

[ ] 7. RELATÓRIO DE SÍNTESE (GO/NO-GO)
  Checklist de viabilidade (6 critérios):
  ☑️ CV(preço) > 5%?
  ☑️ Correlação ln-ln significativa (r > 0.2, p < 0.05)?
  ☑️ Série temporal ≥ 12 meses?
  ☑️ Sazonalidade detectada (componente sazonal > 10% variância)?
  ☑️ ≥ 3 clusters com n > 50 clientes?
  ☑️ Sem valores extremos que inviabilizem regressão?

  DECISÃO GATE:
  ✅ GO (todos ✓) → Prosseguir para Fase 2
  ⚠️ NO-GO (< 4 ✓) → Revisar período, filtros, ou postergar

═══════════════════════════════════════════════════════════════════════════════

FASE 2: MODELAGEM (Dias 3-5) — ELASTICIDADE.IPYNB
─────────────────────────────────────────────────────────────────────────────

[ ] 1. MODELO 1: AGREGADO (Baseline)
  Especificação:
    ln(Volume_t) = α + β × ln(Preço_t) + Tendência_t + Sazonalidade_t + ε_t
  
  Execução:
  • Agregar dados mensais (45 observações)
  • OLS regression (statsmodels)
  • Testar pressupostos:
    - Normalidade dos resíduos (Shapiro-Wilk test)
    - Homocedasticidade (Breusch-Pagan test)
    - Autocorrelação (Durbin-Watson)
  • Extrair: β (elasticidade), SE, p-value, R², IC 95%
  • Output: elasticidade_agregado.csv

[ ] 2. MODELO 2: POR CLUSTER (K=5)
  Especificação:
    Para cada cluster k ∈ {0,1,2,3,4}:
      ln(Volume_k,t) = α_k + β_k × ln(Preço_k,t) + Tendência_k,t + ε_k,t
  
  Execução:
  • Filtrar dados por cluster
  • Rodar 5 regressões (1 por cluster)
  • Comparar coeficientes: β_0, β_1, β_2, β_3, β_4
  • Visualizar: Elasticidades com barras de erro (IC 95%)
  • Testa heterogeneidade: F-test de igualdade de βs?
  • Output: elasticidade_por_cluster.csv, 10_elasticidade_por_cluster.png

[ ] 3. MODELO 3: POR CLUSTER × FAMÍLIA
  Especificação:
    Para cada segmento viável (cluster, família) com n_clientes ≥ 10:
      ln(Volume_i) = α_i + β_i × ln(Preço_i) + Controles_i + ε_i
  
  Execução:
  • Combinar: cluster × família → até 44 segmentos
  • Filtrar: apenas segmentos com ≥ 10 clientes/observações
  • Rodar regressões paralelas
  • Output: elasticidade_por_segmento.csv (segmento, β, SE, p-value, n_obs, R²)

[ ] 4. MODELO 4: PAINEL COM EFEITOS FIXOS
  Especificação:
    ln(Volume_c,t) = α_c + β × ln(Preço_c,t) + Tendência_t + Sazonalidade_t + ε_c,t
    (α_c = efeito fixo por cliente, β = coeficiente comum)
  
  Execução:
  • Dados: cliente-mês (painel não balanceado)
  • Regressão FE (within transformation ou dummies)
  • β = elasticidade "pura" (controla lealdade, estoque, etc.)
  • Testar: Hausman test (FE vs. pooled OLS)
  • Output: elasticidade_painel_fe.csv

[ ] 5. MODELO 5: ROBUSTEZ
  
  Teste A: Sem Outliers
  • Remover top 1% e bottom 1% (preço e volume)
  • Regressão Modelo 1 sem outliers
  • Comparar β antes/depois
  
  Teste B: Períodos Alternativos
  • Trimestral (em vez de mensal)
  • Semestral
  • Comparar estabilidade de β
  
  Teste C: Com Lags
  • Volume_t vs. Preço_t (contemporâneo)
  • Volume_t vs. Preço_{t-1} (lag 1 mês)
  • Volume_t vs. Preço_{t-2} (lag 2 meses)
  • Verificar: há delay na reação de demanda?
  
  Output: elasticidade_robustez.csv (modelo, teste, β, SE, p-value, N, R²)

[ ] 6. CONSOLIDAÇÃO DE RESULTADOS
  Tabela unificada:
  | Modelo | Segmento | β | SE | p-value | R² | N | IC_inf | IC_sup | Interpretação |
  
  Interpretação automática:
    • EPD < -1: "Elástico (sensível a preço)"
    • -1 < EPD < 0: "Inelástico (robusto)"
    • EPD ≈ 0: "Muito inelástico (demanda fixa)"
  
  Output: elasticidade_resultados_consolidado.csv

[ ] 7. SIMULAÇÃO DE CENÁRIOS
  Para cada segmento viável (Cluster e Cluster×Família):
  
  Cenários: -10%, -5%, +5%, +10% de variação de preço
  
  Cálculos:
    Novo_Volume = Volume_atual × (1 + β × Δ% Preço)
    Novo_Preço = Preço_atual × (1 + Δ% Preço)
    Nova_Receita = Novo_Volume × Novo_Preço
    Δ Receita (%) = (Nova_Receita - Receita_atual) / Receita_atual
  
  Matriz de saída:
    Linhas: Segmento
    Colunas: Cenário (-10%, -5%, +5%, +10%), Δ Volume (%), Δ Receita (%)
  
  Visualizar: Top 10 oportunidades (maior upside de receita)
  Output: simulacao_cenarios_*.csv + impacto_simulado.png

[ ] 8. RECOMENDAÇÕES COMERCIAIS
  Regras de decisão:
  
  IF Elasticidade < -1 (elástico):
    → "REDUZIR PREÇO" (demanda muito sensível)
    → Oportunidade: ↓ 5% preço → ↑ 5%+ volume → Receita ↑
    Risco: Margem ↓
  
  ELSE IF -1 ≤ Elasticidade < -0.5 (inelástico moderado):
    → "AUMENTAR PREÇO" (demanda pouco sensível)
    → Oportunidade: ↑ 5% preço → ↓ 2-3% volume → Receita ↑
    Risco: Perda de cliente se muito agressivo
  
  ELSE IF -0.5 ≤ Elasticidade < 0 (muito inelástico):
    → "MAXIMIZAR PREÇO" (demanda fixa)
    → Oportunidade: ↑ 10% preço → Receita ↑↑
    Risco: Pode haver substitutos não capturados
  
  ELSE (Elasticidade ≈ 0 ou positivo):
    → "ANÁLISE ADICIONAL NECESSÁRIA" (possível endogeneidade)
    → Sugestão: revisar especificação, testar com lags
  
  Output: recomendacoes_pricing.csv (segmento, elasticidade, recomendação, prioridade, risco)

═══════════════════════════════════════════════════════════════════════════════

CONSOLIDAÇÃO & ENTREGA (Dia 5)
─────────────────────────────────────────────────────────────────────────────

[ ] 1. EXCEL FINAL (elasticidade_resultados_final.xlsx)
  
  Aba 1: RESUMO EXECUTIVO
    • Elasticidade agregada ± IC 95%
    • Top 5 segmentos por oportunidade (↑ receita %)
    • 1-2 gráficos de impacto simulado
  
  Aba 2: POR CLUSTER
    • Tabela: Cluster | Elasticidade | SE | p-value | R² | Interpretação
    • Gráfico: Elasticidades com barras de erro
  
  Aba 3: POR CLUSTER × FAMÍLIA
    • Tabela: Cluster | Família | Elasticidade | N_clientes | Viável? | Recomendação
    • Filtrar apenas segmentos viáveis (N ≥ 10)
  
  Aba 4: SIMULAÇÃO
    • Matriz: Segmento × Cenário (-10%, -5%, +5%, +10%)
    • Valores: Δ Receita (%), Δ Volume (%)
    • Destaque: Oportunidades positivas (verde), riscos (vermelho)
  
  Aba 5: RECOMENDAÇÕES COMERCIAIS
    • Tabela: Segmento | Elasticidade | Ação | Prioridade (1-5) | Risco | Upside Potencial
    • Ordenar por: Prioridade
  
  Aba 6: METODOLOGIA & LIMITAÇÕES
    • Forma funcional: ln(Volume) = α + β×ln(Preço) + Controles + ε
    • Pressupostos testados (normalidade, homocedasticidade, autocorrelação, VIF)
    • Limitações conhecidas (variância preço limitada, endogeneidade, fatores não capturados)
    • Próximos passos (atualização trimestral, validação com negócio)

[ ] 2. DOCUMENTAÇÃO & LIMPEZA
  • Revisar notebooks: 5.EDA_elasticidade, 6.elasticidade
  • Adicionar comentários e interpretações
  • Salvar figuras em alta qualidade (dpi=300)
  • Criar INDEX.txt com lista de todos os outputs

[ ] 3. APRESENTAÇÃO (PowerPoint/HTML)
  Slide 1: Metodologia (log-log regression, forma funcional, pressupostos)
  Slide 2: Elasticidades por cluster + IC
  Slide 3: Matriz de simulação (Cluster | Cenário | Δ Receita)
  Slide 4: Top 5 recomendações com risco/prioridade
  Slide 5: Limitações & próximos passos

[ ] 4. QUALITY ASSURANCE (30 min)
  ✓ Todos os gráficos salvos em outputs/3.Elasticidade/?
  ✓ Todas as tabelas CSV geradas e sem erros?
  ✓ Excel consolidado com 6 abas concluído?
  ✓ Notebooks sem erros (run all cells)?
  ✓ Nenhum output com valores faltantes (NaN)?
  ✓ Documentação atualizada?

═══════════════════════════════════════════════════════════════════════════════

ENTREGÁVEIS ESPERADOS
─────────────────────────────────────────────────────────────────────────────

outputs/3.Elasticidade/
├── 01_eda_preco_volume.png
├── 02_eda_serie_temporal.png
├── 03_decomposicao_stl.png
├── 04_eda_por_cluster.png
├── 05_correlacao_features.png
├── 10_elasticidade_por_cluster.png
├── 11_modelo_1_diagnostics.png
├── 12_modelo_painel_diagnostics.png
├── EDA_ELASTICIDADE_RELATORIO.csv
├── elasticidade_coeficientes.csv
├── elasticidade_ic.csv
├── elasticidade_robustez.csv
├── elasticidade_por_cluster.csv
├── elasticidade_por_segmento.csv
├── elasticidade_painel_fe.csv
├── simulacao_cenarios_cluster_0.csv
├── simulacao_cenarios_cluster_*.csv
├── impacto_simulado.png
├── recomendacoes_pricing.csv
└── elasticidade_resultados_final.xlsx ⭐ (CONSOLIDADO — 6 abas)

═══════════════════════════════════════════════════════════════════════════════

CRITÉRIOS DE SUCESSO
─────────────────────────────────────────────────────────────────────────────

✅ FASE 1 (Validação)
  • CV(preço) > 5%
  • Correlação log-log significativa (r > 0.2, p < 0.05)
  • Decisão GO/NO-GO clara
  • Relatório de síntese concluído

✅ FASE 2 (Modelagem)
  • Elasticidade agregada p < 0.05
  • Elasticidades por cluster heterogêneas (β_i significativamente diferentes)
  • R² ≥ 0.3 (aceitável para macro data)
  • Pressupostos validados (resíduos normais, sem autocorrelação)
  • Recomendações acionáveis geradas

✅ ENTREGA
  • Excel consolidado com 6 abas pronto
  • Apresentação para comercial pronta
  • Notebooks funcionais (sem erros)
  • Documentação completa

═══════════════════════════════════════════════════════════════════════════════

DECISÕES-CHAVE ANTES DE COMEÇAR
─────────────────────────────────────────────────────────────────────────────

❓ Qual é a granularidade operacional?
  → Por cluster? Cluster × Família? Cliente-mês?
  → Decidir com PM ANTES de Fase 2

❓ Há dados de competidor/custo como instrumentos?
  → SIM: adiciona robustez (controla endogeneidade)
  → NÃO: usar regressão com lags

❓ Qual período focar?
  → Padrão: todo histórico (jan/2023 – set/2026)
  → Se variância baixa: expandir ou simplificar segmentos

═══════════════════════════════════════════════════════════════════════════════

TIMELINE RESUMIDA
─────────────────────────────────────────────────────────────────────────────

DIA 1-2  Fase 1 (EDA_elasticidade)
├─ Setup + Carregamento
├─ Variação de preço + Decision Gate
├─ Série temporal + Clusters
└─ Status: 100% → GO/NO-GO?

DIA 3-4  Fase 2 (Modelagem)
├─ Modelos 1-2 (agregado + cluster)
├─ Modelo 3 (segmento)
├─ Modelo 4-5 (painel + robustez)
└─ Status: 80% → Resultados parciais

DIA 5    Consolidação & Entrega
├─ Excel final
├─ Apresentação
├─ QA
└─ Status: 100% → PRONTO ✅

═══════════════════════════════════════════════════════════════════════════════

🚀 COMECE AGORA!

1. Abra: QUICK_START.txt
2. Confirme com PM: "Vamos fazer elasticidade?"
3. Abra Jupyter: 5.EDA_elasticidade.ipynb
4. Copie: template_5_EDA_elasticidade_skeleton.py
5. Execute seção por seção
6. Volte com resultados Fase 1 (gráficos + relatório)
7. Se GO: inicie Fase 2 (elasticidade.ipynb)

Boa sorte! 🎯
```

---

## 📞 Como Usar

### Opção 1: CLI Direto
```bash
claude_code run --task "Executar análise completa de elasticidade preço-demanda VIBRA LUBRAX

[Cole o PROMPT COMPLETO acima]
"
```

### Opção 2: Arquivo de Tarefa
```bash
# Salvar prompt em arquivo
cat > elasticidade_task.txt << 'EOF'
[Cole o PROMPT COMPLETO aqui]
EOF

# Executar
claude_code run --task-file elasticidade_task.txt
```

### Opção 3: Integração com Workflow
```bash
# Se você usar o Claude Code para automação
claude_code delegate --project "VIBRA LUBRAX" --phase "elasticidade_completa"
```

---

## 🎯 O Que Este Prompt Faz

✅ **Fase 1 (EDA):** Valida dados, gera 5 gráficos, decision gate GO/NO-GO  
✅ **Fase 2 (Modelagem):** 5 modelos de regressão + robustez + simulação  
✅ **Entrega:** Excel consolidado com 6 abas + apresentação  
✅ **Controle:** Checkpoints em cada seção para validação de qualidade  
✅ **Documentação:** Critérios de sucesso, riscos, próximos passos claros  

---

## 📋 Checklist Antes de Executar

- [ ] Tenho base_Lubrax_origem.xlsx acessível?
- [ ] Python 3.10+ instalado com pandas, numpy, matplotlib, seaborn, statsmodels?
- [ ] Pasta `outputs/3.Elasticidade/` criada?
- [ ] Template `template_5_EDA_elasticidade_skeleton.py` em mão?
- [ ] Confirmei com PM: "Vamos proceder com elasticidade?"
- [ ] Decidi: granularidade operacional (cluster? segmento?)?

**Se tudo ✓:** Copie o prompt acima e execute no Claude Code! 🚀

