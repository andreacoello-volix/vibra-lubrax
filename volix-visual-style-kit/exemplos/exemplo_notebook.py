# Exemplo de uso do tema visual Volix em um notebook / script Python.
# Copie a pasta Script/ para a raiz do projeto antes de rodar isto.

import matplotlib.pyplot as plt
import numpy as np

from Script.tema_visual import (
    configurar_tema,
    aplicar_estilo_grafico,
    painel_kpis_terminal,
    tabela_terminal,
    cabecalho_secao,
    nota_aviso,
    fmt_num,
    COR_ACENTO,
    COR_AVISO,
    COR_FUNDO,
    COR_TEXTO,
    COR_MUTED,
)
import pandas as pd

# 1. Ativa o tema (CSS do notebook + rcParams do matplotlib)
configurar_tema()

# 2. Cabeçalho de seção
cabecalho_secao("Diagnóstico de exemplo", badge="DEMO")

# 3. Painel de KPIs
painel_kpis_terminal(
    [
        ("Clientes ativos", fmt_num(1234), COR_ACENTO),
        ("Receita total", f"R$ {fmt_num(2_500_000.0)}", COR_ACENTO),
        ("Elasticidade média", "-1.42", COR_AVISO),
    ],
    titulo="Resumo do período",
)

# 4. Tabela estilizada
df_exemplo = pd.DataFrame(
    {"cliente": ["C1", "C2", "C3"], "receita": [10000, 8500, 12300]}
)
tabela_terminal(df_exemplo, titulo="Top clientes")

# 5. Nota de aviso
nota_aviso(
    "Amostra pequena (n=3): use apenas para validar o layout, não para decisão.",
    titulo="Aviso",
)

# 6. Gráfico com o tema aplicado
fig, ax = plt.subplots(figsize=(9, 5))
x = np.linspace(0, 10, 50)
ax.plot(x, np.sin(x), color=COR_ACENTO, linewidth=2, label="Série principal")
ax.axhline(0, color=COR_MUTED, linewidth=1)
ax.set_title("Exemplo de gráfico com o tema Volix")
ax.set_xlabel("Eixo X")
ax.set_ylabel("Eixo Y")
ax.legend()
aplicar_estilo_grafico(ax)
plt.show()
