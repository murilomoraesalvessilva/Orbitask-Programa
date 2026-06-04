# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox,
    QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from app.models.usuario import criar_usuario, atualizar_usuario, trocar_senha

PERFIS = [
    ("admin",   "Administrador"),
    ("tecnico", "Tecnico"),
]


class DialogoUsuario(QDialog):
    """Dialogo para criar ou editar um usuario."""

    def __init__(self, parent=None, usuario: dict = None, usuario_logado: dict = None):
        super().__init__(parent)
        self.usuario = usuario
        self.usuario_logado = usuario_logado or {}
        self.editando = usuario is not None

        titulo = "Editar Usuario" if self.editando else "Novo Usuario"
        self.setWindowTitle(titulo)
        self.setFixedSize(460, 420 if not self.editando else 480)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

        if self.editando:
            self._preencher_campos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)

        titulo = "Editar Usuario" if self.editando else "Novo Usuario"
        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("titulo")
        layout.addWidget(label_titulo)

        layout.addSpacing(4)

        if self.editando:
            tabs = QTabWidget()
            tabs.setObjectName("tabs")

            # Aba de dados
            aba_dados = QWidget()
            layout_dados = QVBoxLayout(aba_dados)
            layout_dados.setContentsMargins(0, 16, 0, 0)
            layout_dados.setSpacing(12)
            self._campos_dados(layout_dados)
            tabs.addTab(aba_dados, "Dados")

            # Aba de senha
            aba_senha = QWidget()
            layout_senha = QVBoxLayout(aba_senha)
            layout_senha.setContentsMargins(0, 16, 0, 0)
            layout_senha.setSpacing(12)
            self._campos_senha(layout_senha)
            tabs.addTab(aba_senha, "Trocar Senha")

            layout.addWidget(tabs)
            self.tabs = tabs
        else:
            self._campos_dados(layout)
            layout.addSpacing(4)
            self._campo_senha_novo(layout)

        layout.addStretch()

        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)

        texto = "Salvar" if self.editando else "Cadastrar"
        btn_salvar = QPushButton(texto)
        btn_salvar.setObjectName("btn_primario")
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._salvar)
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def _campos_dados(self, layout):
        self.campo_nome = self._campo(layout, "Nome *", "Nome completo")
        self.campo_email = self._campo(layout, "E-mail *", "usuario@email.com")

        label_perfil = QLabel("Perfil *")
        label_perfil.setObjectName("label_campo")
        layout.addWidget(label_perfil)

        self.combo_perfil = QComboBox()
        self.combo_perfil.setObjectName("combo")
        for _, label in PERFIS:
            self.combo_perfil.addItem(label)
        layout.addWidget(self.combo_perfil)

    def _campo_senha_novo(self, layout):
        self.campo_senha = self._campo(layout, "Senha *", "Minimo 6 caracteres", senha=True)
        self.campo_confirmar = self._campo(layout, "Confirmar Senha *", "Repita a senha", senha=True)

    def _campos_senha(self, layout):
        self.campo_senha_atual = self._campo(layout, "Senha Atual", "", senha=True)
        self.campo_nova_senha = self._campo(layout, "Nova Senha", "Minimo 6 caracteres", senha=True)
        self.campo_conf_senha = self._campo(layout, "Confirmar Nova Senha", "", senha=True)

    def _campo(self, layout, label_texto, placeholder, senha=False):
        label = QLabel(label_texto)
        label.setObjectName("label_campo")
        layout.addWidget(label)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setObjectName("campo")
        if senha:
            campo.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(campo)
        return campo

    def _preencher_campos(self):
        self.campo_nome.setText(self.usuario.get("nome", ""))
        self.campo_email.setText(self.usuario.get("email", ""))
        perfil_valores = [k for k, _ in PERFIS]
        perfil_atual = self.usuario.get("perfil", "tecnico")
        if perfil_atual in perfil_valores:
            self.combo_perfil.setCurrentIndex(perfil_valores.index(perfil_atual))

    def _salvar(self):
        # Verifica qual aba esta ativa (se editando)
        if self.editando and self.tabs.currentIndex() == 1:
            self._salvar_senha()
            return

        nome = self.campo_nome.text().strip()
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
            senha = self.campo_senha.text()
            confirmar = self.campo_confirmar.text()

            if not senha:
                QMessageBox.warning(self, "Campos obrigatorios", "A senha e obrigatoria.")
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
        nova = self.campo_nova_senha.text()
        conf = self.campo_conf_senha.text()

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

    def _estilos(self):
        return """
            QDialog {
                background-color: #1a1d27;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titulo {
                font-size: 18px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#label_campo {
                font-size: 12px;
                color: #9ca3af;
                font-weight: bold;
            }
            QLineEdit#campo {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QLineEdit#campo:focus { border: 1px solid #7c6af7; }
            QComboBox#combo {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox#combo::drop-down { border: none; }
            QComboBox#combo QAbstractItemView {
                background-color: #252836;
                color: #e0e0e0;
                selection-background-color: #7c6af7;
            }
            QTabWidget#tabs::pane {
                border: 1px solid #2e3347;
                border-radius: 8px;
                background-color: #1a1d27;
            }
            QTabBar::tab {
                background-color: #252836;
                color: #9ca3af;
                padding: 8px 20px;
                border: none;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #2d2b55;
                color: #7c6af7;
                font-weight: bold;
            }
            QPushButton#btn_primario {
                background-color: #7c6af7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btn_primario:hover { background-color: #6a58e0; }
            QPushButton#btn_secundario {
                background-color: #252836;
                color: #9ca3af;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton#btn_secundario:hover { background-color: #2e3347; color: #e0e0e0; }
        """