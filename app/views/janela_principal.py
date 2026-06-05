# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QStackedWidget,
    QCalendarWidget, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QTimer, QTime
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QCursor
from app.models.cliente import contar_clientes
from app.models.ordem_servico import contar_por_status, listar_prazos, listar_ordens
from app.models.equipamento import contar_equipamentos
from app.models.financeiro import resumo_financeiro


def fmt_brl(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


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
    QLabel#sidebar_nome { font-size: 13px; font-weight: 600; color: #c8dff5; background: transparent; }
    QLabel#sidebar_perfil { font-size: 11px; color: #1a6fd4; background: transparent; }

    QWidget#area_conteudo { background-color: #06101e; }
    QLabel#titulo_pagina { font-size: 20px; font-weight: 700; color: #ffffff; background: transparent; }
    QLabel#label_usuario { font-size: 13px; color: #2a5a8a; background: transparent; }
    QFrame#header_line { background-color: #0a1e34; max-height: 1px; min-height: 1px; }
    QFrame#card_resumo { background-color: #080f1e; border-radius: 10px; border: 1px solid #0a1e34; }
    QFrame#card_resumo:hover { border: 1px solid #1a4a7a; background-color: #0a1428; }
    QLabel#card_titulo { font-size: 11px; color: #2a5a8a; font-weight: 600; letter-spacing: 0.5px; background: transparent; }
    QLabel#label_contador { font-size: 12px; color: #1a4a7a; background: transparent; }
    QLabel#titulo_secao { font-size: 20px; font-weight: 700; color: #ffffff; background: transparent; }
    QLabel#label_sub { font-size: 13px; color: #2a5a8a; background: transparent; }
    QLabel#label_dica { font-size: 12px; color: #1a4a7a; background: transparent; }
    QLabel#placeholder { font-size: 14px; color: #1a3a5a; background: transparent; }

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

    QDialog, QDialog QWidget { background-color: #08121e; color: #c8dff5; }
    QTabWidget::pane { border: 1px solid #0a1e34; border-radius: 8px; background-color: #08121e; }
    QTabBar::tab { background-color: #080f1e; color: #2a5a8a; padding: 9px 22px; border: none; font-size: 13px; }
    QTabBar::tab:selected { background-color: #0d2540; color: #4a9eff; font-weight: 600; border-bottom: 2px solid #1a6fd4; }
    QMessageBox { background-color: #08121e; color: #c8dff5; }
    QMessageBox QPushButton { background-color: #0d2540; color: #4a9eff; border: 1px solid #1a4a7a; border-radius: 5px; padding: 6px 20px; min-width: 80px; }
    QMessageBox QPushButton:hover { background-color: #1a6fd4; color: white; }
    QDateEdit { background-color: #0d1e30; border: 1px solid #0d2e4e; border-radius: 6px; padding: 9px 12px; font-size: 13px; color: #c8dff5; }
    QDateEdit:focus { border: 1px solid #1a6fd4; }
    QDateEdit::drop-down { border: none; }
"""

# Cores e labels dos atalhos do dashboard
ATALHOS = [
    ("Ordens de Servico", 1, "#1a6fd4", "#0d2540"),
    ("Clientes",          2, "#8a6aff", "#1a1040"),
    ("Equipamentos",      3, "#e05a9a", "#2a0a1a"),
    ("Financeiro",        4, "#2ab87a", "#001a10"),
    ("Usuarios",          5, "#f0a030", "#2a1a00"),
    ("Relatorios",        6, "#4a9eff", "#001a3a"),
]

STATUS_COR = {
    "aberta":       ("#4a9eff", "Aberta"),
    "em_andamento": ("#f0a030", "Em Andamento"),
    "concluida":    ("#2ab87a", "Concluida"),
    "cancelada":    ("#e05555", "Cancelada"),
}


class JanelaPrincipal(QMainWindow):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Orbitask")
        self.setMinimumSize(1280, 720)
        self.showMaximized()
        self.setStyleSheet(ESTILO_GLOBAL)
        self._construir_interface()
        self._atualizar_dashboard()

        # Timer para o relogio
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._atualizar_relogio)
        self.timer.start(1000)

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

        sep = QFrame()
        sep.setObjectName("header_line")
        lc.addWidget(sep)

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
        c = QWidget()
        c.setObjectName("area_conteudo")
        l = QVBoxLayout(c)
        l.setContentsMargins(32, 28, 32, 28)
        l.addWidget(widget)
        return c

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
        sub = QLabel("GESTAO DE SERVICOS")
        sub.setObjectName("sidebar_logo_sub")
        layout.addWidget(sub)
        layout.addSpacing(24)

        def sep_label(txt):
            l = QLabel(f"  {txt}")
            l.setStyleSheet("font-size:10px; color:#0d2a44; font-weight:700; letter-spacing:1.5px; padding:4px 6px; background:transparent;")
            return l

        layout.addWidget(sep_label("MENU PRINCIPAL"))
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

        layout.addSpacing(12)
        layout.addWidget(sep_label("ADMINISTRACAO"))
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

        fu = QFrame()
        fu.setObjectName("frame_usuario")
        lu = QVBoxLayout(fu)
        lu.setContentsMargins(12, 10, 12, 10)
        lu.setSpacing(2)
        ln = QLabel(self.usuario["nome"])
        ln.setObjectName("sidebar_nome")
        lu.addWidget(ln)
        lp = QLabel("Administrador" if self.usuario["perfil"] == "admin" else "Tecnico")
        lp.setObjectName("sidebar_perfil")
        lu.addWidget(lp)
        layout.addWidget(fu)
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

        # Relogio
        self.label_relogio = QLabel()
        self.label_relogio.setStyleSheet("font-size:15px; font-weight:700; color:#4a9eff; background:transparent; padding: 4px 12px; border: 1px solid #0a1e34; border-radius:6px;")
        self._atualizar_relogio()
        layout.addWidget(self.label_relogio)

        layout.addSpacing(16)

        nome = self.usuario["nome"].split()[0]
        label_u = QLabel(f"Ola, {nome}")
        label_u.setObjectName("label_usuario")
        layout.addWidget(label_u)
        return frame

    def _atualizar_relogio(self):
        agora = QTime.currentTime().toString("hh:mm:ss")
        self.label_relogio.setText(agora)

    def _criar_pagina_dashboard(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("area_conteudo")

        pagina = QWidget()
        pagina.setObjectName("area_conteudo")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(16)

        # --- ATALHOS DE NAVEGACAO (estilo Map-OS) ---
        grid_atalhos = QGridLayout()
        grid_atalhos.setSpacing(12)

        for i, (nome, idx, cor, fundo) in enumerate(ATALHOS):
            btn = self._btn_atalho(nome, cor, fundo)
            btn.clicked.connect(lambda _, i=idx: self._navegar(i))
            grid_atalhos.addWidget(btn, 0, i)

        layout.addLayout(grid_atalhos)

        # --- LINHA CENTRAL: calendario grande + estatisticas ---
        linha_central = QHBoxLayout()
        linha_central.setSpacing(14)

        # Calendario grande (lado esquerdo)
        linha_central.addWidget(self._criar_bloco_calendario(), stretch=62)

        # Estatisticas (lado direito)
        linha_central.addWidget(self._criar_bloco_estatisticas(), stretch=38)

        layout.addLayout(linha_central)

        scroll.setWidget(pagina)
        return scroll

    def _btn_atalho(self, nome, cor, fundo):
        btn = QPushButton(nome)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(72)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {fundo};
                color: {cor};
                border: 1px solid {cor};
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                padding: 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {cor};
                color: #ffffff;
            }}
        """)
        return btn

    def _criar_bloco_calendario(self):
        frame = QFrame()
        frame.setObjectName("card_resumo")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header do bloco
        topo = QHBoxLayout()
        lbl = QLabel("AGENDA — PRAZOS DAS OS")
        lbl.setObjectName("card_titulo")
        topo.addWidget(lbl)
        topo.addStretch()

        # Legenda
        for cor, txt in [("#4a9eff","Aberta"),("#f0a030","Em Andamento"),("#e05555","Vencida")]:
            dot = QLabel()
            dot.setFixedSize(8,8)
            dot.setStyleSheet(f"background:{cor}; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
            tl = QLabel(txt)
            tl.setStyleSheet("font-size:11px; color:#2a5a8a; background:transparent;")
            topo.addWidget(dot)
            topo.addWidget(tl)
            topo.addSpacing(6)

        layout.addLayout(topo)

        # Calendario grande
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.calendario.setNavigationBarVisible(True)
        self.calendario.setMinimumHeight(380)
        self.calendario.setStyleSheet("""
            QCalendarWidget { background-color: transparent; color: #c8dff5; border: none; }
            QCalendarWidget QToolButton {
                background-color: transparent; color: #4a9eff;
                border: none; font-size: 14px; font-weight: 700; padding: 6px 10px;
            }
            QCalendarWidget QToolButton:hover { background-color: #0d2540; border-radius: 5px; }
            QCalendarWidget QMenu { background-color: #0a1828; color: #c8dff5; border: 1px solid #0d2440; }
            QCalendarWidget QSpinBox { background-color: #0a1828; color: #4a9eff; border: 1px solid #0d2440; border-radius: 4px; padding: 2px 6px; }
            QCalendarWidget QAbstractItemView {
                background-color: transparent; color: #c8dff5;
                selection-background-color: #1a6fd4; selection-color: white;
                outline: none; font-size: 13px;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #1a3a5a; }
            QCalendarWidget #qt_calendar_navigationbar { background-color: #0a1428; border-radius: 8px; padding: 6px; margin-bottom: 6px; }
            QCalendarWidget #qt_calendar_prevmonth, QCalendarWidget #qt_calendar_nextmonth {
                color: #4a9eff; qproperty-icon: none; font-size: 18px; font-weight: bold; padding: 2px 10px;
            }
            QCalendarWidget QWidget { alternate-background-color: #0a1428; }
        """)
        self.calendario.currentPageChanged.connect(self._destacar_prazos)
        layout.addWidget(self.calendario)
        return frame

    def _criar_bloco_estatisticas(self):
        frame = QFrame()
        frame.setObjectName("card_resumo")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        lbl = QLabel("ESTATISTICAS DO SISTEMA")
        lbl.setObjectName("card_titulo")
        layout.addWidget(lbl)

        # Grid 2x2 de stats
        grid = QGridLayout()
        grid.setSpacing(10)

        self.stat_abertas    = self._stat_card("OS Abertas",    "0", "#4a9eff")
        self.stat_andamento  = self._stat_card("Em Andamento",  "0", "#f0a030")
        self.stat_concluidas = self._stat_card("Concluidas",    "0", "#2ab87a")
        self.stat_clientes   = self._stat_card("Clientes",      "0", "#8a6aff")
        self.stat_equipamentos = self._stat_card("Equipamentos","0", "#e05a9a")
        self.stat_os_pagas   = self._stat_card("OS Pagas",      "0", "#4a9eff")

        for i, card in enumerate([self.stat_abertas, self.stat_andamento,
                                   self.stat_concluidas, self.stat_clientes,
                                   self.stat_equipamentos, self.stat_os_pagas]):
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addSpacing(8)

        # Financeiro
        sep = QFrame()
        sep.setStyleSheet("background-color: #0a1e34; max-height: 1px; min-height: 1px;")
        layout.addWidget(sep)

        lbl_fin = QLabel("FINANCEIRO")
        lbl_fin.setObjectName("card_titulo")
        layout.addWidget(lbl_fin)

        self.stat_receita_total    = self._stat_card_largo("Receita Total",    "R$ 0,00", "#4a9eff")
        self.stat_receita_recebida = self._stat_card_largo("Receita Recebida", "R$ 0,00", "#2ab87a")
        self.stat_a_receber        = self._stat_card_largo("A Receber",        "R$ 0,00", "#f0a030")

        layout.addWidget(self.stat_receita_total)
        layout.addWidget(self.stat_receita_recebida)
        layout.addWidget(self.stat_a_receber)
        layout.addStretch()
        return frame

    def _stat_card(self, titulo, valor, cor):
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: #0a1428; border-radius: 8px; border: 1px solid #0a1e34; }} QFrame:hover {{ border-color: {cor}; }}")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        lv = QLabel(valor)
        lv.setStyleSheet(f"color:{cor}; font-size:22px; font-weight:700; background:transparent;")
        layout.addWidget(lv)

        lt = QLabel(titulo)
        lt.setStyleSheet("font-size:11px; color:#2a5a8a; background:transparent;")
        layout.addWidget(lt)

        frame._lv = lv
        return frame

    def _stat_card_largo(self, titulo, valor, cor):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #0a1428; border-radius: 8px; border: 1px solid #0a1e34; }")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)

        dot = QLabel()
        dot.setFixedSize(8,8)
        dot.setStyleSheet(f"background:{cor}; border-radius:4px; min-width:8px; max-width:8px; min-height:8px; max-height:8px;")
        layout.addWidget(dot)
        layout.addSpacing(8)

        lt = QLabel(titulo)
        lt.setStyleSheet("font-size:12px; color:#2a5a8a; background:transparent;")
        layout.addWidget(lt)
        layout.addStretch()

        lv = QLabel(valor)
        lv.setStyleSheet(f"color:{cor}; font-size:14px; font-weight:700; background:transparent;")
        layout.addWidget(lv)

        frame._lv = lv
        return frame

    def _destacar_prazos(self):
        fmt_padrao = QTextCharFormat()
        self.calendario.setDateTextFormat(QDate(), fmt_padrao)

        hoje = QDate.currentDate()
        for p in listar_prazos():
            if not p.get("prazo"):
                continue
            try:
                pts = p["prazo"].split("-")
                data = QDate(int(pts[0]), int(pts[1]), int(pts[2]))
            except Exception:
                continue

            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold)
            if data < hoje:
                fmt.setBackground(QColor("#3a0808"))
                fmt.setForeground(QColor("#e05555"))
            elif p["status"] == "em_andamento":
                fmt.setBackground(QColor("#2a1a00"))
                fmt.setForeground(QColor("#f0a030"))
            else:
                fmt.setBackground(QColor("#001a3a"))
                fmt.setForeground(QColor("#4a9eff"))
            self.calendario.setDateTextFormat(data, fmt)

        fmt_hoje = QTextCharFormat()
        fmt_hoje.setFontWeight(QFont.Weight.Bold)
        fmt_hoje.setForeground(QColor("#ffffff"))
        fmt_hoje.setBackground(QColor("#1a6fd4"))
        self.calendario.setDateTextFormat(hoje, fmt_hoje)

    def _atualizar_dashboard(self):
        contagens = contar_por_status()
        self.stat_abertas._lv.setText(str(contagens.get("aberta", 0)))
        self.stat_andamento._lv.setText(str(contagens.get("em_andamento", 0)))
        self.stat_concluidas._lv.setText(str(contagens.get("concluida", 0)))
        self.stat_clientes._lv.setText(str(contar_clientes()))
        self.stat_equipamentos._lv.setText(str(contar_equipamentos()))

        res = resumo_financeiro()
        self.stat_os_pagas._lv.setText(str(res.get("os_pagas", 0)))
        self.stat_receita_total._lv.setText(fmt_brl(res.get("receita_total", 0)))
        self.stat_receita_recebida._lv.setText(fmt_brl(res.get("receita_recebida", 0)))
        self.stat_a_receber._lv.setText(fmt_brl(res.get("receita_pendente", 0)))

        self._destacar_prazos()

    def _navegar(self, indice: int):
        titulos = ["Dashboard", "Ordens de Servico", "Clientes",
                   "Equipamentos", "Financeiro", "Usuarios", "Relatorios"]
        for i, btn in enumerate(self.botoes_menu):
            btn.setChecked(i == indice)
        self.label_titulo_pagina.setText(titulos[indice])
        self.stack.setCurrentIndex(indice)

        if indice == 0:   self._atualizar_dashboard()
        elif indice == 1: self.pagina_ordens._aplicar_filtros()
        elif indice == 2: self.pagina_clientes._carregar_clientes()
        elif indice == 3: self.pagina_equipamentos._carregar_equipamentos()
        elif indice == 4: self.pagina_financeiro._aplicar_filtros()
        elif indice == 5: self.pagina_usuarios._carregar_usuarios()

    def _sair(self):
        self.timer.stop()
        from app.views.tela_login import TelaLogin
        self.tela_login = TelaLogin()
        self.tela_login.login_sucesso.connect(self._reabrir_principal)
        self.tela_login.show()
        self.close()

    def _reabrir_principal(self, usuario):
        self.nova_janela = JanelaPrincipal(usuario)
        self.nova_janela.show()
        self.tela_login.close()