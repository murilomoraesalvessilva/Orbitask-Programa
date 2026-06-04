# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QStackedWidget,
    QCalendarWidget, QScrollArea, QToolTip
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
from app.models.cliente import contar_clientes
from app.models.ordem_servico import contar_por_status, listar_prazos
from app.models.equipamento import contar_equipamentos
from app.models.financeiro import resumo_financeiro


def fmt_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


ESTILO_GLOBAL = """
    * { font-family: 'Segoe UI', sans-serif; outline: none; }
    QMainWindow, QWidget { background-color: #06101e; color: #c8dff5; }
    QScrollBar:vertical { background: #0a1828; width: 6px; border-radius: 3px; }
    QScrollBar::handle:vertical { background: #1a4a7a; border-radius: 3px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QScrollBar:horizontal { background: #0a1828; height: 6px; border-radius: 3px; }
    QScrollBar::handle:horizontal { background: #1a4a7a; border-radius: 3px; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
    QFrame#sidebar { background-color: #040c18; border-right: 1px solid #0a1e34; }
    QLabel#sidebar_logo { font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 1px; padding: 4px 8px; }
    QLabel#sidebar_logo_sub { font-size: 10px; color: #1a4a7a; letter-spacing: 1px; padding: 0 10px; }
    QPushButton#btn_menu { text-align: left; background-color: transparent; border: none; border-radius: 6px; padding: 11px 14px; font-size: 13px; color: #3a6a9a; }
    QPushButton#btn_menu:hover { background-color: #0a1e30; color: #7ab8f5; }
    QPushButton#btn_menu:checked { background-color: #0d2540; color: #4a9eff; font-weight: 600; border-left: 3px solid #1a6fd4; padding-left: 11px; }
    QPushButton#btn_sair { text-align: left; background-color: transparent; border: none; border-radius: 6px; padding: 11px 14px; font-size: 13px; color: #2a4a6a; }
    QPushButton#btn_sair:hover { background-color: #1a0a0a; color: #e05555; }
    QFrame#frame_usuario { background-color: #0a1828; border-radius: 8px; border: 1px solid #0d2440; }
    QLabel#sidebar_nome { font-size: 13px; font-weight: 600; color: #c8dff5; }
    QLabel#sidebar_perfil { font-size: 11px; color: #1a6fd4; }
    QWidget#area_conteudo { background-color: #06101e; }
    QLabel#titulo_pagina { font-size: 20px; font-weight: 700; color: #ffffff; }
    QLabel#label_usuario { font-size: 13px; color: #2a5a8a; }
    QFrame#header_line { background-color: #0a1e34; max-height: 1px; min-height: 1px; }
    QFrame#card_resumo { background-color: #080f1e; border-radius: 10px; border: 1px solid #0a1e34; }
    QFrame#card_resumo:hover { border: 1px solid #1a4a7a; background-color: #0a1428; }
    QLabel#card_titulo { font-size: 11px; color: #2a5a8a; font-weight: 600; letter-spacing: 0.5px; }
    QTableWidget { background-color: #080f1e; border: 1px solid #0a1e34; border-radius: 10px; gridline-color: transparent; font-size: 13px; color: #c8dff5; alternate-background-color: #0a1428; selection-background-color: #0d2540; selection-color: #4a9eff; }
    QTableWidget::item { padding: 8px; border: none; }
    QTableWidget::item:selected { background-color: #0d2540; color: #4a9eff; }
    QHeaderView::section { background-color: #06101e; color: #2a5a8a; font-size: 11px; font-weight: 700; padding: 12px 8px; border: none; border-bottom: 1px solid #0a1e34; letter-spacing: 0.5px; }
    QLineEdit { background-color: #080f1e; border: 1px solid #0a1e34; border-radius: 6px; padding: 8px 14px; font-size: 13px; color: #c8dff5; }
    QLineEdit:focus { border: 1px solid #1a6fd4; background-color: #0a1428; }
    QComboBox { background-color: #080f1e; border: 1px solid #0a1e34; border-radius: 6px; padding: 8px 14px; font-size: 13px; color: #c8dff5; }
    QComboBox:focus { border: 1px solid #1a6fd4; }
    QComboBox::drop-down { border: none; width: 20px; }
    QComboBox QAbstractItemView { background-color: #0a1828; color: #c8dff5; border: 1px solid #0d2440; selection-background-color: #1a6fd4; outline: none; }
    QTextEdit { background-color: #080f1e; border: 1px solid #0a1e34; border-radius: 6px; padding: 8px 14px; font-size: 13px; color: #c8dff5; }
    QTextEdit:focus { border: 1px solid #1a6fd4; }
    QPushButton#btn_primario { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a6fd4,stop:1 #0d4fa0); color: white; border: none; border-radius: 6px; padding: 9px 18px; font-size: 13px; font-weight: 600; }
    QPushButton#btn_primario:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2a7fe4,stop:1 #1a5fc0); }
    QPushButton#btn_secundario { background-color: #0a1828; color: #3a6a9a; border: 1px solid #0d2440; border-radius: 6px; padding: 9px 18px; font-size: 13px; }
    QPushButton#btn_secundario:hover { background-color: #0d2040; color: #c8dff5; border-color: #1a4a7a; }
    QPushButton#btn_editar { background-color: #0a1e30; color: #4a9eff; border: 1px solid #0d2e4e; border-radius: 5px; padding: 4px 12px; font-size: 12px; }
    QPushButton#btn_editar:hover { background-color: #1a6fd4; color: white; border-color: #1a6fd4; }
    QPushButton#btn_excluir { background-color: #1a0808; color: #e05555; border: 1px solid #3a1010; border-radius: 5px; padding: 4px 12px; font-size: 12px; }
    QPushButton#btn_excluir:hover { background-color: #e05555; color: white; border-color: #e05555; }
    QPushButton#btn_ativar { background-color: #0a1e18; color: #2ab87a; border: 1px solid #0d3020; border-radius: 5px; padding: 4px 12px; font-size: 12px; }
    QPushButton#btn_ativar:hover { background-color: #2ab87a; color: white; }
    QPushButton#btn_desativar { background-color: #1a1008; color: #e0a020; border: 1px solid #3a2808; border-radius: 5px; padding: 4px 12px; font-size: 12px; }
    QPushButton#btn_desativar:hover { background-color: #e0a020; color: white; }
    QDialog { background-color: #08121e; color: #c8dff5; }
    QLabel#titulo { font-size: 17px; font-weight: 700; color: #ffffff; }
    QLabel#label_campo { font-size: 11px; font-weight: 700; color: #2a5a8a; letter-spacing: 0.8px; }
    QLabel#label_contador { font-size: 12px; color: #1a4a7a; }
    QLabel#titulo_secao { font-size: 20px; font-weight: 700; color: #ffffff; }
    QTabWidget::pane { border: 1px solid #0a1e34; border-radius: 8px; background-color: #08121e; }
    QTabBar::tab { background-color: #080f1e; color: #2a5a8a; padding: 9px 22px; border: none; font-size: 13px; }
    QTabBar::tab:selected { background-color: #0d2540; color: #4a9eff; font-weight: 600; border-bottom: 2px solid #1a6fd4; }
    QMessageBox { background-color: #08121e; color: #c8dff5; }
    QMessageBox QPushButton { background-color: #0d2540; color: #4a9eff; border: 1px solid #1a4a7a; border-radius: 5px; padding: 6px 20px; min-width: 80px; }
    QMessageBox QPushButton:hover { background-color: #1a6fd4; color: white; }
    QLabel#placeholder { font-size: 14px; color: #1a3a5a; }
    QLabel#label_dica { font-size: 12px; color: #1a4a7a; }
    QLabel#label_sub { font-size: 13px; color: #2a5a8a; }
"""


class JanelaPrincipal(QMainWindow):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Orbitask")
        self.setMinimumSize(1200, 700)
        self.showMaximized()
        self.setStyleSheet(ESTILO_GLOBAL)
        self._construir_interface()
        self._atualizar_cards()

    def _construir_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_raiz = QHBoxLayout(widget_central)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        layout_raiz.addWidget(self._criar_sidebar())

        area = QWidget()
        area.setObjectName("area_conteudo")
        lc = QVBoxLayout(area)
        lc.setContentsMargins(0, 0, 0, 0)
        lc.setSpacing(0)
        lc.addWidget(self._criar_header())

        linha = QFrame()
        linha.setObjectName("header_line")
        lc.addWidget(linha)

        self.stack = QStackedWidget()

        self.pagina_dashboard = self._criar_pagina_dashboard()
        self.stack.addWidget(self.pagina_dashboard)                           # 0

        from app.views.tela_ordens import TelaOrdens
        self.pagina_ordens = TelaOrdens()
        self.stack.addWidget(self._wrapper(self.pagina_ordens))               # 1

        from app.views.tela_clientes import TelaClientes
        self.pagina_clientes = TelaClientes()
        self.stack.addWidget(self._wrapper(self.pagina_clientes))             # 2

        from app.views.tela_equipamentos import TelaEquipamentos
        self.pagina_equipamentos = TelaEquipamentos()
        self.stack.addWidget(self._wrapper(self.pagina_equipamentos))         # 3

        from app.views.tela_financeiro import TelaFinanceiro
        self.pagina_financeiro = TelaFinanceiro()
        self.stack.addWidget(self._wrapper(self.pagina_financeiro))           # 4

        from app.views.tela_usuarios import TelaUsuarios
        self.pagina_usuarios = TelaUsuarios(usuario_logado=self.usuario)
        self.stack.addWidget(self._wrapper(self.pagina_usuarios))             # 5

        from app.views.tela_relatorios import TelaRelatorios
        self.pagina_relatorios = TelaRelatorios()
        self.stack.addWidget(self._wrapper(self.pagina_relatorios))           # 6

        lc.addWidget(self.stack)
        layout_raiz.addWidget(area, stretch=1)

    def _wrapper(self, widget):
        container = QWidget()
        container.setObjectName("area_conteudo")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.addWidget(widget)
        return container

    def _criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 24, 12, 20)
        layout.setSpacing(2)

        logo = QLabel("Orbitask")
        logo.setObjectName("sidebar_logo")
        layout.addWidget(logo)

        logo_sub = QLabel("GESTAO DE SERVICOS")
        logo_sub.setObjectName("sidebar_logo_sub")
        layout.addWidget(logo_sub)

        layout.addSpacing(28)

        sep1 = QLabel("  MENU PRINCIPAL")
        sep1.setStyleSheet("font-size:10px; color:#0d2a44; font-weight:700; letter-spacing:1.5px; padding:4px 6px;")
        layout.addWidget(sep1)
        layout.addSpacing(4)

        self.botoes_menu = []
        for texto, idx in [("Dashboard",0),("Ordens de Servico",1),("Clientes",2),("Equipamentos",3),("Financeiro",4)]:
            btn = QPushButton(texto)
            btn.setObjectName("btn_menu")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, i=idx: self._navegar(i))
            layout.addWidget(btn)
            self.botoes_menu.append(btn)

        layout.addSpacing(16)
        sep2 = QLabel("  ADMINISTRACAO")
        sep2.setStyleSheet("font-size:10px; color:#0d2a44; font-weight:700; letter-spacing:1.5px; padding:4px 6px;")
        layout.addWidget(sep2)
        layout.addSpacing(4)

        for texto, idx in [("Usuarios",5),("Relatorios",6)]:
            btn = QPushButton(texto)
            btn.setObjectName("btn_menu")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, i=idx: self._navegar(i))
            layout.addWidget(btn)
            self.botoes_menu.append(btn)

        self.botoes_menu[0].setChecked(True)
        layout.addStretch()

        frame_u = QFrame()
        frame_u.setObjectName("frame_usuario")
        lu = QVBoxLayout(frame_u)
        lu.setContentsMargins(12, 10, 12, 10)
        lu.setSpacing(2)
        ln = QLabel(self.usuario["nome"])
        ln.setObjectName("sidebar_nome")
        lu.addWidget(ln)
        lp = QLabel("Administrador" if self.usuario["perfil"] == "admin" else "Tecnico")
        lp.setObjectName("sidebar_perfil")
        lu.addWidget(lp)
        layout.addWidget(frame_u)
        layout.addSpacing(8)

        btn_sair = QPushButton("  Sair do Sistema")
        btn_sair.setObjectName("btn_sair")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.setFixedHeight(40)
        btn_sair.clicked.connect(self._sair)
        layout.addWidget(btn_sair)

        return sidebar

    def _criar_header(self):
        frame = QFrame()
        frame.setObjectName("area_conteudo")
        frame.setFixedHeight(60)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(32, 0, 32, 0)

        self.label_titulo_pagina = QLabel("Dashboard")
        self.label_titulo_pagina.setObjectName("titulo_pagina")
        layout.addWidget(self.label_titulo_pagina)

        layout.addStretch()

        hoje = QDate.currentDate().toString("dddd, dd 'de' MMMM 'de' yyyy")
        label_data = QLabel(hoje)
        label_data.setStyleSheet("font-size:12px; color:#1a4a7a;")
        layout.addWidget(label_data)

        layout.addSpacing(24)

        nome = self.usuario["nome"].split()[0]
        label_u = QLabel(f"Ola, {nome}")
        label_u.setObjectName("label_usuario")
        layout.addWidget(label_u)

        return frame

    def _criar_pagina_dashboard(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("area_conteudo")

        pagina = QWidget()
        pagina.setObjectName("area_conteudo")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Secao OS
        layout.addWidget(self._secao("VISAO GERAL"))
        linha1 = QHBoxLayout()
        linha1.setSpacing(12)
        self.card_abertas      = self._card("Abertas",      "0",        "#4a9eff")
        self.card_andamento    = self._card("Em Andamento", "0",        "#f0a030")
        self.card_concluidas   = self._card("Concluidas",   "0",        "#2ab87a")
        self.card_clientes     = self._card("Clientes",     "0",        "#8a6aff")
        self.card_equipamentos = self._card("Equipamentos", "0",        "#e05a9a")
        for c in [self.card_abertas, self.card_andamento, self.card_concluidas,
                  self.card_clientes, self.card_equipamentos]:
            linha1.addWidget(c)
        layout.addLayout(linha1)

        # Secao Financeiro
        layout.addSpacing(4)
        layout.addWidget(self._secao("FINANCEIRO"))
        linha2 = QHBoxLayout()
        linha2.setSpacing(12)
        self.card_receita_total    = self._card("Receita Total",    "R$ 0,00", "#4a9eff")
        self.card_receita_recebida = self._card("Receita Recebida", "R$ 0,00", "#2ab87a")
        self.card_a_receber        = self._card("A Receber",        "R$ 0,00", "#f0a030")
        self.card_os_pagas         = self._card("OS Pagas",         "0",       "#8a6aff")
        for c in [self.card_receita_total, self.card_receita_recebida,
                  self.card_a_receber, self.card_os_pagas]:
            linha2.addWidget(c)
        layout.addLayout(linha2)

        # Calendario + OS recentes
        layout.addSpacing(4)
        layout.addWidget(self._secao("AGENDA E ATIVIDADE RECENTE"))
        linha3 = QHBoxLayout()
        linha3.setSpacing(12)
        linha3.addWidget(self._criar_calendario(), stretch=42)
        linha3.addWidget(self._criar_recentes(), stretch=58)
        layout.addLayout(linha3)

        scroll.setWidget(pagina)
        return scroll

    def _criar_calendario(self):
        frame = QFrame()
        frame.setObjectName("card_resumo")
        lc = QVBoxLayout(frame)
        lc.setContentsMargins(20, 16, 20, 16)
        lc.setSpacing(10)

        label_cal = QLabel("CALENDARIO DE PRAZOS")
        label_cal.setObjectName("card_titulo")
        lc.addWidget(label_cal)

        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(False)
        self.calendario.setNavigationBarVisible(True)
        self.calendario.setStyleSheet("""
            QCalendarWidget { background-color: transparent; color: #c8dff5; border: none; }
            QCalendarWidget QToolButton {
                background-color: transparent; color: #4a9eff;
                border: none; font-size: 13px; font-weight: 600; padding: 4px 8px;
            }
            QCalendarWidget QToolButton:hover { background-color: #0d2540; border-radius: 4px; }
            QCalendarWidget QMenu { background-color: #0a1828; color: #c8dff5; border: 1px solid #0d2440; }
            QCalendarWidget QSpinBox {
                background-color: #0a1828; color: #4a9eff;
                border: 1px solid #0d2440; border-radius: 4px; padding: 2px 6px;
            }
            QCalendarWidget QAbstractItemView {
                background-color: transparent; color: #c8dff5;
                selection-background-color: #1a6fd4; selection-color: white;
                outline: none; gridline-color: #0a1e34;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #1a3a5a; }
            QCalendarWidget #qt_calendar_navigationbar {
                background-color: transparent; border-bottom: 1px solid #0a1e34; padding: 4px;
            }
            QCalendarWidget #qt_calendar_prevmonth,
            QCalendarWidget #qt_calendar_nextmonth {
                color: #4a9eff; qproperty-icon: none;
                font-size: 16px; font-weight: bold; padding: 2px 8px;
            }
        """)

        # Reconecta sinal para atualizar destaque quando mudar mes
        self.calendario.currentPageChanged.connect(self._destacar_prazos)
        lc.addWidget(self.calendario)

        # Legenda
        leg = QHBoxLayout()
        leg.setSpacing(16)
        for cor, txt in [("#4a9eff", "OS Aberta"), ("#f0a030", "Em Andamento"), ("#e05555", "Vencida")]:
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background-color:{cor}; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
            tl = QLabel(txt)
            tl.setStyleSheet("font-size:11px; color:#2a5a8a;")
            leg.addWidget(dot)
            leg.addWidget(tl)
        leg.addStretch()
        lc.addLayout(leg)

        return frame

    def _criar_recentes(self):
        frame = QFrame()
        frame.setObjectName("card_resumo")
        lr = QVBoxLayout(frame)
        lr.setContentsMargins(20, 16, 20, 16)
        lr.setSpacing(10)

        label_rec = QLabel("ULTIMAS ORDENS DE SERVICO")
        label_rec.setObjectName("card_titulo")
        lr.addWidget(label_rec)

        self.lista_recentes = QVBoxLayout()
        self.lista_recentes.setSpacing(6)
        lr.addLayout(self.lista_recentes)
        lr.addStretch()

        return frame

    def _secao(self, texto):
        label = QLabel(texto)
        label.setStyleSheet("font-size:11px; font-weight:700; color:#1a4a7a; letter-spacing:1.5px;")
        return label

    def _card(self, titulo, valor, cor):
        card = QFrame()
        card.setObjectName("card_resumo")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(95)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(5)

        topo = QHBoxLayout()
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color:{cor}; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
        topo.addWidget(dot)
        topo.addStretch()
        layout.addLayout(topo)

        lv = QLabel(valor)
        lv.setStyleSheet(f"color:{cor}; font-size:24px; font-weight:700;")
        layout.addWidget(lv)

        lt = QLabel(titulo.upper())
        lt.setObjectName("card_titulo")
        layout.addWidget(lt)

        card._label_valor = lv
        return card

    def _destacar_prazos(self):
        """Marca os dias com OS pendentes no calendario com cores."""
        # Limpa formatos anteriores
        fmt_padrao = QTextCharFormat()
        self.calendario.setDateTextFormat(QDate(), fmt_padrao)

        hoje = QDate.currentDate()
        prazos = listar_prazos()

        for p in prazos:
            if not p.get("prazo"):
                continue
            try:
                partes = p["prazo"].split("-")
                data = QDate(int(partes[0]), int(partes[1]), int(partes[2]))
            except Exception:
                continue

            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold)

            if data < hoje:
                # Vencida
                fmt.setBackground(QColor("#3a0808"))
                fmt.setForeground(QColor("#e05555"))
            elif p["status"] == "em_andamento":
                # Em andamento
                fmt.setBackground(QColor("#2a1a00"))
                fmt.setForeground(QColor("#f0a030"))
            else:
                # Aberta
                fmt.setBackground(QColor("#001a3a"))
                fmt.setForeground(QColor("#4a9eff"))

            self.calendario.setDateTextFormat(data, fmt)

        # Destaca hoje sempre
        fmt_hoje = QTextCharFormat()
        fmt_hoje.setFontWeight(QFont.Weight.Bold)
        fmt_hoje.setForeground(QColor("#ffffff"))
        fmt_hoje.setBackground(QColor("#1a6fd4"))
        self.calendario.setDateTextFormat(hoje, fmt_hoje)

    def _atualizar_cards(self):
        contagens = contar_por_status()
        self.card_abertas._label_valor.setText(str(contagens.get("aberta", 0)))
        self.card_andamento._label_valor.setText(str(contagens.get("em_andamento", 0)))
        self.card_concluidas._label_valor.setText(str(contagens.get("concluida", 0)))
        self.card_clientes._label_valor.setText(str(contar_clientes()))
        self.card_equipamentos._label_valor.setText(str(contar_equipamentos()))

        res = resumo_financeiro()
        self.card_receita_total._label_valor.setText(fmt_brl(res.get("receita_total", 0)))
        self.card_receita_recebida._label_valor.setText(fmt_brl(res.get("receita_recebida", 0)))
        self.card_a_receber._label_valor.setText(fmt_brl(res.get("receita_pendente", 0)))
        self.card_os_pagas._label_valor.setText(str(res.get("os_pagas", 0)))

        self._destacar_prazos()
        self._atualizar_recentes()

    def _atualizar_recentes(self):
        while self.lista_recentes.count():
            item = self.lista_recentes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from app.models.ordem_servico import listar_ordens
        ordens = listar_ordens()[:7]

        STATUS_COR = {
            "aberta":       ("#4a9eff", "Aberta"),
            "em_andamento": ("#f0a030", "Em Andamento"),
            "concluida":    ("#2ab87a", "Concluida"),
            "cancelada":    ("#e05555", "Cancelada"),
        }

        for o in ordens:
            item = QFrame()
            item.setStyleSheet("""
                QFrame { background-color: #0a1428; border-radius: 6px; border: 1px solid #0a1e34; }
                QFrame:hover { border-color: #1a4a7a; background-color: #0d1e38; }
            """)
            li = QHBoxLayout(item)
            li.setContentsMargins(12, 8, 12, 8)
            li.setSpacing(10)

            cor, txt_status = STATUS_COR.get(o["status"], ("#fff", o["status"]))

            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background-color:{cor}; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
            li.addWidget(dot)

            col = QVBoxLayout()
            col.setSpacing(1)
            titulo = QLabel(f"#{o['id']} — {o['titulo'][:40]}")
            titulo.setStyleSheet("font-size:12px; color:#c8dff5; font-weight:500;")
            col.addWidget(titulo)

            cliente = QLabel(o.get("cliente_nome") or "Sem cliente")
            cliente.setStyleSheet("font-size:11px; color:#2a5a8a;")
            col.addWidget(cliente)
            li.addLayout(col, stretch=1)

            col_dir = QVBoxLayout()
            col_dir.setSpacing(1)
            col_dir.setAlignment(Qt.AlignmentFlag.AlignRight)

            status = QLabel(txt_status)
            status.setStyleSheet(f"font-size:11px; color:{cor}; font-weight:600;")
            status.setAlignment(Qt.AlignmentFlag.AlignRight)
            col_dir.addWidget(status)

            prazo = o.get("prazo")
            if prazo:
                try:
                    partes = prazo.split("-")
                    data_fmt = f"{partes[2]}/{partes[1]}/{partes[0]}"
                    hoje = QDate.currentDate()
                    data_q = QDate(int(partes[0]), int(partes[1]), int(partes[2]))
                    cor_prazo = "#e05555" if data_q < hoje else "#2a5a8a"
                    label_prazo = QLabel(f"Prazo: {data_fmt}")
                    label_prazo.setStyleSheet(f"font-size:10px; color:{cor_prazo};")
                    label_prazo.setAlignment(Qt.AlignmentFlag.AlignRight)
                    col_dir.addWidget(label_prazo)
                except Exception:
                    pass

            li.addLayout(col_dir)
            self.lista_recentes.addWidget(item)

        if not ordens:
            vazio = QLabel("Nenhuma ordem cadastrada ainda.")
            vazio.setObjectName("placeholder")
            vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lista_recentes.addWidget(vazio)

    def _navegar(self, indice: int):
        titulos = ["Dashboard", "Ordens de Servico", "Clientes",
                   "Equipamentos", "Financeiro", "Usuarios", "Relatorios"]
        for i, btn in enumerate(self.botoes_menu):
            btn.setChecked(i == indice)
        self.label_titulo_pagina.setText(titulos[indice])
        self.stack.setCurrentIndex(indice)

        if indice == 0:   self._atualizar_cards()
        elif indice == 1: self.pagina_ordens._aplicar_filtros()
        elif indice == 2: self.pagina_clientes._carregar_clientes()
        elif indice == 3: self.pagina_equipamentos._carregar_equipamentos()
        elif indice == 4: self.pagina_financeiro._aplicar_filtros()
        elif indice == 5: self.pagina_usuarios._carregar_usuarios()

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