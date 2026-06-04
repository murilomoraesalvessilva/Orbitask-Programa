# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from app.models.cliente import listar_clientes, deletar_cliente
from app.views.dialogo_cliente import DialogoCliente


class TelaClientes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_interface()
        self._carregar_clientes()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QWidget()
        lh = QHBoxLayout(header)
        lh.setContentsMargins(0, 0, 0, 0)
        lh.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(2)
        titulo = QLabel("Clientes")
        titulo.setObjectName("titulo_secao")
        col.addWidget(titulo)
        self.label_contador = QLabel("Carregando...")
        self.label_contador.setObjectName("label_contador")
        col.addWidget(self.label_contador)
        lh.addLayout(col)

        lh.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar por nome, e-mail ou telefone...")
        self.campo_busca.setFixedWidth(260)
        self.campo_busca.setFixedHeight(38)
        self.campo_busca.textChanged.connect(self._filtrar)
        lh.addWidget(self.campo_busca)

        btn_novo = QPushButton("+ Novo Cliente")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.setFixedHeight(38)
        btn_novo.clicked.connect(self._novo)
        lh.addWidget(btn_novo)

        layout.addWidget(header)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["#", "NOME", "TELEFONE", "E-MAIL", "DOCUMENTO", "ACOES"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 50)
        self.tabela.setColumnWidth(2, 140)
        self.tabela.setColumnWidth(4, 130)
        self.tabela.setColumnWidth(5, 160)
        layout.addWidget(self.tabela)

    def _carregar_clientes(self, filtro=""):
        self.clientes = listar_clientes()
        if filtro:
            f = filtro.lower()
            self.clientes = [c for c in self.clientes if
                f in c["nome"].lower() or
                f in (c.get("email") or "").lower() or
                f in (c.get("telefone") or "").lower()]

        self.tabela.setRowCount(0)
        for c in self.clientes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setRowHeight(row, 48)
            self.tabela.setItem(row, 0, self._cel(str(c["id"]), center=True))
            self.tabela.setItem(row, 1, self._cel(c["nome"]))
            self.tabela.setItem(row, 2, self._cel(c.get("telefone") or "—"))
            self.tabela.setItem(row, 3, self._cel(c.get("email") or "—"))
            self.tabela.setItem(row, 4, self._cel(c.get("documento") or "—"))
            self.tabela.setCellWidget(row, 5, self._acoes(c))

        total = len(self.clientes)
        self.label_contador.setText(f"{total} cliente{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}")

    def _cel(self, texto, center=False):
        item = QTableWidgetItem(texto)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _acoes(self, cliente):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(8, 6, 8, 6)
        l.setSpacing(8)
        btn_e = QPushButton("Editar")
        btn_e.setObjectName("btn_editar")
        btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_e.clicked.connect(lambda _, c=cliente: self._editar(c))
        l.addWidget(btn_e)
        btn_x = QPushButton("Excluir")
        btn_x.setObjectName("btn_excluir")
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.clicked.connect(lambda _, c=cliente: self._excluir(c))
        l.addWidget(btn_x)
        l.addStretch()
        return w

    def _filtrar(self, texto):
        self._carregar_clientes(filtro=texto)

    def _novo(self):
        if DialogoCliente(parent=self).exec():
            self._carregar_clientes(filtro=self.campo_busca.text())

    def _editar(self, cliente):
        if DialogoCliente(parent=self, cliente=cliente).exec():
            self._carregar_clientes(filtro=self.campo_busca.text())

    def _excluir(self, cliente):
        r = QMessageBox.question(self, "Confirmar exclusao",
            f"Excluir o cliente '{cliente['nome']}'?\n\nEssa acao nao pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            deletar_cliente(cliente["id"])
            self._carregar_clientes(filtro=self.campo_busca.text())