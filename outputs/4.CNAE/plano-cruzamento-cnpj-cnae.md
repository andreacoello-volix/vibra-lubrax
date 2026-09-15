# Plano — Cruzamento CNPJ → CNAE (segmentação por grupo econômico)

Status: **planejado, não iniciado**. Retomar quando a Fase 2 de features estiver fechada.

## Objetivo

Enriquecer a base de clientes (identificados por CNPJ) com o CNAE (Classificação Nacional de
Atividades Econômicas), para permitir segmentação por **grupo econômico / setor de atuação real**
do cliente — hoje a base só tem `setor_industrial_cliente`, que é 93% "Consumidor" (não discrimina
nada), e não existe CNAE nem em `pricing` nem em `pedidos.csv`.

## Por que base bruta da Receita Federal, e não API pública

Precisamos consultar ~7.500-8.000 CNPJs. Comparado:

| Opção | Problema |
|---|---|
| BrasilAPI (grátis, sem chave) | Sem rate limit publicado, mas sem SLA para lote de milhares de chamadas seguidas |
| ReceitaWS / CNPJ.ws (free tier) | 3 req/min → 40h+ só para consultar nossa base |
| Self-host Minha Receita (Postgres/Docker) | Infra extra injustificada para um enriquecimento pontual de ~8 mil linhas |
| **Base bruta RF (download + join offline)** | **Grátis, repetível, sem dependência de terceiro, atualização mensal** |

## Fonte de dados

- Dataset: "Cadastro Nacional da Pessoa Jurídica — CNPJ" (dados abertos)
- Hospedado em: `arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/` (pastas mensais)
- Indexado em: `dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj`
  e `gov.br/receitafederal/dados`
- Layout dos arquivos: `gov.br/receitafederal/dados/cnpj-metadados.pdf`
- Formato: CSV separado por `;`, encoding ISO-8859-1, sem header
- Atualização: mensal
- Tamanho: cresce a cada mês; estimativa atual (2026) da ordem de 8-12GB compactado / 30GB+
  descompactado (um snapshot de 2021 já tinha 4.68GB/17.1GB)

### Arquivos realmente necessários

Só precisamos de dois grupos, não do dump completo:

- `Estabelecimentos0.zip` a `Estabelecimentos9.zip` (10 arquivos) — contém `cnpj_basico`,
  `cnpj_ordem`, `cnpj_dv`, `cnae_fiscal_principal`, `cnae_fiscal_secundaria` por estabelecimento
- `Cnaes.zip` — dicionário pequeno código → descrição do CNAE

Não precisamos de `Empresas*.zip` (razão social, capital social — não usamos), nem de `Socios*`,
`Simples`, etc.

## Ponto de atenção: CNPJ completo vs raiz (grupo econômico)

CNAE é registrado **por estabelecimento** (CNPJ completo de 14 dígitos), não pela raiz (8 primeiros
dígitos). Matriz e cada filial podem ter CNAEs diferentes. Para "segmentação por grupo econômico"
precisamos decidir uma regra de consolidação quando formos agregar pela raiz:

- usar o CNAE da matriz (ordem `0001`), ou
- usar o CNAE mais frequente entre as filiais do grupo, ou
- manter a distribuição completa (grupo pode atuar em mais de um setor)

Essa decisão fica para quando formos de fato implementar — não é score-blocking para o resto da
Fase 2.

## Esboço de implementação (quando for retomado)

1. Resolver a pasta mensal mais recente no site da RF; baixar (com retomada de download) os 10
   arquivos `Estabelecimentos*.zip` + `Cnaes.zip`.
2. Descompactar; carregar com **DuckDB** (não pandas) lendo os 10 CSVs com schema explícito — mais
   rápido e mais leve em memória para um scan de 20-30GB.
3. Normalizar os CNPJs da nossa base: remover pontuação, zero-pad para 14 dígitos, separar em
   `cnpj_basico` (8) / `cnpj_ordem` (4) / `cnpj_dv` (2).
4. Filtrar Estabelecimentos onde `cnpj_basico || cnpj_ordem || cnpj_dv` está no nosso conjunto de
   CNPJs (ou filtrar só por `cnpj_basico`, se quisermos também capturar filiais irmãs do grupo).
5. Juntar `cnae_fiscal_principal` (e `cnae_fiscal_secundaria`, que vem `;`-separado) com `Cnaes.zip`
   para trazer a descrição do código.
6. Persistir o resultado já filtrado (só nossos ~7.500-8.000 CNPJs) em parquet/CSV, para que
   próximas rodadas não precisem reprocessar a base nacional inteira — só reprocessar quando quisermos
   atualizar para um snapshot mensal mais novo.
7. Empacotar como uma função reutilizável, algo como `lookup_cnae(lista_de_cnpjs) -> DataFrame`
   (CNPJ, CNAE principal, descrição, CNAEs secundários).

## Fontes consultadas

- https://github.com/aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ
- https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj
- https://www.gov.br/receitafederal/dados
- https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf
- https://docs.minhareceita.org/como-usar/
- https://github.com/cuducos/minha-receita
- https://docs.cnpj.ws/referencia-de-api/api-publica/limitacoes
