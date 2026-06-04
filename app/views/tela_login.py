# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen
from app.controllers.auth_controller import fazer_login


class TelaLogin(QWidget):
    login_sucesso = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbitask")
        self.showFullScreen()
        self.setStyleSheet(self._estilos())
        self._construir_interface()

    def _construir_interface(self):
        layout_raiz = QHBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # Painel esquerdo — identidade visual
        painel_esq = QWidget()
        painel_esq.setObjectName("painel_esq")
        painel_esq.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_esq = QVBoxLayout(painel_esq)
        layout_esq.setContentsMargins(60, 60, 60, 60)
        layout_esq.setSpacing(0)

        layout_esq.addStretch()

        label_marca = QLabel("Orbitask")
        label_marca.setObjectName("marca")
        layout_esq.addWidget(label_marca)

        layout_esq.addSpacing(16)

        label_slogan = QLabel("Sistema de Gestao de\nOrdens de Servico")
        label_slogan.setObjectName("slogan")
        layout_esq.addWidget(label_slogan)

        layout_esq.addSpacing(40)

        # Tres bullets de destaque
        bullets = [
            ("Gestao completa de OS",       "Controle total do inicio ao fim de cada atendimento."),
            ("Financeiro integrado",         "Acompanhe receitas, pagamentos e inadimplencias."),
            ("Relatorios em PDF",            "Exporte dados profissionais com um clique."),
        ]
        for titulo, desc in bullets:
            linha = QWidget()
            ll = QHBoxLayout(linha)
            ll.setContentsMargins(0, 0, 0, 0)
            ll.setSpacing(16)

            dot = QLabel()
            dot.setObjectName("bullet_dot")
            dot.setFixedSize(8, 8)
            ll.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)

            col = QVBoxLayout()
            col.setSpacing(2)
            lt = QLabel(titulo)
            lt.setObjectName("bullet_titulo")
            ld = QLabel(desc)
            ld.setObjectName("bullet_desc")
            ld.setWordWrap(True)
            col.addWidget(lt)
            col.addWidget(ld)
            ll.addLayout(col)

            layout_esq.addWidget(linha)
            layout_esq.addSpacing(20)

        layout_esq.addStretch()

        label_versao = QLabel("v1.0 — Uso Interno")
        label_versao.setObjectName("versao")
        layout_esq.addWidget(label_versao)

        layout_raiz.addWidget(painel_esq, stretch=55)

        # Divisor
        div = QFrame()
        div.setFixedWidth(1)
        div.setObjectName("divisor")
        layout_raiz.addWidget(div)

        # Painel direito — formulario de login
        painel_dir = QWidget()
        painel_dir.setObjectName("painel_dir")
        painel_dir.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_dir = QVBoxLayout(painel_dir)
        layout_dir.setContentsMargins(80, 0, 80, 0)

        layout_dir.addStretch()

        label_bem_vindo = QLabel("Bem-vindo de volta")
        label_bem_vindo.setObjectName("bem_vindo")
        layout_dir.addWidget(label_bem_vindo)

        label_sub = QLabel("Faca login para continuar")
        label_sub.setObjectName("login_sub")
        layout_dir.addWidget(label_sub)

        layout_dir.addSpacing(40)

        # E-mail
        label_email = QLabel("E-MAIL")
        label_email.setObjectName("campo_label")
        layout_dir.addWidget(label_email)
        layout_dir.addSpacing(6)

        self.campo_email = QLineEdit()
        self.campo_email.setObjectName("campo_input")
        self.campo_email.setPlaceholderText("seu@email.com")
        self.campo_email.setFixedHeight(48)
        layout_dir.addWidget(self.campo_email)

        layout_dir.addSpacing(20)

        # Senha
        label_senha = QLabel("SENHA")
        label_senha.setObjectName("campo_label")
        layout_dir.addWidget(label_senha)
        layout_dir.addSpacing(6)

        self.campo_senha = QLineEdit()
        self.campo_senha.setObjectName("campo_input")
        self.campo_senha.setPlaceholderText("••••••••")
        self.campo_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_senha.setFixedHeight(48)
        self.campo_senha.returnPressed.connect(self._tentar_login)
        layout_dir.addWidget(self.campo_senha)

        layout_dir.addSpacing(32)

        self.btn_entrar = QPushButton("ENTRAR")
        self.btn_entrar.setObjectName("btn_entrar")
        self.btn_entrar.setFixedHeight(52)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self._tentar_login)
        layout_dir.addWidget(self.btn_entrar)

        layout_dir.addStretch()

        layout_raiz.addWidget(painel_dir, stretch=45)

    def _tentar_login(self):
        email = self.campo_email.text().strip()
        senha = self.campo_senha.text()

        if not email or not senha:
            QMessageBox.warning(self, "Campos obrigatorios", "Preencha o e-mail e a senha.")
            return

        self.btn_entrar.setText("Verificando...")
        self.btn_entrar.setEnabled(False)

        usuario = fazer_login(email, senha)

        if usuario:
            self.login_sucesso.emit(usuario)
        else:
            QMessageBox.critical(self, "Acesso negado", "E-mail ou senha incorretos.")
            self.campo_senha.clear()
            self.campo_senha.setFocus()
            self.btn_entrar.setText("ENTRAR")
            self.btn_entrar.setEnabled(True)

    def _estilos(self):
        return """
            QWidget {
                background-color: #050d1a;
                font-family: 'Segoe UI', sans-serif;
            }
            QWidget#painel_esq {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #050d1a,
                    stop:0.5 #071828,
                    stop:1 #0a2040
                );
            }
            QWidget#painel_dir {
                background-color: #080f1e;
            }
            QFrame#divisor {
                background-color: #0d2444;
            }
            QLabel#marca {
                font-size: 48px;
                font-weight: 800;
                color: #ffffff;
                letter-spacing: 2px;
            }
            QLabel#slogan {
                font-size: 18px;
                color: #4a9eff;
                font-weight: 300;
                line-height: 1.6;
            }
            QLabel#bullet_dot {
                background-color: #1a6fd4;
                border-radius: 4px;
                min-width: 8px;
                min-height: 8px;
                max-width: 8px;
                max-height: 8px;
            }
            QLabel#bullet_titulo {
                font-size: 14px;
                font-weight: 600;
                color: #e8f4ff;
            }
            QLabel#bullet_desc {
                font-size: 12px;
                color: #4a7aaa;
            }
            QLabel#versao {
                font-size: 11px;
                color: #1a3a5c;
            }
            QLabel#bem_vindo {
                font-size: 30px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel#login_sub {
                font-size: 14px;
                color: #3a6a9a;
            }
            QLabel#campo_label {
                font-size: 11px;
                font-weight: 700;
                color: #2a5a8a;
                letter-spacing: 1.5px;
            }
            QLineEdit#campo_input {
                background-color: #0d1e30;
                border: 1px solid #0d2e4e;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
                color: #d0e8ff;
                selection-background-color: #1a6fd4;
            }
            QLineEdit#campo_input:focus {
                border: 1px solid #1a6fd4;
                background-color: #0d2030;
            }
            QLineEdit#campo_input::placeholder {
                color: #1a3a5a;
            }
            QPushButton#btn_entrar {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a6fd4,
                    stop:1 #0d4fa0
                );
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QPushButton#btn_entrar:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2a7fe4,
                    stop:1 #1a5fc0
                );
            }
            QPushButton#btn_entrar:disabled {
                background-color: #0d2040;
                color: #2a4a6a;
            }
        """