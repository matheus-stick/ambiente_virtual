import streamlit as st
import pandas as pd
import time
from unidecode import unidecode

from functions.db_utils import (
    carregar_estoque,
    salvar_estoque
)

# ---------------- HELPERS LOCAIS ----------------

def _norm_local(s: str) -> str:
    """Normaliza igual ao db_utils: minúsculo, sem acento, sem espaços extras."""
    return unidecode((str(s) or "").strip().lower())

ALLOWED_UNITS = ["g", "ml", "un"]

# ---------------- STREAMLIT ----------------

def pagina_ajuste_estoque():
    st.title("📦 Ajuste e Cadastro de Estoque")

    st.info(
        "Aqui você pode visualizar o estoque, ajustar quantidades ou cadastrar novos produtos. "
        "As alterações são salvas automaticamente."
    )

    # Carregar estoque atual
    df_estoque = carregar_estoque()

    if df_estoque.empty:
        st.warning("Nenhum dado de estoque encontrado. Você pode começar cadastrando novos produtos abaixo.")
    else:
        # Exibir tabela com rolagem
        st.subheader("📋 Estoque Atual")
        st.dataframe(df_estoque, use_container_width=True, height=400)

                # ===========================
        # 🔎 BUSCA DE PRODUTO
        # ===========================
        st.markdown("---")
        st.subheader("🔎 Buscar Produto no Estoque")

        # garante que a key exista antes do widget (evita inconsistências)
        if "busca_produto" not in st.session_state:
            st.session_state["busca_produto"] = ""

        def limpar_pesquisa():
            # ✅ alterar dentro do callback é permitido
            st.session_state["busca_produto"] = ""

        col_busca, col_match = st.columns([1, 1.2])  # tabela um pouco mais larga

        # base de produtos
        produtos_base = sorted(df_estoque["produto"].dropna().unique().tolist())

        with col_busca:
            busca_raw = st.text_input(
                "Digite para buscar (ex: arroz):",
                key="busca_produto"
            )
            busca = _norm_local(busca_raw)

            # feedback de existência (quando usuário digitou algo)
            if busca:
                existe_exato = busca in set(produtos_base)
                existe_parcial = any(busca in p for p in produtos_base)

                if existe_exato:
                    st.success(f"✅ Produto encontrado no estoque: **{busca}**")
                elif existe_parcial:
                    st.info("ℹ️ Encontrei produtos parecidos no estoque. Veja a tabela ao lado e o seletor abaixo.")
                else:
                    st.warning("⚠️ Nenhum produto encontrado com esse termo.")

            # ✅ botão sempre visível; desabilita quando não há busca
            # OBS: para ficar vermelho somente ele, use type="primary"
            st.button(
                "Limpar pesquisa",
                key="btn_limpar_pesquisa",
                on_click=limpar_pesquisa,
                disabled=(not busca),
                type="primary"
            )

        # filtra produtos para o selectbox do ajuste (mantém exatamente sua lógica)
        produtos_filtrados = (
            [p for p in produtos_base if busca in p] if busca else produtos_base
        )

        with col_match:
            st.markdown("**Produtos semelhantes**")

            # ✅ quando não tem busca, não mostra dataframe => tela limpa
            if not busca:
                st.caption("Digite um termo de busca para listar os semelhantes.")
            else:
                df_semelhantes = df_estoque[df_estoque["produto"].str.contains(busca, na=False)].copy()

                if df_semelhantes.empty:
                    st.caption("Nenhum semelhante encontrado.")
                else:
                    cols = ["produto", "unidade", "quantidade_disponivel"]
                    if "preco" in df_semelhantes.columns:
                        cols.append("preco")
                    if "quantidade_embalagem" in df_semelhantes.columns:
                        cols.append("quantidade_embalagem")

                    df_semelhantes = df_semelhantes[cols].sort_values("produto")
                    st.dataframe(df_semelhantes, use_container_width=True, height=260)


        # ===========================
        # ✏️ AJUSTE EM PRODUTOS EXISTENTES
        # ===========================
        st.markdown("---")
        st.subheader("✏️ Ajustar Produto Existente no Estoque")

        if not produtos_filtrados:
            st.warning("Nenhum produto para exibir com esse filtro. Limpe a busca para ver todos.")
        else:
            produto_selecionado = st.selectbox("Selecione o produto para ajuste:", produtos_filtrados)

            if produto_selecionado:
                unidade = df_estoque.loc[df_estoque["produto"] == produto_selecionado, "unidade"].values[0]
                qtd_atual = df_estoque.loc[df_estoque["produto"] == produto_selecionado, "quantidade_disponivel"].values[0]
                preco_atual = df_estoque.loc[df_estoque["produto"] == produto_selecionado, "preco"].values[0] if "preco" in df_estoque.columns else 0.0

                col_qtd, col_preco = st.columns(2)

                with col_qtd:
                    st.write(f"📦 Quantidade atual de **{produto_selecionado}**: {qtd_atual} {unidade}")
                    nova_qtd = st.number_input(
                        f"Informe a nova quantidade ({unidade}):",
                        min_value=0.0,
                        step=1.0,
                        key="nova_qtd"
                    )

                    if st.button("Salvar alteração de nova quantidade", key="btn_salvar_existente_quantidade"):
                        df_estoque.loc[df_estoque["produto"] == produto_selecionado, "quantidade_disponivel"] = nova_qtd
                        salvar_estoque(df_estoque)

                        progress_text = "Alterando quantidade..."
                        my_bar = st.progress(0, text=progress_text)
                        for percent_complete in range(100):
                            time.sleep(0.01)
                            my_bar.progress(percent_complete + 1, text=progress_text)
                        time.sleep(0.3)
                        my_bar.empty()

                        st.success(f"✅ Quantidade de '{produto_selecionado}' atualizada com sucesso!")
                        time.sleep(0.8)
                        st.rerun()

                with col_preco:
                    if "preco" not in df_estoque.columns:
                        st.warning("Coluna 'preco' não existe no estoque. Não é possível editar preço.")
                    else:
                        st.write(f"💵 Preço atual de **{produto_selecionado}**: R$ {preco_atual}")
                        novo_preco = st.number_input(
                            "Informe o novo preço (R$):",
                            min_value=0.0,
                            step=0.01,
                            format="%.2f",
                            key="novo_preco"
                        )

                        if st.button("Salvar alteração de novo preço", key="btn_salvar_existente_preco"):
                            df_estoque.loc[df_estoque["produto"] == produto_selecionado, "preco"] = novo_preco
                            salvar_estoque(df_estoque)

                            progress_text = "Alterando preço..."
                            my_bar = st.progress(0, text=progress_text)
                            for percent_complete in range(100):
                                time.sleep(0.01)
                                my_bar.progress(percent_complete + 1, text=progress_text)
                            time.sleep(0.3)
                            my_bar.empty()

                            st.success(f"✅ Preço de '{produto_selecionado}' atualizado com sucesso!")
                            time.sleep(0.8)
                            st.rerun()

    # ---------------- CADASTRO DE NOVO PRODUTO ----------------
    st.markdown("---")
    st.subheader("🆕 Cadastrar Novo Produto no Estoque")

    col_a, col_b = st.columns(2)

    with col_a:
        nome_produto_raw = st.text_input("Nome do produto (ex: farinha de trigo) (Clique ENTER para verificar a existência do produto no estoque.):", value="", key="cad_nome_produto")
        unidade = st.selectbox("Unidade:", ALLOWED_UNITS)

    with col_b:
        quantidade = st.number_input(
            "Quantidade inicial:",
            min_value=0.0,
            step=1.0,
            key="nova_quantidade"
        )
        preco = st.number_input(
            "Preço base (R$):",
            min_value=0.0,
            step=0.01,
            key="valor_produto",
            format="%.2f"
        )

    # 🔒 quantidade_embalagem agora é OBRIGATÓRIA
    if df_estoque.empty or "quantidade_embalagem" not in df_estoque.columns:
        st.error(
            "❌ A coluna 'quantidade_embalagem' não existe no estoque_inicial.xlsx.\n\n"
            "Para cadastrar novos produtos, essa coluna é obrigatória."
        )
        return

    quantidade_embalagem = st.number_input(
        "Quantidade por embalagem (obrigatório):",
        min_value=0.0,
        step=1.0,
        key="quantidade_embalagem"
    )

    # ✅ Checagem instantânea (antes do botão)
    nome_norm_preview = _norm_local(nome_produto_raw)
    if nome_norm_preview and not df_estoque.empty:
        if nome_norm_preview in set(df_estoque["produto"].tolist()):
            st.warning("⚠️ Esse produto já existe no estoque. Use a seção de ajuste para alterar.")
        else:
            st.info("ℹ️ Produto ainda não existe no estoque. Você pode cadastrar.")

    if st.button("Cadastrar Produto", key="btn_cadastrar_novo"):
        nome_produto = _norm_local(nome_produto_raw)

        if not nome_produto:
            st.error("⚠️ Informe o nome do produto para cadastrar.")
            return

        if unidade not in ALLOWED_UNITS:
            st.error(f"⚠️ Unidade inválida. Permitidas: {ALLOWED_UNITS}")
            return

        if preco <= 0:
            st.error("⚠️ O preço deve ser maior que zero para cadastrar um novo produto.")
            return

        if quantidade_embalagem <= 0:
            st.error("⚠️ A quantidade por embalagem deve ser maior que zero.")
            return

        # Recarrega estoque para evitar estado desatualizado
        df_estoque = carregar_estoque()

        if nome_produto in set(df_estoque["produto"].tolist()):
            st.warning(
                "⚠️ Esse produto já existe no estoque. "
                "Use a seção de ajuste para alterar quantidade ou preço."
            )
            return

        novo_registro = {
            "produto": nome_produto,
            "quantidade_disponivel": float(quantidade),
            "unidade": unidade,
            "preco": float(preco),
            "quantidade_embalagem": float(quantidade_embalagem),
        }

        df_novo = pd.DataFrame([novo_registro])
        df_estoque = pd.concat([df_estoque, df_novo], ignore_index=True)

        salvar_estoque(df_estoque)

        progress_text = "Cadastrando novo produto..."
        my_bar = st.progress(0, text=progress_text)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        time.sleep(0.3)
        my_bar.empty()

        st.success(f"✅ Produto '{nome_produto}' cadastrado com sucesso no estoque!")
        time.sleep(0.8)
        st.rerun()