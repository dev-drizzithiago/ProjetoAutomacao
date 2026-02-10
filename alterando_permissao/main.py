from conectando_exechange_online import ProcessoRun

class AlterarPermissaoReunioes:
    def __init__(self):
        self.cmd = """        
            Import-Module ExchangeOnlineManagement 
            Connect-ExchangeOnline -AppId  
              -CertificateThumbprint "" 
              -Organization "segeticonsultoria.onmicrosoft.com" 
            
            Get-EXOMailbox -ResultSize 1
            Disconnect-ExchangeOnline -Confirm:$false            
        """
        self.init_conectar_exchange = ProcessoRun()

    def chamando_obj_conexao(self):
        self.init_conectar_exchange = ProcessoRun()
        resultado = self.init_conectar_exchange.run_spinner(self.cmd, 'Conectando... ')
        print()
        print('---' * 20)
        print(resultado.returncode)


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    init_obj_calendar.chamando_obj_conexao()


