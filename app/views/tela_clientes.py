# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from app.models.cliente import listar_clientes, deletar_cliente
from app.views.dialogo_cliente import DialogoCliente


class TelaClientes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._carregar_clientes()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header da tela
        header = QFrame()
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(0, 0, 0, 0)

        label_titulo = QLabel("Clientes")
        label_titulo.setObjectName("titulo_secao")
        layout_header.addWidget(label_titulo)

        layout_header.addStretch()

        # Campo de busca
        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar cliente...")
        self.campo_busca.setObjectName("campo_busca")
        self.campo_busca.setFixedWidth(240)
        self.campo_busca.textChanged.connect(self._filtrar_clientes)
        layout_header.addWidget(self.campo_busca)

        # Botao novo cliente
        btn_novo = QPushButton("+ Novo Cliente")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._abrir_dialogo_novo)
        layout_header.addWidget(btn_novo)

        layout.addWidget(header)

        # Contador
        self.label_contador = QLabel("0 clientes cadastrados")
        self.label_contador.setObjectName("label_contador")
        layout.addWidget(self.label_contador)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setObjectName("tabela")
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "Telefone", "E-mail", "Documento", "Acoes"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 50)   # ID
        self.tabela.setColumnWidth(2, 140)  # Telefone
        self.tabela.setColumnWidth(4, 130)  # Documento
        self.tabela.setColumnWidth(5, 160)  # Acoes

        layout.addWidget(self.tabela)

    def _carregar_clientes(self, filtro: str = ""):
        self.clientes = listar_clientes()

        if filtro:
            filtro_lower = filtro.lower()
            self.clientes = [
                c for c in self.clientes
                if filtro_lower in c["nome"].lower()
                or filtro_lower in (c["email"] or "").lower()
                or filtro_lower in (c["telefone"] or "").lower()
            ]

        self.tabela.setRowCount(0)

        for cliente in self.clientes:
            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)
            self.tabela.setRowHeight(linha, 48)

            self.tabela.setItem(linha, 0, self._celula(str(cliente["id"]), centralizar=True))
            self.tabela.setItem(linha, 1, self._celula(cliente["nome"]))
            self.tabela.setItem(linha, 2, self._celula(cliente["telefone"] or "-"))
            self.tabela.setItem(linha, 3, self._celula(cliente["email"] or "-"))
            self.tabela.setItem(linha, 4, self._celula(cliente["documento"] or "-"))

            # Celula de acoes
            widget_acoes = QWidget()
            layout_acoes = QHBoxLayout(widget_acoes)
            layout_acoes.setContentsMargins(8, 4, 8, 4)
            layout_acoes.setSpacing(8)

            btn_editar = QPushButton("Editar")
            btn_editar.setObjectName("btn_editar")
            btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_editar.clicked.connect(lambda _, c=cliente: self._abrir_dialogo_edicao(c))
            layout_acoes.addWidget(btn_editar)

            btn_excluir = QPushButton("Excluir")
            btn_excluir.setObjectName("btn_excluir")
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda _, c=cliente: self._confirmar_exclusao(c))
            layout_acoes.addWidget(btn_excluir)

            self.tabela.setCellWidget(linha, 5, widget_acoes)

        total = len(self.clientes)
        self.label_contador.setText(f"{total} cliente{'s' if total != 1 else ''} cadastrado{'s' if total != 1 else ''}")

    def _celula(self, texto: str, centralizar: bool = False):
        item = QTableWidgetItem(texto)
        if centralizar:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _filtrar_clientes(self, texto: str):
        self._carregar_clientes(filtro=texto)

    def _abrir_dialogo_novo(self):
        dialogo = DialogoCliente(parent=self)
        if dialogo.exec():
            self._carregar_clientes(filtro=self.campo_busca.text())

    def _abrir_dialogo_edicao(self, cliente: dict):
        dialogo = DialogoCliente(parent=self, cliente=cliente)
        if dialogo.exec():
            self._carregar_clientes(filtro=self.campo_busca.text())

    def _confirmar_exclusao(self, cliente: dict):
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f"Deseja excluir o cliente '{cliente['nome']}'?\n\nEssa acao nao pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            deletar_cliente(cliente["id"])
            self._carregar_clientes(filtro=self.campo_busca.text())

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
            QPushButton#btn_primario {
                background-color: #7c6af7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btn_primario:hover {
                background-color: #6a58e0;
            }
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
            QTableWidget#tabela::item {
                padding: 8px;
                border: none;
            }
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
            QPushButton#btn_editar:hover {
                background-color: #7c6af7;
                color: white;
            }
            QPushButton#btn_excluir {
                background-color: #2d1f1f;
                color: #f87171;
                border: 1px solid #f87171;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton#btn_excluir:hover {
                background-color: #f87171;
                color: white;
            }
        """