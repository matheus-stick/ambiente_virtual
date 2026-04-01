from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)

from functions.db_utils import preco_receita


SOULFIT_CORES = {
    "primaria": "#e82859",
    "fundo_secundario": "#F9ECF2",
    "rosa_suave": "#E37D9C",
    "amarelo": "#EEAE30",
    "bege": "#EEC7A7",
    "cinza": "#CCC1C9",
    "rosa_destaque": "#EC548C",
}

TITULO_ORCAMENTO = (
    "Uma escolha inteligente para quem valoriza saúde, tempo e bem-estar no dia a dia."
)
LOGO_PATH = Path("images/logo_soulfit_fundo_branco.jpeg")


def _formatar_nome_receita(nome: str) -> str:
    return str(nome).title()


def _formatar_valor_monetario(valor: float) -> str:
    return f"R$ {valor:,.2f}"


def _formatar_quantidade(quantidade: Any) -> str:
    if isinstance(quantidade, float) and quantidade.is_integer():
        return str(int(quantidade))
    if isinstance(quantidade, int):
        return str(quantidade)
    return str(quantidade)


def _deve_ocultar_ingrediente(nome_ingrediente: str) -> bool:
    return str(nome_ingrediente).strip().startswith("1.")


def montar_orcamento_lote(
    receitas_selecionadas: list[str],
    quantidades: dict[str, int],
) -> dict[str, Any]:
    receitas_orcamento: list[dict[str, Any]] = []
    valor_total_geral = 0.0

    for receita in receitas_selecionadas:
        df_receita, preco_unitario = preco_receita(receita)
        qtd_pratos = int(quantidades.get(receita, 0) or 0)
        valor_total_receita = round(preco_unitario * qtd_pratos, 2)
        valor_total_geral += valor_total_receita

        ingredientes_resumidos = []
        for _, row in df_receita.iterrows():
            nome_ingrediente = str(row["Produto"]).strip()
            if _deve_ocultar_ingrediente(nome_ingrediente):
                continue
            ingredientes_resumidos.append(_formatar_nome_receita(nome_ingrediente))

        receitas_orcamento.append(
            {
                "nome": _formatar_nome_receita(receita),
                "ingredientes_resumidos": ", ".join(ingredientes_resumidos)
                if ingredientes_resumidos
                else "Ingredientes não visíveis para este orçamento.",
                "quantidade_pratos": qtd_pratos,
                "preco_unitario": round(preco_unitario, 2),
                "valor_total": valor_total_receita,
            }
        )

    return {
        "titulo": TITULO_ORCAMENTO,
        "receitas": receitas_orcamento,
        "valor_total_geral": round(valor_total_geral, 2),
    }


def gerar_pdf_orcamento_lote(dados_orcamento: dict[str, Any]) -> bytes:

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloSoulfit",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=24,
        textColor=colors.HexColor(SOULFIT_CORES["primaria"]),
        alignment=1,
        spaceAfter=10,
    )
    estilo_secao = ParagraphStyle(
        "SecaoSoulfit",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=17,
        textColor=colors.HexColor(SOULFIT_CORES["primaria"]),
        spaceAfter=4,
        spaceBefore=4,
    )
    estilo_rotulo = ParagraphStyle(
        "RotuloSoulfit",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor(SOULFIT_CORES["rosa_destaque"]),
    )
    estilo_texto = ParagraphStyle(
        "TextoSoulfit",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.black,
    )
    estilo_ingredientes = ParagraphStyle(
        "IngredientesSoulfit",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#333333"),
        spaceAfter=5,
    )
    estilo_meta = ParagraphStyle(
        "MetaSoulfit",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4a4a4a"),
        spaceAfter=6,
    )

    elementos = []

    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH))
        logo.drawHeight = 28 * mm
        logo.drawWidth = 28 * mm
        elementos.append(logo)
        elementos.append(Spacer(1, 6))

    elementos.append(Paragraph(dados_orcamento["titulo"], estilo_titulo))
    elementos.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=colors.HexColor(SOULFIT_CORES["rosa_destaque"]),
            spaceBefore=2,
            spaceAfter=12,
        )
    )

    for receita in dados_orcamento["receitas"]:
        elementos.append(Paragraph(receita["nome"], estilo_secao))
        elementos.append(Paragraph(receita["ingredientes_resumidos"], estilo_ingredientes))
        elementos.append(
            Paragraph(
                (
                    f"Quantidade de pratos: <b>{receita['quantidade_pratos']}</b>"
                    f" &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp; "
                    f"Preço unitário: <b>{_formatar_valor_monetario(receita['preco_unitario'])}</b>"
                    f" &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp; "
                    f"Preço total: <b>{_formatar_valor_monetario(receita['valor_total'])}</b>"
                ),
                estilo_meta,
            )
        )
        elementos.append(Spacer(1, 8))
        elementos.append(
            HRFlowable(
                width="100%",
                thickness=0.8,
                color=colors.HexColor(SOULFIT_CORES["bege"]),
                spaceBefore=2,
                spaceAfter=10,
            )
        )

    elementos.append(Paragraph("Resumo final do orçamento", estilo_secao))
    resumo_final = [
        [
            Paragraph("Receita", estilo_rotulo),
            Paragraph("Qtd. pratos", estilo_rotulo),
            Paragraph("Preço unitário", estilo_rotulo),
            Paragraph("Preço total", estilo_rotulo),
        ]
    ]
    for receita in dados_orcamento["receitas"]:
        resumo_final.append(
            [
                Paragraph(receita["nome"], estilo_texto),
                Paragraph(str(receita["quantidade_pratos"]), estilo_texto),
                Paragraph(_formatar_valor_monetario(receita["preco_unitario"]), estilo_texto),
                Paragraph(_formatar_valor_monetario(receita["valor_total"]), estilo_texto),
            ]
        )

    tabela_resumo_final = Table(
        resumo_final,
        colWidths=[72 * mm, 24 * mm, 34 * mm, 34 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    tabela_resumo_final.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(SOULFIT_CORES["fundo_secundario"])),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(SOULFIT_CORES["fundo_secundario"])),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(SOULFIT_CORES["fundo_secundario"])]),
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor(SOULFIT_CORES["cinza"])),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elementos.append(tabela_resumo_final)
    elementos.append(Spacer(1, 10))

    quadro_total = Table(
        [["Valor final consolidado", _formatar_valor_monetario(dados_orcamento["valor_total_geral"])]],
        colWidths=[95 * mm, 45 * mm],
        hAlign="RIGHT",
    )
    quadro_total.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SOULFIT_CORES["fundo_secundario"])),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(SOULFIT_CORES["primaria"])),
                ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor(SOULFIT_CORES["primaria"])),
                ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor(SOULFIT_CORES["primaria"])),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elementos.append(quadro_total)

    doc.build(elementos)
    return buffer.getvalue()
