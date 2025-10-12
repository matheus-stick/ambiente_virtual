import streamlit as st
from functions.db_utils import verificar_disponibilidade, load_receitas

# ---------------- STREAMLIT ----------------

def pagina_consulta_receitas():
    st.title("🍽️ Consulta de Receitas")

    # Carregar receitas do Excel
    receitas = load_receitas("data/receitas.xlsx")

    # Verificar se há receitas cadastradas
    if not receitas:
        st.warning("⚠️ Nenhuma receita cadastrada até o momento. Cadastre uma nova receita antes de consultar.")
        return

    # Lista de pratos disponíveis
    pratos = list(receitas.keys())

    # Seleção do prato
    prato_escolhido = st.selectbox("Selecione o prato:", pratos)

    # Botão de verificação
    if st.button("Verificar disponibilidade"):
        disponivel, resultado = verificar_disponibilidade(prato_escolhido)

        st.subheader(f"Verificação de estoque para '{prato_escolhido.title()}':")
        for r in resultado:
            st.write(r)

        if disponivel:
            st.success("✅ É possível produzir esse prato com o estoque atual!")
        else:
            st.error("❌ Estoque insuficiente para produzir esse prato.")