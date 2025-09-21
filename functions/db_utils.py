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

# Dicionário de receitas
receitas = {
    "Brisket com Batata Frita": [
        {"produto": "Brisket Prime", "quantidade": 200, "unidade": "g"},
        {"produto": "Batata frita corte fino", "quantidade": 150, "unidade": "g"},
        {"produto": "Filtro p/ Café", "quantidade": 1, "unidade": "Un"}
    ],
    "Café com Copinho": [
        {"produto": "Filtro p/ Café", "quantidade": 1, "unidade": "Un"},
        {"produto": "Copinhos descartavel 80 ml - 100 unid", "quantidade": 1, "unidade": "Un"},
        {"produto": "Açúcar refinado", "quantidade": 10, "unidade": "g"}
    ],
    "Porção de Batata com Brisket Desfiado": [
        {"produto": "Batata frita corte fino", "quantidade": 200, "unidade": "g"},
        {"produto": "Brisket Prime", "quantidade": 100, "unidade": "g"},
        {"produto": "Colherinha de plástico pequena - c/500", "quantidade": 1, "unidade": "Un"}
    ]
}

def verificar_disponibilidade(prato: str, estoque_path="data/estoque_inicial.xlsx"):
    # Carregar estoque
    df_estoque = pd.read_excel(estoque_path)

    # Ingredientes da receita escolhida
    ingredientes = receitas[prato]

    resultado = []
    disponivel = True

    for item in ingredientes:
        produto = item["produto"]
        qtd_necessaria = item["quantidade"]
        unidade = item["unidade"]

        # Buscar produto no estoque
        estoque_item = df_estoque[df_estoque["produto"] == produto]

        if estoque_item.empty:
            resultado.append(f"❌ {produto} não encontrado no estoque")
            disponivel = False
        else:
            qtd_disponivel = estoque_item["quantidade_disponivel"].values[0]
            if qtd_disponivel >= qtd_necessaria:
                resultado.append(f"✅ {produto}: disponível ({qtd_disponivel} {unidade})")
            else:
                resultado.append(f"⚠️ {produto}: insuficiente ({qtd_disponivel}/{qtd_necessaria} {unidade})")
                disponivel = False

    return disponivel, resultado