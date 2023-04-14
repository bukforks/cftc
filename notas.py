import zipfile
import pandas as pd
import requests
import io

link_cftc = 'https://www.cftc.gov/files/dea/history/com_disagg_xls_2023.zip'
download = requests.get(link_cftc)
arquivo = zipfile.ZipFile(io.BytesIO(download.content))
tabela = pd.read_excel(arquivo.open('c_year.xls'))
dados = tabela[['Market_and_Exchange_Names', 'Report_Date_as_MM_DD_YYYY', 'M_Money_Positions_Long_ALL', 'M_Money_Positions_Short_ALL']]

def texto(dados):
  
  commodities = ['WHEAT-SRW - CHICAGO BOARD OF TRADE', 
               'WHEAT-HRW - CHICAGO BOARD OF TRADE', 
               'SOYBEANS - CHICAGO BOARD OF TRADE', 
               'CORN - CHICAGO BOARD OF TRADE', 
               'FRZN CONCENTRATED ORANGE JUICE - ICE FUTURES U.S.', 
               'COTTON NO. 2 - ICE FUTURES U.S.', 
               'COCOA - ICE FUTURES U.S.', 
               'SUGAR NO. 11 - ICE FUTURES U.S.', 
               'COFFEE C - ICE FUTURES U.S.']

  notas = f''

  for commo in commodities:

    dados_final = dados.query('Market_and_Exchange_Names == @commo').reset_index()

    dados_final['Weekly_Balance'] = dados_final['M_Money_Positions_Long_ALL'] - dados_final['M_Money_Positions_Short_ALL']

    coluna_conta = dados_final['Weekly_Balance']

    coluna_nova = abs(coluna_conta)

    dados_final['Weekly_Variation'] = 0

    dados_final['Weekly_Variation'].loc[0] = coluna_nova.loc[0] / coluna_nova.loc[1] * 100 - 100

    variacao = abs(dados_final['Weekly_Variation'].loc[0])

    variacao = round(variacao, 1)

    variacao = str(variacao)

    variacao = variacao.replace('.0', '')

    variacao = variacao.replace('.', ',')

  # Movimento

    if dados_final['Weekly_Balance'].loc[0] > 0:
      inversao = 'alta'
    else:
      inversao = 'baixa'

    if dados_final['Weekly_Balance'].loc[0] > 0 and dados_final['Weekly_Balance'].loc[1] < 0:
      movimento = f'inverteram e agora apostam na {inversao}'
    elif dados_final['Weekly_Balance'].loc[0] < 0 and dados_final['Weekly_Balance'].loc[1] > 0:
      movimento = f'inverteram e agora apostam na {inversao}'
    else:
      if dados_final['Weekly_Variation'].loc[0] > 0:
        movimento = f'aumentaram em {variacao}%'
        tit_mov = 'aumenta'
      else:
        movimento = f'diminuíram em {variacao}%'
        tit_mov = 'recua'

    if dados_final['Weekly_Balance'].loc[0] > 0 and dados_final['Weekly_Balance'].loc[1] > 0:
      aposta = ' a aposta na alta '
    elif dados_final['Weekly_Balance'].loc[0] < 0 and dados_final['Weekly_Balance'].loc[1] < 0:
      aposta = ' a aposta na baixa '
    else:
      aposta = f' '

  # Nome da commodity

    produtos_dicionario = {'WHEAT-SRW - CHICAGO BOARD OF TRADE' : 'do trigo brando na bolsa de Chicago',
                         'WHEAT-HRW - CHICAGO BOARD OF TRADE': 'do trigo duro na bolsa de Chicago',
                         'SOYBEANS - CHICAGO BOARD OF TRADE': 'da soja na bolsa de Chicago',
                         'CORN - CHICAGO BOARD OF TRADE': 'do milho na bolsa de Chicago',
                         'FRZN CONCENTRATED ORANGE JUICE - ICE FUTURES U.S.': 'do suco de laranja concentrado e congelado (FCOJ) na bolsa de Nova York',
                         'COTTON NO. 2 - ICE FUTURES U.S.': 'do algodão na bolsa de Nova York',
                         'SUGAR NO. 11 - ICE FUTURES U.S.': 'do açúcar demerara na bolsa de Nova York',
                         'COFFEE C - ICE FUTURES U.S.': 'do café arábica na bolsa de Nova York',
                         'COCOA - ICE FUTURES U.S.' : 'do cacau na bolsa de Nova York'}


    produto = dados_final['Market_and_Exchange_Names'].loc[0]

    for chave, valor in produtos_dicionario.items():
      produto = produto.replace(chave, valor)

  # Datas    

    data_nova = dados['Report_Date_as_MM_DD_YYYY'].loc[0]
    data_antiga = dados['Report_Date_as_MM_DD_YYYY'].loc[1]

    if data_antiga.strftime('%B') == data_nova.strftime('%B'):
      data_antiga_extenso = data_antiga.strftime('%d')
    else:
      data_antiga_extenso = data_antiga.strftime('%d de %B')

    data_nova_extenso = data_nova.strftime('%d de %B')

    meses = {'January' : 'janeiro',
           'February': 'fevereiro',
           'March': 'março', 
           'April' : 'abril',
           'May' : 'maio',
           'June' :'junho',
           'July' : 'julho',
           'August' : 'agosto',
           'September' : 'setembro',
           'October' : 'outubro',
           'November' : 'novembro',
           'December' : 'dezembro'}

    for chave, valor in meses.items():
      data_antiga_extenso = data_antiga_extenso.replace(chave, valor)
      data_nova_extenso = data_nova_extenso.replace(chave, valor)

  # Frase saldo

    numero_recente = dados_final['Weekly_Balance'].loc[0]
    numero_recente_limpo = coluna_nova.loc[0]
    numero_recente_limpo = '{:,}'.format(numero_recente_limpo)
    numero_recente_limpo = str(numero_recente_limpo)
    numero_recente_limpo = numero_recente_limpo.replace(',', '.')

    numero_antigo = dados_final['Weekly_Balance'].loc[1]
    numero_antigo_limpo = coluna_nova.loc[1]
    numero_antigo_limpo = '{:,}'.format(numero_antigo_limpo)
    numero_antigo_limpo = str(numero_antigo_limpo)
    numero_antigo_limpo = numero_antigo_limpo.replace(',', '.')

    if numero_recente > 0 and numero_antigo > 0:
      frase_saldo = f'o saldo líquido de posições passou de {numero_antigo_limpo} para {numero_recente_limpo} contratos comprados.'
    elif numero_recente > 0 and numero_antigo < 0:
      frase_saldo = f'o saldo líquido de posições passou de {numero_antigo_limpo} contratos vendidos para {numero_recente_limpo} contratos comprados.'
    elif numero_recente < 0 and numero_antigo > 0:
      frase_saldo = f'o saldo líquido de posições passou de {numero_antigo_limpo} contratos comprados para {numero_recente_limpo} contratos vendidos.'
    else:
      frase_saldo = f'o saldo líquido de posições passou de {numero_antigo_limpo} para {numero_recente_limpo} contratos vendidos.'

  #Títulos e texto 

    if movimento == f'inverteram e agora apostam na {inversao}':
      titulo = f'<strong>CFTC: Fundos invertem e apostam na {inversao} {produto} </strong><br>')
    else:
      titulo = f'<strong>CFTC: Aposta na {inversao} {produto} {tit_mov} em {variacao}%</strong> <br>')

    texto = f'Os fundos especulativos {movimento}{aposta}{produto}, segundo a Comissão de Negociação de Futuros de Commodities (CFTC). Entre {data_antiga_extenso} e {data_nova_extenso}, {frase_saldo} <br><br>'
    notas += titulo + texto
  return notas
