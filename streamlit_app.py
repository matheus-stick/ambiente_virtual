import streamlit as st
from app_pages.consulta_receitas import pagina_consulta_receitas as page_consultas
from app_pages.receitas_cadastro import pagina_cadastro_receitas as page_saidas
from app_pages.ajuste_estoque import pagina_ajuste_estoque as page_estoque
from app_pages.precificacao import pagina_precificacao as page_precificacao
from functions.styles import set_sidebar_style

# ---------------- STREAMLIT ----------------


def main():
    st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide", initial_sidebar_state="expanded")

    set_sidebar_style()

    st.sidebar.markdown(
        '<div class="custom-title">SoulFit</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Navegação")

    pages = [
        ("📦 Alteração de Estoque", page_estoque),
        ("📋 Consulta de Receitas", page_consultas),
        ("📝 Cadastro de Receitas", page_saidas),
        ("💲 Precificação", page_precificacao),
    ]

    if "active_page" not in st.session_state:
        st.session_state.active_page = pages[0][0]

    selected = st.sidebar.radio("", [p[0] for p in pages], index=[p[0] for p in pages].index(st.session_state.active_page), key="page_radio")
    st.session_state.active_page = selected

    # Render selected page
    for label, func in pages:
        if label == selected:
            func()
            break



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
        unsafe_allow_html=True,
    )
