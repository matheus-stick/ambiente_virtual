import streamlit as st
import pandas as pd
import altair as alt
from functions.db_utils import (
    verificar_disponibilidade,
    load_receitas,
    preco_receita,
    carregar_estoque,
    salvar_estoque,
    card_metric,
    card_metric_big
)

# ---------------- STREAMLIT ----------------

def pagina_consulta_receitas():
    st.title("🍽️ Consulta e Precificação de Receitas")

    st.info("Verifique a viabilidade de produção, custos dos ingredientes e calcule o valor final estimado do prato.")

    # ---------------- VIABILIDADE DE PRODUÇÃO ----------------
    st.header("🧑‍🍳 Viabilidade de Produção com o Estoque Atual")

    # Carregar receitas
    receitas = load_receitas("data/receitas.xlsx")
    if not receitas:
        st.warning("⚠️ Nenhuma receita cadastrada até o momento. Cadastre uma nova receita antes de consultar.")
        return

    pratos = list(receitas.keys())
    prato_escolhido = st.selectbox("Selecione o prato:", pratos)

    # Verificar disponibilidade
    disponivel, resultado = verificar_disponibilidade(prato_escolhido)

    st.subheader(f"Verificação de estoque para '{prato_escolhido.title()}':")
    for r in resultado:
        st.write(r)

    if disponivel:
        st.success("✅ É possível produzir esse prato com o estoque atual!")
        
        # ---------------- BOTÃO DE BAIXA NO ESTOQUE ----------------
        if st.button("📦 Dar baixa no estoque"):
            try:
                # Carregar estoque e receita
                df_estoque = carregar_estoque("data/estoque_inicial.xlsx")
                receitas = load_receitas("data/receitas.xlsx")
                ingredientes = receitas[prato_escolhido]

                # Atualizar estoque
                for item in ingredientes:
                    produto = str(item["produto"]).strip().lower()
                    qtd_necessaria = float(item["quantidade"])

                    if produto in df_estoque["produto"].values:
                        idx = df_estoque.index[df_estoque["produto"] == produto][0]
                        df_estoque.at[idx, "quantidade_disponivel"] = max(
                            0, df_estoque.at[idx, "quantidade_disponivel"] - qtd_necessaria
                        )

                # Salvar estoque atualizado
                salvar_estoque(df_estoque)
                st.success(f"✅ Baixa no estoque realizada com sucesso para '{prato_escolhido.title()}'.")
                st.experimental_rerun()  # Recarrega a página para refletir o novo estoque
            except Exception as e:
                st.error(f"❌ Erro ao atualizar o estoque: {e}")
    else:
        st.error("❌ Estoque insuficiente para produzir esse prato.")