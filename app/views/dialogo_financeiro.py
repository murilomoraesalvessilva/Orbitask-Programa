# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from app.models.financeiro import atualizar_financeiro, STATUS_PAGAMENTO


class DialogoFinanceiro(QDialog):
    """Dialogo para editar os valores e status de pagamento de uma OS."""

    def __init__(self, parent=None, registro: dict = None):
        super().__init__(parent)
        self.registro = registro or {}
        self.setWindowTitle(f"Financeiro — OS #{registro.get('id', '')}")
        self.setFixedSize(420, 380)
        self.setStyleSheet(self._estilos())
        self._construir_interface()
        self._preencher_campos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)

        label_titulo = QLabel(f"OS #{self.registro.get('id')} — {self.registro.get('titulo', '')[:38]}")
        label_titulo.setObjectName("titulo")
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)

        label_cliente = QLabel(f"Cliente: {self.registro.get('cliente_nome') or 'Nao informado'}")
        label_cliente.setObjectName("label_info")
        layout.addWidget(label_cliente)

        layout.addSpacing(4)

        # Valor do servico
        label_vs = QLabel("Valor do Servico (R$)")
        label_vs.setObjectName("label_campo")
        layout.addWidget(label_vs)

        self.campo_valor_servico = QLineEdit()
        self.campo_valor_servico.setObjectName("campo")
        self.campo_valor_servico.setPlaceholderText("0.00")
        self.campo_valor_servico.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addWidget(self.campo_valor_servico)

        # Valor das pecas
        label_vp = QLabel("Valor das Pecas (R$)")
        label_vp.setObjectName("label_campo")
        layout.addWidget(label_vp)

        self.campo_valor_pecas = QLineEdit()
        self.campo_valor_pecas.setObjectName("campo")
        self.campo_valor_pecas.setPlaceholderText("0.00")
        self.campo_valor_pecas.setValidator(QDoubleValidator(0, 999999, 2))
        self.campo_valor_pecas.textChanged.connect(self._atualizar_total)
        self.campo_valor_servico.textChanged.connect(self._atualizar_total)
        layout.addWidget(self.campo_valor_pecas)

        # Total calculado
        frame_total = QFrame()
        frame_total.setObjectName("frame_total")
        layout_total = QHBoxLayout(frame_total)
        layout_total.setContentsMargins(16, 12, 16, 12)

        QLabel_total_label = QLabel("Total:")
        QLabel_total_label.setObjectName("label_total_texto")
        layout_total.addWidget(QLabel_total_label)

        layout_total.addStretch()

        self.label_total = QLabel("R$ 0,00")
        self.label_total.setObjectName("label_total_valor")
        layout_total.addWidget(self.label_total)

        layout.addWidget(frame_total)

        # Status de pagamento
        label_sp = QLabel("Status de Pagamento")
        label_sp.setObjectName("label_campo")
        layout.addWidget(label_sp)

        self.combo_status = QComboBox()
        self.combo_status.setObjectName("combo")
        for _, label in STATUS_PAGAMENTO:
            self.combo_status.addItem(label)
        layout.addWidget(self.combo_status)

        layout.addStretch()

        # Botoes
        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("btn_primario")
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._salvar)
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def _preencher_campos(self):
        vs = self.registro.get("valor_servico") or 0.0
        vp = self.registro.get("valor_pecas") or 0.0
        self.campo_valor_servico.setText(f"{vs:.2f}".replace(".", ","))
        self.campo_valor_pecas.setText(f"{vp:.2f}".replace(".", ","))

        sp_valores = [k for k, _ in STATUS_PAGAMENTO]
        sp_atual = self.registro.get("status_pagamento", "pendente")
        if sp_atual in sp_valores:
            self.combo_status.setCurrentIndex(sp_valores.index(sp_atual))

        self._atualizar_total()

    def _parse_valor(self, texto: str) -> float:
        try:
            return float(texto.replace(",", "."))
        except ValueError:
            return 0.0

    def _atualizar_total(self):
        vs = self._parse_valor(self.campo_valor_servico.text())
        vp = self._parse_valor(self.campo_valor_pecas.text())
        total = vs + vp
        self.label_total.setText(f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def _salvar(self):
        valor_servico = self._parse_valor(self.campo_valor_servico.text())
        valor_pecas   = self._parse_valor(self.campo_valor_pecas.text())
        status_pag    = STATUS_PAGAMENTO[self.combo_status.currentIndex()][0]

        atualizar_financeiro(
            self.registro["id"],
            valor_servico,
            valor_pecas,
            status_pag
        )
        self.accept()

    def _estilos(self):
        return """
            QDialog {
                background-color: #1a1d27;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titulo {
                font-size: 15px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel#label_info {
                font-size: 12px;
                color: #6b7280;
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
            QLineEdit#campo:focus { border: 1px solid #7c6af7; }
            QFrame#frame_total {
                background-color: #252836;
                border-radius: 8px;
                border: 1px solid #2e3347;
            }
            QLabel#label_total_texto {
                font-size: 13px;
                color: #9ca3af;
                font-weight: bold;
            }
            QLabel#label_total_valor {
                font-size: 16px;
                font-weight: bold;
                color: #10b981;
            }
            QComboBox#combo {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox#combo::drop-down { border: none; }
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
            QPushButton#btn_primario:hover { background-color: #6a58e0; }
            QPushButton#btn_secundario {
                background-color: #252836;
                color: #9ca3af;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton#btn_secundario:hover { background-color: #2e3347; color: #e0e0e0; }
        """