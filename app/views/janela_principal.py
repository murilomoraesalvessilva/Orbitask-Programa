# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt
from app.models.cliente import contar_clientes
from app.models.ordem_servico import contar_por_status
from app.models.equipamento import contar_equipamentos
from app.models.financeiro import resumo_financeiro


def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class JanelaPrincipal(QMainWindow):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Orbitask")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._atualizar_cards()

    def _construir_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_raiz = QHBoxLayout(widget_central)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        sidebar = self._criar_sidebar()
        layout_raiz.addWidget(sidebar)

        area = QWidget()
        area.setObjectName("area_conteudo")
        self.layout_conteudo = QVBoxLayout(area)
        self.layout_conteudo.setContentsMargins(32, 32, 32, 32)
        self.layout_conteudo.setSpacing(24)

        header = self._criar_header()
        self.layout_conteudo.addWidget(header)

        self.stack = QStackedWidget()

        # Pagina 0: Dashboard
        self.pagina_dashboard = self._criar_pagina_dashboard()
        self.stack.addWidget(self.pagina_dashboard)

        # Pagina 1: Ordens de Servico
        from app.views.tela_ordens import TelaOrdens
        self.pagina_ordens = TelaOrdens()
        self.stack.addWidget(self.pagina_ordens)

        # Pagina 2: Clientes
        from app.views.tela_clientes import TelaClientes
        self.pagina_clientes = TelaClientes()
        self.stack.addWidget(self.pagina_clientes)

        # Pagina 3: Equipamentos
        from app.views.tela_equipamentos import TelaEquipamentos
        self.pagina_equipamentos = TelaEquipamentos()
        self.stack.addWidget(self.pagina_equipamentos)

        # Pagina 4: Financeiro
        from app.views.tela_financeiro import TelaFinanceiro
        self.pagina_financeiro = TelaFinanceiro()
        self.stack.addWidget(self.pagina_financeiro)

        # Pagina 5: Usuarios
        from app.views.tela_usuarios import TelaUsuarios
        self.pagina_usuarios = TelaUsuarios(usuario_logado=self.usuario)
        self.stack.addWidget(self.pagina_usuarios)

        # Pagina 6: Relatorios
        from app.views.tela_relatorios import TelaRelatorios
        self.pagina_relatorios = TelaRelatorios()
        self.stack.addWidget(self.pagina_relatorios)

        self.layout_conteudo.addWidget(self.stack)
        layout_raiz.addWidget(area, stretch=1)

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
            "Equipamentos",
            "Financeiro",
            "Usuarios",
            "Relatorios",
        ]

        self.botoes_menu = []
        for i, texto in enumerate(itens):
            btn = QPushButton(texto)
            btn.setObjectName("btn_menu")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, idx=i: self._navegar(idx))
            layout.addWidget(btn)
            self.botoes_menu.append(btn)

        self.botoes_menu[0].setChecked(True)
        layout.addStretch()

        frame_usuario = QFrame()
        frame_usuario.setObjectName("frame_usuario")
        layout_u = QVBoxLayout(frame_usuario)
        layout_u.setContentsMargins(8, 12, 8, 12)
        layout_u.setSpacing(2)

        label_nome = QLabel(self.usuario["nome"].split()[0])
        label_nome.setObjectName("sidebar_nome")
        layout_u.addWidget(label_nome)

        label_perfil = QLabel(
            "Administrador" if self.usuario["perfil"] == "admin" else "Tecnico"
        )
        label_perfil.setObjectName("sidebar_perfil")
        layout_u.addWidget(label_perfil)

        layout.addWidget(frame_usuario)

        btn_sair = QPushButton("Sair")
        btn_sair.setObjectName("btn_sair")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.clicked.connect(self._sair)
        layout.addWidget(btn_sair)

        return sidebar

    def _criar_header(self):
        frame = QFrame()
        layout_header = QHBoxLayout(frame)
        layout_header.setContentsMargins(0, 0, 0, 0)

        self.label_titulo_pagina = QLabel("Dashboard")
        self.label_titulo_pagina.setObjectName("titulo_pagina")
        layout_header.addWidget(self.label_titulo_pagina)

        layout_header.addStretch()

        nome = self.usuario["nome"].split()[0]
        label_usuario = QLabel(f"Ola, {nome}")
        label_usuario.setObjectName("label_usuario")
        layout_header.addWidget(label_usuario)

        return frame

    def _criar_pagina_dashboard(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Linha 1: cards de OS
        linha1 = QHBoxLayout()
        linha1.setSpacing(16)
        self.card_abertas    = self._criar_card("Ordens Abertas", "0",      "#7c6af7")
        self.card_andamento  = self._criar_card("Em Andamento",   "0",      "#f59e0b")
        self.card_concluidas = self._criar_card("Concluidas",     "0",      "#10b981")
        self.card_clientes   = self._criar_card("Clientes",       "0",      "#3b82f6")
        self.card_equipamentos = self._criar_card("Equipamentos", "0",      "#ec4899")
        for c in [self.card_abertas, self.card_andamento, self.card_concluidas,
                  self.card_clientes, self.card_equipamentos]:
            linha1.addWidget(c)

        frame1 = QFrame()
        frame1.setLayout(linha1)
        layout.addWidget(frame1)

        # Linha 2: cards financeiros
        linha2 = QHBoxLayout()
        linha2.setSpacing(16)
        self.card_receita_total    = self._criar_card("Receita Total",    "R$ 0,00", "#7c6af7", grande=True)
        self.card_receita_recebida = self._criar_card("Receita Recebida", "R$ 0,00", "#10b981", grande=True)
        self.card_a_receber        = self._criar_card("A Receber",        "R$ 0,00", "#f59e0b", grande=True)
        self.card_os_pagas         = self._criar_card("OS Pagas",         "0",       "#3b82f6", grande=True)
        for c in [self.card_receita_total, self.card_receita_recebida,
                  self.card_a_receber, self.card_os_pagas]:
            linha2.addWidget(c)

        frame2 = QFrame()
        frame2.setLayout(linha2)
        layout.addWidget(frame2)

        placeholder = QLabel("Bem-vindo ao Orbitask! Selecione uma opcao no menu lateral.")
        placeholder.setObjectName("placeholder")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder, stretch=1)

        return pagina

    def _criar_card(self, titulo, valor, cor, grande=False):
        card = QFrame()
        card.setObjectName("card_resumo")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        tamanho = "20px" if grande else "26px"
        lv = QLabel(valor)
        lv.setObjectName("card_valor")
        lv.setStyleSheet(f"color: {cor}; font-size: {tamanho}; font-weight: bold;")
        layout.addWidget(lv)

        lt = QLabel(titulo)
        lt.setObjectName("card_titulo")
        layout.addWidget(lt)

        card._label_valor = lv
        return card

    def _atualizar_cards(self):
        contagens = contar_por_status()
        self.card_abertas._label_valor.setText(str(contagens.get("aberta", 0)))
        self.card_andamento._label_valor.setText(str(contagens.get("em_andamento", 0)))
        self.card_concluidas._label_valor.setText(str(contagens.get("concluida", 0)))
        self.card_clientes._label_valor.setText(str(contar_clientes()))
        self.card_equipamentos._label_valor.setText(str(contar_equipamentos()))

        res = resumo_financeiro()
        self.card_receita_total._label_valor.setText(formatar_brl(res.get("receita_total", 0)))
        self.card_receita_recebida._label_valor.setText(formatar_brl(res.get("receita_recebida", 0)))
        self.card_a_receber._label_valor.setText(formatar_brl(res.get("receita_pendente", 0)))
        self.card_os_pagas._label_valor.setText(str(res.get("os_pagas", 0)))

    def _navegar(self, indice: int):
        titulos = ["Dashboard", "Ordens de Servico", "Clientes",
                   "Equipamentos", "Financeiro", "Usuarios", "Relatorios"]

        for i, btn in enumerate(self.botoes_menu):
            btn.setChecked(i == indice)

        self.label_titulo_pagina.setText(titulos[indice])
        self.stack.setCurrentIndex(indice)

        if indice == 0:
            self._atualizar_cards()
        elif indice == 1:
            self.pagina_ordens._aplicar_filtros()
        elif indice == 2:
            self.pagina_clientes._carregar_clientes()
        elif indice == 3:
            self.pagina_equipamentos._carregar_equipamentos()
        elif indice == 4:
            self.pagina_financeiro._aplicar_filtros()
        elif indice == 5:
            self.pagina_usuarios._carregar_usuarios()

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
            QFrame#frame_usuario {
                background-color: #252836;
                border-radius: 8px;
                border: 1px solid #2e3347;
            }
            QLabel#sidebar_nome {
                font-size: 13px;
                font-weight: bold;
                color: #e0e0e0;
            }
            QLabel#sidebar_perfil {
                font-size: 11px;
                color: #7c6af7;
            }
            QWidget#area_conteudo { background-color: #0f1117; }
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
                min-height: 90px;
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