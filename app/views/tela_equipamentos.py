# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from app.models.equipamento import listar_equipamentos, deletar_equipamento
from app.views.dialogo_equipamento import DialogoEquipamento


class TelaEquipamentos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_interface()
        self._carregar_equipamentos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        header = QWidget()
        lh = QHBoxLayout(header)
        lh.setContentsMargins(0, 0, 0, 0)
        lh.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(2)
        titulo = QLabel("Equipamentos")
        titulo.setObjectName("titulo_secao")
        col.addWidget(titulo)
        self.label_contador = QLabel("Carregando...")
        self.label_contador.setObjectName("label_contador")
        col.addWidget(self.label_contador)
        lh.addLayout(col)

        lh.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar por nome, marca ou tipo...")
        self.campo_busca.setFixedWidth(240)
        self.campo_busca.setFixedHeight(38)
        self.campo_busca.textChanged.connect(self._filtrar)
        lh.addWidget(self.campo_busca)

        btn_novo = QPushButton("+ Novo Equipamento")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.setFixedHeight(38)
        btn_novo.clicked.connect(self._novo)
        lh.addWidget(btn_novo)

        layout.addWidget(header)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["#", "NOME", "TIPO", "MARCA / MODELO", "N. SERIE", "OS VINCULADA", "ACOES"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 50)
        self.tabela.setColumnWidth(2, 110)
        self.tabela.setColumnWidth(3, 160)
        self.tabela.setColumnWidth(4, 120)
        self.tabela.setColumnWidth(6, 160)
        layout.addWidget(self.tabela)

    def _carregar_equipamentos(self, filtro=""):
        self.equipamentos = listar_equipamentos()
        if filtro:
            f = filtro.lower()
            self.equipamentos = [e for e in self.equipamentos if
                f in e["nome"].lower() or
                f in (e.get("marca") or "").lower() or
                f in (e.get("tipo") or "").lower() or
                f in (e.get("numero_serie") or "").lower()]

        self.tabela.setRowCount(0)
        for e in self.equipamentos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setRowHeight(row, 50)

            marca_modelo = " / ".join(filter(None, [e.get("marca"), e.get("modelo")])) or "—"
            os_titulo = f"#{e['ordem_id']} {e.get('ordem_titulo','')[:30]}" if e.get("ordem_id") else "—"

            self.tabela.setItem(row, 0, self._cel(str(e["id"]), center=True))
            self.tabela.setItem(row, 1, self._cel(e["nome"]))
            self.tabela.setItem(row, 2, self._cel(e.get("tipo") or "—"))
            self.tabela.setItem(row, 3, self._cel(marca_modelo))
            self.tabela.setItem(row, 4, self._cel(e.get("numero_serie") or "—"))
            self.tabela.setItem(row, 5, self._cel(os_titulo))
            self.tabela.setCellWidget(row, 6, self._acoes(e))

        total = len(self.equipamentos)
        self.label_contador.setText(f"{total} equipamento{'s' if total != 1 else ''} cadastrado{'s' if total != 1 else ''}")

    def _cel(self, texto, center=False):
        item = QTableWidgetItem(texto)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _acoes(self, e):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(8, 6, 8, 6)
        l.setSpacing(8)
        btn_e = QPushButton("Editar")
        btn_e.setObjectName("btn_editar")
        btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_e.clicked.connect(lambda _, eq=e: self._editar(eq))
        l.addWidget(btn_e)
        btn_x = QPushButton("Excluir")
        btn_x.setObjectName("btn_excluir")
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.clicked.connect(lambda _, eq=e: self._excluir(eq))
        l.addWidget(btn_x)
        l.addStretch()
        return w

    def _filtrar(self, texto):
        self._carregar_equipamentos(filtro=texto)

    def _novo(self):
        if DialogoEquipamento(parent=self).exec():
            self._carregar_equipamentos(filtro=self.campo_busca.text())

    def _editar(self, e):
        if DialogoEquipamento(parent=self, equipamento=e).exec():
            self._carregar_equipamentos(filtro=self.campo_busca.text())

    def _excluir(self, e):
        r = QMessageBox.question(self, "Confirmar exclusao",
            f"Excluir o equipamento '{e['nome']}'?\n\nEssa acao nao pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            deletar_equipamento(e["id"])
            self._carregar_equipamentos(filtro=self.campo_busca.text())