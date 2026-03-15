import streamlit as st
import pandas as pd
import os
from unidecode import unidecode

from functions.db_utils import carregar_estoque

# Caminho do arquivo de receitas
RECEITAS_PATH = "data/receitas.xlsx"

ALLOWED_UNITS = ["g", "ml", "un"]

# ---------------- HELPERS ----------------

def _norm_local(s: str) -> str:
    """Normaliza: minúsculo, sem acento, sem espaços extras."""
    return unidecode((str(s) or "").strip().lower())

def _texto_unidade(unidade: str) -> str:
    u = _norm_local(unidade)
    if u == "g":
        return "Informe em gramas (g)"
    if u == "ml":
        return "Informe em mililitros (ml)"
    if u == "un":
        return "Informe em unidades (un)"
    return f"Informe em {unidade}"

# ---------------- SETUP ARQUIVO RECEITAS ----------------

if not os.path.exists(RECEITAS_PATH):
    df_receitas = pd.DataFrame(columns=["prato", "produto", "quantidade", "unidade"])
    df_receitas.to_excel(RECEITAS_PATH, index=False)

def salvar_receita(prato: str, ingredientes: list[dict]):
    """Append de registros no arquivo de receitas."""
    df_receitas = pd.read_excel(RECEITAS_PATH)

    prato_norm = _norm_local(prato)

    novos_registros = []
    for item in ingredientes:
        novos_registros.append({
            "prato": prato_norm,
            "produto": _norm_local(item["produto"]),
            "quantidade": float(item["quantidade"]),
            "unidade": _norm_local(item["unidade"])
        })

    df_receitas = pd.concat([df_receitas, pd.DataFrame(novos_registros)], ignore_index=True)
    df_receitas.to_excel(RECEITAS_PATH, index=False)

# ---------------- STREAMLIT ----------------
def pagina_cadastro_receitas():
    st.title("🍽️ Cadastro de Receitas")

    # Carregar produtos do estoque (base única)
    df_estoque = carregar_estoque()

    if df_estoque.empty:
        st.warning("⚠️ Estoque vazio. Cadastre produtos no estoque antes de criar receitas.")
        return

    for col in ["produto", "unidade"]:
        if col not in df_estoque.columns:
            st.error(f"❌ A coluna '{col}' não existe no estoque_inicial.xlsx. Não é possível cadastrar receitas.")
            return

    produtos_disponiveis = sorted(df_estoque["produto"].dropna().unique().tolist())

    # ===========================
    # TOPO: receita + qtd ingredientes
    # ===========================
    c_top1, c_top2 = st.columns([2, 1])

    with c_top1:
        prato = st.text_input("Nome da receita:", key="prato_nome")

    with c_top2:
        num_ingredientes = st.number_input(
            "Quantidade de ingredientes:",
            min_value=1,
            max_value=30,
            step=1,
            key="num_ingredientes"
        )

    st.markdown("---")

    ingredientes = []

    # helper para renderizar 1 ingrediente dentro de uma coluna
    def render_ingrediente(col, idx: int):
        with col:
            produto = st.selectbox(
                f"Ingrediente {idx+1}",
                produtos_disponiveis,
                key=f"produto_{idx}"
            )

            unidade = df_estoque.loc[df_estoque["produto"] == produto, "unidade"].values[0]
            unidade_norm = _norm_local(unidade)

            if unidade_norm not in ALLOWED_UNITS:
                st.error(f"❌ Unidade inválida no estoque: '{unidade}' (permitidas: {ALLOWED_UNITS})")
                st.stop()

            st.caption(f"Unidade: **{unidade_norm}**")

            quantidade = st.number_input(
                "Quantidade",
                min_value=0.0,
                step=1.0,
                key=f"quantidade_{idx}"
            )

        ingredientes.append({
            "produto": produto,
            "quantidade": float(quantidade),
            "unidade": unidade_norm
        })

    # ===========================
    # GRID: 3 ingredientes por linha
    # ===========================
    total = int(num_ingredientes)
    idx = 0

    while idx < total:
        cols = st.columns(3)  # ✅ mesma largura
        st.markdown("---")
        for j in range(3):
            if idx >= total:
                break
            render_ingrediente(cols[j], idx)
            idx += 1

    # Botão para salvar
    if st.button("Salvar Receita"):
        prato_val = st.session_state.get("prato_nome", "")

        if str(prato_val).strip() == "":
            st.error("⚠️ Informe um nome para o prato antes de salvar.")
            return

        # validação: não permitir ingredientes repetidos
        prods = [it["produto"] for it in ingredientes]
        repetidos = sorted({p for p in prods if prods.count(p) > 1})
        if repetidos:
            st.error(f"⚠️ Ingredientes repetidos: {', '.join(repetidos)}. Ajuste antes de salvar.")
            return

        salvar_receita(prato_val, ingredientes)
        st.success(f"✅ Receita '{_norm_local(prato_val)}' salva com sucesso!")