import streamlit as st
from app_pages.consulta_receitas import pagina_consulta_receitas as page_consultas
from app_pages.receitas_cadastro import pagina_cadastro_receitas as page_saidas
from app_pages.ajuste_estoque import pagina_ajuste_estoque as page_estoque
from app_pages.precificacao import pagina_precificacao as page_precificacao

# ---------------- STREAMLIT ----------------

def _set_sidebar_style():
    """Apply a light-mode sidebar style similar to the provided mockup."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
        /* Sidebar container */
        [data-testid="stSidebar"] > div:first-child {
            background: #f7f7f9;
            padding-top: 22px;
            padding-bottom: 40px; /* reduced since no footer */
            position: relative;
        }

        /* Sidebar title and logo */
        [data-testid="stSidebar"] .css-1v0mbdj.e1fqkh3o3 {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        /* Center logo and title */
        [data-testid="stSidebar"] .custom-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            font-style: italic;
            color: #e82859;
            margin-bottom: 20px;
            font-family: 'Montserrat', sans-serif;
        }

        [data-testid="stSidebar"] h3 {
            text-align: center;
        }

        /* Radio buttons (navigation items) */
        .stRadio > div {
            gap: 0.25rem;
        }

        .stRadio label[data-baseweb="radio"] {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.45rem 0.9rem;
            border-radius: 12px;
            transition: background 0.2s ease;
            line-height: 1.3;
        }

        .stRadio label[data-baseweb="radio"]:has(input:checked) {
            background: rgba(34, 139, 230, 0.1);
        }

        .stRadio label[data-baseweb="radio"]:hover {
            background: rgba(34, 139, 230, 0.08);
        }

        .stRadio label[data-baseweb="radio"] input {
            margin: 0;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide", initial_sidebar_state="expanded")

    _set_sidebar_style()

    st.sidebar.markdown(
        '<div class="custom-title">SoulFit</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Navegação")

    pages = [
        ("📋 Consulta de Receitas", page_consultas),
        ("📝 Cadastro de Receitas", page_saidas),
        ("💲 Precificação", page_precificacao),
        ("📦 Alteração de Estoque", page_estoque),
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
