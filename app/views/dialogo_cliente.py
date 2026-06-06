# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from app.models.cliente import criar_cliente, atualizar_cliente

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
        selection-background-color: #1a6fd4;
    }
    QLineEdit:focus {
        border: 1px solid #1a6fd4;
        background-color: #0d2030;
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
    QPushButton#btn_secundario:hover {
        background-color: #0d2040; color: #c8dff5;
    }
"""


class DialogoCliente(QDialog):
    def __init__(self, parent=None, cliente: dict = None):
        super().__init__(parent)
        self.cliente = cliente
        self.editando = cliente is not None
        self.setWindowTitle("Editar Cliente" if self.editando else "Novo Cliente")
        self.setFixedWidth(480)
        self.setStyleSheet(ESTILO)
        self._construir()
        self.adjustSize()
        if self.editando:
            self._preencher()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        titulo = QLabel("Editar Cliente" if self.editando else "Novo Cliente")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        layout.addSpacing(24)

        self.campo_nome      = self._campo(layout, "NOME *",      "Nome completo")
        self.campo_telefone  = self._campo(layout, "TELEFONE",    "(00) 00000-0000")
        self.campo_email     = self._campo(layout, "E-MAIL",      "cliente@email.com")
        self.campo_documento = self._campo(layout, "CPF / CNPJ",  "000.000.000-00")
        self.campo_endereco  = self._campo(layout, "ENDERECO",    "Rua, numero, bairro, cidade")

        layout.addSpacing(8)

        bts = QHBoxLayout()
        bts.setSpacing(12)
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secundario")
        btn_c.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c.clicked.connect(self.reject)
        bts.addWidget(btn_c)

        btn_s = QPushButton("Salvar Alteracoes" if self.editando else "Cadastrar Cliente")
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

    def _preencher(self):
        self.campo_nome.setText(self.cliente.get("nome", ""))
        self.campo_telefone.setText(self.cliente.get("telefone", "") or "")
        self.campo_email.setText(self.cliente.get("email", "") or "")
        self.campo_documento.setText(self.cliente.get("documento", "") or "")
        self.campo_endereco.setText(self.cliente.get("endereco", "") or "")

    def _salvar(self):
        nome = self.campo_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatorio", "O nome do cliente e obrigatorio.")
            return
        if self.editando:
            atualizar_cliente(self.cliente["id"], nome,
                self.campo_telefone.text().strip(),
                self.campo_email.text().strip(),
                self.campo_documento.text().strip(),
                self.campo_endereco.text().strip())
        else:
            criar_cliente(nome,
                self.campo_telefone.text().strip(),
                self.campo_email.text().strip(),
                self.campo_documento.text().strip(),
                self.campo_endereco.text().strip())
        self.accept()