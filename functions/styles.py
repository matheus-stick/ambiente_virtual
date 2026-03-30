import streamlit as st


def set_sidebar_style():
    """Apply a light-mode sidebar style similar to the provided mockup."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
        /* Global app background */
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main {
            background:
                radial-gradient(circle at top left, rgba(236, 84, 140, 0.05), transparent 30%),
                radial-gradient(circle at right center, rgba(227, 125, 156, 0.07), transparent 28%),
                radial-gradient(circle at bottom left, rgba(238, 199, 167, 0.08), transparent 24%),
                linear-gradient(135deg, #FFFDFC 0%, #FDF9FB 45%, #FAF6F8 100%);
            background-attachment: fixed;
        }

        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stAppViewContainer"] > .main .block-container {
            background: transparent;
        }

        /* Sidebar container */
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #fcf7f9 0%, #f8f1f5 100%);
            padding-top: 22px;
            padding-bottom: 40px; /* reduced since no footer */
            position: relative;
            border-right: 1px solid rgba(232, 40, 89, 0.08);
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
            transition: background 0.2s ease, border-color 0.2s ease;
            line-height: 1.3;
            border: 1px solid transparent;
        }

        .stRadio label[data-baseweb="radio"]:has(input:checked) {
            background: rgba(232, 40, 89, 0.09);
            border-color: rgba(232, 40, 89, 0.12);
        }

        .stRadio label[data-baseweb="radio"]:hover {
            background: rgba(232, 40, 89, 0.05);
        }

        .stRadio label[data-baseweb="radio"] input {
            margin: 0;
        }

        /* Form controls */
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > div,
        div[data-baseweb="select"] > div,
        .stNumberInput > div > div,
        .stTextInput > div > div {
            background: #fbfcfd;
            border: 1px solid #e9dde4;
            box-shadow: none;
            transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
        }

        div[data-baseweb="input"] > div:hover,
        div[data-baseweb="base-input"] > div:hover,
        div[data-baseweb="select"] > div:hover,
        .stNumberInput > div > div:hover,
        .stTextInput > div > div:hover {
            background: #ffffff;
            border-color: #e4d3dc;
        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="base-input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        .stNumberInput > div > div:focus-within,
        .stTextInput > div > div:focus-within {
            background: #ffffff;
            border-color: rgba(232, 40, 89, 0.28);
            box-shadow: 0 0 0 3px rgba(232, 40, 89, 0.12);
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input,
        .stNumberInput input,
        .stTextInput input {
            color: #333846;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
