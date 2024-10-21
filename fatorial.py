import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from sklearn import preprocessing
from factor_analyzer import FactorAnalyzer
from factor_analyzer import calculate_bartlett_sphericity, calculate_kmo

# Parâmetros de saída
threshold = 0.6
testBartlett = True
testKMO = True
mostrarAutovalores = True
mostrarScreePlot = False
mostrarVariancia = True
toExcel = True
toLatex = False
libScore = True
overrideNumFatores = 10

# Leitura do arquivo
df = pd.read_csv('dados/dados_preprocessados.csv', encoding='latin-1')
df.drop(columns=[' d.nom_unidade_territorial_fam'], inplace=True)

# Remoção de colunas desnecessárias e padronização dos valores de entrada:
scaler = preprocessing.StandardScaler()
scaler.fit(df)
X = pd.DataFrame(scaler.transform(df))

X.columns = df.columns

X.to_excel('dados/dados_padronizados.xlsx', index=False)
#print(X)

# - - - -

# Teste de esfericidade de Bartlett
## p_value = 0, os dados podem ser fatorados e a matriz de correlação observada não é a identidade.
if testBartlett:
    chi_square_value, p_value = calculate_bartlett_sphericity(X)
    print('Teste da Esfericidade de Bartlett: chi² =', chi_square_value, 'p_value =', p_value)

# Teste de Kaiser-Meyer-Olkin
if testKMO:
    kmo_all, kmo_model = calculate_kmo(X)
    print('Valores de kmo_all =\n', kmo_all, '\n')
    print('KMO =', kmo_model)

# - - - -

# Criação do objeto da FactorAnalysis
## Realiza-se a análise fatorial com o número de fatores igual ao número de características com o método varimax para a
## escolha de quantos fatores serão utilizados na análise fatorial final
### A variável shape contem o número de linhas e o número de colunas do conjunto de dados.
### A posição [1] representa o número de colunas (características) do conjunto.
fa = FactorAnalyzer(n_factors=X.shape[1], method='principal')
fa.fit(X)

# Autovalores e Autovetores
values, vectors = sp.linalg.eigh(fa.corr_)
values = values[::-1]

if mostrarAutovalores:
    autovalores = pd.DataFrame(values)
    pd.DataFrame(values).transpose().to_excel('analise fatorial/autovalores.xlsx')
    #pd.DataFrame([vectors]).to_excel('analise fatorial/autovetores.xlsx')
    print('AUTOVALORES:', values, '\nAUTOVETORES:', vectors)

# Criação do scree plot
if mostrarScreePlot:
    fig, ax = plt.subplots()
    ax.plot(range(1, X.shape[1]+1), values, marker='o')
    ax.set(xlabel='n-ésimo autovalor', ylabel='autovalor')
    ax.grid()
    fig.savefig('analise fatorial/scree plot.png')
    plt.show()

if overrideNumFatores > 0:
    fatores = overrideNumFatores
else:
    fatores = sum(i >= 1.0 for i in values)

# Variância explicada pelos fatores
var_exp = [i / X.shape[1] for i in values]
if mostrarVariancia:
    print('VARIÂNCIA EXPLICADA PELOS FATORES:', np.round(var_exp, 5))

# Variância explicada para os n fatores
var_exp_somada = values[0:fatores].sum() / X.shape[1]
if mostrarVariancia:
    print('VARIÂNCIA EXPLICADA POR', fatores, 'FATORES:', var_exp_somada)

# Realização da análise de componentes principais + análise fatorial
fa = FactorAnalyzer(n_factors=fatores, rotation='varimax', method='principal')
fa.fit(X)

## Lista de nomes para as colunas da matriz abaixo
fatores_lista = ['FA' + str(val) for val in list(range(1, fatores+1))]

# Matriz de cargas fatoriais
L = pd.DataFrame(fa.loadings_)
## Arredondando valores para 4 casas decimais
np.round(L, 4)
L.index = X.columns
L.columns = fatores_lista

# Tabela de Comunalidades
comunalidades = fa.get_communalities()
df_com = pd.DataFrame(comunalidades)

# Cálculo de escores fatoriais realizados pela biblioteca
SCORES = fa.transform(X)
pd.DataFrame(SCORES).to_csv('analise fatorial/scores.csv')

# - - - -

# Cálculos manuais
## Pesos fatoriais
#print(L.shape)
W = np.dot(np.linalg.inv(np.dot(L.transpose(), L)), np.dot(L.transpose(), X.transpose()))
pd.DataFrame(W.transpose()).to_excel('analise fatorial/pesos.xlsx')
#print(W.shape)

## Escores fatoriais
#print(X.shape)
#S = np.dot(X, W)
#pd.DataFrame(S).to_csv('teste/escores.csv')
#print(S.shape)

# - - - -

# Escores final por média ponderada pelo autovetor
def escore_final(S):
    for i in range(fatores):
        return (values[i] * S[i]) / soma_ev


soma_ev = values.sum()
if libScore:
    FS = np.apply_along_axis(escore_final, axis=1, arr=SCORES)
else:
    FS = np.apply_along_axis(escore_final, axis=1, arr=S)
pd.DataFrame(FS).to_csv('analise fatorial/escores_finais.csv')

# Escores finais ordenados
FS_ord = np.sort(FS)
pd.DataFrame(FS_ord).to_csv('analise fatorial/escores_finais_ord.csv')

# Descrição dos dados
print(pd.DataFrame(FS).describe())

# - - - -

if toExcel:
    with pd.ExcelWriter('analise fatorial/analise_fatorial.xlsx',
                        mode='a',
                        engine="openpyxl",
                        if_sheet_exists="replace") as writer:

        df_com.to_excel(writer, sheet_name='Comunalidades', header=False, index=True)
        L.to_excel(writer, sheet_name='Cargas Fatoriais', header=True, index=True)

        for fator in fatores_lista:
            df_positive = L[fator].loc[L[fator] > threshold].sort_values(ascending=False)
            df_negative = L[fator].loc[L[fator] < -threshold].sort_values(ascending=True)
            df_out = pd.concat([df_positive, df_negative], axis=1)
            df_out.to_excel(writer, sheet_name=fator, header=False, index=True, float_format='%.4f')

# - - - -

# Geração do CSV contendo os dados originais + escores finais
df['Escores Finais'] = FS
df.to_csv('analise fatorial/conjunto_com_escores.csv')

# - - - -

if toLatex:
    stylerPesos = pd.DataFrame(W).transpose().style
    stylerPesos.format('{:.4f}')
    stylerPesos.index = X.columns
    stylerPesos.applymap_index(lambda v: "font-weight: bold;", axis="index").relabel_index(X.columns)
    stylerPesos.to_latex(buf='latex/pesos.tex', convert_css=True)

    stylerCargas = L.assign(Com=df_com, VarExp=1-df_com).style
    stylerCargas.format('{:.3f}')
    stylerCargas.index = X.columns
    stylerCargas.applymap_index(lambda v: "font-weight: bold;", axis="index")\
                .applymap_index(lambda v: "font-weight: bold;", axis="columns") \
                .highlight_between(axis=1, subset=fatores_lista, left=threshold, right=1, props='font-weight: bold') \
                .highlight_between(axis=1, subset=fatores_lista, left=-1, right=-threshold, props='font-weight: bold') \
                .relabel_index(X.columns)
    stylerCargas.to_latex(buf='latex/cargas.tex', convert_css=True)

    if mostrarAutovalores:
        stylerAutovalores = autovalores.transpose().style
        stylerAutovalores.format('{:.3f}').hide(axis=0)
        stylerAutovalores.to_latex(buf='latex/autovalores.tex', convert_css=True)
