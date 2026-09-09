# Vibra Lubrax — Segmentação de Clientes para Pricing

Projeto de clusterização (K-Means) da base **Sell In - Lubrificantes** para apoiar pricing
diferenciado por segmento de cliente, enriquecido com família de produto e frequência de compra.

## Estrutura

```text
.
├── docs/README.md         # Documentação consolidada: linhagem, dicionário de dados, metodologia
├── inputs/raw/            # Base principal, sem edição
├── notebooks/             # 1.EDA_Kmeans, 2.Kmeans, 4.Segmentacao-Hibrida, 7.Relatorio-Tecnico
├── outputs/               # Organizado por etapa da análise (1. EDA, 2. Clusterização, 3.Elasticidade)
└── Script/                # Tema visual Volix (matplotlib/Jupyter)
```

## Arquivo principal atual

`inputs/raw/base_Lubrax_origem.xlsx`, aba `Base Exportavel (1)`

- 253.624 registros;
- 110 colunas físicas (108 nomes únicos);
- período: janeiro/2023 a setembro/2026;
- exportação do dashboard Tableau "Sell in - Lubrificantes" (origem: Azure Synapse).

`inputs/raw/` deve ser preservado sem edição. Limpezas e transformações são gravadas em `outputs/`.

**Para tudo (linhagem completa, dicionário de dados, metodologia de clusterização, segmentação
híbrida, mapa de arquivos), veja [`docs/README.md`](docs/README.md).** Para o passo a passo da
análise com resultados, veja
`outputs/2. Clusterização/3.relatorios/relatorio_tecnico_clusterizacao_vibra_lubrax.html`.
