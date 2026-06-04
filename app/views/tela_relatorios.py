# -*- coding: utf-8 -*-
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QFileDialog,
    QMessageBox, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt
from app.models.ordem_servico import listar_ordens
from app.models.cliente import listar_clientes
from app.controllers.relatorio_controller import gerar_relatorio_os, gerar_relatorio_clientes


class TelaRelatorios(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_interface()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header
        col = QVBoxLayout()
        col.setSpacing(4)
        titulo = QLabel("Relatorios")
        titulo.setObjectName("titulo_secao")
        col.addWidget(titulo)
        sub = QLabel("Gere e exporte relatorios profissionais em PDF com um clique.")
        sub.setObjectName("label_sub")
        col.addWidget(sub)
        layout.addLayout(col)

        # Linha separadora
        sep = QFrame()
        sep.setObjectName("header_line")
        layout.addWidget(sep)

        layout.addSpacing(8)

        # Grid de cards
        grid = QHBoxLayout()
        grid.setSpacing(20)
        grid.addWidget(self._card_relatorio(
            "Ordens de Servico",
            "Lista completa de OS com status, prioridade, cliente e tecnico responsavel. Inclui resumo por status no topo do documento.",
            tipo="os"
        ))
        grid.addWidget(self._card_relatorio(
            "Clientes",
            "Cadastro completo de todos os clientes com dados de contato e documentos. Ideal para consultas rapidas.",
            tipo="clientes"
        ))
        layout.addLayout(grid)
        layout.addStretch()

    def _card_relatorio(self, titulo, descricao, tipo):
        card = QFrame()
        card.setObjectName("card_resumo")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(220)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        # Indicador topo
        topo = QHBoxLayout()
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("background-color:#4a9eff; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
        topo.addWidget(dot)
        lbl_tipo = QLabel("PDF")
        lbl_tipo.setStyleSheet("font-size:10px; color:#1a4a7a; font-weight:700; letter-spacing:1px;")
        topo.addWidget(lbl_tipo)
        topo.addStretch()
        layout.addLayout(topo)

        lt = QLabel(titulo)
        lt.setStyleSheet("font-size:17px; font-weight:700; color:#ffffff;")
        layout.addWidget(lt)

        ld = QLabel(descricao)
        ld.setStyleSheet("font-size:12px; color:#2a5a8a; line-height:1.5;")
        ld.setWordWrap(True)
        layout.addWidget(ld)

        layout.addStretch()

        # Filtro apenas para OS
        if tipo == "os":
            lf = QLabel("FILTRAR POR STATUS")
            lf.setObjectName("label_campo")
            layout.addWidget(lf)
            self.combo_status_os = QComboBox()
            self.combo_status_os.setFixedHeight(36)
            self.combo_status_os.addItem("Todos os status", userData=None)
            self.combo_status_os.addItem("Aberta",          userData="aberta")
            self.combo_status_os.addItem("Em Andamento",    userData="em_andamento")
            self.combo_status_os.addItem("Concluida",       userData="concluida")
            self.combo_status_os.addItem("Cancelada",       userData="cancelada")
            layout.addWidget(self.combo_status_os)

        btn = QPushButton("Exportar PDF")
        btn.setObjectName("btn_primario")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda _, t=tipo: self._exportar(t))
        layout.addWidget(btn)

        return card

    def _exportar(self, tipo):
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome = f"relatorio_{'os' if tipo == 'os' else 'clientes'}_{agora}.pdf"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatorio PDF",
            os.path.join(os.path.expanduser("~"), "Desktop", nome),
            "PDF (*.pdf)"
        )
        if not caminho:
            return

        try:
            if tipo == "os":
                filtro = self.combo_status_os.currentData()
                ordens = listar_ordens(filtro_status=filtro)
                filtros = {"status": filtro} if filtro else {}
                gerar_relatorio_os(ordens, filtros, caminho)
            else:
                gerar_relatorio_clientes(listar_clientes(), caminho)

            QMessageBox.information(self, "Relatorio gerado!", f"PDF salvo com sucesso em:\n{caminho}")
            os.startfile(caminho)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao gerar PDF", f"Ocorreu um erro:\n{str(e)}")