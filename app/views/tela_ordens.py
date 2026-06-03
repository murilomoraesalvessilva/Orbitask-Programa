# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from app.models.ordem_servico import listar_ordens, deletar_ordem
from app.views.dialogo_ordem import DialogoOrdem


# Mapeamento de status para exibicao e cor
STATUS_CONFIG = {
    "aberta":       ("Aberta",       "#7c6af7", "#2d2b55"),
    "em_andamento": ("Em Andamento", "#f59e0b", "#332b1a"),
    "concluida":    ("Concluida",    "#10b981", "#1a2e28"),
    "cancelada":    ("Cancelada",    "#f87171", "#2d1f1f"),
}

PRIORIDADE_CONFIG = {
    "baixa":   ("Baixa",   "#6b7280"),
    "normal":  ("Normal",  "#3b82f6"),
    "alta":    ("Alta",    "#f59e0b"),
    "urgente": ("Urgente", "#f87171"),
}


class TelaOrdens(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._carregar_ordens()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.setSpacing(12)

        label_titulo = QLabel("Ordens de Servico")
        label_titulo.setObjectName("titulo_secao")
        layout_header.addWidget(label_titulo)

        layout_header.addStretch()

        # Busca
        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar ordem...")
        self.campo_busca.setObjectName("campo_busca")
        self.campo_busca.setFixedWidth(200)
        self.campo_busca.textChanged.connect(self._aplicar_filtros)
        layout_header.addWidget(self.campo_busca)

        # Filtro de status
        self.combo_filtro = QComboBox()
        self.combo_filtro.setObjectName("combo_filtro")
        self.combo_filtro.addItem("Todos os status", userData=None)
        self.combo_filtro.addItem("Aberta",       userData="aberta")
        self.combo_filtro.addItem("Em Andamento", userData="em_andamento")
        self.combo_filtro.addItem("Concluida",    userData="concluida")
        self.combo_filtro.addItem("Cancelada",    userData="cancelada")
        self.combo_filtro.currentIndexChanged.connect(self._aplicar_filtros)
        layout_header.addWidget(self.combo_filtro)

        # Botao nova OS
        btn_novo = QPushButton("+ Nova Ordem")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._abrir_dialogo_novo)
        layout_header.addWidget(btn_novo)

        layout.addWidget(header)

        # Contador
        self.label_contador = QLabel("0 ordens encontradas")
        self.label_contador.setObjectName("label_contador")
        layout.addWidget(self.label_contador)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setObjectName("tabela")
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Titulo", "Cliente", "Tecnico", "Prioridade", "Status", "Acoes"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 50)   # ID
        self.tabela.setColumnWidth(3, 140)  # Tecnico
        self.tabela.setColumnWidth(4, 90)   # Prioridade
        self.tabela.setColumnWidth(5, 120)  # Status
        self.tabela.setColumnWidth(6, 170)  # Acoes

        layout.addWidget(self.tabela)

    def _carregar_ordens(self, busca: str = "", filtro_status: str = None):
        self.ordens = listar_ordens(filtro_status=filtro_status)

        if busca:
            busca_lower = busca.lower()
            self.ordens = [
                o for o in self.ordens
                if busca_lower in o["titulo"].lower()
                or busca_lower in (o["cliente_nome"] or "").lower()
                or busca_lower in (o["tecnico_nome"] or "").lower()
            ]

        self.tabela.setRowCount(0)

        for ordem in self.ordens:
            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)
            self.tabela.setRowHeight(linha, 52)

            self.tabela.setItem(linha, 0, self._celula(str(ordem["id"]), centralizar=True))
            self.tabela.setItem(linha, 1, self._celula(ordem["titulo"]))
            self.tabela.setItem(linha, 2, self._celula(ordem["cliente_nome"] or "-"))
            self.tabela.setItem(linha, 3, self._celula(ordem["tecnico_nome"] or "-"))

            # Badge de prioridade
            self.tabela.setCellWidget(linha, 4, self._badge_prioridade(ordem["prioridade"]))

            # Badge de status
            self.tabela.setCellWidget(linha, 5, self._badge_status(ordem["status"]))

            # Acoes
            widget_acoes = QWidget()
            layout_acoes = QHBoxLayout(widget_acoes)
            layout_acoes.setContentsMargins(8, 6, 8, 6)
            layout_acoes.setSpacing(8)

            btn_editar = QPushButton("Editar")
            btn_editar.setObjectName("btn_editar")
            btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_editar.clicked.connect(lambda _, o=ordem: self._abrir_dialogo_edicao(o))
            layout_acoes.addWidget(btn_editar)

            btn_excluir = QPushButton("Excluir")
            btn_excluir.setObjectName("btn_excluir")
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda _, o=ordem: self._confirmar_exclusao(o))
            layout_acoes.addWidget(btn_excluir)

            self.tabela.setCellWidget(linha, 6, widget_acoes)

        total = len(self.ordens)
        self.label_contador.setText(f"{total} ordem{'s' if total != 1 else ''} encontrada{'s' if total != 1 else ''}")

    def _celula(self, texto: str, centralizar: bool = False):
        item = QTableWidgetItem(texto)
        if centralizar:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _badge_status(self, status: str):
        texto, cor_texto, cor_fundo = STATUS_CONFIG.get(status, ("Desconhecido", "#fff", "#333"))
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        label = QLabel(texto)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            background-color: {cor_fundo};
            color: {cor_texto};
            border: 1px solid {cor_texto};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        layout.addWidget(label)
        return widget

    def _badge_prioridade(self, prioridade: str):
        texto, cor = PRIORIDADE_CONFIG.get(prioridade, ("Normal", "#3b82f6"))
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        label = QLabel(texto)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            color: {cor};
            font-size: 12px;
            font-weight: bold;
        """)
        layout.addWidget(label)
        return widget

    def _aplicar_filtros(self):
        busca = self.campo_busca.text()
        filtro_status = self.combo_filtro.currentData()
        self._carregar_ordens(busca=busca, filtro_status=filtro_status)

    def _abrir_dialogo_novo(self):
        dialogo = DialogoOrdem(parent=self)
        if dialogo.exec():
            self._aplicar_filtros()

    def _abrir_dialogo_edicao(self, ordem: dict):
        dialogo = DialogoOrdem(parent=self, ordem=ordem)
        if dialogo.exec():
            self._aplicar_filtros()

    def _confirmar_exclusao(self, ordem: dict):
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f"Deseja excluir a ordem '{ordem['titulo']}'?\n\nEssa acao nao pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            deletar_ordem(ordem["id"])
            self._aplicar_filtros()

    def _estilos(self):
        return """
            QLabel#titulo_secao {
                font-size: 20px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#label_contador {
                font-size: 12px;
                color: #6b7280;
            }
            QLineEdit#campo_busca {
                background-color: #1a1d27;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QLineEdit#campo_busca:focus {
                border: 1px solid #7c6af7;
            }
            QComboBox#combo_filtro {
                background-color: #1a1d27;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
                min-width: 150px;
            }
            QComboBox#combo_filtro::drop-down { border: none; }
            QComboBox#combo_filtro QAbstractItemView {
                background-color: #252836;
                color: #e0e0e0;
                selection-background-color: #7c6af7;
            }
            QPushButton#btn_primario {
                background-color: #7c6af7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btn_primario:hover { background-color: #6a58e0; }
            QTableWidget#tabela {
                background-color: #1a1d27;
                border: 1px solid #2e3347;
                border-radius: 10px;
                gridline-color: transparent;
                font-size: 13px;
                color: #e0e0e0;
                alternate-background-color: #1f2233;
                selection-background-color: #2d2b55;
            }
            QTableWidget#tabela::item { padding: 8px; border: none; }
            QHeaderView::section {
                background-color: #252836;
                color: #9ca3af;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid #2e3347;
            }
            QPushButton#btn_editar {
                background-color: #2d2b55;
                color: #7c6af7;
                border: 1px solid #7c6af7;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton#btn_editar:hover { background-color: #7c6af7; color: white; }
            QPushButton#btn_excluir {
                background-color: #2d1f1f;
                color: #f87171;
                border: 1px solid #f87171;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton#btn_excluir:hover { background-color: #f87171; color: white; }
        """