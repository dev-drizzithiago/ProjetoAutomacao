"""
Tem como finalidade compartilhar a caixa de correio da segeticonsultoria.

"""

class ShareCalendarMail:

    def __init__(self, compartilhado, usuario):
        pass
        self.email_compartilhamento = compartilhado
        self.email_usuario = usuario

    def adicionar_AvailabilityOnly(self):
        pass

    def adicionar_LimitedDetails(self):
        pass

    def adicionar_Reviewer(self):
        pass

    def adicionar_Author(self):
        pass

    def adicionar_Editor(self):
        pass

    def adicionar_PublishingEditor(self):
        pass

    def adicionar_Owner(self):
        pass


if __name__ == '__main__':
    print()
    print('Compartilhe um e-mail compartilhado')
    print('---' * 25)
    email_compartilhado = input('Entre com o E-mail compartilhado: ')
    email_usuario = input('Entre com o E-mail do usuário: ')

    obj_calendar = ShareCalendarMail(email_compartilhado, email_usuario)
