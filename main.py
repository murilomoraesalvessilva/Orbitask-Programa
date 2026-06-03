import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.database.migrations import inicializar_banco
from app.views.tela_login import TelaLogin
from app.views.janela_principal import JanelaPrincipal


def main():
    # Inicializa o banco de dados (cria tabelas e admin padrão se necessário)
    inicializar_banco()

    app = QApplication(sys.argv)
    app.setApplicationName("Orbitask")
    app.setStyle("Fusion")  # Estilo base mais neutro para customizar

    # Abre a tela de login
    tela_login = TelaLogin()

    def ao_fazer_login(usuario):
        janela = JanelaPrincipal(usuario)
        janela.show()
        tela_login.close()

    tela_login.login_sucesso.connect(ao_fazer_login)
    tela_login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()