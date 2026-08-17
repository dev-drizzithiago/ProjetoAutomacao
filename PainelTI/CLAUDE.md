# CLAUDE.md - PainelTI

## Perfil do Usuário & Nível Técnico
- **Desenvolvedor:** Administrador de TI (Segeti Consultoria), mantém sozinho um conjunto de
  scripts Python de automação de infraestrutura para a rede da empresa.
- **Abordagem:** Prefere explicações diretas, testes reais (não só `py_compile`) antes de
  considerar algo pronto, e vai testando o app aos poucos, em produção, relatando erros reais
  (prints do app rodando) em vez de pedir revisão de código antecipadamente.

## Contexto do Projeto
- **Nome do App:** PainelTI
- **Objetivo:** Consolidar num único aplicativo (`.exe` autocontido, sem depender de Python
  instalado na máquina de destino) todas as automações de setup/manutenção de máquina que
  antes viviam espalhadas em scripts soltos no repositório `ProjetoAutomacao`.
- **Origem:** Especificado em [gemini-code-1784027848653.md](../gemini-code-1784027848653.md)
  (raiz do repositório).
- **Como é usado:** A equipe de TI abre o `PainelTI.exe` numa máquina (elevando via UAC com a
  conta de domínio `ti`), executa as ações necessárias pelas abas, e fecha. Não é um serviço
  contínuo — exceto pelo checkpoint diário agendado (ver "Diagnóstico & Restauração" abaixo).
- **Distribuição:** O app roda **direto de uma pasta de rede**
  (`\\192.168.0.10\APP Login\Programas Basicos`), sem ser copiado pra cada máquina. Por isso
  ele precisa ser 100% autocontido (ver "Decisões arquiteturais" abaixo) — só a pasta
  `instaladores/` exige manutenção manual (colocar os `.exe`/`.msi` a instalar).

## Estrutura do projeto

```
PainelTI/
  main.py                   # entry point: UAC, --silent (checkpoint agendado), inicia GUI
  CLAUDE.md                 # este arquivo
  .gitignore

  app/
    admin.py                 # is_admin()/relaunch_as_admin() (ShellExecuteW "runas")
    constants.py              # APP_DIR, CONFIG_DIR, RELATORIOS_DIR, ICON_PATH, LOGS_DIR...
    logger.py                 # EventLogger — log estruturado JSON Lines por sessão
    tooltip.py                # CTkToolTip (customtkinter não tem nativo)
    gui.py                    # janela principal (CTkTabview, uma aba por área)
    network_share.py          # pasta C:\Digitalização + compartilhamento SMB + permissão NTFS
    wifi_manager.py           # CRUD de perfis Wi-Fi (JSON) + aplicação via netsh
    instaladores.py           # descobre/instala silenciosamente apps de instaladores/
    backup_usuario.py         # zip de Desktop/Downloads/Documents + extras -> servidor
    manutencao_windows.py     # Diagnóstico Dism/SFC, ponto de restauração, agendamento logon, PDF

    modules/                  # wrappers dos 6 módulos legados ainda usados (import in-process)
      common.py                 # OperationResult compartilhado
      legacy_loader.py          # import_legacy_main() — evita colisão de nomes "main.py"
      anydesk_module.py
      explorer_module.py        # desbloquer_view_explorer (MOTW de PDFs)
      inventario_module.py      # softwares_instalados (scan hardware/software -> Excel)
      rede_segeti_module.py     # utilitarios_segeti/config_adp_rede
      exchange_module.py        # alterando_permissao (Exchange Online)
      mikrotik_module.py        # mikrotik_monitoramento

  legacy/                    # código-fonte dos módulos legados, embutido no .exe (só leitura)
    anydesk/
    alterando_permissao/
    desbloquer_view_explorer/
    mikrotik_monitoramento/
    softwares_instalados/
    utilitarios_segeti/
    CorrecaoSistema/          # NÃO USADO MAIS — funcionalidade portada pra manutencao_windows.py
    GerarPontoRestauracao/    # NÃO USADO MAIS — idem. Mantidos no disco, não vão pro .exe.

  assets/
    icon.ico                 # ícone do app (gerado com Pillow, monitor+engrenagem, tema azul)

  config/                    # visível ao lado do .exe — editável pela equipe de TI
    wifi_profiles.json        # {nome, senha} das redes corporativas
    backup_pastas_extras.json # pastas extras (apps do governo) incluídas no backup

  instaladores/               # visível ao lado do .exe — só isso exige manutenção manual
    config.json                # {"nome_do_arquivo.exe": "flags silenciosos"}
    *.exe / *.msi               # instaladores de terceiros (gitignored, não vão pro Git)

  relatorios/                 # visível ao lado do .exe — saída de Inventário e PDFs de diagnóstico
```

## Abas do app (visão funcional)

1. **Rede** — cria/compartilha `C:\Digitalização` (permissão pro usuário local `ti`) +
   cadastro/aplicação de redes Wi-Fi corporativas.
2. **Manutenção** — reset do AnyDesk, bloquear/desbloquear visualização de PDFs (MOTW).
3. **Diagnóstico & Restauração** — Dism/SFC, criar/listar Pontos de Restauração, agendar
   checkpoint diário no logon, gerar relatório PDF. Substitui os antigos CorrecaoSistema e
   GerarPontoRestauracao (ver "Histórico" abaixo).
4. **Instalação de Apps** — instala silenciosamente tudo que estiver em `instaladores/`.
5. **Backup de Usuário** — zip de Desktop/Downloads/Documents + pastas extras, pro servidor,
   ao desligar um colaborador.
6. **Inventário** — scan de hardware/software da máquina, gera planilhas Excel em `relatorios/`.
7. **Rede SEGETI** — detectar/configurar adaptadores de rede, host DNS, teste de conectividade.
8. **Exchange Online** — shared mailbox/calendário via Exchange Online (requer `.env` em
   `legacy/alterando_permissao/`).
9. **Mikrotik** — busca de logs DHCP + ping nos IPs, sob demanda (não é loop contínuo).

## Decisões arquiteturais importantes (não repetir os mesmos erros)

- **Tudo precisa viver dentro de `PainelTI/`.** Rodar de uma pasta de rede compartilhada só
  funciona se o `.exe` não depender de mais nada fora dessa pasta — por isso os 8 módulos
  legados foram movidos pra `PainelTI/legacy/` (eram pastas soltas na raiz do repo antes) e
  `--add-data` embute cada um dentro do `.exe` no build.
- **Colisão de `main.py`:** `anydesk/main.py`, `alterando_permissao/main.py`,
  `desbloquer_view_explorer/main.py`, `mikrotik_monitoramento/main.py`,
  `softwares_instalados/main.py`, `utilitarios_segeti/main.py` todos se chamam `main.py`.
  `legacy_loader.import_legacy_main()` carrega cada um via `importlib.util.spec_from_file_location`
  com um alias único em `sys.modules`, nunca `import main` direto.
- **`APP_DIR` vs `_bundle_dir()` (`app/constants.py`):** dois conceitos de "pasta base"
  diferentes quando compilado (PyInstaller `--onedir` separa o `.exe` de uma pasta
  `_internal/`):
  - `APP_DIR` = pasta do `.exe` (`sys.executable`'s parent) — usado pra tudo que a equipe de
    TI precisa editar/ver: `config/`, `instaladores/`, `relatorios/`.
  - `_bundle_dir()` = `sys._MEIPASS` (que na prática é `_internal/`) — usado só pra recursos
    empacotados só-leitura: `assets/icon.ico`, `legacy/`.
  - Erro já cometido: botar `instaladores`/`legacy` direto em `--add-data` sem pensar nisso
    fazia tudo cair dentro de `_internal/`, escondido — `instaladores/` teve que virar uma
    pasta criada em runtime (`INSTALADORES_DIR.mkdir(...)`) do lado do `.exe`, não empacotada.
- **`sys.executable` não é Python quando compilado.** Módulos que precisam chamar
  `python <script>.py` como processo separado (não existe mais nenhum caso disso no app hoje,
  mas se voltar a acontecer) não podem usar `sys.executable` — vira o próprio `PainelTI.exe`.
  Usar `"python"` fixo (dependente do PATH) ou, melhor ainda, portar a lógica pra dentro do
  próprio app (foi o que aconteceu com CorrecaoSistema/GerarPontoRestauracao).
- **`.\ti` não resolve de forma confiável** (testado com `icacls` e `.NET NTAccount.Translate()`
  nesta rede — falha mesmo com o usuário `ti` local existindo). `network_share.USUARIO_PADRAO`
  usa `f"{os.environ['COMPUTERNAME']}\\ti"` (nome explícito do computador) em vez do atalho `.`.
- **Permissão de compartilhamento (SMB) ≠ permissão NTFS.** Sempre as duas: `Grant-SmbShareAccess`
  (nível rede) **e** `icacls` (nível disco). Faltar uma dá "Acesso Negado" mesmo a outra estando ok.
- **UAC "duplo hop":** rodando o `.exe` direto da rede, se a elevação UAC troca de credencial
  (digitar usuário/senha do `ti` em vez de só confirmar), a sessão de rede usada pelo processo
  passa a ser a do `ti` também — então dá pra restringir a pasta de rede só pro `ti` sem
  precisar liberar pra "todos".
- **CorrecaoSistema/GerarPontoRestauracao tinham funcionalidade sobreposta** (os dois criavam
  ponto de restauração, os dois agendavam tarefa de logon, os dois geravam PDF com `fpdf2`) —
  consolidados num módulo só (`manutencao_windows.py`) em vez de portar os dois separadamente.
- **`GerarPontoRestauracao/Lib/` e `/share/`** (na raiz do repo, fora de `PainelTI/`) são uma
  virtualenv inteira (~45MB, 2841 arquivos) commitada no Git por engano. Não fazem parte do
  código do app — não foram movidos nem devem ser tratados como código-fonte.

## Diretrizes de Código e Tecnologia
- **Linguagem:** Python 3.10+ com tipagem estática (Type Hinting).
- **Interface Gráfica:** `customtkinter`.
- **Padrão de retorno:** toda função que executa ação de sistema devolve um
  `OperationResult(success: bool, message: str)` — nunca deixa exceção subir até a GUI. Cada
  módulo (`network_share`, `wifi_manager`, `instaladores`, `backup_usuario`,
  `manutencao_windows`, `modules/common.py`) tem sua própria cópia da dataclass (duplicação
  intencional, evita acoplamento entre módulos independentes).
- **Ações longas** rodam em thread via `App._run_async` (`app/gui.py`), atualizando a UI só
  via `self.after(0, ...)` a partir da thread principal do Tk.
- **Segurança / Privilégios:** app roda elevado (UAC) desde o `main.py`. Compilado, o
  manifesto `--uac-admin` do PyInstaller já pede elevação antes mesmo do Python rodar.
- **Compartilhamento de PC do usuário `ti`:** sempre a conta LOCAL (`COMPUTERNAME\ti`), nunca
  confundir com a conta de domínio `ti` usada pra elevar o app.

## Comandos Úteis do Projeto

**Rodar em desenvolvimento:**
```
python PainelTI/main.py
```

**Instalar dependências (ambiente de dev):**
```
pip install customtkinter pandas wmi psutil cryptography librouteros python-dotenv openpyxl xlsxwriter fpdf2 pyinstaller
```

**Compilar o executável** (rodar de dentro de `PainelTI/`):
```
pyinstaller --noconfirm --onedir --windowed --uac-admin ^
  --icon "assets/icon.ico" ^
  --add-data "assets;assets" ^
  --add-data "legacy/anydesk;legacy/anydesk" ^
  --add-data "legacy/alterando_permissao;legacy/alterando_permissao" ^
  --add-data "legacy/desbloquer_view_explorer;legacy/desbloquer_view_explorer" ^
  --add-data "legacy/mikrotik_monitoramento;legacy/mikrotik_monitoramento" ^
  --add-data "legacy/softwares_instalados;legacy/softwares_instalados" ^
  --add-data "legacy/utilitarios_segeti;legacy/utilitarios_segeti" ^
  --hidden-import wmi --hidden-import psutil --hidden-import pandas ^
  --hidden-import xlsxwriter --hidden-import dotenv --hidden-import cryptography ^
  --hidden-import librouteros --hidden-import fpdf ^
  --collect-all wmi --collect-all cryptography --collect-all librouteros --collect-all fpdf ^
  --name "PainelTI" main.py
```
Resultado em `dist/PainelTI/` (`PainelTI.exe` + pasta `_internal/`) — **os dois precisam ser
copiados juntos** pra distribuição/rede, nunca só o `.exe` sozinho.

**Distribuir pra pasta de rede:** copiar o *conteúdo* de `dist/PainelTI/` direto pra
`\\192.168.0.10\APP Login\Programas Basicos\` (sem aninhar em subpasta) — `legacy/` já vai
embutido no `.exe`, só `instaladores/`, `config/` e `relatorios/` são criados/mantidos ali.

## Histórico (fases de desenvolvimento)
1. **MVP** — estrutura base, aba Rede (compartilhamento + Wi-Fi).
2. **Integração dos 8 módulos legados** — import in-process dos 6 simples, subprocess pros 2
   apps completos (CorrecaoSistema/GerarPontoRestauracao).
3. **Instalação de apps** — aba Instalação de Apps, pasta `instaladores/` + `config.json`.
4. **Backup de usuário** — aba Backup, zip pro servidor ao desligar colaborador.
5. **Self-contained** — moveu os 8 módulos legados de pastas soltas na raiz do repo pra
   `PainelTI/legacy/`, corrigiu bug de `sys.executable` quando compilado.
6. **Portar CorrecaoSistema/GerarPontoRestauracao nativamente** — eliminou a dependência de
   Python externo pros dois últimos módulos, consolidando em `manutencao_windows.py` +
   pasta `relatorios/` local pro Inventário (antes ia pro servidor de rede fixo).

Contexto detalhado de cada decisão (incluindo perguntas feitas ao usuário e alternativas
descartadas) está no histórico de conversas — este arquivo é o resumo vivo, atualize-o quando
fizer mudanças estruturais relevantes.
