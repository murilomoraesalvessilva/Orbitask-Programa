# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QAbstractItemView, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from app.models.financeiro import listar_financeiro, resumo_financeiro
from app.views.dialogo_financeiro import DialogoFinanceiro

STATUS_PAG = {
    "pendente":  ("Pendente",  "#f0a030", "#2a1a00"),
    "pago":      ("Pago",      "#2ab87a", "#001a10"),
    "cancelado": ("Cancelado", "#e05555", "#2a0808"),
}

def fmt_brl(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


class TelaFinanceiro(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_interface()
        self._carregar()

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
        titulo = QLabel("Financeiro")
        titulo.setObjectName("titulo_secao")
        col.addWidget(titulo)
        self.label_contador = QLabel("Carregando...")
        self.label_contador.setObjectName("label_contador")
        col.addWidget(self.label_contador)
        lh.addLayout(col)

        lh.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar OS ou cliente...")
        self.campo_busca.setFixedWidth(200)
        self.campo_busca.setFixedHeight(38)
        self.campo_busca.textChanged.connect(self._aplicar_filtros)
        lh.addWidget(self.campo_busca)

        self.combo_filtro = QComboBox()
        self.combo_filtro.setFixedHeight(38)
        self.combo_filtro.setFixedWidth(140)
        self.combo_filtro.addItem("Todos",     userData=None)
        self.combo_filtro.addItem("Pendente",  userData="pendente")
        self.combo_filtro.addItem("Pago",      userData="pago")
        self.combo_filtro.addItem("Cancelado", userData="cancelado")
        self.combo_filtro.currentIndexChanged.connect(self._aplicar_filtros)
        lh.addWidget(self.combo_filtro)

        layout.addWidget(header)

        # Cards resumo
        linha = QHBoxLayout()
        linha.setSpacing(12)
        self.card_total    = self._card("Receita Total",    "R$ 0,00", "#4a9eff")
        self.card_recebida = self._card("Receita Recebida", "R$ 0,00", "#2ab87a")
        self.card_pendente = self._card("A Receber",        "R$ 0,00", "#f0a030")
        self.card_pagas    = self._card("OS Pagas",         "0",       "#8a6aff")
        for c in [self.card_total, self.card_recebida, self.card_pendente, self.card_pagas]:
            linha.addWidget(c)
        layout.addLayout(linha)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "#", "TITULO", "CLIENTE", "SERVICO", "PECAS", "TOTAL", "PAGAMENTO"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 55)
        self.tabela.setColumnWidth(3, 120)
        self.tabela.setColumnWidth(4, 120)
        self.tabela.setColumnWidth(5, 130)
        self.tabela.setColumnWidth(6, 130)
        self.tabela.doubleClicked.connect(self._editar_selecionado)
        layout.addWidget(self.tabela)

        dica = QLabel("Dica: clique duplo em uma linha para editar os valores financeiros.")
        dica.setObjectName("label_dica")
        layout.addWidget(dica)

    def _card(self, titulo, valor, cor):
        card = QFrame()
        card.setObjectName("card_resumo")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(88)
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 14, 20, 14)
        l.setSpacing(5)

        topo = QHBoxLayout()
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color:{cor}; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
        topo.addWidget(dot)
        topo.addStretch()
        l.addLayout(topo)

        lv = QLabel(valor)
        lv.setStyleSheet(f"color:{cor}; font-size:20px; font-weight:700;")
        l.addWidget(lv)

        lt = QLabel(titulo.upper())
        lt.setObjectName("card_titulo")
        l.addWidget(lt)

        card._label_valor = lv
        return card

    def _carregar(self, busca="", filtro_pag=None):
        self.registros = listar_financeiro(filtro_pagamento=filtro_pag)
        if busca:
            b = busca.lower()
            self.registros = [r for r in self.registros if
                b in r["titulo"].lower() or
                b in (r.get("cliente_nome") or "").lower()]

        self.tabela.setRowCount(0)
        for r in self.registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setRowHeight(row, 50)
            self.tabela.setItem(row, 0, self._cel(str(r["id"]), center=True))
            self.tabela.setItem(row, 1, self._cel(r["titulo"]))
            self.tabela.setItem(row, 2, self._cel(r.get("cliente_nome") or "—"))
            self.tabela.setItem(row, 3, self._cel(fmt_brl(r.get("valor_servico") or 0)))
            self.tabela.setItem(row, 4, self._cel(fmt_brl(r.get("valor_pecas") or 0)))
            self.tabela.setItem(row, 5, self._cel(fmt_brl(r.get("valor_total") or 0)))
            self.tabela.setCellWidget(row, 6, self._badge_pag(r.get("status_pagamento", "pendente")))

        total = len(self.registros)
        self.label_contador.setText(f"{total} ordem{'s' if total != 1 else ''} encontrada{'s' if total != 1 else ''}")

        res = resumo_financeiro()
        self.card_total._label_valor.setText(fmt_brl(res.get("receita_total", 0)))
        self.card_recebida._label_valor.setText(fmt_brl(res.get("receita_recebida", 0)))
        self.card_pendente._label_valor.setText(fmt_brl(res.get("receita_pendente", 0)))
        self.card_pagas._label_valor.setText(str(res.get("os_pagas", 0)))

    def _cel(self, texto, center=False):
        item = QTableWidgetItem(texto)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _badge_pag(self, status):
        texto, cor, fundo = STATUS_PAG.get(status, ("?", "#fff", "#111"))
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(6, 4, 6, 4)
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"background-color:{fundo}; color:{cor}; border:1px solid {cor}; border-radius:10px; padding:2px 10px; font-size:11px; font-weight:700;")
        l.addWidget(lbl)
        return w

    def _aplicar_filtros(self):
        self._carregar(busca=self.campo_busca.text(), filtro_pag=self.combo_filtro.currentData())

    def _editar_selecionado(self):
        linha = self.tabela.currentRow()
        if 0 <= linha < len(self.registros):
            if DialogoFinanceiro(parent=self, registro=self.registros[linha]).exec():
                self._aplicar_filtros()