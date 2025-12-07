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

    # Carregar estoque e receitas0.00
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
            resultado.append(f"❌ {produto} não encontrado no estoque (0/{qtd_necessaria} {unidade})")
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

def preco_receita(prato: str, receitas_path="data/receitas.xlsx", estoque_path="data/estoque_inicial.xlsx"):
    """
    Calcula o preço total de uma receita com base nas quantidades e preços do estoque.
    Regras:
    - Se a unidade for g/ml -> preço informado é por Kg ou L, logo dividir por 1000.
    - Se a unidade for Kg/L/Un -> preço informado já é por unidade de venda.
    """
    prato = _norm(prato)
    receitas = load_receitas(receitas_path)
    df_estoque = carregar_estoque(estoque_path)

    if prato not in receitas:
        raise ValueError(f"Receita '{prato}' não encontrada.")

    # Garantir coluna de preço existe
    if "preco" not in df_estoque.columns:
        raise ValueError("A coluna 'preco' não foi encontrada em estoque_inicial.xlsx.")

    ingredientes = receitas[prato]
    resultados = []
    preco_total = 0.0

    for item in ingredientes:
        produto = item["produto"]
        qtd_necessaria = float(item["quantidade"])
        unidade_receita = str(item["unidade"]).strip().lower()

        # Buscar produto no estoque
        estoque_item = df_estoque[df_estoque["produto"] == produto]

        if estoque_item.empty:
            resultados.append({
                "Produto": produto,
                "Quantidade Necessária": qtd_necessaria,
                "Unidade": unidade_receita,
                "Custo da Porção (R$)": 0,
                "Status": "❌ Produto não encontrado"
            })
            continue

        preco_cheio = float(estoque_item["preco"].values[0])
        unidade_estoque = str(estoque_item["unidade"].values[0]).strip().lower()

        if unidade_estoque in ["kg", "l", "Un"]:
            preco_base = preco_cheio  # preço por Kg ou L
        elif unidade_estoque in ["g", "ml"]:
            preco_base = preco_cheio / 1000  # converter para preço por g ou ml

        # ---------------- CONVERSÃO DE UNIDADE ----------------
        # Caso 1: preço informado por Kg ou L
        if unidade_estoque in ["kg", "l"]:
            custo = preco_base * (qtd_necessaria / 1000)

        # Caso 2: preço informado por grama ou mililitro (menos comum)
        elif unidade_estoque in ["g", "ml"]:
            custo = preco_base * qtd_necessaria

        # Caso 3: preço informado por unidade
        elif unidade_estoque in ["un"]:
            custo = preco_base * qtd_necessaria

        else:
            custo = preco_base * qtd_necessaria  # fallback genérico

        preco_total += custo

        resultados.append({
            "Produto": produto,
            "Quantidade Necessária": qtd_necessaria,
            "Unidade": unidade_receita,
            "Custo da Porção (R$)": custo,
            "Status": "✅ Ok"
        })

    # Converter para DataFrame para exibir no Streamlit
    df_resultado = pd.DataFrame(resultados)
    df_resultado["Custo da Porção (R$)"] = df_resultado["Custo da Porção (R$)"].round(2)

    return df_resultado, round(preco_total, 2)