import altair as alt
from datetime import datetime
import time
import pandas as pd
import streamlit as st

from functions.db_utils import load_receitas, preco_receita, card_metric_big
from functions.orcamento_pdf import (
    gerar_pdf_orcamento_lote,
    montar_orcamento_lote,
    montar_preview_pdf_imagens,
)


def _formatar_nome_receita(nome: str) -> str:
    return nome.title()


def _normalizar_nome_cliente(valor: str) -> str:
    return " ".join(str(valor).strip().split())


def _normalizar_nome_cliente_arquivo(nome_cliente: str) -> str:
    return _normalizar_nome_cliente(nome_cliente).replace(" ", "_")


def _resumir_receita(df_receita: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    df_resumo = df_receita[
        [
            "Produto",
            "Quantidade Necessária",
            "Preço Base (R$)",
            "Custo da Porção (R$)",
        ]
    ].copy()
    total_ingredientes = (
        int(df_resumo["Produto"].count()) if not df_resumo.empty else 0
    )
    df_resumo["Custo da Porção (R$)"] = df_resumo["Custo da Porção (R$)"].map(
        lambda x: f"R$ {x:,.2f}"
    )
    return total_ingredientes, df_resumo


def pagina_precificacao():
    st.title("💰 Precificação de Receitas")
    st.info(
        "Acompanhe o custo das receitas de forma individual ou em massa, com foco no impacto dos ingredientes."
    )

    receitas = load_receitas("data/receitas.xlsx")
    if not receitas:
        st.warning("Nenhuma receita cadastrada. Cadastre uma receita antes de precificar.")
        return

    pratos = list(receitas.keys())
    aba_massa, aba_individual = st.tabs(
        ["📦 Precificação em Massa", "🍽️ Precificação Individual"]
    )

    with aba_individual:
        st.subheader("Precificação Individual")
        prato_individual = st.selectbox(
            "Selecione uma receita específica:",
            pratos,
            key="prec_individual",
        )

        df_preco, preco_total = preco_receita(prato_individual)
        df_individual = df_preco[
            [
                "Produto",
                "Quantidade Necessária",
                "Preço Base (R$)",
                "Custo da Porção (R$)",
            ]
        ].copy()
        df_individual["Custo da Porção (R$)"] = df_individual[
            "Custo da Porção (R$)"
        ].round(2)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(f"### Ingredientes de {_formatar_nome_receita(prato_individual)}")
            st.dataframe(df_individual, use_container_width=True, hide_index=True)
        with c2:
            st.metric("Preço total do prato", f"R$ {preco_total:,.2f}")
            st.metric("Ingredientes na receita", len(df_individual))

    with aba_massa:
        st.subheader("Precificação em Massa")
        receitas_selecionadas = st.multiselect(
            "Selecione as receitas para o lote:",
            pratos,
            key="prec_massa",
        )

        if not receitas_selecionadas:
            st.warning("Selecione ao menos uma receita para continuar.")
        else:
            dados_receitas: dict[str, dict] = {}
            for receita in receitas_selecionadas:
                df_receita, preco_prato = preco_receita(receita)
                total_ingredientes, df_resumo = _resumir_receita(df_receita)
                dados_receitas[receita] = {
                    "df_resumo": df_resumo,
                    "preco_prato": preco_prato,
                    "qtd_ingredientes_total": total_ingredientes,
                    "qtd_itens": len(df_receita),
                }

            for receita in receitas_selecionadas:
                dados = dados_receitas[receita]
                with st.expander(
                    f"{_formatar_nome_receita(receita)} • custo R$ {dados['preco_prato']:,.2f} • "
                    f"{dados['qtd_itens']} ingredientes"
                ):
                    topo1, topo2 = st.columns(2)
                    with topo1:
                        st.caption(f"Preço de custo: R$ {dados['preco_prato']:,.2f}")
                    with topo2:
                        st.caption(
                            f"Quantidade total de ingredientes: {dados['qtd_ingredientes_total']}"
                        )

                    st.dataframe(
                        dados["df_resumo"],
                        use_container_width=True,
                        hide_index=True,
                        height=min(245, 70 + len(dados["df_resumo"]) * 35),
                    )

            st.markdown("---")

            st.write("Informe quantos pratos de cada receita serão produzidos.")
            cols_qtd = st.columns(min(len(receitas_selecionadas), 3))
            quantidades: dict[str, int] = {}
            for idx, receita in enumerate(receitas_selecionadas):
                with cols_qtd[idx % len(cols_qtd)]:
                    quantidades[receita] = st.number_input(
                        f"{_formatar_nome_receita(receita)}",
                        min_value=1,
                        value=1,
                        step=1,
                        key=f"qtd_{receita}",
                    )

            dados_lote: list[dict] = []
            total_lote = 0.0

            for receita in receitas_selecionadas:
                dados = dados_receitas[receita]
                qtd_pratos = quantidades[receita]
                custo_total_receita = dados["preco_prato"] * qtd_pratos
                qtd_ingredientes_total = dados["qtd_ingredientes_total"] * qtd_pratos
                total_lote += custo_total_receita

                dados_lote.append(
                    {
                        "Receita": _formatar_nome_receita(receita),
                        "Quantidade de pratos": qtd_pratos,
                        "Custo unitário (R$)": round(dados["preco_prato"], 2),
                        "Valor total (R$)": round(custo_total_receita, 2),
                        "Qtd. ingredientes total": int(qtd_ingredientes_total),
                        "Rótulo": f"{qtd_ingredientes_total} itens • R$ {custo_total_receita:,.2f}",
                    }
                )

            df_lote = pd.DataFrame(dados_lote).sort_values(
                "Valor total (R$)", ascending=False
            )

            col_preco_total, col_grafico = st.columns([1.05, 1.2])

            with col_preco_total:
                card_metric_big(
                    "Custo total do lote",
                    f"{total_lote:,.2f}",
                    prefixo_medida="R$",
                )

            with col_grafico:
                st.write("#### Impacto por receita no total")
                base = alt.Chart(df_lote).encode(
                    y=alt.Y("Receita:N", sort="-x", title=None),
                    x=alt.X("Valor total (R$)", title="Valor total (R$)"),
                    tooltip=[
                        alt.Tooltip("Receita:N"),
                        alt.Tooltip("Quantidade de pratos:Q"),
                        alt.Tooltip("Valor total (R$):Q", format=",.2f"),
                    ],
                )

                barras = base.mark_bar(
                    color="#EC548C", cornerRadiusEnd=6, size=28
                )
                texto = base.mark_text(
                    align="left",
                    baseline="middle",
                    dx=8,
                    color="#1f2937",
                ).encode(text="Rótulo:N")

                st.altair_chart(
                    (barras + texto).properties(height=max(220, len(df_lote) * 70)),
                    use_container_width=True,
                )

            st.markdown("---")
            st.write("#### Geração do orçamento")
            c1, c2 = st.columns([2, 2])
            with c1:
                nome_cliente = st.text_input(
                    "Informe o nome e sobrenome do cliente:",
                    max_chars=30,
                    key="nome_cliente",
                    placeholder="Ex.: Ana Souza",
                )

            try:
                dados_orcamento = montar_orcamento_lote(
                    receitas_selecionadas=receitas_selecionadas,
                    quantidades=quantidades,
                )
                # Reaproveita os bytes.
                pdf_bytes = gerar_pdf_orcamento_lote(dados_orcamento)
                area_feedback = st.empty()
                nome_cliente = _normalizar_nome_cliente(nome_cliente)

                with c2:
                    if not nome_cliente:
                        st.info(
                            "O preview já está disponível. Preencha nome e sobrenome para liberar o download."
                        )
                    elif len(nome_cliente.split()) < 2:
                        st.warning("Informe nome e sobrenome do cliente.")
                    else:
                        st.markdown("<br>", unsafe_allow_html=True) 
                        prefixo_orcamento = "Orcamento_Soulfit"
                        data_orcamento = datetime.now().strftime("%Y_%m_%d")
                        nome_cliente_arquivo = _normalizar_nome_cliente_arquivo(nome_cliente)
                        nome_arquivo = (
                            f"{prefixo_orcamento}_{data_orcamento}_{nome_cliente_arquivo}.pdf"
                        )

                        clicou_download = st.download_button(
                            "📩 Baixar PDF do orçamento.",
                            data=pdf_bytes,
                            file_name=nome_arquivo,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        if clicou_download:
                            area_feedback.info("Download efetuado ☑️")
                            time.sleep(2)
                            area_feedback.empty()

                # Mostra o preview.
                st.write("#### Pré-visualização do orçamento")
                with st.expander("Clique para expandir o preview do PDF gerado"):
                    st.caption("As imagens abaixo correspondem ao PDF final do orçamento.")
                    try:
                        # Gera as páginas.
                        preview_paginas = montar_preview_pdf_imagens(pdf_bytes)
                        for pagina_idx, pagina_bytes in enumerate(preview_paginas, start=1):
                            # Exibe a página.
                            st.image(
                                pagina_bytes,
                                caption=f"Página {pagina_idx}",
                                use_column_width=True,
                            )
                    except Exception as preview_exc:
                        st.error(
                            f"Não foi possível renderizar a pré-visualização do PDF: {preview_exc}"
                        )

            except Exception as exc:
                st.error(f"Não foi possível preparar o PDF para visualização ou download: {exc}")
