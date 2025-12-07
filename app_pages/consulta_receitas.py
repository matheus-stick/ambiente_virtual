import streamlit as st
from functions.db_utils import verificar_disponibilidade, load_receitas, preco_receita

# ---------------- STREAMLIT ----------------

def pagina_consulta_receitas():
    st.title("🍽️ Consulta e Precificação de Receitas")

    st.info("Verifique a viabilidade de produção, custos dos ingredientes e calcule o valor final estimado do prato.")

    # ---------------- VIABILIDADE DE PRODUÇÃO ----------------
    st.subheader("🔪 Viabilidade de Produção com o Estoque Atual")

    # Carregar receitas
    receitas = load_receitas("data/receitas.xlsx")
    if not receitas:
        st.warning("⚠️ Nenhuma receita cadastrada até o momento. Cadastre uma nova receita antes de consultar.")
        return

    pratos = list(receitas.keys())
    prato_escolhido = st.selectbox("Selecione o prato:", pratos)

    # Verificar disponibilidade
    
    disponivel, resultado = verificar_disponibilidade(prato_escolhido)

    st.subheader(f"Verificação de estoque para '{prato_escolhido.title()}':")
    for r in resultado:
        st.write(r)

    if disponivel:
        st.success("✅ É possível produzir esse prato com o estoque atual!")
    else:
        st.error("❌ Estoque insuficiente para produzir esse prato.")

    # ---------------- PRECIFICAÇÃO DO PRODUTO ----------------
    st.markdown("---")
    st.subheader("💰 Precificação da Receita")

    df_preco, preco_total = preco_receita(prato_escolhido)

    st.write("### Detalhamento do Custo dos Ingredientes:")
    st.dataframe(df_preco, use_container_width=True, hide_index=True)

    st.success(f"💵 Custo total estimado dos ingredientes: **R$ {preco_total:,.2f}**")

    # ---------------- CUSTOS ADICIONAIS ----------------
    st.markdown("---")
    st.subheader("🧮 Custos Adicionais para Precificação Completa")

    cA, cB, cC, cD= st.columns(4)
    with cA:
        tempo_minutos = st.number_input(
            "Tempo de preparo (minutos):", min_value=0, max_value=60, step=5, value=60
        )
        custo_hora = st.number_input("Custo por hora de preparo (R$):", min_value=0.0, step=0.1, format="%.2f")

    with cB:
        comissoes = st.number_input("Comissões (R$):", min_value=0.0, step=0.1, format="%.2f")
    with cC:
        impostos = st.number_input("Impostos (R$):", min_value=0.0, step=0.1, format="%.2f")
    with cD:
        outros_custos = st.number_input("Outros custos (R$):", min_value=0.0, step=0.1, format="%.2f")

    # Calcular custo de tempo proporcional
    if custo_hora > 0 and tempo_minutos > 0:
        custo_tempo = (tempo_minutos / 60) * custo_hora
    else:
        custo_tempo = 0.0

    # Calcular valor final total
    valor_final = preco_total + custo_tempo + comissoes + impostos + outros_custos

    # Mostrar resumo dos custos
    st.markdown("---")
    st.subheader("📊 Resumo da Precificação")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.write(f"🧂 **Ingredientes:** R$ {preco_total:,.2f}")
    with c2:
        st.write(f"⏱️ **Custo de tempo:** R$ {custo_tempo:,.2f}")
    with c3:
        st.write(f"💸 **Comissões:** R$ {comissoes:,.2f}")
    with c4:
        st.write(f"🏛️ **Impostos:** R$ {impostos:,.2f}")
    with c5:
        st.write(f"⚙️ **Outros custos:** R$ {outros_custos:,.2f}")

    st.success(f"💰 **Valor final estimado do prato '{prato_escolhido.title()}': R$ {valor_final:,.2f}**")
