import sklearn.metrics as met
import pandas as pd

df = pd.read_excel('comparacao.xlsx')

# print(df.head(10))

fx = [0.2, 0.3, 0.4, 0.5, 1.0]
fx_list = ['baixíssima', 'baixa', 'média', 'alta', 'altíssima']

def faixa(x):
    for i in range(len(fx)):
        if fx[i] >= x:
            return fx_list[i]


ivfpr = df['% IVFPR'].apply(lambda x: faixa(x)).astype("category").cat.set_categories(fx_list)
ivaf = df['Fatorial R'].apply(lambda x: faixa(x)).astype("category").cat.set_categories(fx_list)

print(ivfpr.value_counts(), ivaf.value_counts())

kappa = met.cohen_kappa_score(ivfpr, ivaf)

print('Cohen Kappa Score:', kappa)

print(ivfpr)

# ivfprcount = ivfpr.sort_values()
# ivafcount = ivaf.value_counts()
#
# print(ivfprcount.values, ivafcount.values)
#
matrix = pd.DataFrame(met.confusion_matrix(ivfpr, ivaf, labels=fx_list), columns=fx_list, index=fx_list)

matrix.to_excel("matriz de confusao ivfpr ivaf.xlsx")
#
print(matrix)