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
    "admin":   ("Administrador", "#f0a030", "#2a1a00"),
    "tecnico": ("Tecnico",       "#4a9eff", "#001a3a"),
}
ATIVO_CONFIG = {
    1: ("Ativo",   "#2ab87a", "#001a10"),
    0: ("Inativo", "#e05555", "#2a0808"),
}


class TelaUsuarios(QWidget):
    def __init__(self, usuario_logado: dict, parent=None):
        super().__init__(parent)
        self.usuario_logado = usuario_logado
        self._construir_interface()
        self._carregar_usuarios()

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
        titulo = QLabel("Usuarios")
        titulo.setObjectName("titulo_secao")
        col.addWidget(titulo)
        self.label_contador = QLabel("Carregando...")
        self.label_contador.setObjectName("label_contador")
        col.addWidget(self.label_contador)
        lh.addLayout(col)

        lh.addStretch()

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar usuario...")
        self.campo_busca.setFixedWidth(220)
        self.campo_busca.setFixedHeight(38)
        self.campo_busca.textChanged.connect(self._filtrar)
        lh.addWidget(self.campo_busca)

        if self.usuario_logado.get("perfil") == "admin":
            btn_novo = QPushButton("+ Novo Usuario")
            btn_novo.setObjectName("btn_primario")
            btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_novo.setFixedHeight(38)
            btn_novo.clicked.connect(self._novo)
            lh.addWidget(btn_novo)

        layout.addWidget(header)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["#", "NOME", "E-MAIL", "PERFIL", "STATUS", "ACOES"])
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
        self.tabela.setColumnWidth(5, 210)
        layout.addWidget(self.tabela)

    def _carregar_usuarios(self, filtro=""):
        self.usuarios = listar_usuarios()
        if filtro:
            f = filtro.lower()
            self.usuarios = [u for u in self.usuarios if
                f in u["nome"].lower() or f in u["email"].lower()]

        self.tabela.setRowCount(0)
        for u in self.usuarios:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setRowHeight(row, 50)
            self.tabela.setItem(row, 0, self._cel(str(u["id"]), center=True))
            self.tabela.setItem(row, 1, self._cel(u["nome"]))
            self.tabela.setItem(row, 2, self._cel(u["email"]))
            self.tabela.setCellWidget(row, 3, self._badge(*PERFIL_CONFIG.get(u["perfil"], ("?","#fff","#111"))))
            self.tabela.setCellWidget(row, 4, self._badge(*ATIVO_CONFIG.get(u["ativo"], ("?","#fff","#111"))))
            self.tabela.setCellWidget(row, 5, self._acoes(u))

        total = len(self.usuarios)
        self.label_contador.setText(f"{total} usuario{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}")

    def _cel(self, texto, center=False):
        item = QTableWidgetItem(texto)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _badge(self, texto, cor, fundo):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(6, 4, 6, 4)
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"background-color:{fundo}; color:{cor}; border:1px solid {cor}; border-radius:10px; padding:2px 10px; font-size:11px; font-weight:700;")
        l.addWidget(lbl)
        return w

    def _acoes(self, u):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(8, 6, 8, 6)
        l.setSpacing(8)

        pode_editar = (self.usuario_logado.get("perfil") == "admin" or
                       self.usuario_logado.get("id") == u["id"])
        if pode_editar:
            btn_e = QPushButton("Editar")
            btn_e.setObjectName("btn_editar")
            btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_e.clicked.connect(lambda _, usr=u: self._editar(usr))
            l.addWidget(btn_e)

        if (self.usuario_logado.get("perfil") == "admin" and
                self.usuario_logado.get("id") != u["id"]):
            txt = "Desativar" if u["ativo"] == 1 else "Ativar"
            obj = "btn_desativar" if u["ativo"] == 1 else "btn_ativar"
            btn_t = QPushButton(txt)
            btn_t.setObjectName(obj)
            btn_t.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_t.clicked.connect(lambda _, usr=u: self._toggle(usr))
            l.addWidget(btn_t)

        l.addStretch()
        return w

    def _filtrar(self, texto):
        self._carregar_usuarios(filtro=texto)

    def _novo(self):
        if DialogoUsuario(parent=self, usuario_logado=self.usuario_logado).exec():
            self._carregar_usuarios(filtro=self.campo_busca.text())

    def _editar(self, usuario):
        if DialogoUsuario(parent=self, usuario=usuario, usuario_logado=self.usuario_logado).exec():
            self._carregar_usuarios(filtro=self.campo_busca.text())

    def _toggle(self, usuario):
        acao = "desativar" if usuario["ativo"] == 1 else "ativar"
        r = QMessageBox.question(self, "Confirmar", f"Deseja {acao} o usuario '{usuario['nome']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            alternar_ativo(usuario["id"])
            self._carregar_usuarios(filtro=self.campo_busca.text())