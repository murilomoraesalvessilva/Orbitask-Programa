# -*- coding: utf-8 -*-
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QFileDialog,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from app.models.ordem_servico import listar_ordens
from app.models.cliente import listar_clientes
from app.controllers.relatorio_controller import gerar_relatorio_os, gerar_relatorio_clientes


class TelaRelatorios(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Titulo
        label_titulo = QLabel("Relatorios")
        label_titulo.setObjectName("titulo_secao")
        layout.addWidget(label_titulo)

        label_sub = QLabel("Gere e exporte relatorios em PDF diretamente do sistema.")
        label_sub.setObjectName("label_sub")
        layout.addWidget(label_sub)

        # Grid de cards de relatorio
        grid = QHBoxLayout()
        grid.setSpacing(20)

        grid.addWidget(self._card_relatorio(
            titulo="Ordens de Servico",
            descricao="Lista completa das OS com status, prioridade, cliente e tecnico responsavel.",
            tipo="os"
        ))

        grid.addWidget(self._card_relatorio(
            titulo="Clientes",
            descricao="Cadastro completo de todos os clientes com contatos e documentos.",
            tipo="clientes"
        ))

        layout.addLayout(grid)
        layout.addStretch()

    def _card_relatorio(self, titulo: str, descricao: str, tipo: str):
        card = QFrame()
        card.setObjectName("card_relatorio")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("card_titulo")
        layout.addWidget(label_titulo)

        label_desc = QLabel(descricao)
        label_desc.setObjectName("card_desc")
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)

        layout.addSpacing(8)

        # Filtro de status (apenas para OS)
        if tipo == "os":
            label_filtro = QLabel("Filtrar por status:")
            label_filtro.setObjectName("label_filtro")
            layout.addWidget(label_filtro)

            combo = QComboBox()
            combo.setObjectName("combo")
            combo.addItem("Todos os status", userData=None)
            combo.addItem("Aberta",          userData="aberta")
            combo.addItem("Em Andamento",    userData="em_andamento")
            combo.addItem("Concluida",       userData="concluida")
            combo.addItem("Cancelada",       userData="cancelada")
            layout.addWidget(combo)
            self.combo_status_os = combo

        layout.addSpacing(4)

        btn = QPushButton("Exportar PDF")
        btn.setObjectName("btn_exportar")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda _, t=tipo: self._exportar(t))
        layout.addWidget(btn)

        return card

    def _exportar(self, tipo: str):
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")

        if tipo == "os":
            nome_sugerido = f"relatorio_os_{agora}.pdf"
        else:
            nome_sugerido = f"relatorio_clientes_{agora}.pdf"

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio PDF",
            os.path.join(os.path.expanduser("~"), "Desktop", nome_sugerido),
            "PDF (*.pdf)"
        )

        if not caminho:
            return

        try:
            if tipo == "os":
                filtro_status = self.combo_status_os.currentData()
                ordens = listar_ordens(filtro_status=filtro_status)
                filtros = {}
                if filtro_status:
                    filtros["status"] = filtro_status
                gerar_relatorio_os(ordens, filtros, caminho)

            elif tipo == "clientes":
                clientes = listar_clientes()
                gerar_relatorio_clientes(clientes, caminho)

            QMessageBox.information(
                self,
                "Relatorio gerado!",
                f"PDF salvo com sucesso em:\n{caminho}"
            )

            # Abre o arquivo automaticamente
            os.startfile(caminho)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao gerar PDF",
                f"Ocorreu um erro ao gerar o relatorio:\n{str(e)}"
            )

    def _estilos(self):
        return """
            QLabel#titulo_secao {
                font-size: 20px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#label_sub {
                font-size: 13px;
                color: #6b7280;
            }
            QFrame#card_relatorio {
                background-color: #1a1d27;
                border: 1px solid #2e3347;
                border-radius: 12px;
                min-height: 240px;
            }
            QLabel#card_titulo {
                font-size: 16px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#card_desc {
                font-size: 12px;
                color: #9ca3af;
                line-height: 1.5;
            }
            QLabel#label_filtro {
                font-size: 12px;
                color: #9ca3af;
                font-weight: bold;
            }
            QComboBox#combo {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox#combo::drop-down { border: none; }
            QComboBox#combo QAbstractItemView {
                background-color: #252836;
                color: #e0e0e0;
                selection-background-color: #7c6af7;
            }
            QPushButton#btn_exportar {
                background-color: #7c6af7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btn_exportar:hover { background-color: #6a58e0; }
        """