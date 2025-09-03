import pandas as pd
from unidecode import unidecode
import os

def load_dim_produtos(file_path='data/dim_produtos.xlsx'):
    dim_produto = pd.read_excel('data/dim_produtos.xlsx',index_col=False)

    #TRATAMENTO DAS COLUNAS PARA PADRONIZAÇÃO, RETIRANDO ACENTOS, ESPAÇOS E COLOCANDO TUDO EM MINÚSCULO

    #print(f'Colunas pré-processamento: {dim_produto.columns}')

    dim_produto.columns = [unidecode(col).lower().replace(" ", "_") for col in dim_produto.columns]

    #print(f'Colunas pós-processamento: {dim_produto.columns}')

    #print(f'Processamento finalizado!')

    return dim_produto


def _norm(s: str) -> str:
    return unidecode((str(s) or "").strip().lower())

def filtra_produtos(df: pd.DataFrame, query: str, top_n: int = 10) -> list[str]:
    """Filtra a coluna 'descricao' por contains insensível a acento/caixa."""
    if not query:
        return []
    q = _norm(query)
    mask = df["descricao"].astype(str).map(_norm).str.contains(q, na=False)
    return (
        df.loc[mask, "descricao"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .head(top_n)
        .tolist()
    )