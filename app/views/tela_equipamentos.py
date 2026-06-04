# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from app.models.equipamento import listar_equipamentos, deletar_equipamento
from app.views.dialogo_equipamento import DialogoEquipamento


class TelaEquipamentos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._carregar_equipamentos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.setSpacing(12)

        label_titulo = QLabel("Equipamentos")
        label_titulo.setObjectName("titulo_secao")
        layout_header.addWidget(label_titulo)

        layout_header.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar equipamento...")
        self.campo_busca.setObjectName("campo_busca")
        self.campo_busca.setFixedWidth(220)
        self.campo_busca.textChanged.connect(self._filtrar)
        layout_header.addWidget(self.campo_busca)

        btn_novo = QPushButton("+ Novo Equipamento")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._abrir_dialogo_novo)
        layout_header.addWidget(btn_novo)

        layout.addWidget(header)

        self.label_contador = QLabel("")
        self.label_contador.setObjectName("label_contador")
        layout.addWidget(self.label_contador)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setObjectName("tabela")
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "Tipo", "Marca / Modelo", "N. Serie", "OS Vinculada", "Acoes"
        ])
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

    def _carregar_equipamentos(self, filtro: str = ""):
        self.equipamentos = listar_equipamentos()

        if filtro:
            f = filtro.lower()
            self.equipamentos = [
                e for e in self.equipamentos
                if f in e["nome"].lower()
                or f in (e.get("marca") or "").lower()
                or f in (e.get("modelo") or "").lower()
                or f in (e.get("tipo") or "").lower()
                or f in (e.get("numero_serie") or "").lower()
            ]

        self.tabela.setRowCount(0)

        for e in self.equipamentos:
            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)
            self.tabela.setRowHeight(linha, 50)

            marca_modelo = " / ".join(filter(None, [e.get("marca"), e.get("modelo")])) or "-"
            os_titulo = f"#{e['ordem_id']} {e.get('ordem_titulo', '')[:35]}" if e.get("ordem_id") else "-"

            self.tabela.setItem(linha, 0, self._celula(str(e["id"]), centralizar=True))
            self.tabela.setItem(linha, 1, self._celula(e["nome"]))
            self.tabela.setItem(linha, 2, self._celula(e.get("tipo") or "-"))
            self.tabela.setItem(linha, 3, self._celula(marca_modelo))
            self.tabela.setItem(linha, 4, self._celula(e.get("numero_serie") or "-"))
            self.tabela.setItem(linha, 5, self._celula(os_titulo))

            # Acoes
            widget_acoes = QWidget()
            layout_acoes = QHBoxLayout(widget_acoes)
            layout_acoes.setContentsMargins(8, 6, 8, 6)
            layout_acoes.setSpacing(8)

            btn_editar = QPushButton("Editar")
            btn_editar.setObjectName("btn_editar")
            btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_editar.clicked.connect(lambda _, eq=e: self._abrir_dialogo_edicao(eq))
            layout_acoes.addWidget(btn_editar)

            btn_excluir = QPushButton("Excluir")
            btn_excluir.setObjectName("btn_excluir")
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda _, eq=e: self._confirmar_exclusao(eq))
            layout_acoes.addWidget(btn_excluir)

            layout_acoes.addStretch()
            self.tabela.setCellWidget(linha, 6, widget_acoes)

        total = len(self.equipamentos)
        self.label_contador.setText(
            f"{total} equipamento{'s' if total != 1 else ''} cadastrado{'s' if total != 1 else ''}"
        )

    def _celula(self, texto: str, centralizar: bool = False):
        item = QTableWidgetItem(texto)
        if centralizar:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _filtrar(self, texto: str):
        self._carregar_equipamentos(filtro=texto)

    def _abrir_dialogo_novo(self):
        dialogo = DialogoEquipamento(parent=self)
        if dialogo.exec():
            self._carregar_equipamentos(filtro=self.campo_busca.text())

    def _abrir_dialogo_edicao(self, equipamento: dict):
        dialogo = DialogoEquipamento(parent=self, equipamento=equipamento)
        if dialogo.exec():
            self._carregar_equipamentos(filtro=self.campo_busca.text())

    def _confirmar_exclusao(self, equipamento: dict):
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f"Deseja excluir o equipamento '{equipamento['nome']}'?\n\nEssa acao nao pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            deletar_equipamento(equipamento["id"])
            self._carregar_equipamentos(filtro=self.campo_busca.text())

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
            QLineEdit#campo_busca:focus { border: 1px solid #7c6af7; }
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