import streamlit as st
import pandas as pd
from functions.db_utils import (
    carregar_estoque,
    salvar_estoque,
    produtos_faltantes_no_estoque
)

# ---------------- STREAMLIT ----------------

def pagina_ajuste_estoque():
    st.title("📦 Ajuste e Cadastro de Estoque")

    st.info("Aqui você pode visualizar o estoque, ajustar quantidades ou cadastrar novos produtos. As alterações são salvas automaticamente.")

    # Carregar estoque atual
    df_estoque = carregar_estoque()

    if df_estoque.empty:
        st.warning("Nenhum dado de estoque encontrado. Você pode começar cadastrando novos produtos abaixo.")
    else:
        # Exibir tabela com rolagem
        st.subheader("📋 Estoque Atual")
        st.dataframe(df_estoque, use_container_width=True, height=400)

        # Seção de ajuste de produto existente
        st.markdown("---")
        st.subheader("✏️ Ajustar Quantidade de Produto Existente")

        produtos = df_estoque["produto"].tolist()
        produto_selecionado = st.selectbox("Selecione o produto para ajuste:", produtos)

        if produto_selecionado:
            unidade = df_estoque.loc[df_estoque["produto"] == produto_selecionado, "unidade"].values[0]
            qtd_atual = df_estoque.loc[df_estoque["produto"] == produto_selecionado, "quantidade_disponivel"].values[0]

            st.write(f"📦 Quantidade atual de **{produto_selecionado}**: {qtd_atual} {unidade}")

            nova_qtd = st.number_input(f"Informe a nova quantidade ({unidade}):", min_value=0.0, step=1.0, key="nova_qtd")

            if st.button("Salvar Alteração", key="btn_salvar_existente"):
                df_estoque.loc[df_estoque["produto"] == produto_selecionado, "quantidade_disponivel"] = nova_qtd
                salvar_estoque(df_estoque)
                st.success(f"✅ Quantidade de '{produto_selecionado}' atualizada com sucesso!")
                st.experimental_rerun()  # 🔁 recarrega a página automaticamente

    # ---------------- CADASTRO DE NOVO PRODUTO ----------------
    st.markdown("---")
    st.subheader("🆕 Cadastrar Novo Produto no Estoque")

    df_faltantes = produtos_faltantes_no_estoque()

    if df_faltantes.empty:
        st.success("✅ Todos os produtos da dimensão já estão cadastrados no estoque.")
        return

    novo_produto = st.selectbox("Selecione um produto para cadastrar:", df_faltantes["descricao"].tolist())

    if novo_produto:
        unidade = df_faltantes.loc[df_faltantes["descricao"] == novo_produto, "unidade_de_medida"].values[0]
        quantidade = st.number_input(f"Informe a quantidade inicial ({unidade}):", min_value=0.0, step=1.0, key="nova_quantidade")

        if st.button("Cadastrar Produto", key="btn_cadastrar_novo"):
            novo_registro = pd.DataFrame([{
                "produto": novo_produto,
                "quantidade_disponivel": quantidade,
                "unidade": unidade
            }])
            df_estoque = pd.concat([df_estoque, novo_registro], ignore_index=True)
            salvar_estoque(df_estoque)
            st.success(f"✅ Produto '{novo_produto}' cadastrado com sucesso no estoque!")
            st.experimental_rerun()  # 🔁 recarrega automaticamente após cadastro