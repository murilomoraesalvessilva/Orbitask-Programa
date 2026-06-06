# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from app.models.ordem_servico import criar_ordem, atualizar_ordem
from app.models.cliente import listar_clientes
from app.database.connection import get_connection

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
        padding: 10px 14px;
        font-size: 13px;
        color: #c8dff5;
        min-height: 20px;
    }
    QLineEdit:focus { border: 1px solid #1a6fd4; background-color: #0d2030; }
    QTextEdit {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #c8dff5;
    }
    QTextEdit:focus { border: 1px solid #1a6fd4; }
    QComboBox {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #c8dff5;
        min-height: 20px;
    }
    QComboBox:focus { border: 1px solid #1a6fd4; }
    QComboBox::drop-down { border: none; width: 20px; }
    QComboBox QAbstractItemView {
        background-color: #0a1828; color: #c8dff5;
        selection-background-color: #1a6fd4; outline: none;
    }
    QDateEdit {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #c8dff5;
        min-height: 20px;
    }
    QDateEdit:focus { border: 1px solid #1a6fd4; }
    QDateEdit::drop-down { border: none; width: 20px; }
    QCalendarWidget { background-color: #0a1828; color: #c8dff5; }
    QCalendarWidget QAbstractItemView {
        background-color: #0a1828; color: #c8dff5;
        selection-background-color: #1a6fd4;
    }
    QPushButton#btn_primario {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a6fd4,stop:1 #0d4fa0);
        color: white; border: none; border-radius: 6px;
        padding: 11px 20px; font-size: 13px; font-weight: 600;
    }
    QPushButton#btn_primario:hover {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2a7fe4,stop:1 #1a5fc0);
    }
    QPushButton#btn_secundario {
        background-color: #0a1828; color: #3a6a9a;
        border: 1px solid #0d2440; border-radius: 6px;
        padding: 11px 20px; font-size: 13px;
    }
    QPushButton#btn_secundario:hover { background-color: #0d2040; color: #c8dff5; }
    QPushButton#btn_toggle_prazo {
        background-color: #0a1828; color: #2a5a8a;
        border: 1px solid #0d2440; border-radius: 5px;
        padding: 6px 12px; font-size: 11px; font-weight: 600;
    }
    QPushButton#btn_toggle_prazo:checked { color: #4a9eff; border-color: #1a6fd4; }
"""

STATUS_OPCOES     = [("aberta","Aberta"),("em_andamento","Em Andamento"),("concluida","Concluida"),("cancelada","Cancelada")]
PRIORIDADE_OPCOES = [("baixa","Baixa"),("normal","Normal"),("alta","Alta"),("urgente","Urgente")]


def listar_tecnicos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE ativo = 1 ORDER BY nome ASC")
    result = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return result


class DialogoOrdem(QDialog):
    def __init__(self, parent=None, ordem: dict = None):
        super().__init__(parent)
        self.ordem    = ordem
        self.editando = ordem is not None
        self.setWindowTitle("Editar Ordem de Servico" if self.editando else "Nova Ordem de Servico")
        self.setFixedWidth(540)
        self.setStyleSheet(ESTILO)
        self._construir()
        self.adjustSize()
        if self.editando:
            self._preencher()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        titulo = QLabel("Editar Ordem de Servico" if self.editando else "Nova Ordem de Servico")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        layout.addSpacing(24)

        # Titulo da OS
        self.campo_titulo = self._campo(layout, "TITULO *", "Ex: Manutencao do computador")

        # Descricao
        lbl_desc = QLabel("DESCRICAO")
        lbl_desc.setObjectName("campo_label")
        layout.addWidget(lbl_desc)
        layout.addSpacing(5)
        self.campo_descricao = QTextEdit()
        self.campo_descricao.setPlaceholderText("Detalhe o problema ou servico a ser realizado...")
        self.campo_descricao.setFixedHeight(90)
        layout.addWidget(self.campo_descricao)
        layout.addSpacing(14)

        # Linha: Prioridade + Status + Prazo
        linha1 = QHBoxLayout()
        linha1.setSpacing(14)

        col_prio = QVBoxLayout()
        col_prio.setSpacing(0)
        lbl_p = QLabel("PRIORIDADE")
        lbl_p.setObjectName("campo_label")
        col_prio.addWidget(lbl_p)
        col_prio.addSpacing(5)
        self.combo_prioridade = QComboBox()
        self.combo_prioridade.setFixedHeight(42)
        for _, v in PRIORIDADE_OPCOES:
            self.combo_prioridade.addItem(v)
        col_prio.addWidget(self.combo_prioridade)
        linha1.addLayout(col_prio)

        col_st = QVBoxLayout()
        col_st.setSpacing(0)
        lbl_s = QLabel("STATUS")
        lbl_s.setObjectName("campo_label")
        col_st.addWidget(lbl_s)
        col_st.addSpacing(5)
        self.combo_status = QComboBox()
        self.combo_status.setFixedHeight(42)
        for _, v in STATUS_OPCOES:
            self.combo_status.addItem(v)
        if not self.editando:
            self.combo_status.setEnabled(False)
        col_st.addWidget(self.combo_status)
        linha1.addLayout(col_st)

        col_prazo = QVBoxLayout()
        col_prazo.setSpacing(0)
        lbl_pz = QLabel("PRAZO")
        lbl_pz.setObjectName("campo_label")
        col_prazo.addWidget(lbl_pz)
        col_prazo.addSpacing(5)
        self.campo_prazo = QDateEdit()
        self.campo_prazo.setCalendarPopup(True)
        self.campo_prazo.setDate(QDate.currentDate())
        self.campo_prazo.setDisplayFormat("dd/MM/yyyy")
        self.campo_prazo.setFixedHeight(42)
        col_prazo.addWidget(self.campo_prazo)
        col_prazo.addSpacing(5)
        self.btn_sem_prazo = QPushButton("Sem prazo")
        self.btn_sem_prazo.setObjectName("btn_toggle_prazo")
        self.btn_sem_prazo.setCheckable(True)
        self.btn_sem_prazo.setChecked(True)
        self.btn_sem_prazo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sem_prazo.clicked.connect(self._toggle_prazo)
        col_prazo.addWidget(self.btn_sem_prazo)
        self._toggle_prazo()
        linha1.addLayout(col_prazo)

        layout.addLayout(linha1)
        layout.addSpacing(14)

        # Cliente
        lbl_cli = QLabel("CLIENTE")
        lbl_cli.setObjectName("campo_label")
        layout.addWidget(lbl_cli)
        layout.addSpacing(5)
        self.combo_cliente = QComboBox()
        self.combo_cliente.setFixedHeight(42)
        self.combo_cliente.addItem("-- Nenhum --", userData=None)
        for c in listar_clientes():
            self.combo_cliente.addItem(c["nome"], userData=c["id"])
        layout.addWidget(self.combo_cliente)
        layout.addSpacing(14)

        # Tecnico
        lbl_tec = QLabel("TECNICO RESPONSAVEL")
        lbl_tec.setObjectName("campo_label")
        layout.addWidget(lbl_tec)
        layout.addSpacing(5)
        self.combo_tecnico = QComboBox()
        self.combo_tecnico.setFixedHeight(42)
        self.combo_tecnico.addItem("-- Nenhum --", userData=None)
        for t in listar_tecnicos():
            self.combo_tecnico.addItem(t["nome"], userData=t["id"])
        layout.addWidget(self.combo_tecnico)
        layout.addSpacing(20)

        # Botoes
        bts = QHBoxLayout()
        bts.setSpacing(12)
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secundario")
        btn_c.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c.clicked.connect(self.reject)
        bts.addWidget(btn_c)
        btn_s = QPushButton("Salvar Alteracoes" if self.editando else "Abrir Ordem")
        btn_s.setObjectName("btn_primario")
        btn_s.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_s.clicked.connect(self._salvar)
        bts.addWidget(btn_s)
        layout.addLayout(bts)

    def _campo(self, layout, label_txt, placeholder):
        lbl = QLabel(label_txt)
        lbl.setObjectName("campo_label")
        layout.addWidget(lbl)
        layout.addSpacing(5)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setFixedHeight(42)
        layout.addWidget(campo)
        layout.addSpacing(14)
        return campo

    def _toggle_prazo(self):
        sem = self.btn_sem_prazo.isChecked()
        self.campo_prazo.setEnabled(not sem)
        self.btn_sem_prazo.setText("Sem prazo" if sem else "Definir prazo")

    def _preencher(self):
        self.campo_titulo.setText(self.ordem.get("titulo", ""))
        self.campo_descricao.setPlainText(self.ordem.get("descricao", "") or "")
        self.combo_status.setEnabled(True)

        prio_vals = [k for k, _ in PRIORIDADE_OPCOES]
        prio = self.ordem.get("prioridade", "normal")
        if prio in prio_vals:
            self.combo_prioridade.setCurrentIndex(prio_vals.index(prio))

        st_vals = [k for k, _ in STATUS_OPCOES]
        st = self.ordem.get("status", "aberta")
        if st in st_vals:
            self.combo_status.setCurrentIndex(st_vals.index(st))

        prazo = self.ordem.get("prazo")
        if prazo:
            try:
                pts = prazo.split("-")
                self.campo_prazo.setDate(QDate(int(pts[0]), int(pts[1]), int(pts[2])))
                self.btn_sem_prazo.setChecked(False)
                self._toggle_prazo()
            except Exception:
                pass

        cid = self.ordem.get("cliente_id")
        if cid:
            for i in range(self.combo_cliente.count()):
                if self.combo_cliente.itemData(i) == cid:
                    self.combo_cliente.setCurrentIndex(i)
                    break

        tid = self.ordem.get("tecnico_id")
        if tid:
            for i in range(self.combo_tecnico.count()):
                if self.combo_tecnico.itemData(i) == tid:
                    self.combo_tecnico.setCurrentIndex(i)
                    break

    def _salvar(self):
        titulo = self.campo_titulo.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Campo obrigatorio", "O titulo da ordem e obrigatorio.")
            return
        descricao  = self.campo_descricao.toPlainText().strip()
        prioridade = PRIORIDADE_OPCOES[self.combo_prioridade.currentIndex()][0]
        status     = STATUS_OPCOES[self.combo_status.currentIndex()][0]
        cliente_id = self.combo_cliente.currentData()
        tecnico_id = self.combo_tecnico.currentData()
        prazo = None
        if not self.btn_sem_prazo.isChecked():
            prazo = self.campo_prazo.date().toString("yyyy-MM-dd")

        if self.editando:
            atualizar_ordem(self.ordem["id"], titulo, descricao, status,
                            prioridade, prazo, cliente_id, tecnico_id)
        else:
            criar_ordem(titulo, descricao, prioridade, prazo, cliente_id, tecnico_id)
        self.accept()