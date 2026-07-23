


# CLAUDE.md - Configurações e Diretrizes do Projeto

# Colinha
# <contexto>quem você é e o que está acontecendo</contexto>
# <dados>números, textos, inputs</dados>
# <tarefa>o que você quer que ele faça</tarefa>
# <formato>como quer a resposta</formato>

## Perfil do Usuário & Nível Técnico
- **Desenvolvedor:** Programador Pleno / Administrador de TI.
- **Abordagem:** Prefere explicações diretas, código limpo, modular, tipado e pronto para produção. Evite redundâncias e explicações excessivamente básicas.

## Contexto do Projeto
- **Nome do App:** pointRestaurations
- **Objetivo:** Criar um utilitário em Python para automatizar a criação diária de Pontos de Restauração do Windows no momento do login.
- **Interface:** Interface gráfica moderna utilizando Tkinter (preferencialmente a biblioteca `customtkinter` para o visual moderno).
- **Diretório Operacional:** `%LocalAppData%\pointRestaurations` (para o executável/scripts).
- **Logs e Relatórios:** Salvar relatórios de execução estruturados na pasta de documentos do usuário (`%UserProfile%\Documents`).
- **Automação:** Configurar e injetar tarefas programadas no Agendador de Tarefas do Windows (Task Scheduler) disparadas no Logon.

## Diretrizes de Código e Tecnologia
- **Linguagem:** Python 3.10+ com tipagem estática nos argumentos (Type Hinting).
- **Interface Gráfica:** `customtkinter` para componentes modernos e suporte a Dark/Light mode nativo.
- **Integração Windows:** Uso de `subprocess` executando comandos PowerShell em modo administrativo (`Checkpoint-Computer`) ou chamadas via `ctypes` / `win32com`.
- **Segurança / Privilégios:** O app requer privilégios de Administrador (UAC Elevation). Incluir validação no início do script (`ctypes.windll.shell32.IsUserAnAdmin()`).
- **Tratamento de Erros:** Capturar falhas de permissão, restrições do registro do Windows (limitação padrão de 24h para pontos de restauração por script) e gravar em arquivo de log formatado em JSON ou texto limpo.

## Comandos Úteis do Projeto
- **Instalação de Dependências:** `pip install customtkinter`
- **Execução do Script:** `python main.py`
- **Compilação do Executável (com UAC Admin e ícone):** `pyinstaller --noconfirm --onedir --windowed --uac-admin --icon "pointRestaurations/assets/icon.ico" --add-data "pointRestaurations/assets;pointRestaurations/assets" --name "pointRestaurations" main.py`

"Skills/Diretrizes"
## Automatização de Relatórios (PDF)
- Quando solicitado a estruturar ou gerar relatórios em PDF via Python, priorize o uso da biblioteca `fpdf2` ou `reportlab` por serem leves e fáceis de empacotar com o PyInstaller.
- O design dos relatórios deve seguir um padrão corporativo limpo: fontes como Helvetica/Arial, tabelas com linhas alternadas (zebra striping) e realces em azul escuro (`#1e3a8a`).
- Os PDFs gerados pelo sistema devem ser sempre direcionados para a pasta de Documentos do usuário de forma dinâmica usando `os.path.expanduser("~\\Documents")`.