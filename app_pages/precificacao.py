import streamlit as st
import pandas as pd
import altair as alt
from functions.db_utils import load_receitas, preco_receita


def pagina_precificacao():
    st.title("💰 Precificação de Receitas")
    st.info(
        "Calcule o custo de produção das suas receitas, adicione custos variáveis "
        "e simule margens de lucro — individualmente ou em massa."
    )

    # ----------------------------------------------------------------
    # Carregar receitas disponíveis
    # ----------------------------------------------------------------
    receitas = load_receitas("data/receitas.xlsx")
    if not receitas:
        st.warning(
            "⚠️ Nenhuma receita cadastrada. Cadastre uma receita antes de precificar."
        )
        return

    pratos = list(receitas.keys())

    # ================================================================
    # SEÇÃO 1 — Consulta Individual de Receita
    # ================================================================
    st.header("🔍 Consulta Individual de Receita")

    prato_individual = st.selectbox(
        "Selecione uma receita para ver o detalhamento:",
        pratos,
        key="prec_individual",
    )

    df_preco, preco_total = preco_receita(prato_individual)

    st.write("#### Ingredientes e Custos")
    st.dataframe(df_preco, use_container_width=True, hide_index=True)
    st.success(
        f"💵 Custo total dos ingredientes de "
        f"**{prato_individual.title()}**: **R$ {preco_total:,.2f}**"
    )

    # ================================================================
    # SEÇÃO 2 — Precificação em Massa
    # ================================================================
    st.markdown("---")
    st.header("📦 Precificação em Massa")
    st.write(
        "Selecione várias receitas, defina a quantidade de cada uma e calcule "
        "o custo total de produção de todo o lote."
    )

    # ---------- seleção de receitas ----------
    receitas_selecionadas = st.multiselect(
        "Selecione as receitas para o lote:",
        pratos,
        key="prec_massa",
    )

    if not receitas_selecionadas:
        st.warning("Selecione ao menos uma receita para continuar.")
        return

    # ---------- quantidades por receita ----------
    st.subheader("📝 Quantidades por Receita")
    cols_qtd = st.columns(min(len(receitas_selecionadas), 4))

    quantidades: dict[str, int] = {}
    for idx, receita in enumerate(receitas_selecionadas):
        with cols_qtd[idx % len(cols_qtd)]:
            quantidades[receita] = st.number_input(
                f"{receita.title()}",
                min_value=1,
                value=1,
                step=1,
                key=f"qtd_{receita}",
            )

    # ---------- calcular custos de ingredientes ----------
    dados_lote: list[dict] = []
    custo_ingredientes_total = 0.0

    for receita in receitas_selecionadas:
        df_r, custo_unitario = preco_receita(receita)
        qtd = quantidades[receita]
        custo_linha = custo_unitario * qtd

        dados_lote.append(
            {
                "Receita": receita.title(),
                "Custo Unitário (R$)": custo_unitario,
                "Quantidade": qtd,
                "Custo Total (R$)": round(custo_linha, 2),
            }
        )
        custo_ingredientes_total += custo_linha

    df_lote = pd.DataFrame(dados_lote)

    st.write("#### Resumo do Lote")
    st.dataframe(df_lote, use_container_width=True, hide_index=True)
    st.success(
        f"🧂 **Custo total de ingredientes do lote:** R$ {custo_ingredientes_total:,.2f}"
    )

    # ---------- detalhamento por receita (expansível) ----------
    with st.expander("📋 Ver detalhamento de ingredientes por receita"):
        for receita in receitas_selecionadas:
            df_det, _ = preco_receita(receita)
            st.write(f"**{receita.title()}**")
            st.dataframe(df_det, use_container_width=True, hide_index=True)

    # ================================================================
    # SEÇÃO 3 — Custos Variáveis
    # ================================================================
    st.markdown("---")
    st.header("🧮 Custos Variáveis")
    st.write("Informe os custos adicionais que incidem sobre o lote.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        impostos_pct = st.number_input(
            "Impostos (%)", min_value=0.0, max_value=100.0,
            step=0.5, value=0.0, format="%.2f", key="impostos_pct",
        )
    with c2:
        frete = st.number_input(
            "Frete (R$)", min_value=0.0, step=1.0, format="%.2f", key="frete",
        )
    with c3:
        custo_hora = st.number_input(
            "Custo por hora de trabalho (R$)", min_value=0.0,
            step=1.0, format="%.2f", key="custo_hora",
        )
    with c4:
        horas_trabalho = st.number_input(
            "Horas de trabalho", min_value=0.0,
            step=0.5, value=1.0, format="%.1f", key="horas_trabalho",
        )

    outros_custos = st.number_input(
        "Outros custos (R$)", min_value=0.0, step=1.0, format="%.2f",
        key="outros_custos",
    )

    # ---------- totalização ----------
    valor_impostos = custo_ingredientes_total * (impostos_pct / 100)
    custo_mao_obra = custo_hora * horas_trabalho
    custo_variavel_total = valor_impostos + frete + custo_mao_obra + outros_custos
    custo_total_lote = custo_ingredientes_total + custo_variavel_total

    st.markdown("---")
    st.subheader("📊 Resumo Geral de Custos do Lote")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("🧂 Ingredientes", f"R$ {custo_ingredientes_total:,.2f}")
    with r2:
        st.metric("📦 Custos Variáveis", f"R$ {custo_variavel_total:,.2f}")
    with r3:
        st.metric("💰 Custo Total do Lote", f"R$ {custo_total_lote:,.2f}")

    with st.expander("🔎 Detalhamento dos custos variáveis"):
        det1, det2, det3, det4 = st.columns(4)
        with det1:
            st.write(f"🏛️ **Impostos ({impostos_pct:.2f}%):** R$ {valor_impostos:,.2f}")
        with det2:
            st.write(f"🚚 **Frete:** R$ {frete:,.2f}")
        with det3:
            st.write(f"⏱️ **Mão de obra ({horas_trabalho:.1f}h × R$ {custo_hora:,.2f}):** R$ {custo_mao_obra:,.2f}")
        with det4:
            st.write(f"⚙️ **Outros custos:** R$ {outros_custos:,.2f}")

    # ================================================================
    # SEÇÃO 4 — Simulação de Margem por Receita e Global
    # ================================================================
    st.markdown("---")
    st.header("📈 Simulação de Margem de Lucro")

    # Distribuir custos variáveis proporcionalmente ao custo de ingredientes
    st.write(
        "Os custos variáveis são distribuídos proporcionalmente ao custo de "
        "ingredientes de cada receita."
    )

    # ---------- margem por receita ----------
    st.subheader("🎯 Margem por Receita")

    dados_margem: list[dict] = []
    total_receita_lote = 0.0

    for item in dados_lote:
        receita_nome = item["Receita"]
        custo_ingr = item["Custo Total (R$)"]

        # proporção do custo de ingredientes
        proporcao = (
            custo_ingr / custo_ingredientes_total
            if custo_ingredientes_total > 0
            else 0
        )
        custo_var_rateado = custo_variavel_total * proporcao
        custo_total_receita = custo_ingr + custo_var_rateado

        margem = st.slider(
            f"Margem de lucro para **{receita_nome}** (%)",
            min_value=0,
            max_value=200,
            value=30,
            step=1,
            key=f"margem_{receita_nome}",
        )

        preco_venda = custo_total_receita * (1 + margem / 100)
        lucro = preco_venda - custo_total_receita
        qtd = item["Quantidade"]
        preco_venda_unitario = preco_venda / qtd if qtd > 0 else 0

        dados_margem.append(
            {
                "Receita": receita_nome,
                "Qtd": qtd,
                "Custo Ingredientes (R$)": round(custo_ingr, 2),
                "Custos Var. Rateados (R$)": round(custo_var_rateado, 2),
                "Custo Total (R$)": round(custo_total_receita, 2),
                "Margem (%)": margem,
                "Preço Venda Total (R$)": round(preco_venda, 2),
                "Preço Venda Unitário (R$)": round(preco_venda_unitario, 2),
                "Lucro (R$)": round(lucro, 2),
            }
        )
        total_receita_lote += preco_venda

    df_margem = pd.DataFrame(dados_margem)

    st.markdown("---")
    st.subheader("📋 Tabela Final de Precificação")
    st.dataframe(df_margem, use_container_width=True, hide_index=True)

    # ---------- resultado global ----------
    lucro_total = total_receita_lote - custo_total_lote

    st.markdown("---")
    st.subheader("🏁 Resultado Final do Lote")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.metric("💰 Custo Total", f"R$ {custo_total_lote:,.2f}")
    with f2:
        st.metric("🛒 Receita Total (Venda)", f"R$ {total_receita_lote:,.2f}")
    with f3:
        margem_global = (
            ((total_receita_lote / custo_total_lote) - 1) * 100
            if custo_total_lote > 0
            else 0
        )
        st.metric(
            "📈 Lucro Bruto",
            f"R$ {lucro_total:,.2f}",
            delta=f"{margem_global:,.1f}% de margem",
        )

    # ---------- gráfico de preços de venda ----------
    if len(df_margem) > 1:
        st.markdown("---")
        st.subheader("📊 Visualização de Preços de Venda por Receita")

        chart = (
            alt.Chart(df_margem)
            .mark_bar(color="#73a40a")
            .encode(
                x=alt.X("Receita:N", title="Receita", sort="-y"),
                y=alt.Y("Preço Venda Total (R$):Q", title="Preço de Venda (R$)"),
                tooltip=[
                    alt.Tooltip("Receita:N"),
                    alt.Tooltip("Custo Total (R$):Q", format=",.2f"),
                    alt.Tooltip("Preço Venda Total (R$):Q", format=",.2f"),
                    alt.Tooltip("Lucro (R$):Q", format=",.2f"),
                ],
            )
            .properties(width="container", height=400)
        )

        text = (
            alt.Chart(df_margem)
            .mark_text(
                align="center",
                baseline="bottom",
                dy=-5,
                fontSize=14,
                font="monospace",
                color="#73a40a",
            )
            .encode(
                x=alt.X("Receita:N", sort="-y"),
                y="Preço Venda Total (R$):Q",
                text=alt.Text("Preço Venda Total (R$):Q", format=",.2f"),
            )
        )

        st.altair_chart(chart + text, use_container_width=True)
