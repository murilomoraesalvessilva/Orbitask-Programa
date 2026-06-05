# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox,
    QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from app.models.usuario import criar_usuario, atualizar_usuario, trocar_senha

ESTILO = """
    QDialog, QWidget {
        background-color: #08121e;
        color: #c8dff5;
        font-family: 'Segoe UI', sans-serif;
    }
    QLabel {
        background-color: transparent;
        color: #c8dff5;
        font-size: 13px;
    }
    QLabel#campo_label {
        background-color: transparent;
        color: #2a5a8a;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
    }
    QLabel#titulo {
        background-color: transparent;
        color: #ffffff;
        font-size: 17px;
        font-weight: 700;
    }
    QLineEdit {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 9px 12px;
        font-size: 13px;
        color: #c8dff5;
    }
    QLineEdit:focus { border: 1px solid #1a6fd4; }
    QComboBox {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 9px 12px;
        font-size: 13px;
        color: #c8dff5;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background-color: #0a1828;
        color: #c8dff5;
        selection-background-color: #1a6fd4;
        outline: none;
    }
    QTabWidget::pane {
        border: 1px solid #0a1e34;
        border-radius: 8px;
        background-color: #08121e;
    }
    QTabBar::tab {
        background-color: #080f1e;
        color: #2a5a8a;
        padding: 9px 22px;
        border: none;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #0d2540;
        color: #4a9eff;
        font-weight: 600;
        border-bottom: 2px solid #1a6fd4;
    }
    QPushButton#btn_primario {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a6fd4,stop:1 #0d4fa0);
        color: white; border: none; border-radius: 6px;
        padding: 10px 20px; font-size: 13px; font-weight: 600;
    }
    QPushButton#btn_primario:hover {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2a7fe4,stop:1 #1a5fc0);
    }
    QPushButton#btn_secundario {
        background-color: #0a1828; color: #3a6a9a;
        border: 1px solid #0d2440; border-radius: 6px; padding: 10px 20px; font-size: 13px;
    }
    QPushButton#btn_secundario:hover { background-color: #0d2040; color: #c8dff5; }
"""

PERFIS = [("admin", "Administrador"), ("tecnico", "Tecnico")]


class DialogoUsuario(QDialog):
    def __init__(self, parent=None, usuario: dict = None, usuario_logado: dict = None):
        super().__init__(parent)
        self.usuario = usuario
        self.usuario_logado = usuario_logado or {}
        self.editando = usuario is not None
        self.setWindowTitle("Editar Usuario" if self.editando else "Novo Usuario")
        self.setFixedSize(460, 480 if self.editando else 440)
        self.setStyleSheet(ESTILO)
        self._construir()
        if self.editando:
            self._preencher()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        titulo = QLabel("Editar Usuario" if self.editando else "Novo Usuario")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        layout.addSpacing(20)

        if self.editando:
            tabs = QTabWidget()
            tabs.setObjectName("tabs")

            aba_dados = QWidget()
            ld = QVBoxLayout(aba_dados)
            ld.setContentsMargins(0, 16, 0, 0)
            ld.setSpacing(0)
            self._campos_dados(ld)
            tabs.addTab(aba_dados, "Dados")

            aba_senha = QWidget()
            ls = QVBoxLayout(aba_senha)
            ls.setContentsMargins(0, 16, 0, 0)
            ls.setSpacing(0)
            self._campos_senha(ls)
            tabs.addTab(aba_senha, "Trocar Senha")

            layout.addWidget(tabs)
            self.tabs = tabs
        else:
            self._campos_dados(layout)
            layout.addSpacing(12)
            self._campo_senha_novo(layout)

        layout.addSpacing(20)

        bts = QHBoxLayout()
        bts.setSpacing(12)
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secundario")
        btn_c.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c.clicked.connect(self.reject)
        bts.addWidget(btn_c)

        btn_s = QPushButton("Salvar" if self.editando else "Cadastrar")
        btn_s.setObjectName("btn_primario")
        btn_s.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_s.clicked.connect(self._salvar)
        bts.addWidget(btn_s)
        layout.addLayout(bts)

    def _campo(self, layout, label_txt, placeholder, senha=False):
        lbl = QLabel(label_txt)
        lbl.setObjectName("campo_label")
        layout.addWidget(lbl)
        layout.addSpacing(4)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        if senha:
            campo.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(campo)
        layout.addSpacing(12)
        return campo

    def _campos_dados(self, layout):
        self.campo_nome  = self._campo(layout, "NOME *",   "Nome completo")
        self.campo_email = self._campo(layout, "E-MAIL *", "usuario@email.com")

        lbl = QLabel("PERFIL *")
        lbl.setObjectName("campo_label")
        layout.addWidget(lbl)
        layout.addSpacing(4)
        self.combo_perfil = QComboBox()
        for _, label in PERFIS:
            self.combo_perfil.addItem(label)
        layout.addWidget(self.combo_perfil)

    def _campo_senha_novo(self, layout):
        self.campo_senha     = self._campo(layout, "SENHA *",            "Minimo 6 caracteres", senha=True)
        self.campo_confirmar = self._campo(layout, "CONFIRMAR SENHA *",  "Repita a senha",       senha=True)

    def _campos_senha(self, layout):
        self.campo_senha_atual = self._campo(layout, "SENHA ATUAL",        "",                     senha=True)
        self.campo_nova_senha  = self._campo(layout, "NOVA SENHA",         "Minimo 6 caracteres",  senha=True)
        self.campo_conf_senha  = self._campo(layout, "CONFIRMAR NOVA SENHA","",                    senha=True)

    def _preencher(self):
        self.campo_nome.setText(self.usuario.get("nome", ""))
        self.campo_email.setText(self.usuario.get("email", ""))
        perfil_vals = [k for k, _ in PERFIS]
        perfil = self.usuario.get("perfil", "tecnico")
        if perfil in perfil_vals:
            self.combo_perfil.setCurrentIndex(perfil_vals.index(perfil))

    def _salvar(self):
        if self.editando and self.tabs.currentIndex() == 1:
            self._salvar_senha()
            return

        nome  = self.campo_nome.text().strip()
        email = self.campo_email.text().strip()
        perfil = PERFIS[self.combo_perfil.currentIndex()][0]

        if not nome or not email:
            QMessageBox.warning(self, "Campos obrigatorios", "Nome e e-mail sao obrigatorios.")
            return

        if self.editando:
            ok, erro = atualizar_usuario(self.usuario["id"], nome, email, perfil)
            if not ok:
                QMessageBox.warning(self, "Erro", erro)
                return
        else:
            senha    = self.campo_senha.text()
            confirmar = self.campo_confirmar.text()
            if not senha:
                QMessageBox.warning(self, "Campo obrigatorio", "A senha e obrigatoria.")
                return
            if len(senha) < 6:
                QMessageBox.warning(self, "Senha fraca", "A senha deve ter pelo menos 6 caracteres.")
                return
            if senha != confirmar:
                QMessageBox.warning(self, "Senhas diferentes", "As senhas nao coincidem.")
                return
            novo_id, erro = criar_usuario(nome, email, senha, perfil)
            if erro:
                QMessageBox.warning(self, "Erro", erro)
                return
        self.accept()

    def _salvar_senha(self):
        atual = self.campo_senha_atual.text()
        nova  = self.campo_nova_senha.text()
        conf  = self.campo_conf_senha.text()
        if not atual or not nova:
            QMessageBox.warning(self, "Campos obrigatorios", "Preencha todos os campos de senha.")
            return
        if len(nova) < 6:
            QMessageBox.warning(self, "Senha fraca", "A nova senha deve ter pelo menos 6 caracteres.")
            return
        if nova != conf:
            QMessageBox.warning(self, "Senhas diferentes", "As novas senhas nao coincidem.")
            return
        ok, erro = trocar_senha(self.usuario["id"], atual, nova)
        if not ok:
            QMessageBox.warning(self, "Erro", erro)
            return
        QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso!")
        self.accept()