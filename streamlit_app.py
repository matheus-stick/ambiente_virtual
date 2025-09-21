import streamlit as st
from pages.entradas_saidas import page_entradas

st.set_page_config(page_title="Gestão de Estoque", page_icon="📦")
st.title("Gestão de Estoque")

menu = st.sidebar.radio(
    "Navegação",
    ["Entradas/Saídas"],  # adicione mais páginas aqui
)

if menu == "Entradas/Saídas":
    # importa e roda sua página
    page_entradas()