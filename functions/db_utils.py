import pandas as pd
import openpyxl
from unidecode import unidecode
import os
import json
import streamlit as st

# ============================================================
# UTILITÁRIOS DE PADRONIZAÇÃO
# ============================================================

def _norm(s: str) -> str:
    """Normaliza string: minúsculo, sem acento, sem espaços extras."""
    return unidecode((str(s) or "").strip().lower())

# ============================================================
# CARREGAMENTO DE BASES
# ============================================================

def load_dim_produtos(file_path='data/dim_produtos.xlsx'):
    """Carrega e padroniza a planilha de produtos."""
    dim_produto = pd.read_excel(file_path, index_col=False)
    dim_produto.columns = [unidecode(col).lower().replace(" ", "_") for col in dim_produto.columns]
    return dim_produto


def load_receitas(file_path="data/receitas.xlsx") -> dict:
    """Lê receitas do Excel e retorna um dicionário agrupado por prato."""
    if not os.path.exists(file_path):
        return {}

    df_receitas = pd.read_excel(file_path)

    # Normalizar colunas e texto
    df_receitas.columns = [unidecode(c).strip().lower() for c in df_receitas.columns]
    df_receitas['prato'] = df_receitas['prato'].map(_norm)
    df_receitas['produto'] = df_receitas['produto'].map(_norm)

    receitas = {}

    for prato in df_receitas['prato'].unique():
        subset = df_receitas[df_receitas['prato'] == prato]
        ingredientes = []
        for _, row in subset.iterrows():
            ingredientes.append({
                "produto": row["produto"],
                "quantidade": row["quantidade"],
                "unidade": row["unidade"]
            })
        receitas[prato] = ingredientes

    return receitas


def salvar_receitas_json(file_path_excel="data/receitas.xlsx", file_path_json="data/receitas.json"):
    """Gera um JSON com as receitas (útil para backup ou outras integrações)."""
    receitas = load_receitas(file_path_excel)
    with open(file_path_json, "w", encoding="utf-8") as f:
        json.dump(receitas, f, ensure_ascii=False, indent=4)
    return file_path_json

# ============================================================
# FUNÇÃO PRINCIPAL DE VERIFICAÇÃO DE ESTOQUE
# ============================================================

def verificar_disponibilidade(prato: str, estoque_path="data/estoque_inicial.xlsx", receitas_path="data/receitas.xlsx"):
    # Normalizar nome do prato
    prato = _norm(prato)

    # Carregar estoque e receitas
    df_estoque = pd.read_excel(estoque_path)
    df_estoque['produto'] = df_estoque['produto'].map(_norm)
    receitas = load_receitas(receitas_path)

    if prato not in receitas:
        return False, [f"❌ Receita '{prato}' não encontrada no arquivo de receitas."]

    ingredientes = receitas[prato]
    resultado = []
    disponivel = True

    for item in ingredientes:
        produto = item["produto"]
        qtd_necessaria = item["quantidade"]
        unidade = item["unidade"]

        estoque_item = df_estoque[df_estoque["produto"] == produto]

        if estoque_item.empty:
            resultado.append(f"❌ {produto} não encontrado no estoque")
            disponivel = False
        else:
            qtd_disponivel = estoque_item["quantidade_disponivel"].values[0]
            if qtd_disponivel >= qtd_necessaria:
                resultado.append(f"✅ {produto}: disponível ({qtd_disponivel}/{qtd_necessaria} {unidade})")
            else:
                resultado.append(f"⚠️ {produto}: insuficiente ({qtd_disponivel}/{qtd_necessaria} {unidade})")
                disponivel = False

    return disponivel, resultado

# ============================================================
# FUNÇÃO PRINCIPAL DE ALTERAÇÃO DE ESTOQUE
# ============================================================

# Caminho do arquivo de estoque
ESTOQUE_PATH = "data/estoque_inicial.xlsx"

# ---------------- FUNÇÕES AUXILIARES ----------------

def carregar_estoque(path="data/estoque_inicial.xlsx"):
    """Carrega e padroniza o arquivo de estoque."""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["produto", "quantidade_disponivel", "unidade"])
    
    df = pd.read_excel(path)
    df.columns = [unidecode(c).strip().lower().replace(" ", "_") for c in df.columns]
    df["produto"] = df["produto"].map(_norm)
    return df


def salvar_estoque(df, path="data/estoque_inicial.xlsx"):
    """Salva o DataFrame atualizado no arquivo Excel."""
    df.to_excel(path, index=False)


def produtos_faltantes_no_estoque(dim_path="data/dim_produtos.xlsx", estoque_path="data/estoque_inicial.xlsx"):
    """Retorna os produtos da dimensão que ainda não estão no estoque."""
    if not os.path.exists(dim_path):
        return []

    df_dim = pd.read_excel(dim_path)
    df_dim.columns = [unidecode(c).strip().lower().replace(" ", "_") for c in df_dim.columns]
    df_dim["descricao"] = df_dim["descricao"].map(_norm)
    df_dim["unidade_de_medida"] = df_dim["unidade_de_medida"].map(str)

    df_estoque = carregar_estoque(estoque_path)

    # Identificar produtos que ainda não estão no estoque
    produtos_no_estoque = set(df_estoque["produto"].tolist())
    produtos_faltantes = df_dim[~df_dim["descricao"].isin(produtos_no_estoque)]

    return produtos_faltantes[["descricao", "unidade_de_medida"]]