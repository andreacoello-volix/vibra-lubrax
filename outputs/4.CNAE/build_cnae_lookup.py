# -*- coding: utf-8 -*-
"""
Cruzamento CNPJ -> CNAE usando a base aberta da Receita Federal (snapshot 2026-08).

Le os 10 arquivos Estabelecimentos*.zip (dentro de raw_rf_cnpj_2026-08/) direto,
sem precisar descompactar manualmente -- o DuckDB le CSV dentro de zip via a
extensao 'httpfs'/'zipfs' nao e nativa, entao aqui descompactamos uma vez para
CSV (fica em disco, ~15-20GB) e depois consultamos com DuckDB.

Uso:
    python build_cnae_lookup.py
"""
import zipfile
import time
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(r'C:\Volix\vibra-lubrax')
CNAE_DIR = ROOT / 'outputs' / '4.CNAE'
RAW_DIR = CNAE_DIR / 'raw_rf_cnpj_2026-08'
EXTRACTED_DIR = RAW_DIR / 'extracted'
EXTRACTED_DIR.mkdir(exist_ok=True)

CNPJS_PATH = CNAE_DIR / 'cnpjs_projeto.csv'
OUT_PATH = CNAE_DIR / 'cnae_por_cnpj.csv'
OUT_GRUPO_PATH = CNAE_DIR / 'cnae_por_grupo_economico.csv'

ESTAB_COLS = [
    'cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'identificador_matriz_filial', 'nome_fantasia',
    'situacao_cadastral', 'data_situacao_cadastral', 'motivo_situacao_cadastral',
    'nome_cidade_exterior', 'pais', 'data_inicio_atividade', 'cnae_fiscal_principal',
    'cnae_fiscal_secundaria', 'tipo_logradouro', 'logradouro', 'numero', 'complemento',
    'bairro', 'cep', 'uf', 'municipio', 'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2',
    'ddd_fax', 'fax', 'correio_eletronico', 'situacao_especial', 'data_situacao_especial',
]


def extrair_zips():
    zips = sorted(RAW_DIR.glob('Estabelecimentos*.zip'))
    assert zips, f'Nenhum Estabelecimentos*.zip encontrado em {RAW_DIR}'
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                dest = EXTRACTED_DIR / name
                if dest.exists() and dest.stat().st_size > 0:
                    print(f'  já extraído: {name}')
                    continue
                print(f'  extraindo {name} de {z.name}...')
                t0 = time.perf_counter()
                zf.extract(name, EXTRACTED_DIR)
                print(f'  ok em {time.perf_counter() - t0:.1f}s')

    zip_cnaes = RAW_DIR / 'Cnaes.zip'
    with zipfile.ZipFile(zip_cnaes) as zf:
        for name in zf.namelist():
            dest = EXTRACTED_DIR / name
            if not dest.exists():
                zf.extract(name, EXTRACTED_DIR)


def ler_estabelecimentos_filtrado(csv_files, cnpj_basico_set):
    """DuckDB's read_csv rejeita esses arquivos com 'File is not latin-1 encoded'
    (parece um bug de validação da versão instalada) -- lendo com pandas em chunks
    em vez disso, que lida com latin-1 sem problema."""
    # usecols e names precisam estar na MESMA ordem crescente de posição --
    # pandas zip(usecols_ordenado, names) e não por posição original, então uma
    # ordem diferente (ex.: cnae antes de situacao_cadastral) bagunça o mapeamento.
    usecols = [0, 1, 2, 3, 5, 11, 12, 19, 20]
    names = ['cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'identificador_matriz_filial',
             'situacao_cadastral', 'cnae_fiscal_principal', 'cnae_fiscal_secundaria', 'uf', 'municipio']
    partes = []
    for f in csv_files:
        print(f'   lendo {f.name} ({f.stat().st_size / 1e9:.2f} GB)...')
        t0 = time.perf_counter()
        n_linhas = 0
        n_match = 0
        for chunk in pd.read_csv(f, sep=';', header=None, usecols=usecols, names=names,
                                  dtype=str, encoding='latin-1', chunksize=2_000_000,
                                  on_bad_lines='skip'):
            n_linhas += len(chunk)
            filtrado = chunk[chunk['cnpj_basico'].isin(cnpj_basico_set)]
            n_match += len(filtrado)
            if len(filtrado):
                partes.append(filtrado)
        print(f'     {n_linhas:,} linhas lidas, {n_match:,} match ({time.perf_counter()-t0:.1f}s)')
    if partes:
        return pd.concat(partes, ignore_index=True)
    return pd.DataFrame(columns=names)


def main():
    print('1) Extraindo zips (só na primeira vez)...')
    extrair_zips()

    print('\n2) Carregando lista de CNPJs do projeto...')
    cnpjs = pd.read_csv(CNPJS_PATH, dtype=str)
    print(f'   {len(cnpjs):,} CNPJs completos (14 dígitos), {cnpjs["cnpj_basico"].nunique():,} raízes únicas')
    cnpj_basico_set = set(cnpjs['cnpj_basico'])

    con = duckdb.connect()
    con.execute(f"CREATE TEMP TABLE cnpjs_projeto AS SELECT * FROM read_csv_auto('{CNPJS_PATH.as_posix()}', ALL_VARCHAR=TRUE)")

    csv_files = sorted(EXTRACTED_DIR.glob('*ESTABELE*'))
    if not csv_files:
        csv_files = [p for p in EXTRACTED_DIR.iterdir() if p.is_file() and 'CNAE' not in p.name.upper()]
    print(f'\n3) Arquivos CSV de estabelecimentos encontrados: {len(csv_files)}')

    print('\n4) Lendo e filtrando estabelecimentos (pode levar alguns minutos)...')
    t0 = time.perf_counter()
    estab_df = ler_estabelecimentos_filtrado(csv_files, cnpj_basico_set)
    con.register('estab', estab_df)
    n = len(estab_df)
    print(f'   {n:,} estabelecimentos encontrados para as raízes de CNPJ do projeto ({time.perf_counter()-t0:.1f}s)')

    print('\n5) Carregando dicionário de CNAEs...')
    cnaes_csv = list(EXTRACTED_DIR.glob('*CNAE*'))
    assert cnaes_csv, 'Cnaes.csv não encontrado'
    cnaes_df = pd.read_csv(cnaes_csv[0], sep=';', header=None, names=['cnae', 'cnae_descricao'],
                            dtype=str, encoding='latin-1')
    con.register('cnaes', cnaes_df)

    print('\n6) Juntando por CNPJ completo (14 dígitos) -- nível estabelecimento...')
    con.execute("""
        CREATE TEMP TABLE cnpj_completo AS
        SELECT p.cnpj_14, p.cnpj_basico, p.cnpj_ordem, p.cnpj_dv,
               e.identificador_matriz_filial, e.situacao_cadastral, e.uf, e.municipio,
               e.cnae_fiscal_principal, c.cnae_descricao AS cnae_principal_descricao,
               e.cnae_fiscal_secundaria
        FROM cnpjs_projeto p
        LEFT JOIN estab e
          ON p.cnpj_basico = e.cnpj_basico AND p.cnpj_ordem = e.cnpj_ordem AND p.cnpj_dv = e.cnpj_dv
        LEFT JOIN cnaes c ON e.cnae_fiscal_principal = c.cnae
    """)
    df_cnpj = con.execute("SELECT * FROM cnpj_completo").df()
    df_cnpj.to_csv(OUT_PATH, index=False, encoding='utf-8-sig')
    encontrados = df_cnpj['cnae_fiscal_principal'].notna().sum()
    print(f'   {encontrados:,} de {len(df_cnpj):,} CNPJs do projeto encontrados na base da RF')
    print(f'   Salvo em: {OUT_PATH}')

    print('\n7) Visão por grupo econômico (raiz do CNPJ, cnae mais frequente entre as filiais)...')
    con.execute("""
        CREATE TEMP TABLE grupo AS
        SELECT cnpj_basico,
               mode(cnae_fiscal_principal) AS cnae_mais_frequente,
               count(*) AS n_estabelecimentos_encontrados,
               count(DISTINCT cnae_fiscal_principal) AS n_cnaes_distintos
        FROM estab
        GROUP BY cnpj_basico
    """)
    con.execute("""
        CREATE TEMP TABLE grupo_final AS
        SELECT g.cnpj_basico, g.cnae_mais_frequente, c.cnae_descricao,
               g.n_estabelecimentos_encontrados, g.n_cnaes_distintos
        FROM grupo g
        LEFT JOIN cnaes c ON g.cnae_mais_frequente = c.cnae
    """)
    df_grupo = con.execute("SELECT * FROM grupo_final").df()
    df_grupo.to_csv(OUT_GRUPO_PATH, index=False, encoding='utf-8-sig')
    print(f'   {len(df_grupo):,} raízes de CNPJ (grupos econômicos) com CNAE resolvido')
    print(f'   Salvo em: {OUT_GRUPO_PATH}')

    print('\nCONCLUÍDO.')


if __name__ == '__main__':
    main()
