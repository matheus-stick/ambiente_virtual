import streamlit as st
from functions.db_utils import save_to_csv, load_csv

st.title('Página de Cadastros!')

col1, col2, col3 = st.columns(3)

with col1:
    # --- Cadastro de Categorias ---
    st.subheader("Cadastrar Nova Categoria")
    categoria = st.text_input("Nome da Categoria")
    if st.button("Cadastrar Categoria"):
        if categoria.strip():
            save_to_csv("categorias.csv", [categoria.strip().title()], ["categoria"])
            st.success("Categoria cadastrada com sucesso!")
        else:
            st.warning("Preencha o nome da categoria.")

with col2:
    # --- Cadastro de Marcas ---
    st.subheader("Cadastrar Nova Marca")
    marca = st.text_input("Nome da Marca")
    if st.button("Cadastrar Marca"):
        if marca.strip():
            save_to_csv("marcas.csv", [marca.strip().title()], ["marca"])
            st.success("Marca cadastrada com sucesso!")
        else:
            st.warning("Preencha o nome da marca.")

with col3:
    # --- Cadastro de Fornecedores ---
    st.subheader("Cadastrar Novo Fornecedor")
    fornecedor = st.text_input("Nome do Fornecedor")
    if st.button("Cadastrar Fornecedor"):
        if fornecedor.strip():
            save_to_csv("fornecedores.csv", [fornecedor.strip().title()], ["fornecedor"])
            st.success("Fornecedor cadastrado com sucesso!")
        else:
            st.warning("Preencha o nome do fornecedor.")

# --- Cadastro de Produtos ---
st.header("Cadastrar Novo Produto")
nome_produto = st.text_input("Nome do Produto")

categorias = load_csv("categorias.csv", ["categoria"])["categoria"].tolist()
marcas = load_csv("marcas.csv", ["marca"])["marca"].tolist()
fornecedores = load_csv("fornecedores.csv", ["fornecedor"])["fornecedor"].tolist()

categoria_produto = st.selectbox("Categoria", categorias)
marca_produto = st.selectbox("Marca", marcas)
fornecedor_produto = st.selectbox("Fornecedor", fornecedores)
unidade = st.text_input("Unidade de Medida (Ex.: kg, litro, unidade)")
validade = st.date_input("Validade do Produto")

if st.button("Cadastrar Produto"):
    if all([nome_produto.strip(), categoria_produto, marca_produto, fornecedor_produto, unidade.strip().title()]):
        data = [
            nome_produto.strip(),
            categoria_produto,
            marca_produto,
            fornecedor_produto,
            unidade.strip(),
            validade
        ]
        columns = ["produto", "categoria", "marca", "fornecedor", "unidade", "validade"]
        save_to_csv("produtos.csv", data, columns)
        st.success("Produto cadastrado com sucesso!")
    else:
        st.warning("Preencha todos os campos obrigatórios.")