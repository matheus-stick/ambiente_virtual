import streamlit as st
import pandas as pd
import time
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
            preco_atual = df_estoque.loc[df_estoque["produto"] == produto_selecionado, "preco"].values[0]

            col_qtd, col_preco = st.columns(2)

            with col_qtd:

                st.write(f"📦 Quantidade atual de **{produto_selecionado}**: {qtd_atual} {unidade}")

                nova_qtd = st.number_input(f"Informe a nova quantidade ({unidade}):", min_value=0.0, step=1.0, key="nova_qtd")

                if st.button("Salvar alteração de nova quantidade", key="btn_salvar_existente_quantidade"):
                    df_estoque.loc[df_estoque["produto"] == produto_selecionado, "quantidade_disponivel"] = nova_qtd
                    salvar_estoque(df_estoque)
                    progress_text = "Alterando quantidade..."
                    my_bar = st.progress(0, text=progress_text)

                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=progress_text)
                    time.sleep(1)
                    my_bar.empty()
                    st.success(f"✅ Quantidade de '{produto_selecionado}' atualizada com sucesso!")
                    time.sleep(2)

                    st.rerun()  # 🔁 recarrega a página automaticamente
            
            with col_preco:

                st.write(f"💵 Preço atual de **{produto_selecionado}**: R$ {preco_atual}")

                novo_preco = st.number_input("Informe o novo preço (R$):", min_value=0.0, step=0.01, format="%.2f", key="novo_preco")

                if st.button("Salvar alteração de novo preço", key="btn_salvar_existente_preco"):
                    df_estoque.loc[df_estoque["produto"] == produto_selecionado, "preco"] = novo_preco
                    salvar_estoque(df_estoque)
                    progress_text = "Alterando preço..."
                    my_bar = st.progress(0, text=progress_text)

                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=progress_text)
                    time.sleep(1)
                    my_bar.empty()
                    st.success(f"✅ Preço de '{produto_selecionado}' atualizado com sucesso!")
                    time.sleep(2)

                    st.rerun()  # 🔁 recarrega a página automaticamente

    # ---------------- CADASTRO DE NOVO PRODUTO ----------------
    st.markdown("---")
    st.subheader("🆕 Cadastrar Novo Produto no Estoque")

    df_faltantes = produtos_faltantes_no_estoque()

    if df_faltantes.empty:
        st.success("✅ Todos os produtos da dimensão já estão cadastrados no estoque.")
        return

    novo_produto = st.selectbox("Selecione um produto para cadastrar:", df_faltantes["descricao"].tolist())

    if novo_produto:

        col_qtd, col_preco = st.columns(2)

        with col_qtd:

            unidade = df_faltantes.loc[df_faltantes["descricao"] == novo_produto, "unidade_de_medida"].values[0]
            quantidade = st.number_input(f"Informe a quantidade inicial ({unidade}):", min_value=0.0, step=1.0, key="nova_quantidade")

        with col_preco:  
            # Padronizando como deve ser informado o preco do produto
            if unidade == 'g':
                texto_unidade_preco = 'Informe o preço (R$) para cada quilograma (Kg)'
            elif unidade == 'mL':
                texto_unidade_preco = 'Informe o preço (R$) para cada litro (L)'
            elif unidade == 'Kg':
                texto_unidade_preco = 'Informe o preço (R$) para cada quilograma (Kg)'
            elif unidade == 'L':
                texto_unidade_preco = 'Informe o preço (R$) para cada litro (L)'
            elif unidade == 'Un':
                texto_unidade_preco = 'Informe o preço (R$) para cada quilograma (Kg)'
            else:
                texto_unidade_preco = f'informe em {unidade}'

            preco = st.number_input(f"{texto_unidade_preco}:", min_value=0.0, step=1.0, key="valor_produto",format="%.2f")
        
        if st.button("Cadastrar Produto", key="btn_cadastrar_novo"):
            if preco <= 0:
                st.error("⚠️ O preço deve ser maior que zero para cadastrar um novo produto.")
                return
            else:
                novo_registro = pd.DataFrame([{
                "produto": novo_produto,
                "quantidade_disponivel": quantidade,
                "unidade": unidade,
                "preco": preco
            }])
                df_estoque = pd.concat([df_estoque, novo_registro], ignore_index=True)
                salvar_estoque(df_estoque)
                progress_text = "Cadastrando novo produto..."
                my_bar = st.progress(0, text=progress_text)

                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                time.sleep(1)
                my_bar.empty()
                st.success(f"✅ Produto '{novo_produto}' cadastrado com sucesso no estoque!")
                time.sleep(2)
                st.rerun()  # 🔁 recarrega automaticamente após cadastro
    