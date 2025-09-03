import pandas as pd
from unidecode import unidecode
import os

def load_dim_produtos(file_path='data/dim_produtos.xlsx'):
    dim_produto = pd.read_excel('data/dim_produtos.xlsx',index_col=False)

    #TRATAMENTO DAS COLUNAS PARA PADRONIZAÇÃO, RETIRANDO ACENTOS, ESPAÇOS E COLOCANDO TUDO EM MINÚSCULO

    print(f'Colunas pré-processamento: {dim_produto.columns}')

    dim_produto.columns = [unidecode(col).lower().replace(" ", "_") for col in dim_produto.columns]

    print(f'Colunas pós-processamento: {dim_produto.columns}')

    print(f'Processamento finalizado!')

    return dim_produto