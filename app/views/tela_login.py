# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QTime
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QByteArray
from app.controllers.auth_controller import fazer_login

LOGO_SVG = b"""
<svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="110" cy="110" rx="98" ry="98" fill="none" stroke="#1a6fd4" stroke-width="1.5" opacity="0.3"/>
  <ellipse cx="110" cy="110" rx="98" ry="38" fill="none" stroke="#1a6fd4" stroke-width="2" opacity="0.8" transform="rotate(-30 110 110)"/>
  <ellipse cx="110" cy="110" rx="55" ry="55" fill="none" stroke="#4a9eff" stroke-width="1" opacity="0.25"/>
  <circle cx="110" cy="110" r="30" fill="#0d2540"/>
  <circle cx="110" cy="110" r="30" fill="none" stroke="#1a6fd4" stroke-width="2"/>
  <circle cx="110" cy="110" r="20" fill="#1a6fd4" opacity="0.95"/>
  <circle cx="100" cy="102" r="6" fill="#4a9eff" opacity="0.5"/>
  <circle cx="191" cy="72" r="9" fill="#4a9eff"/>
  <circle cx="191" cy="72" r="5" fill="#ffffff" opacity="0.9"/>
  <circle cx="30" cy="145" r="6" fill="#2ab87a"/>
  <circle cx="30" cy="145" r="3" fill="#ffffff" opacity="0.8"/>
  <circle cx="110" cy="12" r="4" fill="#4a9eff" opacity="0.4"/>
  <circle cx="208" cy="110" r="3" fill="#8a6aff" opacity="0.5"/>
</svg>
"""


class TelaLogin(QWidget):
    login_sucesso = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbitask")
        self.showFullScreen()
        self.setStyleSheet(self._estilos())
        self._construir_interface()

        self.timer_relogio = QTimer(self)
        self.timer_relogio.timeout.connect(self._atualizar_relogio)
        self.timer_relogio.start(1000)
        self._atualizar_relogio()

    def _construir_interface(self):
        layout_raiz = QHBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # ---- PAINEL ESQUERDO ----
        painel_esq = QWidget()
        painel_esq.setObjectName("painel_esq")
        painel_esq.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        le = QVBoxLayout(painel_esq)
        le.setContentsMargins(64, 56, 64, 40)
        le.setSpacing(0)

        # Logo SVG
        logo_svg = QSvgWidget()
        logo_svg.load(QByteArray(LOGO_SVG))
        logo_svg.setFixedSize(160, 160)
        logo_svg.setStyleSheet("background: transparent;")
        le.addWidget(logo_svg)

        le.addSpacing(20)

        # Nome do sistema
        label_nome = QLabel("Orbitask")
        label_nome.setObjectName("marca")
        le.addWidget(label_nome)

        le.addSpacing(8)

        label_slogan = QLabel("Sistema Profissional de\nGestao de Ordens de Servico")
        label_slogan.setObjectName("slogan")
        le.addWidget(label_slogan)

        le.addSpacing(48)

        # Linha separadora
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #0d2440;")
        le.addWidget(sep)

        le.addSpacing(32)

        # Bullets de funcionalidades
        bullets = [
            ("Ordens de Servico",   "Controle completo do ciclo de atendimento"),
            ("Financeiro Integrado","Receitas, pagamentos e relatorios em PDF"),
            ("Calendario de Prazos","Visualize prazos e compromissos em tempo real"),
            ("Multi-usuario",       "Perfis de Admin e Tecnico com permissoes"),
        ]
        for titulo, desc in bullets:
            linha = QWidget()
            linha.setStyleSheet("background: transparent;")
            ll = QHBoxLayout(linha)
            ll.setContentsMargins(0, 0, 0, 0)
            ll.setSpacing(14)

            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet("background-color:#1a6fd4; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
            ll.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop)

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

            le.addWidget(linha)
            le.addSpacing(16)

        le.addStretch()

        # Relogio no rodape
        self.label_relogio = QLabel()
        self.label_relogio.setObjectName("relogio")
        le.addWidget(self.label_relogio)

        le.addSpacing(8)

        label_versao = QLabel("Orbitask v1.0 — Uso Interno")
        label_versao.setObjectName("versao")
        le.addWidget(label_versao)

        layout_raiz.addWidget(painel_esq, stretch=55)

        # Divisor
        div = QWidget()
        div.setFixedWidth(1)
        div.setStyleSheet("background-color: #0d2440;")
        layout_raiz.addWidget(div)

        # ---- PAINEL DIREITO ----
        painel_dir = QWidget()
        painel_dir.setObjectName("painel_dir")
        painel_dir.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ld = QVBoxLayout(painel_dir)
        ld.setContentsMargins(80, 0, 80, 0)

        ld.addStretch()

        # Logo pequena no formulario
        logo_pequena = QSvgWidget()
        logo_pequena.load(QByteArray(LOGO_SVG))
        logo_pequena.setFixedSize(64, 64)
        logo_pequena.setStyleSheet("background: transparent;")
        ld.addWidget(logo_pequena)

        ld.addSpacing(16)

        label_bv = QLabel("Bem-vindo de volta")
        label_bv.setObjectName("bem_vindo")
        ld.addWidget(label_bv)

        label_sub = QLabel("Faca login para acessar o sistema")
        label_sub.setObjectName("login_sub")
        ld.addWidget(label_sub)

        ld.addSpacing(40)

        # Campo e-mail
        lbl_email = QLabel("E-MAIL")
        lbl_email.setObjectName("campo_label")
        ld.addWidget(lbl_email)
        ld.addSpacing(6)
        self.campo_email = QLineEdit()
        self.campo_email.setObjectName("campo_input")
        self.campo_email.setPlaceholderText("seu@email.com")
        self.campo_email.setFixedHeight(50)
        ld.addWidget(self.campo_email)

        ld.addSpacing(20)

        # Campo senha
        lbl_senha = QLabel("SENHA")
        lbl_senha.setObjectName("campo_label")
        ld.addWidget(lbl_senha)
        ld.addSpacing(6)
        self.campo_senha = QLineEdit()
        self.campo_senha.setObjectName("campo_input")
        self.campo_senha.setPlaceholderText("••••••••")
        self.campo_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_senha.setFixedHeight(50)
        self.campo_senha.returnPressed.connect(self._tentar_login)
        ld.addWidget(self.campo_senha)

        ld.addSpacing(32)

        self.btn_entrar = QPushButton("ENTRAR NO SISTEMA")
        self.btn_entrar.setObjectName("btn_entrar")
        self.btn_entrar.setFixedHeight(54)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self._tentar_login)
        ld.addWidget(self.btn_entrar)

        ld.addSpacing(24)

        label_dica = QLabel("Acesso restrito a usuarios autorizados")
        label_dica.setObjectName("dica_acesso")
        label_dica.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ld.addWidget(label_dica)

        ld.addStretch()

        layout_raiz.addWidget(painel_dir, stretch=45)

    def _atualizar_relogio(self):
        agora = QTime.currentTime().toString("hh:mm:ss")
        self.label_relogio.setText(agora)

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
            self.timer_relogio.stop()
            self.login_sucesso.emit(usuario)
        else:
            QMessageBox.critical(self, "Acesso negado", "E-mail ou senha incorretos.")
            self.campo_senha.clear()
            self.campo_senha.setFocus()
            self.btn_entrar.setText("ENTRAR NO SISTEMA")
            self.btn_entrar.setEnabled(True)

    def _estilos(self):
        return """
            QWidget {
                background-color: #050d1a;
                font-family: 'Segoe UI', sans-serif;
            }
            QWidget#painel_esq {
                background-color: #040c18;
            }
            QWidget#painel_dir {
                background-color: #06101e;
            }
            QLabel {
                background-color: transparent;
                color: #c8dff5;
            }
            QLabel#marca {
                font-size: 42px;
                font-weight: 800;
                color: #ffffff;
                letter-spacing: 2px;
                background: transparent;
            }
            QLabel#slogan {
                font-size: 16px;
                color: #2a6aaa;
                font-weight: 300;
                line-height: 1.6;
                background: transparent;
            }
            QLabel#bullet_titulo {
                font-size: 13px;
                font-weight: 600;
                color: #c8dff5;
                background: transparent;
            }
            QLabel#bullet_desc {
                font-size: 12px;
                color: #2a5a8a;
                background: transparent;
            }
            QLabel#relogio {
                font-size: 28px;
                font-weight: 700;
                color: #1a6fd4;
                letter-spacing: 3px;
                background: transparent;
            }
            QLabel#versao {
                font-size: 11px;
                color: #0d2440;
                background: transparent;
            }
            QLabel#bem_vindo {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
                background: transparent;
            }
            QLabel#login_sub {
                font-size: 13px;
                color: #1a4a7a;
                background: transparent;
            }
            QLabel#campo_label {
                font-size: 11px;
                font-weight: 700;
                color: #1a4a7a;
                letter-spacing: 1.5px;
                background: transparent;
            }
            QLabel#dica_acesso {
                font-size: 11px;
                color: #0d2440;
                background: transparent;
            }
            QLineEdit#campo_input {
                background-color: #0a1828;
                border: 1px solid #0d2e4e;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                color: #c8dff5;
                selection-background-color: #1a6fd4;
            }
            QLineEdit#campo_input:focus {
                border: 1px solid #1a6fd4;
                background-color: #0d2030;
            }
            QPushButton#btn_entrar {
                background-color: #1a6fd4;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QPushButton#btn_entrar:hover {
                background-color: #2a7fe4;
            }
            QPushButton#btn_entrar:disabled {
                background-color: #0d2040;
                color: #2a4a6a;
            }
        """