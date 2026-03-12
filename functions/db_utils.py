import pandas as pd
from unidecode import unidecode
import os
import json
import streamlit as st
from textwrap import dedent
import html

# ============================================================
# UTILITÁRIOS DE PADRONIZAÇÃO
# ============================================================

ALLOWED_UNITS = {"g", "ml", "un"}

def _norm(s: str) -> str:
    """Normaliza string: minúsculo, sem acento, sem espaços extras."""
    return unidecode((str(s) or "").strip().lower())

def _norm_col(c: str) -> str:
    return unidecode(str(c)).strip().lower().replace(" ", "_")

def _norm_unit(u: str) -> str:
    u = _norm(u)
    # garante minúsculo e remove espaços
    u = u.replace(".", "").strip()
    return u

# ============================================================
# CARREGAMENTO DE RECEITAS
# ============================================================

def load_receitas(file_path="data/receitas.xlsx") -> dict:
    """Lê receitas do Excel e retorna um dicionário agrupado por prato."""
    if not os.path.exists(file_path):
        return {}

    df_receitas = pd.read_excel(file_path)

    # Normalizar colunas e texto
    df_receitas.columns = [_norm_col(c) for c in df_receitas.columns]

    # Esperado: prato, produto, quantidade, unidade
    for col in ["prato", "produto", "quantidade", "unidade"]:
        if col not in df_receitas.columns:
            raise ValueError(f"Coluna obrigatória '{col}' não encontrada em {file_path}.")

    df_receitas["prato"] = df_receitas["prato"].map(_norm)
    df_receitas["produto"] = df_receitas["produto"].map(_norm)
    df_receitas["unidade"] = df_receitas["unidade"].map(_norm_unit)

    receitas = {}
    for prato in df_receitas["prato"].unique():
        subset = df_receitas[df_receitas["prato"] == prato]
        ingredientes = []
        for _, row in subset.iterrows():
            ingredientes.append({
                "produto": row["produto"],
                "quantidade": float(row["quantidade"]),
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
# ESTOQUE (BASE ÚNICA)
# ============================================================

ESTOQUE_PATH = "data/estoque_inicial.xlsx"

def carregar_estoque(path=ESTOQUE_PATH, sheet_name="Sheet1"):
    """Carrega e padroniza o arquivo de estoque."""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["produto", "quantidade_disponivel", "unidade", "preco", "quantidade_embalagem"])

    df = pd.read_excel(path, sheet_name=sheet_name)
    df.columns = [_norm_col(c) for c in df.columns]

    # Colunas mínimas esperadas
    required = {"produto", "quantidade_disponivel", "unidade"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltam colunas obrigatórias no estoque ({path}): {sorted(missing)}")

    df["produto"] = df["produto"].map(_norm)
    df["unidade"] = df["unidade"].map(_norm_unit)

    # validação de unidade (somente g/ml/un)
    unidades_invalidas = sorted(set(df["unidade"].dropna()) - ALLOWED_UNITS)
    if unidades_invalidas:
        raise ValueError(
            f"Unidades inválidas encontradas no estoque: {unidades_invalidas}. "
            f"Permitidas: {sorted(ALLOWED_UNITS)}"
        )

    return df


def salvar_estoque(df, path=ESTOQUE_PATH, sheet_name="Sheet1"):
    """Salva o DataFrame atualizado no arquivo Excel."""
    df.to_excel(path, sheet_name=sheet_name, index=False)

# ============================================================
# VERIFICAÇÃO DE DISPONIBILIDADE (RECEITA x ESTOQUE)
# ============================================================

def verificar_disponibilidade(
    prato: str,
    estoque_path=ESTOQUE_PATH,
    receitas_path="data/receitas.xlsx",
    sheet_path="Sheet1"
):
    prato = _norm(prato)

    df_estoque = carregar_estoque(estoque_path, sheet_name=sheet_path)
    receitas = load_receitas(receitas_path)

    if prato not in receitas:
        return False, [f"❌ Receita '{prato}' não encontrada no arquivo de receitas."]

    ingredientes = receitas[prato]
    resultado = []
    disponivel = True

    for item in ingredientes:
        produto = item["produto"]
        qtd_necessaria = int(item["quantidade"])
        unidade_receita = _norm_unit(item["unidade"])

        if unidade_receita not in ALLOWED_UNITS:
            resultado.append(f"❌ Unidade inválida na receita para {produto}: '{unidade_receita}'")
            disponivel = False
            continue

        estoque_item = df_estoque[df_estoque["produto"] == produto]

        if estoque_item.empty:
            resultado.append(f"❌ {produto} não encontrado no estoque (0/{qtd_necessaria} {unidade_receita})")
            disponivel = False
            continue

        qtd_disponivel = int(estoque_item["quantidade_disponivel"].values[0])
        unidade_estoque = _norm_unit(estoque_item["unidade"].values[0])

        # conflito de unidade
        if unidade_estoque != unidade_receita:
            resultado.append(
                f"⚠️ {produto}: unidade divergente (estoque: {unidade_estoque} vs receita: {unidade_receita})"
            )
            disponivel = False
            continue

        if qtd_disponivel >= qtd_necessaria:
            resultado.append(f"✅ {produto}: disponível ({qtd_disponivel}/{qtd_necessaria} {unidade_receita})")
        else:
            resultado.append(f"⚠️ {produto}: insuficiente ({qtd_disponivel}/{qtd_necessaria} {unidade_receita})")
            disponivel = False

    return disponivel, resultado

# ============================================================
# PRODUTOS FALTANTES NO ESTOQUE (COM BASE NAS RECEITAS)
# ============================================================

def produtos_faltantes_no_estoque_por_receitas(
    receitas_path="data/receitas.xlsx",
    estoque_path=ESTOQUE_PATH,
    sheet_name="Sheet1"
):
    """
    Retorna produtos citados nas receitas que não existem no estoque.
    (Substitui a função antiga que dependia do dim_produtos.)
    """
    receitas = load_receitas(receitas_path)
    df_estoque = carregar_estoque(estoque_path, sheet_name=sheet_name)

    produtos_estoque = set(df_estoque["produto"].tolist())

    faltantes = set()
    for prato, ingredientes in receitas.items():
        for ing in ingredientes:
            if ing["produto"] not in produtos_estoque:
                faltantes.add(ing["produto"])

    return sorted(faltantes)

# ============================================================
# CUSTO DA RECEITA (SEM Kg/L)
# ============================================================

def preco_receita(
    prato: str,
    receitas_path="data/receitas.xlsx",
    estoque_path=ESTOQUE_PATH,
    sheet_path="Sheet1"
):
    """
    Calcula o custo total de uma receita com base nas quantidades e preços do estoque.

    Regras novas (somente g/ml/un):
    - 'preco' no estoque deve estar no MESMO referencial da unidade (preço por g, por ml, ou por unidade).
    - Se a unidade da receita divergir da unidade do estoque para o produto -> marca conflito e custo 0 daquele item.
    """
    prato = _norm(prato)
    receitas = load_receitas(receitas_path)
    df_estoque = carregar_estoque(estoque_path, sheet_name=sheet_path)

    if prato not in receitas:
        raise ValueError(f"Receita '{prato}' não encontrada.")

    if "preco" not in df_estoque.columns:
        raise ValueError("A coluna 'preco' não foi encontrada em estoque_inicial.xlsx.")

    ingredientes = receitas[prato]
    resultados = []
    preco_total = 0.0

    for item in ingredientes:
        produto = item["produto"]
        qtd_necessaria = int(item["quantidade"])
        estoque_item = df_estoque[df_estoque["produto"] == produto]
        unidade_embalagem = estoque_item['quantidade_embalagem'].values[0]

        if estoque_item.empty:
            resultados.append({
                "Produto": produto,
                "Quantidade Necessária": qtd_necessaria,
                "Preço Base (R$)": 0.0,
                "Custo da Porção (R$)": 0.0,
                "Status": "❌ Produto não encontrado no estoque"
            })
            continue

        unidade_estoque = _norm_unit(estoque_item["unidade"].values[0])
        preco_base = float(estoque_item["preco"].values[0])
        preco_base_label = f'R$ {int(preco_base)}/{int(unidade_embalagem)}{unidade_estoque}'

        # validação de unidade (somente g/ml/un)
        if unidade_estoque not in ALLOWED_UNITS:
            resultados.append({
                "Produto": produto,
                "Quantidade Necessária": qtd_necessaria,
                "Preço Base (R$)": preco_base_label,
                "Custo da Porção (R$)": 0.0,
                "Status": f"❌ Unidade inválida na receita (permitidas: {sorted(ALLOWED_UNITS)})"
            })
            continue

        if unidade_estoque not in ALLOWED_UNITS:
            resultados.append({
                "Produto": produto,
                "Quantidade Necessária": qtd_necessaria,
                "Preço Base (R$)": preco_base_label,
                "Custo da Porção (R$)": 0.0,
                "Status": f"❌ Unidade inválida no estoque (permitidas: {sorted(ALLOWED_UNITS)})"
            })
            continue

        custo_unitario = preco_base/unidade_embalagem

        custo = custo_unitario * qtd_necessaria

        preco_total += custo

        resultados.append({
            "Produto": produto,
            "Quantidade Necessária": qtd_necessaria,
            "Preço Base (R$)": preco_base_label,
            "Custo da Porção (R$)": custo,
            "Status": "✅ Ok"
        })

    df_resultado = pd.DataFrame(resultados)
    df_resultado["Custo da Porção (R$)"] = df_resultado["Custo da Porção (R$)"].round(2)

    return df_resultado, round(preco_total, 2)

# ============================================================
# VISUAIS PERSONALIZADOS
# ============================================================

def card_metric(titulo, valor, prefixo_medida='R$'):
    """
    Objetivo: cria um card para uma metrica isolada usando html e não st padrão

    Parâmetros: 
        titulo: Texto que ficará escrito sobre o valor
        valor: Valor informado com destaque no card
        prefixo_medida: Informa o que será prefixo do card. R$ é o padrão
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 12px;
        border-radius: 14px;
        text-align: center;
    ">
        <div style="font-size:14px; opacity:0.7;">{titulo}</div>
        <div style="font-size:25px; font-weight:400;">{prefixo_medida} {valor}</div>
    </div>
    """, unsafe_allow_html=True)

def card_metric_big(titulo, valor, prefixo_medida="R$"):
    """
    Cria um card grande centralizado (HTML) para métricas.
    - Centraliza vertical/horizontal
    - Não quebra linha entre 'R$' e o valor
    """

    html = dedent(f"""
    <div style="
        width: 280px;
        height: 430px;
        background: linear-gradient(135deg, #14532d, #052e16);
        border-radius: 14px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 24px;
        box-sizing: border-box;
    ">
        <div style="font-size: 14px; opacity: 0.7; margin-bottom: 12px; max-width: 220px; word-wrap: break-word;">{titulo}</div>
        <div style="font-size: 34px; font-weight: 800; line-height: 1.1; white-space: nowrap;">{prefixo_medida} {valor}</div>
    </div>
    """).strip()

    st.markdown(html, unsafe_allow_html=True)