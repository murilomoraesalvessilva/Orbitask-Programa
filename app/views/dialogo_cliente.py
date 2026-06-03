# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from app.models.cliente import criar_cliente, atualizar_cliente


class DialogoCliente(QDialog):
    """Dialogo para criar ou editar um cliente."""

    def __init__(self, parent=None, cliente: dict = None):
        super().__init__(parent)
        self.cliente = cliente  # None = novo cliente, dict = edicao
        self.editando = cliente is not None

        titulo = "Editar Cliente" if self.editando else "Novo Cliente"
        self.setWindowTitle(titulo)
        self.setFixedSize(480, 460)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

        if self.editando:
            self._preencher_campos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Titulo
        titulo = "Editar Cliente" if self.editando else "Novo Cliente"
        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("titulo")
        layout.addWidget(label_titulo)

        layout.addSpacing(8)

        # Campos
        self.campo_nome = self._criar_campo(layout, "Nome *", "Nome completo")
        self.campo_telefone = self._criar_campo(layout, "Telefone", "(00) 00000-0000")
        self.campo_email = self._criar_campo(layout, "E-mail", "cliente@email.com")
        self.campo_documento = self._criar_campo(layout, "CPF / CNPJ", "000.000.000-00")
        self.campo_endereco = self._criar_campo(layout, "Endereco", "Rua, numero, bairro, cidade")

        layout.addStretch()

        # Botoes
        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)

        texto_salvar = "Salvar Alteracoes" if self.editando else "Cadastrar Cliente"
        btn_salvar = QPushButton(texto_salvar)
        btn_salvar.setObjectName("btn_primario")
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._salvar)
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def _criar_campo(self, layout, label_texto, placeholder):
        label = QLabel(label_texto)
        label.setObjectName("label_campo")
        layout.addWidget(label)

        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setObjectName("campo")
        layout.addWidget(campo)

        return campo

    def _preencher_campos(self):
        self.campo_nome.setText(self.cliente.get("nome", ""))
        self.campo_telefone.setText(self.cliente.get("telefone", "") or "")
        self.campo_email.setText(self.cliente.get("email", "") or "")
        self.campo_documento.setText(self.cliente.get("documento", "") or "")
        self.campo_endereco.setText(self.cliente.get("endereco", "") or "")

    def _salvar(self):
        nome = self.campo_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatorio", "O nome do cliente e obrigatorio.")
            self.campo_nome.setFocus()
            return

        telefone = self.campo_telefone.text().strip()
        email = self.campo_email.text().strip()
        documento = self.campo_documento.text().strip()
        endereco = self.campo_endereco.text().strip()

        if self.editando:
            atualizar_cliente(self.cliente["id"], nome, telefone, email, documento, endereco)
        else:
            criar_cliente(nome, telefone, email, documento, endereco)

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