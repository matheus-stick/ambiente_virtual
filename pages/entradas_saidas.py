import streamlit as st
import pandas as pd
from unidecode import unidecode
from functions.db_utils import load_dim_produtos

#LEITURA DO ARQUIVO DE DIMENSAO DO PRODUTO

dim_produto = load_dim_produtos()

## DEFININDO AS VARIÁVEIS QUE SERÃO USADAS NOS CAMPOS DE SELEÇÃO

tipo_produto = dim_produto['tipo'].unique()

descricao_produto = dim_produto['descricao'].unique()

## CRIANDO CAMPOS DE SELECAO

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

# =========================
# UI
# =========================
st.subheader("Entradas / Saídas — Seleção de Produto")

# 1) Seleciona tipo (filtro primário)
tipo_escolhido = st.selectbox("Selecione o tipo do produto", tipo_produto, key="tipo_produto")

# Filtra DF pelo tipo selecionado
df_tipo = dim_produto.loc[dim_produto["tipo"] == tipo_escolhido].copy()

# 2) Campo de busca (autocomplete)
st.write("### 🔎 Buscar produto (por descrição)")
col1, col2 = st.columns([2, 1])  # <-- sem vertical_alignment (compatível com 1.34)

with col1:
    query_desc = st.text_input(
        "Nome / parte do nome",
        placeholder="Digite parte da descrição… (ex.: arroz, feijao, vinho)",
        help="A busca ignora acentos e maiúsculas/minúsculas.",
        key="query_produto",
    )

sugestoes_desc = filtra_produtos(df_tipo, query_desc, top_n=10) if not df_tipo.empty else []

with col2:
    st.caption("Sugestões")
    descricao_produto_sel = st.selectbox(
        "Resultados",
        options=(sugestoes_desc if sugestoes_desc else ["— sem resultados —"]),
        index=0,
        label_visibility="collapsed",
        key="descricao_produto",
    )

# 3) Seleciona unidade de medida conforme produto escolhido
unidade_options = []
if descricao_produto_sel and descricao_produto_sel != "— sem resultados —":
    unidade_options = (
        df_tipo.loc[df_tipo["descricao"] == descricao_produto_sel, "unidade_de_medida"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

if unidade_options:
    unidade_sel = st.selectbox("Unidade de medida", unidade_options, key="unidade_de_medida")
else:
    st.info("Selecione um produto para carregar a unidade de medida.")

# 4) (Opcional) Exibição do contexto selecionado
if descricao_produto_sel and descricao_produto_sel != "— sem resultados —":
    st.success(
        f"Tipo: **{tipo_escolhido}** | Produto: **{descricao_produto_sel}**"
        + (f" | Unidade: **{unidade_sel}**" if unidade_options else "")
    )