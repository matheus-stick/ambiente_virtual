import streamlit as st
import pandas as pd
import altair as alt

from functions.db_utils import (
    load_receitas,
    preco_receita,
)

# ---------------------------
# Página: Precificação (Nova UI)
# ---------------------------

def _injetar_css_soulfit():
    # Paleta aproximada a partir do logo:
    # - Rosa/Vermelho: destaque principal
    # - Amarelo/dourado: acento
    st.markdown(
        """
        <style>
            :root{
                --sf-primary: #E83C5B;   /* rosa/vermelho SoulFit */
                --sf-primary-2: #C61F43; /* variação mais escura */
                --sf-accent: #F3B21A;    /* amarelo/dourado */
                --sf-bg: #FFF7FA;        /* fundo rosado bem leve */
                --sf-card: #FFFFFF;
                --sf-text: #231F20;
                --sf-muted: rgba(35,31,32,.65);
                --sf-border: rgba(232, 60, 91, .18);
                --sf-shadow: 0 10px 24px rgba(35,31,32,.10);
                --sf-radius: 18px;
            }

            /* Container geral */
            .sf-wrap{
                background: linear-gradient(180deg, var(--sf-bg) 0%, #FFFFFF 55%);
                border: 1px solid var(--sf-border);
                border-radius: var(--sf-radius);
                padding: 22px 22px 14px 22px;
                box-shadow: var(--sf-shadow);
            }

            /* Top bar */
            .sf-top{
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:16px;
                margin-bottom: 10px;
            }
            .sf-title{
                font-size: 28px;
                font-weight: 800;
                color: var(--sf-text);
                margin: 0;
                line-height: 1.1;
            }
            .sf-subtitle{
                margin: 4px 0 0 0;
                color: var(--sf-muted);
                font-size: 14px;
            }
            .sf-badge{
                display:inline-flex;
                align-items:center;
                gap:8px;
                background: rgba(232, 60, 91, .10);
                border: 1px solid rgba(232, 60, 91, .20);
                color: var(--sf-primary-2);
                border-radius: 999px;
                padding: 8px 12px;
                font-weight: 700;
                font-size: 12px;
                white-space: nowrap;
            }
            .sf-dot{
                width:10px;height:10px;border-radius:999px;
                background: var(--sf-accent);
                box-shadow: 0 0 0 4px rgba(243,178,26,.18);
            }

            /* Seções */
            .sf-section{
                margin-top: 16px;
                padding-top: 14px;
                border-top: 1px dashed rgba(232,60,91,.22);
            }
            .sf-h2{
                margin: 0 0 8px 0;
                font-size: 18px;
                font-weight: 800;
                color: var(--sf-primary-2);
            }
            .sf-help{
                margin: 0 0 10px 0;
                color: var(--sf-muted);
                font-size: 13px;
            }

            /* Cards de métricas */
            .sf-grid{
                display:grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
            }
            @media (max-width: 900px){
                .sf-grid{ grid-template-columns: 1fr; }
            }
            .sf-card{
                background: var(--sf-card);
                border: 1px solid rgba(35,31,32,.08);
                border-radius: 16px;
                padding: 14px 14px;
                box-shadow: 0 8px 18px rgba(35,31,32,.06);
            }
            .sf-label{
                font-size: 12px;
                color: var(--sf-muted);
                margin: 0 0 6px 0;
                font-weight: 700;
                letter-spacing: .2px;
            }
            .sf-value{
                font-size: 20px;
                color: var(--sf-text);
                margin: 0;
                font-weight: 900;
            }
            .sf-big{
                border: 1px solid rgba(232,60,91,.22);
                background: linear-gradient(180deg, rgba(232,60,91,.08), rgba(243,178,26,.08));
            }
            .sf-big .sf-value{
                font-size: 28px;
                color: var(--sf-primary-2);
            }

            /* Notas / callouts */
            .sf-callout{
                background: rgba(243,178,26,.10);
                border: 1px solid rgba(243,178,26,.28);
                border-radius: 14px;
                padding: 12px 14px;
                color: var(--sf-text);
                font-size: 13px;
                margin-top: 10px;
            }

            /* Ajustes de espaçamento Streamlit */
            div.block-container { padding-top: 1.4rem; }
        </style>
        """,
        unsafe_allow_html=True
    )


def pagina_precificacao():
    _injetar_css_soulfit()

    st.markdown(
        """
        <div class="sf-wrap">
            <div class="sf-top">
                <div>
                    <p class="sf-title">💰 Precificação SoulFit</p>
                    <p class="sf-subtitle">Calcule custo de ingredientes, custos adicionais e simule margens de lucro.</p>
                </div>
                <div class="sf-badge"><span class="sf-dot"></span> Marmitas Personalizadas</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- Carregar receitas ----------------
    receitas = load_receitas("data/receitas.xlsx")
    if not receitas:
        st.warning("⚠️ Nenhuma receita cadastrada até o momento. Cadastre uma receita antes de precificar.")
        return

    pratos = list(receitas.keys())

    st.markdown("<div class='sf-section'><p class='sf-h2'>1) Selecione a receita</p></div>", unsafe_allow_html=True)
    prato_escolhido = st.selectbox("Prato:", pratos)

    # ---------------- Custo de ingredientes ----------------
    st.markdown("<div class='sf-section'><p class='sf-h2'>2) Custo dos ingredientes</p></div>", unsafe_allow_html=True)

    df_preco, preco_total = preco_receita(prato_escolhido)

    cA, cB = st.columns([1.3, 1])

    with cA:
        st.markdown("<p class='sf-help'>Detalhamento do custo por ingrediente (com base no seu estoque/cadastro de preços).</p>", unsafe_allow_html=True)
        st.dataframe(df_preco, use_container_width=True, hide_index=True)

    with cB:
        st.markdown(
            f"""
            <div class="sf-card sf-big">
                <p class="sf-label">Custo total (ingredientes)</p>
                <p class="sf-value">R$ {preco_total:,.2f}</p>
            </div>
            <div class="sf-callout">
                Dica: mantenha seu cadastro de preços e unidades consistente (kg, g, L, ml) para o custo sair fiel.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- Custos adicionais ----------------
    st.markdown("<div class='sf-section'><p class='sf-h2'>3) Custos adicionais</p><p class='sf-help'>Inclua custos variáveis para um preço mais realista.</p></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        tempo_horas = st.number_input("Tempo de preparo (horas)", min_value=0, max_value=24, step=1, value=1)
        custo_hora = st.number_input("Custo por hora (R$)", min_value=0.0, step=0.5, format="%.2f")
        frete = st.number_input("Frete (R$)", min_value=0.0, step=0.5, format="%.2f")

    with col2:
        impostos = st.number_input("Impostos (R$)", min_value=0.0, step=0.5, format="%.2f")
        outros_custos = st.number_input("Outros custos (R$)", min_value=0.0, step=0.5, format="%.2f")
        st.caption("Ex.: embalagem, gás, taxa do app, perdas, etc.")

    # Cálculos
    custo_tempo = float(tempo_horas) * float(custo_hora)
    valor_final = float(preco_total) + float(custo_tempo) + float(frete) + float(impostos) + float(outros_custos)

    with col3:
        st.markdown(
            f"""
            <div class="sf-grid">
                <div class="sf-card">
                    <p class="sf-label">Ingredientes</p>
                    <p class="sf-value">R$ {preco_total:,.2f}</p>
                </div>
                <div class="sf-card">
                    <p class="sf-label">Custo de tempo</p>
                    <p class="sf-value">R$ {custo_tempo:,.2f}</p>
                </div>
                <div class="sf-card">
                    <p class="sf-label">Frete</p>
                    <p class="sf-value">R$ {frete:,.2f}</p>
                </div>
                <div class="sf-card">
                    <p class="sf-label">Impostos</p>
                    <p class="sf-value">R$ {impostos:,.2f}</p>
                </div>
                <div class="sf-card">
                    <p class="sf-label">Outros</p>
                    <p class="sf-value">R$ {outros_custos:,.2f}</p>
                </div>
                <div class="sf-card sf-big">
                    <p class="sf-label">Custo total (base)</p>
                    <p class="sf-value">R$ {valor_final:,.2f}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- Simulação de margens ----------------
    st.markdown("<div class='sf-section'><p class='sf-h2'>4) Simulação de margens</p><p class='sf-help'>Compare preços sugeridos e lucros por margem.</p></div>", unsafe_allow_html=True)

    margens = list(range(5, 55, 5))
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

    modo = st.radio("Visualização:", ["📊 Tabela", "📈 Gráfico"], horizontal=True)

    if modo == "📊 Tabela":
        st.dataframe(df_margens, use_container_width=True, hide_index=True)
    else:
        metrica = st.selectbox("Métrica do gráfico:", ["Lucro Bruto (R$)", "Preço de Venda (R$)"])

        chart = (
            alt.Chart(df_margens)
            .mark_bar()
            .encode(
                x=alt.X("Margem (%)", title="Margem de Lucro (%)"),
                y=alt.Y(metrica, title=metrica),
                tooltip=[alt.Tooltip("Margem (%)"), alt.Tooltip(metrica)]
            )
            .properties(width="container", height=360)
        )

        text = (
            alt.Chart(df_margens)
            .mark_text(align="center", baseline="bottom", dy=-6, fontSize=14)
            .encode(
                x="Margem (%)",
                y=metrica,
                text=alt.Text(metrica, format=".2f")
            )
        )

        st.altair_chart(chart + text, use_container_width=True)

    # ---------------- Slider margem desejada ----------------
    st.markdown("<div class='sf-section'><p class='sf-h2'>5) Margem desejada</p><p class='sf-help'>Defina a margem alvo e obtenha o preço sugerido final.</p></div>", unsafe_allow_html=True)

    margem_escolhida = st.slider("Margem de lucro (%)", 1, 100, 20, step=1)
    preco_venda_final = valor_final * (1 + margem_escolhida / 100)
    lucro_final = preco_venda_final - valor_final

    st.markdown(
        f"""
        <div class="sf-card sf-big">
            <p class="sf-label">Resultado para <b>{prato_escolhido.title()}</b></p>
            <p class="sf-value">Preço sugerido: R$ {preco_venda_final:,.2f}</p>
            <p class="sf-subtitle">Lucro bruto estimado: <b>R$ {lucro_final:,.2f}</b> (margem {margem_escolhida}%)</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Para rodar diretamente (opcional)
if __name__ == "__main__":
    pagina_precificacao()