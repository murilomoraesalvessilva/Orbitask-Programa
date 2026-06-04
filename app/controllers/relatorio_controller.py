# -*- coding: utf-8 -*-
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)

# Paleta azul escura
AZUL_FORTE   = colors.HexColor("#1a6fd4")
AZUL_ESCURO  = colors.HexColor("#06101e")
AZUL_CARD    = colors.HexColor("#080f1e")
AZUL_LINHA   = colors.HexColor("#0a1e34")
AZUL_TEXTO   = colors.HexColor("#c8dff5")
AZUL_SUB     = colors.HexColor("#2a5a8a")
BRANCO       = colors.HexColor("#ffffff")
VERDE        = colors.HexColor("#2ab87a")
AMARELO      = colors.HexColor("#f0a030")
VERMELHO     = colors.HexColor("#e05555")
ROXO         = colors.HexColor("#8a6aff")
CINZA_CLARO  = colors.HexColor("#e8f4ff")
CINZA_LINHA  = colors.HexColor("#dce8f5")

STATUS_LABEL = {
    "aberta":       "Aberta",
    "em_andamento": "Em Andamento",
    "concluida":    "Concluida",
    "cancelada":    "Cancelada",
}
PRIORIDADE_LABEL = {
    "baixa":   "Baixa",
    "normal":  "Normal",
    "alta":    "Alta",
    "urgente": "Urgente",
}


def _estilos():
    return {
        "titulo": ParagraphStyle(
            "titulo", fontName="Helvetica-Bold", fontSize=24,
            textColor=BRANCO, spaceAfter=4, leading=28
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", fontName="Helvetica", fontSize=11,
            textColor=AZUL_SUB, spaceAfter=2, leading=16
        ),
        "secao": ParagraphStyle(
            "secao", fontName="Helvetica-Bold", fontSize=10,
            textColor=AZUL_SUB, spaceBefore=20, spaceAfter=8,
            leading=14, letterSpacing=1
        ),
        "normal": ParagraphStyle(
            "normal", fontName="Helvetica", fontSize=10,
            textColor=AZUL_ESCURO, leading=14
        ),
        "rodape": ParagraphStyle(
            "rodape", fontName="Helvetica", fontSize=8,
            textColor=AZUL_SUB, alignment=TA_CENTER, leading=12
        ),
        "tabela_header": ParagraphStyle(
            "tabela_header", fontName="Helvetica-Bold", fontSize=9,
            textColor=BRANCO, leading=12
        ),
        "tabela_cel": ParagraphStyle(
            "tabela_cel", fontName="Helvetica", fontSize=9,
            textColor=AZUL_ESCURO, leading=12
        ),
        "card_valor": ParagraphStyle(
            "card_valor", fontName="Helvetica-Bold", fontSize=20,
            textColor=BRANCO, alignment=TA_CENTER, leading=24
        ),
        "card_label": ParagraphStyle(
            "card_label", fontName="Helvetica", fontSize=8,
            textColor=AZUL_SUB, alignment=TA_CENTER, leading=12
        ),
    }


def _estilo_tabela_principal():
    return TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_FORTE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BRANCO),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("TOPPADDING",    (0, 0), (-1, 0),  10),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  10),
        ("LEFTPADDING",   (0, 0), (-1, 0),  10),
        ("RIGHTPADDING",  (0, 0), (-1, 0),  10),
        # Corpo linhas pares
        ("BACKGROUND",    (0, 1), (-1, -1), BRANCO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TOPPADDING",    (0, 1), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 9),
        ("LEFTPADDING",   (0, 1), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 1), (-1, -1), 10),
        ("TEXTCOLOR",     (0, 1), (-1, -1), AZUL_ESCURO),
        # Bordas suaves
        ("LINEBELOW",     (0, 0), (-1, -1), 0.5, CINZA_LINHA),
        ("LINEABOVE",     (0, 0), (-1, 0),  1,   AZUL_FORTE),
        ("BOX",           (0, 0), (-1, -1), 0.5, CINZA_LINHA),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS",[4, 4, 4, 4]),
    ])


def _cabecalho_doc(elementos, titulo_rel, subtitulo, agora, st):
    """Gera o cabecalho visual do documento."""
    # Fundo azul escuro no cabecalho via tabela
    dados_header = [[
        Paragraph("Orbitask", ParagraphStyle(
            "hd", fontName="Helvetica-Bold", fontSize=22,
            textColor=BRANCO, leading=26
        )),
        Paragraph(
            f"{titulo_rel}<br/><font size='10' color='#2a5a8a'>{subtitulo}</font>",
            ParagraphStyle("hd2", fontName="Helvetica-Bold", fontSize=13,
                           textColor=BRANCO, leading=18, alignment=TA_RIGHT)
        ),
    ]]
    t_header = Table(dados_header, colWidths=[9*cm, 8.5*cm])
    t_header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_ESCURO),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW",     (0, 0), (-1, -1), 2, AZUL_FORTE),
    ]))
    elementos.append(t_header)
    elementos.append(Spacer(1, 6))

    # Data e filtros
    elementos.append(Paragraph(
        f"Gerado em: <b>{agora}</b>",
        ParagraphStyle("meta", fontName="Helvetica", fontSize=9,
                       textColor=AZUL_SUB, leading=14)
    ))
    elementos.append(Spacer(1, 16))


def _cards_resumo(elementos, dados_cards):
    """Gera uma linha de cards de resumo estilo dashboard."""
    celulas = []
    for label, valor, cor_hex in dados_cards:
        cor = colors.HexColor(cor_hex)
        conteudo = [
            [Paragraph(str(valor), ParagraphStyle(
                "cv", fontName="Helvetica-Bold", fontSize=18,
                textColor=cor, alignment=TA_CENTER, leading=22
            ))],
            [Paragraph(label, ParagraphStyle(
                "cl", fontName="Helvetica", fontSize=8,
                textColor=colors.HexColor("#2a5a8a"),
                alignment=TA_CENTER, leading=12
            ))],
        ]
        t_card = Table(conteudo, colWidths=[4*cm])
        t_card.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f0f6ff")),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("LINEABOVE",     (0, 0), (-1, 0),  3, cor),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#dce8f5")),
            ("ROUNDEDCORNERS",[3, 3, 3, 3]),
        ]))
        celulas.append(t_card)

    largura = 17.5 / len(celulas)
    linha = Table([celulas], colWidths=[largura*cm] * len(celulas))
    linha.setStyle(TableStyle([
        ("ALIGN",   (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",  (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(linha)
    elementos.append(Spacer(1, 20))


def _secao_titulo(elementos, texto):
    elementos.append(Paragraph(texto.upper(), ParagraphStyle(
        "sec", fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.HexColor("#1a6fd4"),
        spaceBefore=16, spaceAfter=8, leading=14, letterSpacing=0.5
    )))
    elementos.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor("#dce8f5"), spaceAfter=8
    ))


def _rodape(elementos, agora):
    elementos.append(Spacer(1, 20))
    elementos.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor("#dce8f5"), spaceAfter=6
    ))
    elementos.append(Paragraph(
        f"Orbitask &nbsp;&nbsp;|&nbsp;&nbsp; Relatorio gerado em {agora} &nbsp;&nbsp;|&nbsp;&nbsp; Uso Interno",
        ParagraphStyle("rod", fontName="Helvetica", fontSize=8,
                       textColor=colors.HexColor("#2a5a8a"),
                       alignment=TA_CENTER, leading=12)
    ))


def gerar_relatorio_os(ordens, filtros, caminho_saida, empresa="Orbitask"):
    doc = SimpleDocTemplate(
        caminho_saida, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    elementos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    filtro_txt = STATUS_LABEL.get(filtros.get("status", ""), "Todos os status")
    _cabecalho_doc(elementos, "Relatorio de Ordens de Servico", filtro_txt, agora, None)

    # Cards de resumo
    total     = len(ordens)
    abertas   = sum(1 for o in ordens if o["status"] == "aberta")
    andamento = sum(1 for o in ordens if o["status"] == "em_andamento")
    concluidas= sum(1 for o in ordens if o["status"] == "concluida")
    canceladas= sum(1 for o in ordens if o["status"] == "cancelada")

    _secao_titulo(elementos, "Resumo Geral")
    _cards_resumo(elementos, [
        ("Total de OS",    total,      "#1a6fd4"),
        ("Abertas",        abertas,    "#4a9eff"),
        ("Em Andamento",   andamento,  "#f0a030"),
        ("Concluidas",     concluidas, "#2ab87a"),
        ("Canceladas",     canceladas, "#e05555"),
    ])

    # Tabela de OS
    _secao_titulo(elementos, "Listagem Detalhada")

    if not ordens:
        elementos.append(Paragraph(
            "Nenhuma ordem encontrada para os filtros selecionados.",
            ParagraphStyle("vaz", fontName="Helvetica-Oblique", fontSize=10,
                           textColor=colors.HexColor("#2a5a8a"), leading=14)
        ))
    else:
        cabecalho = ["#", "Titulo", "Cliente", "Tecnico", "Prazo", "Prioridade", "Status"]
        larguras  = [0.8*cm, 5.5*cm, 3.2*cm, 3.2*cm, 2*cm, 1.8*cm, 2*cm]

        dados = [cabecalho]
        for o in ordens:
            prazo = "—"
            if o.get("prazo"):
                try:
                    p = o["prazo"].split("-")
                    prazo = f"{p[2]}/{p[1]}/{p[0]}"
                except Exception:
                    pass
            dados.append([
                str(o["id"]),
                o["titulo"][:45] + ("..." if len(o["titulo"]) > 45 else ""),
                (o.get("cliente_nome") or "—")[:22],
                (o.get("tecnico_nome") or "—")[:22],
                prazo,
                PRIORIDADE_LABEL.get(o["prioridade"], o["prioridade"]),
                STATUS_LABEL.get(o["status"], o["status"]),
            ])

        tabela = Table(dados, colWidths=larguras, repeatRows=1)
        tabela.setStyle(_estilo_tabela_principal())
        elementos.append(tabela)

    _rodape(elementos, agora)
    doc.build(elementos)
    return caminho_saida


def gerar_relatorio_clientes(clientes, caminho_saida, empresa="Orbitask"):
    doc = SimpleDocTemplate(
        caminho_saida, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    elementos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    _cabecalho_doc(elementos, "Relatorio de Clientes",
                   f"Total: {len(clientes)} cliente{'s' if len(clientes) != 1 else ''}",
                   agora, None)

    _secao_titulo(elementos, "Resumo")
    _cards_resumo(elementos, [
        ("Total de Clientes", len(clientes), "#1a6fd4"),
        ("Com E-mail",  sum(1 for c in clientes if c.get("email")),  "#2ab87a"),
        ("Com Telefone",sum(1 for c in clientes if c.get("telefone")),"#f0a030"),
        ("Com Documento",sum(1 for c in clientes if c.get("documento")),"#8a6aff"),
    ])

    _secao_titulo(elementos, "Cadastro de Clientes")

    if not clientes:
        elementos.append(Paragraph(
            "Nenhum cliente cadastrado.",
            ParagraphStyle("vaz", fontName="Helvetica-Oblique", fontSize=10,
                           textColor=colors.HexColor("#2a5a8a"), leading=14)
        ))
    else:
        cabecalho = ["#", "Nome", "Telefone", "E-mail", "CPF / CNPJ", "Endereco"]
        larguras  = [0.8*cm, 4.5*cm, 3*cm, 4*cm, 3*cm, 4.2*cm]

        dados = [cabecalho]
        for c in clientes:
            dados.append([
                str(c["id"]),
                c["nome"][:38] + ("..." if len(c["nome"]) > 38 else ""),
                c.get("telefone") or "—",
                (c.get("email") or "—")[:28],
                c.get("documento") or "—",
                (c.get("endereco") or "—")[:30],
            ])

        tabela = Table(dados, colWidths=larguras, repeatRows=1)
        tabela.setStyle(_estilo_tabela_principal())
        elementos.append(tabela)

    _rodape(elementos, agora)
    doc.build(elementos)
    return caminho_saida