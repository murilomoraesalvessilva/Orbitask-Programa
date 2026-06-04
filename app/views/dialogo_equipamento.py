# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from app.models.equipamento import criar_equipamento, atualizar_equipamento
from app.models.ordem_servico import listar_ordens

TIPOS = [
    "Computador", "Notebook", "Impressora", "Monitor", "Celular",
    "Tablet", "Servidor", "Switch", "Roteador", "Periferico", "Outro"
]


class DialogoEquipamento(QDialog):
    def __init__(self, parent=None, equipamento: dict = None, ordem_id: int = None):
        super().__init__(parent)
        self.equipamento = equipamento
        self.ordem_id_fixo = ordem_id  # Se aberto a partir de uma OS
        self.editando = equipamento is not None

        self.setWindowTitle("Editar Equipamento" if self.editando else "Novo Equipamento")
        self.setFixedSize(480, 540)
        self.setStyleSheet(self._estilos())
        self._construir_interface()

        if self.editando:
            self._preencher_campos()

    def _construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)

        titulo = "Editar Equipamento" if self.editando else "Novo Equipamento"
        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("titulo")
        layout.addWidget(label_titulo)

        layout.addSpacing(4)

        self.campo_nome = self._campo(layout, "Nome *", "Ex: Notebook Dell Inspiron")

        # Tipo
        label_tipo = QLabel("Tipo")
        label_tipo.setObjectName("label_campo")
        layout.addWidget(label_tipo)
        self.combo_tipo = QComboBox()
        self.combo_tipo.setObjectName("combo")
        for t in TIPOS:
            self.combo_tipo.addItem(t)
        layout.addWidget(self.combo_tipo)

        # Linha marca + modelo
        linha = QHBoxLayout()
        linha.setSpacing(12)
        col_marca = QVBoxLayout()
        label_marca = QLabel("Marca")
        label_marca.setObjectName("label_campo")
        col_marca.addWidget(label_marca)
        self.campo_marca = QLineEdit()
        self.campo_marca.setPlaceholderText("Ex: Dell")
        self.campo_marca.setObjectName("campo")
        col_marca.addWidget(self.campo_marca)
        linha.addLayout(col_marca)

        col_modelo = QVBoxLayout()
        label_modelo = QLabel("Modelo")
        label_modelo.setObjectName("label_campo")
        col_modelo.addWidget(label_modelo)
        self.campo_modelo = QLineEdit()
        self.campo_modelo.setPlaceholderText("Ex: Inspiron 15")
        self.campo_modelo.setObjectName("campo")
        col_modelo.addWidget(self.campo_modelo)
        linha.addLayout(col_modelo)
        layout.addLayout(linha)

        self.campo_serie = self._campo(layout, "Numero de Serie", "Ex: SN123456")

        # Ordem de servico vinculada
        label_os = QLabel("Ordem de Servico vinculada")
        label_os.setObjectName("label_campo")
        layout.addWidget(label_os)

        self.combo_ordem = QComboBox()
        self.combo_ordem.setObjectName("combo")
        self.combo_ordem.addItem("-- Nenhuma --", userData=None)
        self.ordens = listar_ordens()
        for o in self.ordens:
            self.combo_ordem.addItem(f"#{o['id']} — {o['titulo'][:40]}", userData=o["id"])
        layout.addWidget(self.combo_ordem)

        # Se aberto de dentro de uma OS, fixa o vinculo
        if self.ordem_id_fixo:
            for i in range(self.combo_ordem.count()):
                if self.combo_ordem.itemData(i) == self.ordem_id_fixo:
                    self.combo_ordem.setCurrentIndex(i)
                    self.combo_ordem.setEnabled(False)
                    break

        # Descricao
        label_desc = QLabel("Observacoes")
        label_desc.setObjectName("label_campo")
        layout.addWidget(label_desc)
        self.campo_descricao = QTextEdit()
        self.campo_descricao.setObjectName("campo_desc")
        self.campo_descricao.setFixedHeight(70)
        self.campo_descricao.setPlaceholderText("Condicoes, defeitos, observacoes...")
        layout.addWidget(self.campo_descricao)

        layout.addStretch()

        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar" if self.editando else "Cadastrar")
        btn_salvar.setObjectName("btn_primario")
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._salvar)
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def _campo(self, layout, label_texto, placeholder):
        label = QLabel(label_texto)
        label.setObjectName("label_campo")
        layout.addWidget(label)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setObjectName("campo")
        layout.addWidget(campo)
        return campo

    def _preencher_campos(self):
        self.campo_nome.setText(self.equipamento.get("nome", ""))
        tipo = self.equipamento.get("tipo", "")
        if tipo in TIPOS:
            self.combo_tipo.setCurrentIndex(TIPOS.index(tipo))
        self.campo_marca.setText(self.equipamento.get("marca", "") or "")
        self.campo_modelo.setText(self.equipamento.get("modelo", "") or "")
        self.campo_serie.setText(self.equipamento.get("numero_serie", "") or "")
        self.campo_descricao.setPlainText(self.equipamento.get("descricao", "") or "")
        ordem_id = self.equipamento.get("ordem_id")
        if ordem_id:
            for i in range(self.combo_ordem.count()):
                if self.combo_ordem.itemData(i) == ordem_id:
                    self.combo_ordem.setCurrentIndex(i)
                    break

    def _salvar(self):
        nome = self.campo_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatorio", "O nome do equipamento e obrigatorio.")
            return

        tipo       = self.combo_tipo.currentText()
        marca      = self.campo_marca.text().strip()
        modelo     = self.campo_modelo.text().strip()
        serie      = self.campo_serie.text().strip()
        descricao  = self.campo_descricao.toPlainText().strip()
        ordem_id   = self.combo_ordem.currentData()

        if self.editando:
            atualizar_equipamento(self.equipamento["id"], nome, tipo, marca,
                                   modelo, serie, descricao, ordem_id)
        else:
            criar_equipamento(nome, tipo, marca, modelo, serie, descricao, ordem_id)

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
            QLineEdit#campo:focus { border: 1px solid #7c6af7; }
            QTextEdit#campo_desc {
                background-color: #252836;
                border: 1px solid #2e3347;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QTextEdit#campo_desc:focus { border: 1px solid #7c6af7; }
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