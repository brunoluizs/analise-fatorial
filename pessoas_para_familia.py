import pandas as pd
import visual
import sys

# Recuperação dos dados
df_in = pd.read_csv('dados/dados_preprocessados.csv', encoding='latin-1')

ivout = sys.argv[1]
if ivout == 'ivfpr':
    print('Processando dados para o IVFPR')
    toIVFPR = True
elif ivout == 'raw':
    print('Processando dados puros')
    toIVFPR = False
else:
    print('INVÁLIDO:', ivout, 'não corresponde à [ivfpr] ou [raw].')
    sys.exit(1)

df = df_in[[' d.vlr_renda_media_fam',
            ' d.vlr_renda_total_fam',
            ' d.qtd_comodos_dormitorio_fam',
            ' d.cod_material_domic_fam',
            ' d.cod_agua_canalizada_fam',
            ' d.cod_banheiro_domic_fam',
            ' d.cod_escoa_sanitario_domic_fam',
            ' d.qtd_pessoas_domic_fam',
            ' p.ind_trabalho_infantil_pessoa',
            ' d.qtd_pessoa_inter_0_17_anos_fam',
            ' d.qtd_pessoa_inter_18_64_anos_fam',
            ' d.qtd_pessoa_inter_65_anos_fam',
            ' p.cod_parentesco_rf_pessoa',
            ' p.cod_deficiencia_memb',
            ' p.cod_sabe_ler_escrever_memb',
            ' p.cod_trabalhou_memb',
            ' p.cod_principal_trab_memb',
            ' p.ind_frequenta_escola_memb',
            ' p.cod_ano_serie_frequenta_memb',
            ' p.cod_curso_frequentou_pessoa_memb',
            ' p.cod_ano_serie_frequentou_memb',
            ' p.cod_concluiu_frequentou_memb',
            ' p.cod_ajuda_memb',
            ' p.idade',
            'lat',
            'lon',
            'regiao'
            ]]


# Valor máximo do índice
ind_max = df.shape[0]
c = 0

df_out = pd.DataFrame(columns=df.columns)

for ind in df.index:
    visual.printProgressBar(ind, ind_max, prefix='Progress:', suffix='Complete', length=50)
    # Se for um responsável familiar, copiar os dados
    if df[' p.cod_parentesco_rf_pessoa'][ind] == 1:
        dict_out = df.loc[ind].to_dict()

        k = list(range(int(-df[' d.qtd_pessoas_domic_fam'][ind]) + 1, int(df[' d.qtd_pessoas_domic_fam'][ind])))
        if 0 in k:
            k.remove(0)

        # Dados iniciais: assumem-se inexistentes
        dict_out.update({' d.qtd_defic_fam': 0, ' d.qtd_ajuda_fam': 0, ' p.conjuge': 2, ' d.qtd_criancas': 0,
                         ' d.qtd_idosos': 0, ' d.qtd_idosos_agregados': 0, ' d.qtd_criancas_0_5_fora_escola': 0,
                         ' d.qtd_criancas_6_17_fora_escola': 0, ' d.qtd_adultos' : 0 if df[' p.idade'][ind] < 18 else 1,
                         ' d.adulto_sem_ef': 1 if df[' p.cod_sabe_ler_escrever_memb'][ind] == 2 else 0,
                         ' d.criancas_defasagem': 0})
        for i in k:
            # Conferindo se os dados são da mesma família
            if ind + i > 0 and ind + i < ind_max and df.iloc[ind, 0:11].equals(df.iloc[ind + i, 0:11]):
                # Conferindo a existencia de pessoas deficientes e ajuda
                if df[' p.cod_deficiencia_memb'][ind + i] == 1:
                    dict_out.update({' d.qtd_defic_fam': dict_out[' d.qtd_defic_fam'] + 1})
                if df[' p.cod_ajuda_memb'][ind + i] == 1:
                    dict_out.update({' d.qtd_ajuda_fam': dict_out[' d.qtd_ajuda_fam'] + 1})

                # Contagem de pessoas na casa (conjuges, criancas, idosos, outros)
                if df[' p.cod_parentesco_rf_pessoa'][ind + i] == 2:
                    dict_out.update({' p.conjuge': 1,
                                     ' d.adulto_sem_ef': dict_out[' d.adulto_sem_ef'] + 1 if df[' p.cod_sabe_ler_escrever_memb'][ind + i] == 2 else dict_out[' d.adulto_sem_ef']})
                if df[' p.idade'][ind + i] < 18:
                    dict_out.update({' d.qtd_criancas': dict_out[' d.qtd_criancas'] + 1})
                    dict_out.update({' d.criancas_defasagem': dict_out[' d.criancas_defasagem'] + 1 if (dict_out[' p.idade'] - dict_out[' p.cod_ano_serie_frequenta_memb'] + 5) >= 3 else dict_out[' d.criancas_defasagem']})
                    # JUNTAR EM UMA VARIÁVEL DE CONTAGEM SÓ, REMOVER ÍNDICES PESSOAIS REDUNDANTES!!
                    if df[' p.ind_frequenta_escola_memb'][ind + i] in [3, 4]:
                        if df[' p.idade'][ind + i] < 5:
                            dict_out.update({' d.qtd_criancas_0_5_fora_escola': dict_out[' d.qtd_criancas_0_5_fora_escola'] + 1})
                        else:
                            dict_out.update({' d.qtd_criancas_6_17_fora_escola': dict_out[' d.qtd_criancas_6_17_fora_escola'] + 1})
                elif df[' p.idade'][ind + i] > 64:
                    dict_out.update({' d.qtd_idosos': dict_out[' d.qtd_idosos'] + 1})
                    if df[' p.cod_parentesco_rf_pessoa'][ind + i] in [10, 11]:
                        dict_out.update({' d.qtd_idosos_agregados': dict_out[' d.qtd_idosos_agregados'] + 1})
                else:
                    dict_out.update({' d.qtd_adultos': dict_out[' d.qtd_adultos'] + 1,
                                     ' d.adulto_sem_ef': dict_out[' d.adulto_sem_ef'] + 1 if df[' p.cod_sabe_ler_escrever_memb'][ind] == 2 else dict_out[' d.adulto_sem_ef']})

                if df[' p.ind_trabalho_infantil_pessoa'][ind + i] == 1:
                    print('UEPA:', c)
                    c += 1
                    dict_out.update({' p.ind_trabalho_infantil_pessoa': 1})

        df_out = pd.concat([df_out, pd.DataFrame(data=dict_out, index=[ind])])

if toIVFPR:
    df_out.drop(columns=[' p.cod_deficiencia_memb', ' p.cod_ajuda_memb'], inplace=True)
    df_out.to_csv('dados/dados_familias.csv')
    df_out.to_excel('dados/dados_familias.xlsx')

else:
    df_out[' d.qtd_pessoa_inter'] = df_out.filter(regex=' d.qtd_pessoa_inter').sum(axis=1)
    df_out[' d.qtd_adultos'] = df_out[' d.qtd_adultos'] + df_out[' d.qtd_idosos']
    df_out[' d.qtd_criancas_fora_escola'] = df_out.filter(regex=' d.qtd.criancas_').sum(axis=1)
    df_out.drop(columns=[' p.conjuge', ' d.qtd_criancas',
                         ' d.qtd_idosos', ' d.qtd_idosos_agregados', ' d.qtd_criancas_0_5_fora_escola',
                         ' d.qtd_criancas_6_17_fora_escola',
                         ' p.cod_concluiu_frequentou_memb', ' d.qtd_pessoa_inter_0_17_anos_fam',
                         ' d.qtd_pessoa_inter_18_64_anos_fam',
                         ' d.qtd_pessoa_inter_65_anos_fam', ' p.cod_ajuda_memb',
                         ' d.adulto_sem_ef'], inplace=True)
    df_out.drop(columns=[' p.ind_trabalho_infantil_pessoa',
                         ' p.cod_parentesco_rf_pessoa'
                         ], inplace=True)

    df_out.to_csv('dados/dados_fam_filtrados.csv')
    df_out.to_excel('dados/dados_fam_filtrados.xlsx')

