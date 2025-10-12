import streamlit as st
from app_pages.receitas import pagina_consulta_receitas as page_consultas
from app_pages.receitas_cadastro import pagina_cadastro_receitas as page_saidas
from app_pages.ajuste_estoque import pagina_ajuste_estoque as page_estoque

# ---------------- STREAMLIT ----------------
def main():
    st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

    st.sidebar.title("Navegação")
    pagina = st.sidebar.radio("Ir para:", ("Consulta de Receitas", "Cadastro de Receitas","Alteração de Estoque"))

    if pagina == "Consulta de Receitas":
        page_consultas()
    elif pagina == "Cadastro de Receitas":
        page_saidas()
    elif pagina == "Alteração de Estoque":
        page_estoque()

if __name__ == "__main__":
    main()