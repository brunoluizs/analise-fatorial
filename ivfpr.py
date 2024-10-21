import pandas as pd
import visual

salario_min = 1320

# Recuperação dos dados
df = pd.read_csv('dados/dados_familias.csv', encoding='latin-1', sep=',')

#print(df.columns)

df_out = pd.DataFrame()
rawdata_out = pd.DataFrame()

ind_max = df.shape[0]

for ind in df.index:
    visual.printProgressBar(ind, ind_max, prefix='Progress:', suffix='Complete', length=50)

    # Dimensão Domicílio
    ivfpr = {'1.2': 3 if (df[' d.qtd_pessoas_domic_fam'][ind] / df[' d.qtd_comodos_dormitorio_fam'][ind]) > 3 else 0,
             '1.3': 2 if df[' d.cod_material_domic_fam'][ind] not in [1, 2, 3] else 0,
             '1.4': 3 if df[' d.cod_agua_canalizada_fam'][ind] == 2 else 0,
             '1.5': 4 if df[' d.cod_banheiro_domic_fam'][ind] == 2 else 0 if df[' d.cod_escoa_sanitario_domic_fam'][ind] == 1 else 2}

    data = {'dens_pessoas_dorm': (df[' d.qtd_pessoas_domic_fam'][ind] / df[' d.qtd_comodos_dormitorio_fam'][ind]) if df[' d.qtd_comodos_dormitorio_fam'][ind] > 0 else 0,
            'cod_material_domic': df[' d.cod_material_domic_fam'][ind],
            'cod_agua_canalizada': df[' d.cod_agua_canalizada_fam'][ind],
            'cod_banheiro': df[' d.cod_banheiro_domic_fam'][ind],
            'cod_escoamento': df[' d.cod_escoa_sanitario_domic_fam'][ind]}

    # Dimensão de Composição Familiar
    ivfpr.update({'2.1': 2 if df[' p.conjuge'][ind] == 2 else 0,
                  '2.2': 6 if df[' p.idade'][ind] < 18 else 2 if (df[' d.qtd_criancas'][ind]/(df[' d.qtd_pessoas_domic_fam'][ind]-df[' d.qtd_criancas'][ind])) >= 1 else 0,
                  '2.3': 2 if df[' p.ind_trabalho_infantil_pessoa'][ind] == 1 else 0,
                  '2.4': 1 if df[' d.qtd_pessoa_inter_0_17_anos_fam'][ind] == 1 else 0,
                  '2.5': 1 if df[' d.qtd_pessoa_inter_18_64_anos_fam'][ind] == 1 else 0,
                  '2.6': 1 if df[' d.qtd_pessoa_inter_65_anos_fam'][ind] == 1 else 0,
                  '2.7': 3 if df[' d.qtd_defic_fam'][ind] > 1 else 1 if df[' d.qtd_defic_fam'][ind] == 1 else 0,
                  '2.8': 2 if df[' d.qtd_idosos_agregados'][ind] > 1 else 0,
                  '2.9': 2 if df[' p.cod_sabe_ler_escrever_memb'][ind] == 2 else 0})

    data.update({'conjuge': df[' p.conjuge'][ind],
                 'idade_rf': df[' p.idade'][ind],
                 'prop_criancas_adultos': df[' d.qtd_criancas'][ind]/(df[' d.qtd_pessoas_domic_fam'][ind]-df[' d.qtd_criancas'][ind]) if (df[' d.qtd_pessoas_domic_fam'][ind]-df[' d.qtd_criancas'][ind]) > 0 else 0,
                 'trab_infantil': df[' p.ind_trabalho_infantil_pessoa'][ind],
                 'qtd_internados': df[' d.qtd_pessoa_inter_0_17_anos_fam'][ind] +
                                   df[' d.qtd_pessoa_inter_18_64_anos_fam'][ind] +
                                   df[' d.qtd_pessoa_inter_65_anos_fam'][ind],
                 'qtd_defic': df[' d.qtd_defic_fam'][ind],
                 'qtd_idosos_ag': df[' d.qtd_idosos_agregados'][ind],
                 'cod_sabe_ler_escrever_rf': df[' p.cod_sabe_ler_escrever_memb'][ind]})

    # Dimensão Renda e Trabalho
    ivfpr.update({'3.1': 7 if (df[' d.qtd_adultos'][ind] == 0 and df[' d.qtd_idosos'][ind] == 0) else
                         5 if (df[' d.qtd_adultos'][ind] == 0 and df[' d.vlr_renda_total_fam'][ind] == 0) else
                         4 if (df[' d.qtd_adultos'][ind]/(df[' d.qtd_idosos'][ind]+df[' d.qtd_criancas'][ind]) < 0.5) else
                         2 if (df[' d.qtd_adultos'][ind]/(df[' d.qtd_idosos'][ind]+df[' d.qtd_criancas'][ind]) < 0.75) else 0,
                  '3.2': 6 if df[' d.vlr_renda_media_fam'][ind] <= salario_min/4 else
                         3 if df[' d.vlr_renda_media_fam'][ind] <= salario_min/2 else 0})

    data.update({'adultos_idade_ativa': 0 if df[' d.qtd_adultos'][ind] == 0 else df[' d.qtd_adultos'][ind] if (df[' d.qtd_idosos'][ind]+df[' d.qtd_criancas'][ind]) == 0 else
                    df[' d.qtd_adultos'][ind]/(df[' d.qtd_idosos'][ind]+df[' d.qtd_criancas'][ind]),
                 'renda_total': df[' d.vlr_renda_total_fam'][ind],
                 'renda_media': df[' d.vlr_renda_media_fam'][ind]})

    # Dimensão Escolaridade
    ivfpr.update({'4.1': 4 if df[' d.qtd_criancas_6_17_fora_escola'][ind] > 1 else
                         3 if df[' d.qtd_criancas_6_17_fora_escola'][ind] == 1 else
                         2 if df[' d.qtd_criancas_0_5_fora_escola'][ind] >= 1 else 0,
                  '4.2': 2 if df[' d.criancas_defasagem'][ind] >= 1 else 0,
                  '4.3': 2 if df[' d.adulto_sem_ef'][ind] >= 1 else 0
            })

    data.update({'qtd_criancas_fora_escola': df[' d.qtd_criancas_6_17_fora_escola'][ind]+df[' d.qtd_criancas_0_5_fora_escola'][ind],
                 'qtd_criancas_defasagem': df[' d.criancas_defasagem'][ind],
                 'adulto_sem_ef': df[' d.adulto_sem_ef'][ind]})

    rawdata_out = pd.concat([rawdata_out, pd.DataFrame(data=data, index=[ind])])
    df_out = pd.concat([df_out, pd.DataFrame(data=ivfpr, index=[ind])])

print('\nGerando dimensões')
df_out['DIM 1'] = df_out.filter(regex='1.').sum(axis=1)
df_out['DIM 2'] = df_out.filter(regex='2.').sum(axis=1)
df_out['DIM 3'] = df_out.filter(regex='3.').sum(axis=1)
df_out['DIM 4'] = df_out.filter(regex='4.').sum(axis=1)

print('Calculando índice')
df_out['% D1'] = df_out['DIM 1'] / 12
df_out['% D2'] = df_out['DIM 2'] / 20
df_out['% D3'] = df_out['DIM 3'] / 13
df_out['% D4'] = df_out['DIM 4'] / 8

df_out['IVFPR'] = df_out.filter(regex='DIM').sum(axis=1)
df_out['% IVFPR'] = df_out.filter(regex='% D').sum(axis=1) / 4
print('Processo finalizado')

df_out['lat'] = df['lat']
df_out['lon'] = df['lon']
df_out['regiao'] = df['regiao']

df_out.to_csv('dados/ivfpr.csv')
print('@out ivfpr.csv')
#df_out.sort_values(by=['% IVFPR'], inplace=True)
#df_out.to_excel('dados/ivfpr.xlsx')

rawdata_out['lat'] = df['lat']
rawdata_out['lon'] = df['lon']
rawdata_out['regiao'] = df['regiao']
rawdata_out.to_csv('dados/rawdata.csv')
print('@out rawdata.csv')
rawdata_out.to_excel('dados/rawdata.xlsx')
