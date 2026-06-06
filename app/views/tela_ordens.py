# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView, QComboBox
)
from PyQt6.QtCore import Qt, QDate
from app.models.ordem_servico import listar_ordens, deletar_ordem
from app.views.dialogo_ordem import DialogoOrdem

STATUS_CONFIG = {
    "aberta":       ("Aberta",       "#4a9eff", "#001a3a"),
    "em_andamento": ("Em Andamento", "#f0a030", "#2a1a00"),
    "concluida":    ("Concluida",    "#2ab87a", "#001a10"),
    "cancelada":    ("Cancelada",    "#e05555", "#2a0808"),
}
PRIORIDADE_CONFIG = {
    "baixa":   ("Baixa",   "#3a6a9a"),
    "normal":  ("Normal",  "#4a9eff"),
    "alta":    ("Alta",    "#f0a030"),
    "urgente": ("Urgente", "#e05555"),
}


class TelaOrdens(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_interface()
        self._carregar_ordens()

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
        titulo = QLabel("Ordens de Servico")
        titulo.setObjectName("titulo_secao")
        col.addWidget(titulo)
        self.label_contador = QLabel("Carregando...")
        self.label_contador.setObjectName("label_contador")
        col.addWidget(self.label_contador)
        lh.addLayout(col)

        lh.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar por titulo, cliente ou tecnico...")
        self.campo_busca.setFixedWidth(240)
        self.campo_busca.setFixedHeight(38)
        self.campo_busca.textChanged.connect(self._aplicar_filtros)
        lh.addWidget(self.campo_busca)

        self.combo_filtro = QComboBox()
        self.combo_filtro.setFixedHeight(38)
        self.combo_filtro.setFixedWidth(160)
        self.combo_filtro.addItem("Todos os status", userData=None)
        self.combo_filtro.addItem("Aberta",          userData="aberta")
        self.combo_filtro.addItem("Em Andamento",    userData="em_andamento")
        self.combo_filtro.addItem("Concluida",       userData="concluida")
        self.combo_filtro.addItem("Cancelada",       userData="cancelada")
        self.combo_filtro.currentIndexChanged.connect(self._aplicar_filtros)
        lh.addWidget(self.combo_filtro)

        btn_novo = QPushButton("+ Nova Ordem")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.setFixedHeight(38)
        btn_novo.clicked.connect(self._novo)
        lh.addWidget(btn_novo)

        layout.addWidget(header)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "#", "TITULO", "CLIENTE", "TECNICO", "PRAZO", "PRIORIDADE", "STATUS", "ACOES"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 50)
        self.tabela.setColumnWidth(3, 130)
        self.tabela.setColumnWidth(4, 100)
        self.tabela.setColumnWidth(5, 90)
        self.tabela.setColumnWidth(6, 130)
        self.tabela.setColumnWidth(7, 160)
        layout.addWidget(self.tabela)

    def _carregar_ordens(self, busca="", filtro_status=None):
        self.ordens = listar_ordens(filtro_status=filtro_status)
        if busca:
            b = busca.lower()
            self.ordens = [o for o in self.ordens if
                b in o["titulo"].lower() or
                b in (o.get("cliente_nome") or "").lower() or
                b in (o.get("tecnico_nome") or "").lower()]

        self.tabela.setRowCount(0)
        hoje = QDate.currentDate()

        for o in self.ordens:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setRowHeight(row, 50)

            self.tabela.setItem(row, 0, self._cel(str(o["id"]), center=True))
            self.tabela.setItem(row, 1, self._cel(o["titulo"]))
            self.tabela.setItem(row, 2, self._cel(o.get("cliente_nome") or "—"))
            self.tabela.setItem(row, 3, self._cel(o.get("tecnico_nome") or "—"))

            # Prazo com cor se vencido
            prazo = o.get("prazo")
            if prazo:
                try:
                    p = prazo.split("-")
                    data_q = QDate(int(p[0]), int(p[1]), int(p[2]))
                    texto_prazo = f"{p[2]}/{p[1]}/{p[0]}"
                    item_prazo = QTableWidgetItem(texto_prazo)
                    item_prazo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    from PyQt6.QtGui import QColor
                    if data_q < hoje and o["status"] not in ("concluida", "cancelada"):
                        item_prazo.setForeground(QColor("#e05555"))
                    else:
                        item_prazo.setForeground(QColor("#2a5a8a"))
                    self.tabela.setItem(row, 4, item_prazo)
                except Exception:
                    self.tabela.setItem(row, 4, self._cel("—", center=True))
            else:
                self.tabela.setItem(row, 4, self._cel("—", center=True))

            self.tabela.setCellWidget(row, 5, self._badge_prioridade(o["prioridade"]))
            self.tabela.setCellWidget(row, 6, self._badge_status(o["status"]))
            self.tabela.setCellWidget(row, 7, self._acoes(o))

        total = len(self.ordens)
        self.label_contador.setText(f"{total} ordem{'s' if total != 1 else ''} encontrada{'s' if total != 1 else ''}")

    def _cel(self, texto, center=False):
        item = QTableWidgetItem(texto)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _badge_status(self, status):
        texto, cor, fundo = STATUS_CONFIG.get(status, ("?", "#fff", "#111"))
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFixedWidth(108)
        lbl.setFixedHeight(24)
        lbl.setStyleSheet(f"background-color:{fundo}; color:{cor}; border:1px solid {cor}; border-radius:12px; font-size:11px; font-weight:700;")
        return lbl

    def _badge_prioridade(self, prioridade):
        texto, cor = PRIORIDADE_CONFIG.get(prioridade, ("Normal", "#4a9eff"))
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(6, 4, 6, 4)
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color:{cor}; font-size:12px; font-weight:600;")
        l.addWidget(lbl)
        return w

    def _acoes(self, ordem):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(8, 6, 8, 6)
        l.setSpacing(8)
        btn_e = QPushButton("Editar")
        btn_e.setObjectName("btn_editar")
        btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_e.clicked.connect(lambda _, o=ordem: self._editar(o))
        l.addWidget(btn_e)
        btn_x = QPushButton("Excluir")
        btn_x.setObjectName("btn_excluir")
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.clicked.connect(lambda _, o=ordem: self._excluir(o))
        l.addWidget(btn_x)
        l.addStretch()
        return w

    def _aplicar_filtros(self):
        self._carregar_ordens(busca=self.campo_busca.text(), filtro_status=self.combo_filtro.currentData())

    def _novo(self):
        if DialogoOrdem(parent=self).exec():
            self._aplicar_filtros()

    def _editar(self, ordem):
        if DialogoOrdem(parent=self, ordem=ordem).exec():
            self._aplicar_filtros()

    def _excluir(self, ordem):
        r = QMessageBox.question(self, "Confirmar exclusao",
            f"Excluir a ordem '{ordem['titulo']}'?\n\nEssa acao nao pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            deletar_ordem(ordem["id"])
            self._aplicar_filtros()