"""
Tem como finalidade compartilhar a caixa de correio da segeticonsultoria.

"""
import subprocess

class ShareCalendarMail:

    def __init__(self, compartilhado, usuario):
        pass
        self.email_compartilhamento = compartilhado
        self.email_usuario = usuario

    def adicionar_AvailabilityOnly(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights AvailabilityOnly -SendNotificationToUser $true'
        )

    def adicionar_LimitedDetails(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights LimitedDetails -SendNotificationToUser $true'
        )

    def adicionar_Reviewer(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights Reviewer -SendNotificationToUser $true'
        )

    def adicionar_Author(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights Author -SendNotificationToUser $true'
        )

    def adicionar_Editor(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights Editor -SendNotificationToUser $true'
        )

    def adicionar_PublishingEditor(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights PublishingEditor -SendNotificationToUser $true'
        )

    def adicionar_Owner(self):
        comando_shell = (
            f'Add-MailboxFolderPermission -Identity "{self.email_compartilhamento}" '
            f'-User {self.email_usuario} -AccessRights Owner -SendNotificationToUser $true'
        )


if __name__ == '__main__':
    print()
    print('Compartilhe um e-mail compartilhado')
    print('---' * 25)
    email_compartilhado = input('Entre com o E-mail compartilhado: ')
    email_usuario = input('Entre com o E-mail do usuário: ')

    obj_calendar = ShareCalendarMail(email_compartilhado, email_usuario)
