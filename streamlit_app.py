import streamlit as st
from app_pages.receitas import pagina_consulta_receitas as page_consultas
from app_pages.receitas_cadastro import pagina_cadastro_receitas as page_saidas

# ---------------- STREAMLIT ----------------
def main():
    st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

    st.sidebar.title("Navegação")
    pagina = st.sidebar.radio("Ir para:", ("Consulta de Receitas", "Cadastro de Receitas"))

    if pagina == "Consulta de Receitas":
        page_consultas()
    elif pagina == "Cadastro de Receitas":
        page_saidas()

if __name__ == "__main__":
    main()