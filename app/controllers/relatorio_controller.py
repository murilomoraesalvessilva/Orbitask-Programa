# -*- coding: utf-8 -*-
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Paleta de cores do Orbitask
COR_PRIMARIA    = colors.HexColor("#7c6af7")
COR_ESCURA      = colors.HexColor("#1a1d27")
COR_TEXTO       = colors.HexColor("#1a1a2e")
COR_SUBTEXTO    = colors.HexColor("#6b7280")
COR_LINHA       = colors.HexColor("#e5e7eb")
COR_VERDE       = colors.HexColor("#10b981")
COR_AMARELO     = colors.HexColor("#f59e0b")
COR_VERMELHO    = colors.HexColor("#f87171")
COR_AZUL        = colors.HexColor("#3b82f6")
COR_HEADER_BG   = colors.HexColor("#f3f4f6")


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
    base = getSampleStyleSheet()
    estilos = {
        "titulo": ParagraphStyle(
            "titulo", fontSize=22, textColor=COR_PRIMARIA,
            fontName="Helvetica-Bold", spaceAfter=4
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", fontSize=11, textColor=COR_SUBTEXTO,
            fontName="Helvetica", spaceAfter=2
        ),
        "secao": ParagraphStyle(
            "secao", fontSize=13, textColor=COR_TEXTO,
            fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=8
        ),
        "normal": ParagraphStyle(
            "normal", fontSize=10, textColor=COR_TEXTO,
            fontName="Helvetica"
        ),
        "rodape": ParagraphStyle(
            "rodape", fontSize=8, textColor=COR_SUBTEXTO,
            fontName="Helvetica", alignment=TA_CENTER
        ),
    }
    return estilos


def _estilo_tabela():
    return TableStyle([
        # Header
        ("BACKGROUND",  (0, 0), (-1, 0),  COR_PRIMARIA),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING",    (0, 0), (-1, 0), 10),
        # Corpo
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 9),
        ("TOPPADDING",  (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_HEADER_BG]),
        ("GRID",        (0, 0), (-1, -1), 0.5, COR_LINHA),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ])


def gerar_relatorio_os(ordens: list, filtros: dict, caminho_saida: str, empresa: str = "Orbitask"):
    """Gera um PDF com o relatorio de ordens de servico."""
    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    st = _estilos()
    elementos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Cabecalho
    elementos.append(Paragraph(empresa, st["titulo"]))
    elementos.append(Paragraph("Relatorio de Ordens de Servico", st["subtitulo"]))
    elementos.append(Paragraph(f"Gerado em: {agora}", st["subtitulo"]))
    elementos.append(HRFlowable(width="100%", thickness=1, color=COR_PRIMARIA, spaceAfter=12))

    # Filtros aplicados
    if filtros:
        partes = []
        if filtros.get("status"):
            partes.append(f"Status: {STATUS_LABEL.get(filtros['status'], filtros['status'])}")
        if filtros.get("periodo"):
            partes.append(f"Periodo: {filtros['periodo']}")
        if partes:
            elementos.append(Paragraph("Filtros: " + "  |  ".join(partes), st["subtitulo"]))
            elementos.append(Spacer(1, 8))

    # Resumo
    total = len(ordens)
    abertas     = sum(1 for o in ordens if o["status"] == "aberta")
    andamento   = sum(1 for o in ordens if o["status"] == "em_andamento")
    concluidas  = sum(1 for o in ordens if o["status"] == "concluida")
    canceladas  = sum(1 for o in ordens if o["status"] == "cancelada")

    elementos.append(Paragraph("Resumo", st["secao"]))

    dados_resumo = [
        ["Total de OS", "Abertas", "Em Andamento", "Concluidas", "Canceladas"],
        [str(total), str(abertas), str(andamento), str(concluidas), str(canceladas)],
    ]
    tabela_resumo = Table(dados_resumo, colWidths=[3.4*cm]*5)
    tabela_resumo.setStyle(_estilo_tabela())
    elementos.append(tabela_resumo)
    elementos.append(Spacer(1, 16))

    # Listagem
    elementos.append(Paragraph("Listagem Detalhada", st["secao"]))

    if not ordens:
        elementos.append(Paragraph("Nenhuma ordem encontrada para os filtros selecionados.", st["normal"]))
    else:
        cabecalho = ["#", "Titulo", "Cliente", "Tecnico", "Prioridade", "Status", "Data"]
        larguras = [1*cm, 5*cm, 3.5*cm, 3.5*cm, 2*cm, 2.5*cm, 2.5*cm]

        dados = [cabecalho]
        for o in ordens:
            data = o.get("criado_em", "")[:10] if o.get("criado_em") else "-"
            dados.append([
                str(o["id"]),
                o["titulo"][:40] + ("..." if len(o["titulo"]) > 40 else ""),
                (o.get("cliente_nome") or "-")[:22],
                (o.get("tecnico_nome") or "-")[:22],
                PRIORIDADE_LABEL.get(o["prioridade"], o["prioridade"]),
                STATUS_LABEL.get(o["status"], o["status"]),
                data,
            ])

        tabela = Table(dados, colWidths=larguras, repeatRows=1)
        tabela.setStyle(_estilo_tabela())
        elementos.append(tabela)

    # Rodape
    elementos.append(Spacer(1, 24))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=COR_LINHA))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph(f"Orbitask — Relatorio gerado em {agora}", st["rodape"]))

    doc.build(elementos)
    return caminho_saida


def gerar_relatorio_clientes(clientes: list, caminho_saida: str, empresa: str = "Orbitask"):
    """Gera um PDF com o relatorio de clientes."""
    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    st = _estilos()
    elementos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    elementos.append(Paragraph(empresa, st["titulo"]))
    elementos.append(Paragraph("Relatorio de Clientes", st["subtitulo"]))
    elementos.append(Paragraph(f"Gerado em: {agora}", st["subtitulo"]))
    elementos.append(HRFlowable(width="100%", thickness=1, color=COR_PRIMARIA, spaceAfter=12))
    elementos.append(Paragraph(f"Total de clientes: {len(clientes)}", st["normal"]))
    elementos.append(Spacer(1, 12))

    if not clientes:
        elementos.append(Paragraph("Nenhum cliente cadastrado.", st["normal"]))
    else:
        cabecalho = ["#", "Nome", "Telefone", "E-mail", "Documento"]
        larguras = [1*cm, 5*cm, 3.5*cm, 5*cm, 3.5*cm]

        dados = [cabecalho]
        for c in clientes:
            dados.append([
                str(c["id"]),
                c["nome"][:35] + ("..." if len(c["nome"]) > 35 else ""),
                c.get("telefone") or "-",
                (c.get("email") or "-")[:30],
                c.get("documento") or "-",
            ])

        tabela = Table(dados, colWidths=larguras, repeatRows=1)
        tabela.setStyle(_estilo_tabela())
        elementos.append(tabela)

    elementos.append(Spacer(1, 24))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=COR_LINHA))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph(f"Orbitask — Relatorio gerado em {agora}", st["rodape"]))

    doc.build(elementos)
    return caminho_saida