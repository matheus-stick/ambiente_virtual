import streamlit as st
import pandas as pd
import os
from unidecode import unidecode  # <-- importa para remover acentos

# Caminhos dos arquivos
DIM_PRODUTOS_PATH = "data/dim_produtos.xlsx"
RECEITAS_PATH = "data/receitas.xlsx"

# Carregar produtos disponíveis
df_produtos = pd.read_excel(DIM_PRODUTOS_PATH)

# Removendo espaços no inicio/fim das descrições
df_produtos['Descrição'] = df_produtos['Descrição'].str.strip()

# Removendo acentos e padronizando para letras minúsculas (opcional)
df_produtos['Descrição'] = df_produtos['Descrição'].apply(lambda x: unidecode(str(x)))

# Filtrando apenas Insumos
df_produtos = df_produtos[df_produtos['Tipo'] == 'Insumo']

# Ordenando dataset por ordem alfabética
df_produtos = df_produtos.sort_values(by='Descrição', ascending=True)

# Garantir que arquivo de receitas exista
if not os.path.exists(RECEITAS_PATH):
    df_receitas = pd.DataFrame(columns=["prato", "produto", "quantidade", "unidade"])
    df_receitas.to_excel(RECEITAS_PATH, index=False)

# Função para salvar a receita
def salvar_receita(prato, ingredientes):
    df_receitas = pd.read_excel(RECEITAS_PATH)

    novos_registros = []
    for item in ingredientes:
        novos_registros.append({
            "prato": prato,
            "produto": item["produto"],
            "quantidade": item["quantidade"],
            "unidade": item["unidade"]
        })

    df_receitas = pd.concat([df_receitas, pd.DataFrame(novos_registros)], ignore_index=True)
    df_receitas.to_excel(RECEITAS_PATH, index=False)

# ---------------- STREAMLIT ----------------
def pagina_cadastro_receitas():
    
    st.title("🍽️ Cadastro de Receitas")

    # Nome do prato
    prato = st.text_input("Nome do prato:")

    # Seleção da quantidade de ingredientes
    num_ingredientes = st.number_input("Quantos ingredientes esse prato terá?", min_value=1, max_value=20, step=1)

    ingredientes = []
    for i in range(num_ingredientes):
        st.markdown(f"### Ingrediente {i+1}")

        produto = st.selectbox(
            f"Selecione o produto {i+1}:",
            df_produtos["Descrição"].tolist(),
            key=f"produto_{i}"
        )

        unidade = df_produtos.loc[df_produtos["Descrição"] == produto, "Unidade de medida"].values[0]

        if unidade == 'g':
            texto_unidade = 'informe em gramas (g)'
        elif unidade == 'mL':
            texto_unidade = 'informe em mililitros (ml)'
        elif unidade == 'Kg':
            texto_unidade = 'informe em gramas (g)'
        elif unidade == 'L':
            texto_unidade = 'informe em mililitros (ml)'
        elif unidade == 'Un':
            texto_unidade = 'informe em gramas (g)'
        else:
            texto_unidade = f'informe em {unidade}'

        quantidade = st.number_input(f"{texto_unidade}:", min_value=0, step=1, key=f"quantidade_{i}")

        ingredientes.append({
            "produto": produto,
            "quantidade": quantidade,
            "unidade": unidade
        })

    # Botão para salvar
    if st.button("Salvar Receita"):
        if prato.strip() == "":
            st.error("⚠️ Informe um nome para o prato antes de salvar.")
        else:
            salvar_receita(prato, ingredientes)
            st.success(f"✅ Receita '{prato}' salva com sucesso!")