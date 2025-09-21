import streamlit as st
import pandas as pd
from unidecode import unidecode
from functions.db_utils import load_dim_produtos, _norm, filtra_produtos

#LEITURA DO ARQUIVO DE DIMENSAO DO PRODUTO

dim_produto = load_dim_produtos()

## DEFININDO AS VARIÁVEIS QUE SERÃO USADAS NOS CAMPOS DE SELEÇÃO

tipo_produto = dim_produto['tipo'].unique()

descricao_produto = dim_produto['descricao'].unique()

# =========================
# UX
# =========================

def page_entradas():
    """Função principal da página Entradas/Saídas."""
    
    st.subheader("Entradas / Saídas — Seleção de Produto")

    # 1) Seleciona tipo (filtro primário)
    tipo_escolhido = st.selectbox("Selecione o tipo do produto", tipo_produto, key="tipo_produto")

    # Filtra DF pelo tipo selecionado
    df_tipo = dim_produto.loc[dim_produto["tipo"] == tipo_escolhido].copy()

    # 2) Campo de busca (autocomplete)
    st.write("### 🔎 Buscar produto (por descrição)")

    query_desc = st.text_input(
        "Nome do produto",
        placeholder="Digite parte da descrição… (ex.: arroz, feijao, vinho)",
        help="A busca ignora acentos e maiúsculas/minúsculas.",
        key="query_produto",
    )

    col1, col2 = st.columns([2, 1])

    sugestoes_desc = filtra_produtos(df_tipo, query_desc, top_n=25) if not df_tipo.empty else []

    with col1:
        descricao_produto_sel = st.selectbox(
            "Sugestões",
            options=(sugestoes_desc if sugestoes_desc else ["— sem resultados —"]),
            index=0,
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

    with col2:
        if unidade_options:
            unidade_sel = st.selectbox(label="Unidade de medida",options= unidade_options, key="unidade_de_medida")
        else:
            st.info("Selecione um produto para carregar a unidade de medida.")

    # 4) (Opcional) Exibição do contexto selecionado
    if descricao_produto_sel and descricao_produto_sel != "— sem resultados —":
        st.success(
            f"Tipo: **{tipo_escolhido}** | Produto: **{descricao_produto_sel}**"
            + (f" | Unidade: **{unidade_sel}**" if unidade_options else "")
        )