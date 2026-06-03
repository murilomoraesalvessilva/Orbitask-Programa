# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt


class JanelaPrincipal(QMainWindow):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Orbitask")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

    def _construir_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_raiz = QHBoxLayout(widget_central)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        sidebar = self._criar_sidebar()
        layout_raiz.addWidget(sidebar)

        self.area_conteudo = QWidget()
        self.area_conteudo.setObjectName("area_conteudo")
        layout_conteudo = QVBoxLayout(self.area_conteudo)
        layout_conteudo.setContentsMargins(32, 32, 32, 32)
        layout_conteudo.setSpacing(24)

        header = self._criar_header()
        layout_conteudo.addWidget(header)

        cards = self._criar_cards_resumo()
        layout_conteudo.addWidget(cards)

        placeholder = QLabel("Selecione uma opcao no menu lateral para comecar.")
        placeholder.setObjectName("placeholder")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_conteudo.addWidget(placeholder, stretch=1)

        layout_raiz.addWidget(self.area_conteudo, stretch=1)

    def _criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(4)

        logo = QLabel("Orbitask")
        logo.setObjectName("sidebar_logo")
        layout.addWidget(logo)

        layout.addSpacing(24)

        itens = [
            "Dashboard",
            "Ordens de Servico",
            "Clientes",
            "Usuarios",
            "Relatorios",
        ]

        self.botoes_menu = []
        for texto in itens:
            btn = QPushButton(texto)
            btn.setObjectName("btn_menu")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            layout.addWidget(btn)
            self.botoes_menu.append(btn)

        self.botoes_menu[0].setChecked(True)

        layout.addStretch()

        btn_sair = QPushButton("Sair")
        btn_sair.setObjectName("btn_sair")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.clicked.connect(self._sair)
        layout.addWidget(btn_sair)

        return sidebar

    def _criar_header(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        label_titulo = QLabel("Dashboard")
        label_titulo.setObjectName("titulo_pagina")
        layout.addWidget(label_titulo)

        layout.addStretch()

        nome = self.usuario['nome'].split()[0]
        label_usuario = QLabel(f"Ola, {nome}")
        label_usuario.setObjectName("label_usuario")
        layout.addWidget(label_usuario)

        return frame

    def _criar_cards_resumo(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        dados_cards = [
            ("Ordens Abertas",   "0", "#7c6af7"),
            ("Em Andamento",     "0", "#f59e0b"),
            ("Concluidas",       "0", "#10b981"),
            ("Clientes",         "0", "#3b82f6"),
        ]

        for titulo, valor, cor in dados_cards:
            card = self._criar_card(titulo, valor, cor)
            layout.addWidget(card)

        return frame

    def _criar_card(self, titulo, valor, cor):
        card = QFrame()
        card.setObjectName("card_resumo")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        label_valor = QLabel(valor)
        label_valor.setObjectName("card_valor")
        label_valor.setStyleSheet(f"color: {cor}; font-size: 32px; font-weight: bold;")
        layout.addWidget(label_valor)

        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("card_titulo")
        layout.addWidget(label_titulo)

        return card

    def _sair(self):
        from app.views.tela_login import TelaLogin
        self.tela_login = TelaLogin()
        self.tela_login.login_sucesso.connect(self._reabrir_principal)
        self.tela_login.show()
        self.close()

    def _reabrir_principal(self, usuario):
        self.nova_janela = JanelaPrincipal(usuario)
        self.nova_janela.show()
        self.tela_login.close()

    def _estilos(self):
        return """
            QMainWindow, QWidget {
                background-color: #0f1117;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#sidebar {
                background-color: #1a1d27;
                border-right: 1px solid #2e3347;
            }
            QLabel#sidebar_logo {
                font-size: 20px;
                font-weight: bold;
                color: #7c6af7;
                padding: 4px 8px;
            }
            QPushButton#btn_menu {
                text-align: left;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                color: #9ca3af;
            }
            QPushButton#btn_menu:hover {
                background-color: #252836;
                color: #e0e0e0;
            }
            QPushButton#btn_menu:checked {
                background-color: #2d2b55;
                color: #7c6af7;
                font-weight: bold;
            }
            QPushButton#btn_sair {
                text-align: left;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                color: #6b7280;
            }
            QPushButton#btn_sair:hover {
                background-color: #2d1f1f;
                color: #f87171;
            }
            QWidget#area_conteudo {
                background-color: #0f1117;
            }
            QLabel#titulo_pagina {
                font-size: 22px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#label_usuario {
                font-size: 13px;
                color: #9ca3af;
            }
            QFrame#card_resumo {
                background-color: #1a1d27;
                border-radius: 12px;
                border: 1px solid #2e3347;
                min-height: 120px;
            }
            QLabel#card_titulo {
                font-size: 12px;
                color: #6b7280;
            }
            QLabel#placeholder {
                font-size: 15px;
                color: #4b5563;
            }
        """