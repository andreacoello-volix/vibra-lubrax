# -*- coding: utf-8 -*-
import json, uuid

NB_PATH = r'C:\Volix\vibra-lubrax\notebooks\2.Kmeans.ipynb'


def new_id():
    return uuid.uuid4().hex[:16]


def md(src):
    return {'cell_type': 'markdown', 'metadata': {}, 'id': new_id(), 'source': src.splitlines(keepends=True)}


def code(src):
    return {'cell_type': 'code', 'metadata': {}, 'id': new_id(), 'execution_count': None, 'outputs': [],
            'source': src.splitlines(keepends=True)}


nb = json.load(open(NB_PATH, encoding='utf-8'))
cells = nb['cells']

idx_leitura = next(i for i, c in enumerate(cells)
                    if c['cell_type'] == 'markdown' and 'frequência de compra traz informação nova de segmentação' in ''.join(c['source']))

code_onde_vai = code(
    "# Onde os clientes do cluster Especial (modelo atual) vão parar no candidato de 6 features?\n"
    "data_cmp_freq = data.copy()\n"
    "data_cmp_freq['cluster_atual_nome'] = pd.Series(clusters_final, index=data.index).map(NOMES_CLUSTER)\n"
    "data_cmp_freq['cluster_candidato'] = labels_freq\n"
    "\n"
    "print(\"Perfil dos clusters no candidato de 6 features:\")\n"
    "perfil_freq = data_cmp_freq.groupby('cluster_candidato')[FEATURES_COM_FREQ].mean().round(2)\n"
    "perfil_freq['n_clientes'] = data_cmp_freq['cluster_candidato'].value_counts()\n"
    "display(perfil_freq.sort_values('volume_total'))\n"
    "\n"
    "print(\"\\nComo o cluster Especial atual (5 features) se redistribui no candidato (6 features), em %:\")\n"
    "ct_freq = pd.crosstab(data_cmp_freq['cluster_atual_nome'], data_cmp_freq['cluster_candidato'], normalize='index') * 100\n"
    "display(ct_freq.round(1))\n"
)

md_decisao = md(
    "**Decisão:** `frequencia_mensal_corrigida` **melhora as métricas** (silhueta 0,3436 vs. "
    "0,3186; Davies-Bouldin 1,0787 vs. 1,1048) e reorganiza clientes de verdade (ARI=0,554) — "
    "diferente de todas as outras candidatas testadas neste notebook, que pioravam pelo menos "
    "uma métrica. Ainda assim, **optamos por não adicioná-la ao K-Means**: olhando o perfil dos "
    "clusters e o cruzamento acima, 93,8% dos clientes do grupo **Especial** (o achado central "
    "desta segmentação — preço ~50% acima da média, pior margem) são absorvidos pelo mesmo "
    "cluster que recebe 95,7% do grupo **Pequeno**, e o preço médio desse cluster combinado "
    "(R$ 13.391/m³) fica perto do Pequeno, não do Especial — o sinal de preço que define o "
    "Especial se dilui. É uma troca real: métricas agregadas um pouco melhores, mas o segmento "
    "de negócio mais acionável do projeto deixa de existir como grupo isolado. Optamos pelo "
    "modelo de 5 features. `frequencia_mensal_corrigida` segue disponível como **enriquecimento** "
    "(`nivel_frequencia`, `4.Segmentacao-Hibrida.ipynb`).\n"
)

cells[idx_leitura + 1:idx_leitura + 1] = [code_onde_vai, md_decisao]

nb['cells'] = cells
with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('patched, total cells:', len(cells))
