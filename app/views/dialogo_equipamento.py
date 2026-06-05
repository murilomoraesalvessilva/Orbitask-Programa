# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from app.models.equipamento import criar_equipamento, atualizar_equipamento
from app.models.ordem_servico import listar_ordens

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
        padding: 9px 12px;
        font-size: 13px;
        color: #c8dff5;
    }
    QLineEdit:focus { border: 1px solid #1a6fd4; }
    QTextEdit {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #c8dff5;
    }
    QTextEdit:focus { border: 1px solid #1a6fd4; }
    QComboBox {
        background-color: #0d1e30;
        border: 1px solid #0d2e4e;
        border-radius: 6px;
        padding: 9px 12px;
        font-size: 13px;
        color: #c8dff5;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background-color: #0a1828;
        color: #c8dff5;
        selection-background-color: #1a6fd4;
        outline: none;
    }
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
    QPushButton#btn_toggle {
        background-color: #0a1828; color: #2a5a8a;
        border: 1px solid #0d2440; border-radius: 5px;
        padding: 5px 10px; font-size: 11px;
    }
    QPushButton#btn_toggle:checked { color: #1a6fd4; border-color: #1a6fd4; }
"""

TIPOS = ["Computador","Notebook","Impressora","Monitor","Celular",
         "Tablet","Servidor","Switch","Roteador","Periferico","Outro"]


class DialogoEquipamento(QDialog):
    def __init__(self, parent=None, equipamento: dict = None, ordem_id: int = None):
        super().__init__(parent)
        self.equipamento  = equipamento
        self.ordem_id_fixo = ordem_id
        self.editando = equipamento is not None
        self.setWindowTitle("Editar Equipamento" if self.editando else "Novo Equipamento")
        self.setFixedSize(480, 520)
        self.setStyleSheet(ESTILO)
        self._construir()
        if self.editando:
            self._preencher()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        titulo = QLabel("Editar Equipamento" if self.editando else "Novo Equipamento")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        layout.addSpacing(20)

        self.campo_nome = self._campo(layout, "NOME *", "Ex: Notebook Dell Inspiron")

        lbl_tipo = QLabel("TIPO")
        lbl_tipo.setObjectName("campo_label")
        layout.addWidget(lbl_tipo)
        layout.addSpacing(4)
        self.combo_tipo = QComboBox()
        for t in TIPOS:
            self.combo_tipo.addItem(t)
        layout.addWidget(self.combo_tipo)
        layout.addSpacing(12)

        linha = QHBoxLayout()
        linha.setSpacing(12)

        col_marca = QVBoxLayout()
        col_marca.setSpacing(0)
        lbl_m = QLabel("MARCA")
        lbl_m.setObjectName("campo_label")
        col_marca.addWidget(lbl_m)
        col_marca.addSpacing(4)
        self.campo_marca = QLineEdit()
        self.campo_marca.setPlaceholderText("Ex: Dell")
        col_marca.addWidget(self.campo_marca)
        linha.addLayout(col_marca)

        col_modelo = QVBoxLayout()
        col_modelo.setSpacing(0)
        lbl_mod = QLabel("MODELO")
        lbl_mod.setObjectName("campo_label")
        col_modelo.addWidget(lbl_mod)
        col_modelo.addSpacing(4)
        self.campo_modelo = QLineEdit()
        self.campo_modelo.setPlaceholderText("Ex: Inspiron 15")
        col_modelo.addWidget(self.campo_modelo)
        linha.addLayout(col_modelo)

        layout.addLayout(linha)
        layout.addSpacing(12)

        self.campo_serie = self._campo(layout, "NUMERO DE SERIE", "Ex: SN123456")

        lbl_os = QLabel("ORDEM DE SERVICO VINCULADA")
        lbl_os.setObjectName("campo_label")
        layout.addWidget(lbl_os)
        layout.addSpacing(4)
        self.combo_ordem = QComboBox()
        self.combo_ordem.addItem("-- Nenhuma --", userData=None)
        for o in listar_ordens():
            self.combo_ordem.addItem(f"#{o['id']} — {o['titulo'][:40]}", userData=o["id"])
        if self.ordem_id_fixo:
            for i in range(self.combo_ordem.count()):
                if self.combo_ordem.itemData(i) == self.ordem_id_fixo:
                    self.combo_ordem.setCurrentIndex(i)
                    self.combo_ordem.setEnabled(False)
                    break
        layout.addWidget(self.combo_ordem)
        layout.addSpacing(12)

        lbl_desc = QLabel("OBSERVACOES")
        lbl_desc.setObjectName("campo_label")
        layout.addWidget(lbl_desc)
        layout.addSpacing(4)
        self.campo_descricao = QTextEdit()
        self.campo_descricao.setFixedHeight(70)
        self.campo_descricao.setPlaceholderText("Condicoes, defeitos, observacoes...")
        layout.addWidget(self.campo_descricao)
        layout.addSpacing(20)

        bts = QHBoxLayout()
        bts.setSpacing(12)
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secundario")
        btn_c.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c.clicked.connect(self.reject)
        bts.addWidget(btn_c)
        btn_s = QPushButton("Salvar" if self.editando else "Cadastrar")
        btn_s.setObjectName("btn_primario")
        btn_s.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_s.clicked.connect(self._salvar)
        bts.addWidget(btn_s)
        layout.addLayout(bts)

    def _campo(self, layout, label_txt, placeholder):
        lbl = QLabel(label_txt)
        lbl.setObjectName("campo_label")
        layout.addWidget(lbl)
        layout.addSpacing(4)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        layout.addWidget(campo)
        layout.addSpacing(12)
        return campo

    def _preencher(self):
        self.campo_nome.setText(self.equipamento.get("nome", ""))
        tipo = self.equipamento.get("tipo", "")
        if tipo in TIPOS:
            self.combo_tipo.setCurrentIndex(TIPOS.index(tipo))
        self.campo_marca.setText(self.equipamento.get("marca", "") or "")
        self.campo_modelo.setText(self.equipamento.get("modelo", "") or "")
        self.campo_serie.setText(self.equipamento.get("numero_serie", "") or "")
        self.campo_descricao.setPlainText(self.equipamento.get("descricao", "") or "")
        oid = self.equipamento.get("ordem_id")
        if oid:
            for i in range(self.combo_ordem.count()):
                if self.combo_ordem.itemData(i) == oid:
                    self.combo_ordem.setCurrentIndex(i)
                    break

    def _salvar(self):
        nome = self.campo_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatorio", "O nome do equipamento e obrigatorio.")
            return
        args = (
            nome,
            self.combo_tipo.currentText(),
            self.campo_marca.text().strip(),
            self.campo_modelo.text().strip(),
            self.campo_serie.text().strip(),
            self.campo_descricao.toPlainText().strip(),
            self.combo_ordem.currentData(),
        )
        if self.editando:
            atualizar_equipamento(self.equipamento["id"], *args)
        else:
            criar_equipamento(*args)
        self.accept()