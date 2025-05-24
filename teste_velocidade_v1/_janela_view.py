import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel

app = QApplication(sys.argv) # Gerencia a aplicação.


class JanelaPrincipal:
    def __init__(self):
        self.janela_principal = QWidget()  # Cria uma janela básica.
        self.janela_principal.setWindowTitle('Teste de velocidade')  # Define o título da janela
        self.janela_principal.resize(400, 300)

        self.label_titulo = QLabel('Teste de velocidade', self.janela_principal)
        self.label_titulo.move(150, 10)

        self.janela_principal.show()  # Exibe a janela na tela.


if __name__ == '__main__':
    iniciando_obj_janela = JanelaPrincipal()
    sys.exit(app.exec())  # Mantém a aplicação rodando até que o usuário feche a janela.
