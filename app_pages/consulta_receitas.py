import streamlit as st
import pandas as pd
import altair as alt
from functions.db_utils import (
    verificar_disponibilidade,
    load_receitas,
    preco_receita,
    carregar_estoque,
    salvar_estoque
)

# ---------------- STREAMLIT ----------------

def pagina_consulta_receitas():
    st.title("🍽️ Consulta e Precificação de Receitas")

    st.info("Verifique a viabilidade de produção, custos dos ingredientes e calcule o valor final estimado do prato.")

    # ---------------- VIABILIDADE DE PRODUÇÃO ----------------
    st.header("🧑‍🍳 Viabilidade de Produção com o Estoque Atual")

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
        
        # ---------------- BOTÃO DE BAIXA NO ESTOQUE ----------------
        if st.button("📦 Dar baixa no estoque"):
            try:
                # Carregar estoque e receita
                df_estoque = carregar_estoque("data/estoque_inicial.xlsx")
                receitas = load_receitas("data/receitas.xlsx")
                ingredientes = receitas[prato_escolhido]

                # Atualizar estoque
                for item in ingredientes:
                    produto = str(item["produto"]).strip().lower()
                    qtd_necessaria = float(item["quantidade"])

                    if produto in df_estoque["produto"].values:
                        idx = df_estoque.index[df_estoque["produto"] == produto][0]
                        df_estoque.at[idx, "quantidade_disponivel"] = max(
                            0, df_estoque.at[idx, "quantidade_disponivel"] - qtd_necessaria
                        )

                # Salvar estoque atualizado
                salvar_estoque(df_estoque)
                st.success(f"✅ Baixa no estoque realizada com sucesso para '{prato_escolhido.title()}'.")
                st.experimental_rerun()  # Recarrega a página para refletir o novo estoque
            except Exception as e:
                st.error(f"❌ Erro ao atualizar o estoque: {e}")
    else:
        st.error("❌ Estoque insuficiente para produzir esse prato.")

    # ---------------- PRECIFICAÇÃO DO PRODUTO ----------------
    st.markdown("---")
    st.header("💰 Precificação da Receita")

    df_preco, preco_total = preco_receita(prato_escolhido)

    st.write("### Detalhamento do Custo dos Ingredientes:")
    st.dataframe(df_preco, use_container_width=True, hide_index=True)

    st.success(f"💵 Custo total estimado dos ingredientes: **R$ {preco_total:,.2f}**")

    # ---------------- CUSTOS ADICIONAIS ----------------
    st.markdown("---")
    st.subheader("🧮 Custos Adicionais para Precificação Completa")

    cA, cB, cC, cD = st.columns(4)
    with cA:
        tempo_minutos = st.number_input("Tempo de preparo (minutos):", min_value=0, max_value=60, step=5, value=60)
        custo_hora = st.number_input("Custo por hora de preparo (R$):", min_value=0.0, step=0.1, format="%.2f")

    with cB:
        comissoes = st.number_input("Comissões (R$):", min_value=0.0, step=0.1, format="%.2f")
    with cC:
        impostos = st.number_input("Impostos (R$):", min_value=0.0, step=0.1, format="%.2f")
    with cD:
        outros_custos = st.number_input("Outros custos (R$):", min_value=0.0, step=0.1, format="%.2f")

    # Calcular custo de tempo proporcional
    custo_tempo = (tempo_minutos / 60) * custo_hora if custo_hora > 0 and tempo_minutos > 0 else 0.0

    # Calcular valor final total (custo total do prato)
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

    # ---------------- TABELA/GRÁFICO DE MARGENS DE LUCRO ----------------
    st.markdown("---")
    st.subheader("📈 Simulação de Margens de Lucro")

    margens = list(range(5, 55, 5))  # 5%, 10%, 15% ... até 50%
    dados_margens = []

    for m in margens:
        preco_venda = valor_final * (1 + m / 100)
        lucro_bruto = preco_venda - valor_final
        dados_margens.append({
            "Margem (%)": m,
            "Preço de Venda (R$)": round(preco_venda, 2),
            "Lucro Bruto (R$)": round(lucro_bruto, 2)
        })

    df_margens = pd.DataFrame(dados_margens)
    modo_visualizacao = st.radio("Selecione o modo de visualização:", ["📊 Tabela", "📈 Gráfico de Colunas"])

    if modo_visualizacao == "📊 Tabela":
        st.dataframe(df_margens, use_container_width=True, hide_index=True)
    else:
        # Escolha da métrica do gráfico
        metrica = st.selectbox(
            "Escolha o que deseja visualizar no gráfico:",
            ["Lucro Bruto (R$)", "Preço de Venda (R$)"]
        )

        # Criação do gráfico com rótulos
        chart = (
            alt.Chart(df_margens)
            .mark_bar(color="#73a40a")
            .encode(
                x=alt.X("Margem (%)", title="Margem de Lucro (%)"),
                y=alt.Y(metrica, title=metrica),
                tooltip=[alt.Tooltip("Margem (%)"), alt.Tooltip(metrica)]
            )
            .properties(width="container", height=400)
        )

        # Adicionando rótulos acima das barras
        text = (
            alt.Chart(df_margens)
            .mark_text(align="center", baseline="bottom", dy=-5, fontSize=18,font='monospace', color="#73a40a")
            .encode(
                x="Margem (%)",
                y=metrica,
                text=alt.Text(metrica, format=".2f")
            )
        )

        st.altair_chart(chart + text, use_container_width=True)

    # ---------------- SLIDER INTERATIVO ---------------- 
    st.markdown("---")
    
    st.subheader("🎯 Defina a Margem de Lucro Desejada") 
    
    margem_escolhida = st.slider("Selecione a margem de lucro (%)", 1, 100, 20, step=1) 
    preco_venda_final = valor_final * (1 + margem_escolhida / 100) 
    lucro_final = preco_venda_final - valor_final 
    
    st.info( f"Com uma margem de **{margem_escolhida}%**, " f"o preço sugerido de venda é **R\\$ {preco_venda_final:,.2f}.** " f"e o lucro bruto estimado é **R\\$ {lucro_final:,.2f}.**" )