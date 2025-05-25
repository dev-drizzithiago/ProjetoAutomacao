import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton

class JanelaPrincipal:
    def __init__(self):
        self.janela_principal = QWidget()  # Cria uma janela básica.
        self.janela_principal.setWindowTitle('Teste de velocidade')  # Define o título da janela
        self.janela_principal.resize(400, 300)

        self.label_titulo = QLabel('Teste de velocidade', self.janela_principal)
        self.label_titulo.move(150, 10)

        self.botao_iniciar_teste = QPushButton("Iniciar", self.janela_principal)
        self.botao_iniciar_teste.setFont('Time')
        self.botao_iniciar_teste.setStyleSheet('font-size: 40px')
        self.botao_iniciar_teste.move(150, 30)

        self.janela_principal.show()  # Exibe a janela na tela.


if __name__ == '__main__':
    app = QApplication(sys.argv)
    iniciando_obj_janela = JanelaPrincipal()
    sys.exit(app.exec())  # Mantém a aplicação rodando até que o usuário feche a janela.
