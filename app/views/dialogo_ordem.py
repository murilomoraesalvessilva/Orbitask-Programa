# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
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


STATUS_OPCOES = [
    ("aberta",       "Aberta"),
    ("em_andamento", "Em Andamento"),
    ("concluida",    "Concluida"),
    ("cancelada",    "Cancelada"),
]

PRIORIDADE_OPCOES = [
    ("baixa",   "Baixa"),
    ("normal",  "Normal"),
    ("alta",    "Alta"),
    ("urgente", "Urgente"),
]


class DialogoOrdem(QDialog):
    """Dialogo para criar ou editar uma Ordem de Servico."""

    def __init__(self, parent=None, ordem: dict = None):
        super().__init__(parent)
        self.ordem = ordem
        self.editando = ordem is not None

        titulo = "Editar Ordem de Servico" if self.editando else "Nova Ordem de Servico"
        self.setWindowTitle(titulo)
        self.setFixedSize(520, 580)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

        if self.editando:
            self._preencher_campos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)

        titulo = "Editar Ordem de Servico" if self.editando else "Nova Ordem de Servico"
        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("titulo")
        layout.addWidget(label_titulo)

        layout.addSpacing(4)

        # Titulo da OS
        self.campo_titulo = self._campo_texto(layout, "Titulo *", "Ex: Manutencao do computador")

        # Descricao
        label_desc = QLabel("Descricao")
        label_desc.setObjectName("label_campo")
        layout.addWidget(label_desc)

        self.campo_descricao = QTextEdit()
        self.campo_descricao.setObjectName("campo_desc")
        self.campo_descricao.setPlaceholderText("Detalhe o problema ou servico a ser realizado...")
        self.campo_descricao.setFixedHeight(90)
        layout.addWidget(self.campo_descricao)

        # Linha: Prioridade + Status
        linha1 = QHBoxLayout()
        linha1.setSpacing(16)

        col_prioridade = QVBoxLayout()
        label_prio = QLabel("Prioridade")
        label_prio.setObjectName("label_campo")
        col_prioridade.addWidget(label_prio)
        self.combo_prioridade = self._criar_combo([v for _, v in PRIORIDADE_OPCOES])
        col_prioridade.addWidget(self.combo_prioridade)
        linha1.addLayout(col_prioridade)

        col_status = QVBoxLayout()
        label_status = QLabel("Status")
        label_status.setObjectName("label_campo")
        col_status.addWidget(label_status)
        self.combo_status = self._criar_combo([v for _, v in STATUS_OPCOES])
        if not self.editando:
            self.combo_status.setEnabled(False)
        col_status.addWidget(self.combo_status)
        linha1.addLayout(col_status)

        layout.addLayout(linha1)

        # Cliente
        label_cliente = QLabel("Cliente")
        label_cliente.setObjectName("label_campo")
        layout.addWidget(label_cliente)

        self.combo_cliente = self._criar_combo([])
        self.clientes = listar_clientes()
        self.combo_cliente.addItem("-- Nenhum --", userData=None)
        for c in self.clientes:
            self.combo_cliente.addItem(c["nome"], userData=c["id"])
        layout.addWidget(self.combo_cliente)

        # Tecnico responsavel
        label_tec = QLabel("Tecnico Responsavel")
        label_tec.setObjectName("label_campo")
        layout.addWidget(label_tec)

        self.combo_tecnico = self._criar_combo([])
        self.tecnicos = listar_tecnicos()
        self.combo_tecnico.addItem("-- Nenhum --", userData=None)
        for t in self.tecnicos:
            self.combo_tecnico.addItem(t["nome"], userData=t["id"])
        layout.addWidget(self.combo_tecnico)

        layout.addStretch()

        # Botoes
        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)

        texto_salvar = "Salvar Alteracoes" if self.editando else "Abrir Ordem"
        btn_salvar = QPushButton(texto_salvar)
        btn_salvar.setObjectName("btn_primario")
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._salvar)
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def _campo_texto(self, layout, label_texto, placeholder):
        label = QLabel(label_texto)
        label.setObjectName("label_campo")
        layout.addWidget(label)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setObjectName("campo")
        layout.addWidget(campo)
        return campo

    def _criar_combo(self, opcoes: list):
        combo = QComboBox()
        combo.setObjectName("combo")
        for op in opcoes:
            combo.addItem(op)
        return combo

    def _preencher_campos(self):
        self.campo_titulo.setText(self.ordem.get("titulo", ""))
        self.campo_descricao.setPlainText(self.ordem.get("descricao", "") or "")
        self.combo_status.setEnabled(True)

        # Prioridade
        prio_valores = [k for k, _ in PRIORIDADE_OPCOES]
        prio_atual = self.ordem.get("prioridade", "normal")
        if prio_atual in prio_valores:
            self.combo_prioridade.setCurrentIndex(prio_valores.index(prio_atual))

        # Status
        status_valores = [k for k, _ in STATUS_OPCOES]
        status_atual = self.ordem.get("status", "aberta")
        if status_atual in status_valores:
            self.combo_status.setCurrentIndex(status_valores.index(status_atual))

        # Cliente
        cliente_id = self.ordem.get("cliente_id")
        if cliente_id:
            for i in range(self.combo_cliente.count()):
                if self.combo_cliente.itemData(i) == cliente_id:
                    self.combo_cliente.setCurrentIndex(i)
                    break

        # Tecnico
        tecnico_id = self.ordem.get("tecnico_id")
        if tecnico_id:
            for i in range(self.combo_tecnico.count()):
                if self.combo_tecnico.itemData(i) == tecnico_id:
                    self.combo_tecnico.setCurrentIndex(i)
                    break

    def _salvar(self):
        titulo = self.campo_titulo.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Campo obrigatorio", "O titulo da ordem e obrigatorio.")
            self.campo_titulo.setFocus()
            return

        descricao = self.campo_descricao.toPlainText().strip()
        prioridade = PRIORIDADE_OPCOES[self.combo_prioridade.currentIndex()][0]
        status = STATUS_OPCOES[self.combo_status.currentIndex()][0]
        cliente_id = self.combo_cliente.currentData()
        tecnico_id = self.combo_tecnico.currentData()

        if self.editando:
            atualizar_ordem(self.ordem["id"], titulo, descricao, status,
                            prioridade, cliente_id, tecnico_id)
        else:
            criar_ordem(titulo, descricao, prioridade, cliente_id, tecnico_id)

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
            QLineEdit#campo:focus {
                border: 1px solid #7c6af7;
            }
            QTextEdit#campo_desc {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QTextEdit#campo_desc:focus {
                border: 1px solid #7c6af7;
            }
            QComboBox#combo {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox#combo:focus {
                border: 1px solid #7c6af7;
            }
            QComboBox#combo::drop-down {
                border: none;
            }
            QComboBox#combo QAbstractItemView {
                background-color: #252836;
                color: #e0e0e0;
                selection-background-color: #7c6af7;
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
            QPushButton#btn_primario:hover {
                background-color: #6a58e0;
            }
            QPushButton#btn_secundario {
                background-color: #252836;
                color: #9ca3af;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton#btn_secundario:hover {
                background-color: #2e3347;
                color: #e0e0e0;
            }
        """