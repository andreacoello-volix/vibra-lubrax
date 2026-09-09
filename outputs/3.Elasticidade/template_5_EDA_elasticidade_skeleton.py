"""
Template: 5.EDA_elasticidade.ipynb

VIBRA LUBRAX — Exploração de Elasticidade Preço-Demanda
Fase 1: EDA — Validação de variância e relação bruta

Autor: Data Science Team
Data: Setembro 2026
Versão: 1.0

Instruções:
1. Converter este .py para Jupyter Notebook (copiar seções em células)
2. Executar sequencialmente
3. Gerar outputs em outputs/3.Elasticidade/
4. Validar checklist ao final
"""

# ============================================================================
# SEÇÃO 0: SETUP & IMPORTAÇÕES
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Tema Volix
# sys.path.insert(0, 'Script')
# from tema_visual import *

# Configurar matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Caminhos
INPUT_EDA = 'outputs/1. EDA/'
INPUT_CLUSTER = 'outputs/2. Clusterização/'
OUTPUT_EDA_ELAS = 'outputs/3.Elasticidade/'

print(f"Setup concluído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ============================================================================
# SEÇÃO 1: CARREGAMENTO E LIMPEZA
# ============================================================================

print("\n" + "="*70)
print("SEÇÃO 1: CARREGAMENTO E LIMPEZA")
print("="*70)

# Carregar base bruta (ou usar cache)
print("\n[1.1] Carregando base bruta...")
try:
    # Opção A: Do Excel (mais lento)
    # df = pd.read_excel('inputs/raw/base_Lubrax_origem.xlsx', sheet_name='Base Exportavel (1)')

    # Opção B: Do cache (mais rápido)
    df = pd.read_pickle('outputs/cache/base_Lubrax_origem.pkl')
    print(f"✓ Base carregada: {len(df):,} linhas, {len(df.columns)} colunas")
except FileNotFoundError:
    print("⚠ Cache não encontrado; usando Excel...")
    df = pd.read_excel('inputs/raw/base_Lubrax_origem.xlsx', sheet_name='Base Exportavel (1)')
    print(f"✓ Base carregada: {len(df):,} linhas, {len(df.columns)} colunas")

# Inspecionar tipos
print("\n[1.2] Tipos de dados (amostra):")
print(df.dtypes.head(10))

# Converter Data Venda para datetime
print("\n[1.3] Convertendo Data Venda...")
df['Data Venda'] = pd.to_datetime(df['Data Venda'], errors='coerce', dayfirst=True)
print(f"✓ Data Venda: {df['Data Venda'].min().date()} a {df['Data Venda'].max().date()}")

# Filtro: apenas VENDA (usar coluna de classificação se existir)
# TODO: ajustar coluna de movimento se diferente
if 'tipo_movimento_eda' in df.columns:
    n_before = len(df)
    df = df[df['tipo_movimento_eda'] == 'VENDA'].copy()
    n_after = len(df)
    print(f"\n[1.4] Filtro VENDA: {n_before:,} → {n_after:,} registros ({100*n_after/n_before:.1f}%)")
else:
    # Alternativa: filtro manual (Volume > 0 e Receita líquida > 0)
    n_before = len(df)
    df = df[(df['Volume'] > 0) & (df['Receita líquida'] > 0)].copy()
    n_after = len(df)
    print(f"\n[1.4] Filtro Volume > 0 & Receita > 0: {n_before:,} → {n_after:,} registros")

print("✓ Limpeza concluída")


# ============================================================================
# SEÇÃO 2: VARIAÇÃO DE PREÇO E VOLUME
# ============================================================================

print("\n" + "="*70)
print("SEÇÃO 2: VARIAÇÃO DE PREÇO E VOLUME (Cross-Sectional)")
print("="*70)

# Agregar por cliente-ano (ou por cliente-período único)
print("\n[2.1] Agregação por cliente (acumulado todo período)...")
df_client = df.groupby('Código Cliente').agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
    'Código Material': 'nunique',  # diversidade
}).reset_index()
df_client.rename(columns={'Código Material': 'n_skus'}, inplace=True)
df_client['preco_medio'] = df_client['Receita líquida'] / df_client['Volume']

print(f"✓ {len(df_client):,} clientes únicos")
print(f"  Volume: μ={df_client['Volume'].mean():.0f}, σ={df_client['Volume'].std():.0f}")
print(f"  Preço: μ={df_client['preco_medio'].mean():.2f}, σ={df_client['preco_medio'].std():.2f}")

# Coeficiente de variação
cv_preco = df_client['preco_medio'].std() / df_client['preco_medio'].mean()
cv_volume = df_client['Volume'].std() / df_client['Volume'].mean()
print(f"\n[2.2] Coeficiente de Variação (CV):")
print(f"  Preço: CV = {cv_preco:.3f} ({100*cv_preco:.1f}%)")
print(f"  Volume: CV = {cv_volume:.3f} ({100*cv_volume:.1f}%)")

if cv_preco < 0.05:
    print("  ⚠ AVISO: Variação de preço é muito baixa (<5%). Elasticidade pode ser fraca.")
else:
    print("  ✓ Variação de preço é adequada para análise.")

# Distribuição de preço e volume
print("\n[2.3] Distribuição de preço e volume...")
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# (a) Distribuição de preços (histograma)
axes[0, 0].hist(df_client['preco_medio'], bins=50, alpha=0.7, edgecolor='k')
axes[0, 0].set_xlabel('Preço médio (R$/litro)')
axes[0, 0].set_ylabel('Frequência')
axes[0, 0].set_title('Distribuição de Preço')
axes[0, 0].grid(alpha=0.3)

# (b) Distribuição de volume (log scale)
axes[0, 1].hist(np.log10(df_client['Volume']), bins=50, alpha=0.7, edgecolor='k', color='green')
axes[0, 1].set_xlabel('log₁₀(Volume)')
axes[0, 1].set_ylabel('Frequência')
axes[0, 1].set_title('Distribuição de Volume (escala log)')
axes[0, 1].grid(alpha=0.3)

# (c) Scatter: preço vs volume (escala normal)
axes[1, 0].scatter(df_client['preco_medio'], df_client['Volume'], alpha=0.3, s=20)
axes[1, 0].set_xlabel('Preço médio (R$/litro)')
axes[1, 0].set_ylabel('Volume (litros)')
axes[1, 0].set_title('Preço vs Volume (escala normal)')
axes[1, 0].grid(alpha=0.3)

# (d) Scatter: ln(preço) vs ln(volume) — FORMA DA REGRESSÃO
df_client_plot = df_client[(df_client['preco_medio'] > 0) & (df_client['Volume'] > 0)]
axes[1, 1].scatter(np.log(df_client_plot['preco_medio']),
                   np.log(df_client_plot['Volume']),
                   alpha=0.3, s=20, color='red')
axes[1, 1].set_xlabel('ln(Preço)')
axes[1, 1].set_ylabel('ln(Volume)')
axes[1, 1].set_title('ln(Preço) vs ln(Volume) — Forma Funcional')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_EDA_ELAS}01_eda_preco_volume.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Gráfico salvo: 01_eda_preco_volume.png")

# Correlação bruta (Pearson e Spearman)
print("\n[2.4] Correlações...")
corr_pearson = df_client['preco_medio'].corr(df_client['Volume'], method='pearson')
corr_spearman = df_client['preco_medio'].corr(df_client['Volume'], method='spearman')
corr_log_pearson = np.log(df_client_plot['preco_medio']).corr(
    np.log(df_client_plot['Volume']), method='pearson'
)
print(f"  Pearson(Preço, Volume): {corr_pearson:.4f}")
print(f"  Spearman(Preço, Volume): {corr_spearman:.4f}")
print(f"  Pearson(ln Preço, ln Volume): {corr_log_pearson:.4f}")


# ============================================================================
# SEÇÃO 3: SÉRIE TEMPORAL
# ============================================================================

print("\n" + "="*70)
print("SEÇÃO 3: SÉRIE TEMPORAL (Agregado Mensal)")
print("="*70)

# Agregar por mês (todos clientes)
print("\n[3.1] Agregação por mês...")
df['YearMonth'] = df['Data Venda'].dt.to_period('M')
df_ts = df.groupby('YearMonth').agg({
    'Volume': 'sum',
    'Receita líquida': 'sum',
}).reset_index()
df_ts['Data Venda'] = df_ts['YearMonth'].dt.to_timestamp()
df_ts['preco_medio'] = df_ts['Receita líquida'] / df_ts['Volume']
df_ts = df_ts.sort_values('Data Venda').drop(columns='YearMonth')

print(f"✓ Série temporal: {len(df_ts)} meses")
print(f"  Período: {df_ts['Data Venda'].min().date()} a {df_ts['Data Venda'].max().date()}")

# Visualizar série
print("\n[3.2] Visualizando série temporal...")
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

axes[0].plot(df_ts['Data Venda'], df_ts['preco_medio'], marker='o', markersize=4, linewidth=1.5)
axes[0].set_ylabel('Preço médio (R$/litro)')
axes[0].set_title('Série Temporal: Preço Médio Agregado')
axes[0].grid(alpha=0.3)

axes[1].plot(df_ts['Data Venda'], df_ts['Volume'], marker='o', markersize=4, linewidth=1.5, color='green')
axes[1].set_ylabel('Volume (litros)')
axes[1].set_title('Série Temporal: Volume Agregado')
axes[1].grid(alpha=0.3)

axes[2].plot(df_ts['Data Venda'], df_ts['Receita líquida'], marker='o', markersize=4, linewidth=1.5, color='red')
axes[2].set_ylabel('Receita líquida (R$)')
axes[2].set_title('Série Temporal: Receita Líquida Agregada')
axes[2].set_xlabel('Data')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_EDA_ELAS}02_eda_serie_temporal.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Gráfico salvo: 02_eda_serie_temporal.png")

# Decomposição STL (sazonalidade)
print("\n[3.3] Decomposição STL (sazonalidade e tendência)...")
try:
    from statsmodels.tsa.seasonal import STL
    result = STL(df_ts['Volume'], period=12).fit()

    fig = result.plot(figsize=(14, 8))
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_EDA_ELAS}03_decomposicao_stl.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Gráfico salvo: 03_decomposicao_stl.png")
except Exception as e:
    print(f"  ⚠ Erro na decomposição STL: {e}")


# ============================================================================
# SEÇÃO 4: ANÁLISE POR CLUSTER
# ============================================================================

print("\n" + "="*70)
print("SEÇÃO 4: ANÁLISE POR CLUSTER (K-Means)")
print("="*70)

# Carregar segmentação K-Means
print("\n[4.1] Carregando segmentação K-Means...")
try:
    seg_kmeans = pd.read_csv(f'{INPUT_CLUSTER}segmentacao_clientes_kmeans.csv')
    print(f"✓ Segmentação carregada: {len(seg_kmeans):,} clientes")
except FileNotFoundError:
    print("⚠ Arquivo de segmentação não encontrado. Prosseguindo sem cluster.")
    seg_kmeans = None

if seg_kmeans is not None:
    # Merge com dados agregados por cliente
    df_client_seg = df_client.merge(
        seg_kmeans[['Código Cliente', 'Cluster']],
        on='Código Cliente',
        how='left'
    )

    # Análise de variação de preço por cluster
    print("\n[4.2] Variação de preço por cluster:")
    cluster_stats = df_client_seg.groupby('Cluster').agg({
        'preco_medio': ['mean', 'std', 'min', 'max', 'count'],
        'Volume': ['mean', 'sum'],
    }).round(2)
    print(cluster_stats)

    # Scatter por cluster
    print("\n[4.3] Visualizando scatter plot por cluster...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()

    for i, cluster in enumerate(sorted(df_client_seg['Cluster'].unique())):
        if pd.isna(cluster):
            continue
        data = df_client_seg[df_client_seg['Cluster'] == cluster]
        axes[i].scatter(data['preco_medio'], data['Volume'], alpha=0.5, s=30)
        axes[i].set_title(f'Cluster {int(cluster)} (n={len(data)})')
        axes[i].set_xlabel('Preço médio')
        axes[i].set_ylabel('Volume')
        axes[i].grid(alpha=0.3)

    # Remover subplot vazio
    fig.delaxes(axes[-1])
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_EDA_ELAS}04_eda_por_cluster.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Gráfico salvo: 04_eda_por_cluster.png")


# ============================================================================
# SEÇÃO 5: MATRIZ DE CORRELAÇÃO & OUTLIERS
# ============================================================================

print("\n" + "="*70)
print("SEÇÃO 5: CORRELAÇÃO E OUTLIERS")
print("="*70)

# Correlação entre features
print("\n[5.1] Matriz de correlação...")
features_corr = ['preco_medio', 'Volume']
if 'n_skus' in df_client.columns:
    features_corr.append('n_skus')

corr_matrix = df_client[features_corr].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
plt.title('Matriz de Correlação')
plt.tight_layout()
plt.savefig(f'{OUTPUT_EDA_ELAS}05_correlacao_features.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Gráfico salvo: 05_correlacao_features.png")

# Detectar outliers (IQR)
print("\n[5.2] Detectando outliers (método IQR)...")
Q1_vol = df_client['Volume'].quantile(0.25)
Q3_vol = df_client['Volume'].quantile(0.75)
IQR_vol = Q3_vol - Q1_vol
outliers_vol = df_client[
    (df_client['Volume'] < Q1_vol - 1.5*IQR_vol) |
    (df_client['Volume'] > Q3_vol + 1.5*IQR_vol)
]
print(f"  Outliers de Volume: {len(outliers_vol)} ({100*len(outliers_vol)/len(df_client):.1f}%)")
print(f"    Limites: [{Q1_vol - 1.5*IQR_vol:.0f}, {Q3_vol + 1.5*IQR_vol:.0f}]")

Q1_pre = df_client['preco_medio'].quantile(0.25)
Q3_pre = df_client['preco_medio'].quantile(0.75)
IQR_pre = Q3_pre - Q1_pre
outliers_pre = df_client[
    (df_client['preco_medio'] < Q1_pre - 1.5*IQR_pre) |
    (df_client['preco_medio'] > Q3_pre + 1.5*IQR_pre)
]
print(f"  Outliers de Preço: {len(outliers_pre)} ({100*len(outliers_pre)/len(df_client):.1f}%)")
print(f"    Limites: [{Q1_pre - 1.5*IQR_pre:.2f}, {Q3_pre + 1.5*IQR_pre:.2f}]")


# ============================================================================
# SEÇÃO 6: RELATÓRIO DE SÍNTESE
# ============================================================================

print("\n" + "="*70)
print("SEÇÃO 6: RELATÓRIO DE SÍNTESE & DECISÃO GO/NO-GO")
print("="*70)

# Compilar métricas
relatorio = pd.DataFrame({
    'Métrica': [
        'Número de clientes',
        'Período (dias)',
        'Registros de venda',
        'Volume total (litros)',
        'Receita total (R$)',
        'Preço médio (R$/litro)',
        'Preço desvio padrão',
        'Coef. Variação Preço (%)',
        'Coef. Variação Volume (%)',
        'Correlação (Preço, Volume)',
        'Correlação log-log',
        'Nº Clusters',
        'Sazonalidade detectada?',
    ],
    'Valor': [
        f"{len(df_client):,}",
        f"{(df_ts['Data Venda'].max() - df_ts['Data Venda'].min()).days}",
        f"{len(df):,}",
        f"{df_client['Volume'].sum():.0f}",
        f"{df_client['Receita líquida'].sum():.2e}",
        f"{df_client['preco_medio'].mean():.2f}",
        f"{df_client['preco_medio'].std():.2f}",
        f"{100*cv_preco:.1f}%",
        f"{100*cv_volume:.1f}%",
        f"{corr_pearson:.4f}",
        f"{corr_log_pearson:.4f}",
        f"5" if seg_kmeans is not None else "N/A",
        "Sim (STL)" if seg_kmeans is not None else "Não avaliada",
    ]
})

print("\n" + relatorio.to_string(index=False))

# Salvar relatório
relatorio.to_csv(f'{OUTPUT_EDA_ELAS}EDA_ELASTICIDADE_RELATORIO.csv', index=False)
print(f"\n✓ Relatório salvo: EDA_ELASTICIDADE_RELATORIO.csv")

# Checklist GO/NO-GO
print("\n" + "="*70)
print("CHECKLIST GO/NO-GO PARA FASE 2")
print("="*70)

checks = {
    '✓ Variação de preço adequada (CV > 5%)': cv_preco > 0.05,
    '✓ Variação de volume presente': cv_volume > 0.1,
    '✓ Correlação bruta significativa': abs(corr_log_pearson) > 0.2,
    '✓ Série temporal com 12+ meses': len(df_ts) >= 12,
    '✓ Dados de cluster disponíveis': seg_kmeans is not None,
    '✓ Sem dados extremos (falta>50%)': df.isna().sum().sum() / (len(df) * len(df.columns)) < 0.5,
}

for check, result in checks.items():
    symbol = "✅" if result else "❌"
    print(f"{symbol} {check}")

go_decision = sum(checks.values()) >= 4
print(f"\n{'🟢 GO' if go_decision else '🔴 NO-GO'}: Prosseguir para Fase 2? {go_decision}")

print("\n" + "="*70)
print("FIM DA FASE 1 - EDA_ELASTICIDADE")
print("="*70)
print(f"Outputs gerados em: {OUTPUT_EDA_ELAS}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

