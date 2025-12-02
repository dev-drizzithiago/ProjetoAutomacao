"""
Tem como finalidade compartilhar a caixa de correio da segeticonsultoria.

"""
import subprocess
import itertools
from time import sleep
from threading import Event, Thread

class ShareCalendarMail:

    def __init__(self, compartilhado, usuario):
        pass
        self.email_compartilhamento = compartilhado
        self.email_usuario = usuario

    def _run_processo_powershell(self, comando_shell):
        resultado_processo = run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", comando_shell],
            shell=True,
            check=False,
            capture_output=True
        )
        return resultado_processo

    def _spinner(self, stop_event, prefix='Processando... '):

        ciclo = itertools.cycle(['|', '/', '-', '\\'])

        while not stop_event.is_set():
            # \r volta o cursor para início da linha
            print(f"\r{prefix} {next(ciclo)}", end='', flush=True)
            sleep(0.1)

        # limpa linha ao finalizar
        print('\n' + ' ' * 60 + '\r', end='', flush=True)

    def _run_spinner(self, comando_str, texto_spinner):
        stop_event = Event()
        _thread = Thread(target=self._spinner, args=(stop_event, texto_spinner), daemon=True)
        _thread.start()
        try:
            result = self._run_processo_powershell(comando_str)
            return result
        finally:
            stop_event.set()
            _thread.join()

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
