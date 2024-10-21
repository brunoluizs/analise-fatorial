import pandas as pd
import numpy as np

splitRegioes = False
output = True

# Recuperação dos dados
df = pd.read_csv('dados/dados do Cadastro Único.csv', encoding='latin-1', sep=';')

# Contagem de dados faltantes e porcentagem
df_null = pd.DataFrame()

df_null['NULL'] = df.isnull().sum()
df_null['NULL PERCENT'] = np.round(df_null['NULL'] / len(df.index) * 100, 2)
df_null['DADO'] = df.columns

df_null.to_excel('dados/dados nulos.xlsx', index=False)

if splitRegioes:
    print('Filtrando dados por região')
    regioes = [x for _, x in df.groupby([' d.nom_unidade_territorial_fam'])]

    with pd.ExcelWriter('dados/dados_por_regiao.xlsx',
                            engine='openpyxl',
                            if_sheet_exists="replace",
                            mode='a') as writer:
        for i in range(len(regioes)):
            regioes[i].to_excel(writer, sheet_name='regiao '+str(i))

# Listar as regiões por nome
regioes = df[' d.nom_unidade_territorial_fam'].unique()
print(regioes)
# Gerar lista numérica equivalente às regiões
regioes_numerico = list(range(1, len(regioes)+1))
# Substituir os nomes por números
df[' d.nom_unidade_territorial_fam'] = df[' d.nom_unidade_territorial_fam'].replace(to_replace=regioes, value=regioes_numerico)

# Calcular a idade de cada uma das entradas baseados na data de nascimento
df[' p.idade'] = pd.to_datetime(df[' p.dta_nasc_pessoa'], format='%d/%m/%Y').apply(lambda x : (pd.to_datetime('now').year - x.year))
df.drop(columns=[' p.fx_idade'], inplace=True)

# Isolar apenas variáveis numéricas
df = df.select_dtypes(['number'])
df.drop(columns=['d.cd_ibge'], inplace=True)
df.drop(list(df.filter(regex=' p.fx_renda_individual')), axis=1, inplace=True)
print('\n\nCOLUNAS FILTRADAS:\n', df.columns)

# Agrupar índices de ajuda
ind_ajuda = df.filter(regex=' p.ind_ajuda(?!_nao)').fillna(0).max(axis=1)
df[' p.cod_ajuda_memb'] = ind_ajuda

# VERIFICAR FAIXA DE RENDA E TRATAR

# Remoção de colunas com mais de 80% de valores faltantes
limite = int(0.15*(len(df)))
df_out = df.dropna(axis=1, thresh=limite)
print('Colunas com mais de 85% de dados nulos removidas')

print('\n\nCOLUNAS FILTRADAS:\n', df_out.columns)

# Preenchimento de dados com o valor médio
## Mediana para valores discretos
## Média para valores contínuos
df_out = df_out.apply(lambda x: x.fillna(x.mean()) if ('val' in x.name or 'vlr' in x.name) else x.fillna(x.median()))
print('Preenchendo com a média ou mediana')

df_out.drop(df_out[df_out[' d.qtd_pessoas_domic_fam'] > 20].index, inplace=True)
df_out.drop(df_out[df_out[' d.qtd_pessoas_domic_fam'] < df_out[' d.qtd_familias_domic_fam']].index, inplace=True)


if output:
    df_out.to_csv('dados/dados_preprocessados.csv', index=False)
    print('CSV gerado')
    df_out.to_excel('dados/dados_preprocessados.xlsx', index=False)
    print('XLSX gerado')