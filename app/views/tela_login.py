from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from app.controllers.auth_controller import fazer_login


class TelaLogin(QWidget):
    # Sinal emitido quando o login é bem-sucedido, carregando os dados do usuário
    login_sucesso = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbitask — Login")
        self.setFixedSize(420, 500)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

    def _construir_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # Card central
        card = QFrame()
        card.setObjectName("card")
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(40, 50, 40, 50)
        layout_card.setSpacing(16)

        # Logo / título
        label_logo = QLabel("🪐 Orbitask")
        label_logo.setObjectName("logo")
        label_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(label_logo)

        label_sub = QLabel("Sistema de Gestão de Ordens de Serviço")
        label_sub.setObjectName("subtitulo")
        label_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_sub.setWordWrap(True)
        layout_card.addWidget(label_sub)

        layout_card.addSpacing(20)

        # Campo e-mail
        label_email = QLabel("E-mail")
        label_email.setObjectName("label_campo")
        layout_card.addWidget(label_email)

        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("seu@email.com")
        self.campo_email.setObjectName("campo")
        layout_card.addWidget(self.campo_email)

        layout_card.addSpacing(8)

        # Campo senha
        label_senha = QLabel("Senha")
        label_senha.setObjectName("label_campo")
        layout_card.addWidget(label_senha)

        self.campo_senha = QLineEdit()
        self.campo_senha.setPlaceholderText("••••••••")
        self.campo_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_senha.setObjectName("campo")
        self.campo_senha.returnPressed.connect(self._tentar_login)
        layout_card.addWidget(self.campo_senha)

        layout_card.addSpacing(24)

        # Botão entrar
        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setObjectName("btn_primario")
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self._tentar_login)
        layout_card.addWidget(self.btn_entrar)

        layout_card.addSpacing(12)

        # Rodapé
        label_rodape = QLabel("Orbitask v1.0 — Uso interno")
        label_rodape.setObjectName("rodape")
        label_rodape.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(label_rodape)

        layout_principal.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _tentar_login(self):
        email = self.campo_email.text().strip()
        senha = self.campo_senha.text()

        if not email or not senha:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha o e-mail e a senha.")
            return

        self.btn_entrar.setText("Entrando...")
        self.btn_entrar.setEnabled(False)

        usuario = fazer_login(email, senha)

        if usuario:
            self.login_sucesso.emit(usuario)
        else:
            QMessageBox.critical(self, "Acesso negado", "E-mail ou senha incorretos.")
            self.campo_senha.clear()
            self.campo_senha.setFocus()
            self.btn_entrar.setText("Entrar")
            self.btn_entrar.setEnabled(True)

    def _estilos(self):
        return """
            QWidget {
                background-color: #0f1117;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#card {
                background-color: #1a1d27;
                border-radius: 16px;
                min-width: 360px;
                max-width: 360px;
            }
            QLabel#logo {
                font-size: 28px;
                font-weight: bold;
                color: #7c6af7;
            }
            QLabel#subtitulo {
                font-size: 12px;
                color: #6b7280;
            }
            QLabel#label_campo {
                font-size: 13px;
                color: #9ca3af;
                font-weight: bold;
            }
            QLineEdit#campo {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #e0e0e0;
            }
            QLineEdit#campo:focus {
                border: 1px solid #7c6af7;
            }
            QPushButton#btn_primario {
                background-color: #7c6af7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton#btn_primario:hover {
                background-color: #6a58e0;
            }
            QPushButton#btn_primario:disabled {
                background-color: #3d3d5c;
                color: #888;
            }
            QLabel#rodape {
                font-size: 11px;
                color: #4b5563;
            }
        """