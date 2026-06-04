# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QAbstractItemView, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from app.models.financeiro import listar_financeiro, resumo_financeiro
from app.views.dialogo_financeiro import DialogoFinanceiro


STATUS_PAG_CONFIG = {
    "pendente":  ("Pendente",  "#f59e0b", "#332b1a"),
    "pago":      ("Pago",      "#10b981", "#1a2e28"),
    "cancelado": ("Cancelado", "#f87171", "#2d1f1f"),
}


def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class TelaFinanceiro(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._carregar()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.setSpacing(12)

        label_titulo = QLabel("Financeiro")
        label_titulo.setObjectName("titulo_secao")
        layout_header.addWidget(label_titulo)

        layout_header.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar OS ou cliente...")
        self.campo_busca.setObjectName("campo_busca")
        self.campo_busca.setFixedWidth(200)
        self.campo_busca.textChanged.connect(self._aplicar_filtros)
        layout_header.addWidget(self.campo_busca)

        self.combo_filtro = QComboBox()
        self.combo_filtro.setObjectName("combo_filtro")
        self.combo_filtro.addItem("Todos",     userData=None)
        self.combo_filtro.addItem("Pendente",  userData="pendente")
        self.combo_filtro.addItem("Pago",      userData="pago")
        self.combo_filtro.addItem("Cancelado", userData="cancelado")
        self.combo_filtro.currentIndexChanged.connect(self._aplicar_filtros)
        layout_header.addWidget(self.combo_filtro)

        layout.addWidget(header)

        # Cards de resumo
        self.frame_cards = QFrame()
        layout_cards = QHBoxLayout(self.frame_cards)
        layout_cards.setContentsMargins(0, 0, 0, 0)
        layout_cards.setSpacing(16)

        self.card_total     = self._criar_card("Receita Total",    "R$ 0,00", "#7c6af7")
        self.card_recebida  = self._criar_card("Receita Recebida", "R$ 0,00", "#10b981")
        self.card_pendente  = self._criar_card("A Receber",        "R$ 0,00", "#f59e0b")
        self.card_os_pagas  = self._criar_card("OS Pagas",         "0",       "#3b82f6")

        for card in [self.card_total, self.card_recebida, self.card_pendente, self.card_os_pagas]:
            layout_cards.addWidget(card)

        layout.addWidget(self.frame_cards)

        self.label_contador = QLabel("")
        self.label_contador.setObjectName("label_contador")
        layout.addWidget(self.label_contador)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setObjectName("tabela")
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "OS #", "Titulo", "Cliente", "Servico", "Pecas", "Total", "Pagamento"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setColumnWidth(0, 55)
        self.tabela.setColumnWidth(3, 110)
        self.tabela.setColumnWidth(4, 110)
        self.tabela.setColumnWidth(5, 120)
        self.tabela.setColumnWidth(6, 130)

        self.tabela.doubleClicked.connect(self._editar_selecionado)
        layout.addWidget(self.tabela)

        label_dica = QLabel("Dica: clique duplo em uma linha para editar os valores financeiros.")
        label_dica.setObjectName("label_dica")
        layout.addWidget(label_dica)

    def _criar_card(self, titulo, valor, cor):
        card = QFrame()
        card.setObjectName("card_resumo")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(6)

        lv = QLabel(valor)
        lv.setObjectName("card_valor")
        lv.setStyleSheet(f"color: {cor}; font-size: 20px; font-weight: bold;")
        layout.addWidget(lv)

        lt = QLabel(titulo)
        lt.setObjectName("card_titulo")
        layout.addWidget(lt)

        card._label_valor = lv
        return card

    def _carregar(self, busca: str = "", filtro_pag: str = None):
        self.registros = listar_financeiro(filtro_pagamento=filtro_pag)

        if busca:
            b = busca.lower()
            self.registros = [
                r for r in self.registros
                if b in r["titulo"].lower()
                or b in (r.get("cliente_nome") or "").lower()
            ]

        self.tabela.setRowCount(0)

        for r in self.registros:
            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)
            self.tabela.setRowHeight(linha, 50)

            self.tabela.setItem(linha, 0, self._celula(str(r["id"]), centralizar=True))
            self.tabela.setItem(linha, 1, self._celula(r["titulo"]))
            self.tabela.setItem(linha, 2, self._celula(r.get("cliente_nome") or "-"))
            self.tabela.setItem(linha, 3, self._celula(formatar_brl(r.get("valor_servico") or 0)))
            self.tabela.setItem(linha, 4, self._celula(formatar_brl(r.get("valor_pecas") or 0)))
            self.tabela.setItem(linha, 5, self._celula(formatar_brl(r.get("valor_total") or 0)))
            self.tabela.setCellWidget(linha, 6, self._badge_pagamento(r.get("status_pagamento", "pendente")))

        total = len(self.registros)
        self.label_contador.setText(f"{total} ordem{'s' if total != 1 else ''} encontrada{'s' if total != 1 else ''}")

        # Atualiza cards de resumo
        res = resumo_financeiro()
        self.card_total._label_valor.setText(formatar_brl(res.get("receita_total", 0)))
        self.card_recebida._label_valor.setText(formatar_brl(res.get("receita_recebida", 0)))
        self.card_pendente._label_valor.setText(formatar_brl(res.get("receita_pendente", 0)))
        self.card_os_pagas._label_valor.setText(str(res.get("os_pagas", 0)))

    def _celula(self, texto: str, centralizar: bool = False):
        item = QTableWidgetItem(texto)
        if centralizar:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _badge_pagamento(self, status: str):
        texto, cor_texto, cor_fundo = STATUS_PAG_CONFIG.get(status, ("?", "#fff", "#333"))
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

    def _aplicar_filtros(self):
        self._carregar(
            busca=self.campo_busca.text(),
            filtro_pag=self.combo_filtro.currentData()
        )

    def _editar_selecionado(self):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self.registros):
            return
        registro = self.registros[linha]
        dialogo = DialogoFinanceiro(parent=self, registro=registro)
        if dialogo.exec():
            self._aplicar_filtros()

    def _estilos(self):
        return """
            QLabel#titulo_secao {
                font-size: 20px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#label_contador, QLabel#label_dica {
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
            QLineEdit#campo_busca:focus { border: 1px solid #7c6af7; }
            QComboBox#combo_filtro {
                background-color: #1a1d27;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
                min-width: 120px;
            }
            QComboBox#combo_filtro::drop-down { border: none; }
            QComboBox#combo_filtro QAbstractItemView {
                background-color: #252836;
                color: #e0e0e0;
                selection-background-color: #7c6af7;
            }
            QFrame#card_resumo {
                background-color: #1a1d27;
                border-radius: 12px;
                border: 1px solid #2e3347;
                min-height: 90px;
            }
            QLabel#card_titulo {
                font-size: 12px;
                color: #6b7280;
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
        """