import streamlit as st
from app_pages.consulta_receitas import pagina_consulta_receitas as page_consultas
from app_pages.receitas_cadastro import pagina_cadastro_receitas as page_saidas
from app_pages.ajuste_estoque import pagina_ajuste_estoque as page_estoque
from app_pages.precificacao import pagina_precificacao as page_precificacao

# ---------------- STREAMLIT ----------------
def main():
    st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

    st.sidebar.image("images/logo_soulfit_fundo_branco.jpeg", width=150)

    st.sidebar.title("Navegação")
    pagina = st.sidebar.radio("Ir para:", ("Consulta de Receitas", "Cadastro de Receitas","Alteração de Estoque","Precificação"))

    if pagina == "Consulta de Receitas":
        page_consultas()
    elif pagina == "Cadastro de Receitas":
        page_saidas()
    elif pagina == "Alteração de Estoque":
        page_estoque()
    elif pagina == 'Precificação':
        page_precificacao()

if __name__ == "__main__":
    main()

    st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        background-color: transparent;
        color: #808080;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        © 2025 Nexus Tech - Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True
    )