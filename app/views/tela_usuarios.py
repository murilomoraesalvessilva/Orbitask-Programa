# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from app.models.usuario import listar_usuarios, alternar_ativo
from app.views.dialogo_usuario import DialogoUsuario


PERFIL_CONFIG = {
    "admin":   ("Administrador", "#f59e0b", "#332b1a"),
    "tecnico": ("Tecnico",       "#3b82f6", "#1a2233"),
}

ATIVO_CONFIG = {
    1: ("Ativo",    "#10b981", "#1a2e28"),
    0: ("Inativo",  "#f87171", "#2d1f1f"),
}


class TelaUsuarios(QWidget):
    def __init__(self, usuario_logado: dict, parent=None):
        super().__init__(parent)
        self.usuario_logado = usuario_logado
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._carregar_usuarios()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.setSpacing(12)

        label_titulo = QLabel("Usuarios")
        label_titulo.setObjectName("titulo_secao")
        layout_header.addWidget(label_titulo)

        layout_header.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar usuario...")
        self.campo_busca.setObjectName("campo_busca")
        self.campo_busca.setFixedWidth(220)
        self.campo_busca.textChanged.connect(self._filtrar)
        layout_header.addWidget(self.campo_busca)

        # Apenas admins podem criar usuarios
        if self.usuario_logado.get("perfil") == "admin":
            btn_novo = QPushButton("+ Novo Usuario")
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
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "E-mail", "Perfil", "Status", "Acoes"
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
        self.tabela.setColumnWidth(5, 200)

        layout.addWidget(self.tabela)

    def _carregar_usuarios(self, filtro: str = ""):
        self.usuarios = listar_usuarios()

        if filtro:
            f = filtro.lower()
            self.usuarios = [
                u for u in self.usuarios
                if f in u["nome"].lower() or f in u["email"].lower()
            ]

        self.tabela.setRowCount(0)

        for u in self.usuarios:
            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)
            self.tabela.setRowHeight(linha, 52)

            self.tabela.setItem(linha, 0, self._celula(str(u["id"]), centralizar=True))
            self.tabela.setItem(linha, 1, self._celula(u["nome"]))
            self.tabela.setItem(linha, 2, self._celula(u["email"]))
            self.tabela.setCellWidget(linha, 3, self._badge(
                *PERFIL_CONFIG.get(u["perfil"], ("Desconhecido", "#fff", "#333"))
            ))
            self.tabela.setCellWidget(linha, 4, self._badge(
                *ATIVO_CONFIG.get(u["ativo"], ("?", "#fff", "#333"))
            ))

            # Acoes
            widget_acoes = QWidget()
            layout_acoes = QHBoxLayout(widget_acoes)
            layout_acoes.setContentsMargins(8, 6, 8, 6)
            layout_acoes.setSpacing(8)

            # Editar — qualquer um pode editar o proprio perfil; admin edita todos
            pode_editar = (
                self.usuario_logado.get("perfil") == "admin"
                or self.usuario_logado.get("id") == u["id"]
            )
            if pode_editar:
                btn_editar = QPushButton("Editar")
                btn_editar.setObjectName("btn_editar")
                btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_editar.clicked.connect(lambda _, usr=u: self._abrir_dialogo_edicao(usr))
                layout_acoes.addWidget(btn_editar)

            # Ativar/Desativar — apenas admin, nao pode desativar a si mesmo
            if (self.usuario_logado.get("perfil") == "admin"
                    and self.usuario_logado.get("id") != u["id"]):
                texto_toggle = "Desativar" if u["ativo"] == 1 else "Ativar"
                obj_toggle = "btn_desativar" if u["ativo"] == 1 else "btn_ativar"
                btn_toggle = QPushButton(texto_toggle)
                btn_toggle.setObjectName(obj_toggle)
                btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_toggle.clicked.connect(lambda _, usr=u: self._toggle_ativo(usr))
                layout_acoes.addWidget(btn_toggle)

            layout_acoes.addStretch()
            self.tabela.setCellWidget(linha, 5, widget_acoes)

        total = len(self.usuarios)
        self.label_contador.setText(
            f"{total} usuario{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    def _celula(self, texto: str, centralizar: bool = False):
        item = QTableWidgetItem(texto)
        if centralizar:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _badge(self, texto, cor_texto, cor_fundo):
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

    def _filtrar(self, texto: str):
        self._carregar_usuarios(filtro=texto)

    def _abrir_dialogo_novo(self):
        dialogo = DialogoUsuario(parent=self, usuario_logado=self.usuario_logado)
        if dialogo.exec():
            self._carregar_usuarios(filtro=self.campo_busca.text())

    def _abrir_dialogo_edicao(self, usuario: dict):
        dialogo = DialogoUsuario(parent=self, usuario=usuario, usuario_logado=self.usuario_logado)
        if dialogo.exec():
            self._carregar_usuarios(filtro=self.campo_busca.text())

    def _toggle_ativo(self, usuario: dict):
        acao = "desativar" if usuario["ativo"] == 1 else "ativar"
        resposta = QMessageBox.question(
            self,
            f"Confirmar acao",
            f"Deseja {acao} o usuario '{usuario['nome']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            alternar_ativo(usuario["id"])
            self._carregar_usuarios(filtro=self.campo_busca.text())

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
            QPushButton#btn_desativar {
                background-color: #2d1f1f;
                color: #f87171;
                border: 1px solid #f87171;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton#btn_desativar:hover { background-color: #f87171; color: white; }
            QPushButton#btn_ativar {
                background-color: #1a2e28;
                color: #10b981;
                border: 1px solid #10b981;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton#btn_ativar:hover { background-color: #10b981; color: white; }
        """