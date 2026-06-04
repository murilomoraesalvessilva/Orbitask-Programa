# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from app.models.ordem_servico import criar_ordem, atualizar_ordem
from app.models.cliente import listar_clientes
from app.database.connection import get_connection


def listar_tecnicos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE ativo = 1 ORDER BY nome ASC")
    tecnicos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tecnicos


STATUS_OPCOES   = [("aberta","Aberta"),("em_andamento","Em Andamento"),("concluida","Concluida"),("cancelada","Cancelada")]
PRIORIDADE_OPCOES = [("baixa","Baixa"),("normal","Normal"),("alta","Alta"),("urgente","Urgente")]


class DialogoOrdem(QDialog):
    def __init__(self, parent=None, ordem: dict = None):
        super().__init__(parent)
        self.ordem = ordem
        self.editando = ordem is not None
        self.setWindowTitle("Editar Ordem de Servico" if self.editando else "Nova Ordem de Servico")
        self.setFixedSize(540, 620)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        if self.editando:
            self._preencher_campos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)

        titulo = QLabel("Editar Ordem de Servico" if self.editando else "Nova Ordem de Servico")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        layout.addSpacing(4)

        self.campo_titulo = self._campo(layout, "TITULO *", "Ex: Manutencao do computador")

        label_desc = QLabel("DESCRICAO")
        label_desc.setObjectName("label_campo")
        layout.addWidget(label_desc)
        self.campo_descricao = QTextEdit()
        self.campo_descricao.setObjectName("campo_desc")
        self.campo_descricao.setPlaceholderText("Detalhe o problema ou servico a ser realizado...")
        self.campo_descricao.setFixedHeight(80)
        layout.addWidget(self.campo_descricao)

        # Linha: Prioridade + Status + Prazo
        linha1 = QHBoxLayout()
        linha1.setSpacing(12)

        col_prio = QVBoxLayout()
        lp = QLabel("PRIORIDADE")
        lp.setObjectName("label_campo")
        col_prio.addWidget(lp)
        self.combo_prioridade = self._combo([v for _, v in PRIORIDADE_OPCOES])
        col_prio.addWidget(self.combo_prioridade)
        linha1.addLayout(col_prio)

        col_st = QVBoxLayout()
        ls = QLabel("STATUS")
        ls.setObjectName("label_campo")
        col_st.addWidget(ls)
        self.combo_status = self._combo([v for _, v in STATUS_OPCOES])
        if not self.editando:
            self.combo_status.setEnabled(False)
        col_st.addWidget(self.combo_status)
        linha1.addLayout(col_st)

        col_prazo = QVBoxLayout()
        lpz = QLabel("PRAZO")
        lpz.setObjectName("label_campo")
        col_prazo.addWidget(lpz)
        self.campo_prazo = QDateEdit()
        self.campo_prazo.setObjectName("campo_data")
        self.campo_prazo.setCalendarPopup(True)
        self.campo_prazo.setDate(QDate.currentDate())
        self.campo_prazo.setDisplayFormat("dd/MM/yyyy")
        self.campo_prazo.setSpecialValueText("Sem prazo")
        self.campo_prazo.setMinimumDate(QDate(2000, 1, 1))
        col_prazo.addWidget(self.campo_prazo)

        # Checkbox para sem prazo
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

        # Cliente
        lc = QLabel("CLIENTE")
        lc.setObjectName("label_campo")
        layout.addWidget(lc)
        self.combo_cliente = self._combo([])
        self.clientes = listar_clientes()
        self.combo_cliente.addItem("-- Nenhum --", userData=None)
        for c in self.clientes:
            self.combo_cliente.addItem(c["nome"], userData=c["id"])
        layout.addWidget(self.combo_cliente)

        # Tecnico
        lt2 = QLabel("TECNICO RESPONSAVEL")
        lt2.setObjectName("label_campo")
        layout.addWidget(lt2)
        self.combo_tecnico = self._combo([])
        self.tecnicos = listar_tecnicos()
        self.combo_tecnico.addItem("-- Nenhum --", userData=None)
        for t in self.tecnicos:
            self.combo_tecnico.addItem(t["nome"], userData=t["id"])
        layout.addWidget(self.combo_tecnico)

        layout.addStretch()

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

    def _toggle_prazo(self):
        sem = self.btn_sem_prazo.isChecked()
        self.campo_prazo.setEnabled(not sem)
        self.btn_sem_prazo.setText("Sem prazo" if sem else "Definir prazo")

    def _campo(self, layout, label_texto, placeholder):
        label = QLabel(label_texto)
        label.setObjectName("label_campo")
        layout.addWidget(label)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setObjectName("campo")
        layout.addWidget(campo)
        return campo

    def _combo(self, opcoes):
        combo = QComboBox()
        combo.setObjectName("combo")
        for op in opcoes:
            combo.addItem(op)
        return combo

    def _preencher_campos(self):
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

        # Prazo
        prazo = self.ordem.get("prazo")
        if prazo:
            try:
                partes = prazo.split("-")
                self.campo_prazo.setDate(QDate(int(partes[0]), int(partes[1]), int(partes[2])))
                self.btn_sem_prazo.setChecked(False)
                self._toggle_prazo()
            except Exception:
                pass

        # Cliente
        cid = self.ordem.get("cliente_id")
        if cid:
            for i in range(self.combo_cliente.count()):
                if self.combo_cliente.itemData(i) == cid:
                    self.combo_cliente.setCurrentIndex(i)
                    break

        # Tecnico
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

        # Prazo
        prazo = None
        if not self.btn_sem_prazo.isChecked():
            prazo = self.campo_prazo.date().toString("yyyy-MM-dd")

        if self.editando:
            atualizar_ordem(self.ordem["id"], titulo, descricao, status,
                            prioridade, prazo, cliente_id, tecnico_id)
        else:
            criar_ordem(titulo, descricao, prioridade, prazo, cliente_id, tecnico_id)

        self.accept()

    def _estilos(self):
        return """
            QDialog {
                background-color: #08121e;
                color: #c8dff5;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titulo { font-size: 17px; font-weight: 700; color: #ffffff; }
            QLabel#label_campo { font-size: 11px; font-weight: 700; color: #2a5a8a; letter-spacing: 0.8px; }
            QLineEdit#campo {
                background-color: #0a1828; border: 1px solid #0d2440;
                border-radius: 6px; padding: 9px 12px; font-size: 13px; color: #c8dff5;
            }
            QLineEdit#campo:focus { border-color: #1a6fd4; }
            QTextEdit#campo_desc {
                background-color: #0a1828; border: 1px solid #0d2440;
                border-radius: 6px; padding: 8px 12px; font-size: 13px; color: #c8dff5;
            }
            QTextEdit#campo_desc:focus { border-color: #1a6fd4; }
            QComboBox#combo {
                background-color: #0a1828; border: 1px solid #0d2440;
                border-radius: 6px; padding: 9px 12px; font-size: 13px; color: #c8dff5;
            }
            QComboBox#combo::drop-down { border: none; }
            QComboBox#combo QAbstractItemView {
                background-color: #0a1828; color: #c8dff5;
                selection-background-color: #1a6fd4; outline: none;
            }
            QDateEdit#campo_data {
                background-color: #0a1828; border: 1px solid #0d2440;
                border-radius: 6px; padding: 9px 12px; font-size: 13px; color: #c8dff5;
            }
            QDateEdit#campo_data:focus { border-color: #1a6fd4; }
            QDateEdit#campo_data::drop-down { border: none; }
            QCalendarWidget {
                background-color: #0a1828; color: #c8dff5;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #0a1828; color: #c8dff5;
                selection-background-color: #1a6fd4;
            }
            QPushButton#btn_toggle_prazo {
                background-color: #0a1828; color: #2a5a8a;
                border: 1px solid #0d2440; border-radius: 5px;
                padding: 5px 10px; font-size: 11px;
            }
            QPushButton#btn_toggle_prazo:checked { color: #1a6fd4; border-color: #1a6fd4; }
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