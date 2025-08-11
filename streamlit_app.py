import streamlit as st

pages = {
    "Cadastro": [
        st.Page("pages\cadastro_itens.py.py", title="Cadastre o Item"),
        st.Page("pages\entradas_saidas_materia_prima.py", title="Entrada e saidas"),
    ],
    "Resources": [
        st.Page("learn.py", title="Learn about us"),
        st.Page("trial.py", title="Try it out"),
    ],
}

pg = st.navigation(pages)
pg.run()