import streamlit as st
from functions.db_utils import verificar_disponibilidade, receitas

# Seleção do prato
prato_escolhido = st.selectbox("Selecione o prato:", list(receitas.keys()))

if st.button("Verificar disponibilidade"):
    disponivel, resultado = verificar_disponibilidade(prato_escolhido)

    st.subheader(f"Verificação de estoque para {prato_escolhido}:")
    for r in resultado:
        st.write(r)

    if disponivel:
        st.success("✅ É possível produzir esse prato com o estoque atual!")
    else:
        st.error("❌ Estoque insuficiente para produzir esse prato.")