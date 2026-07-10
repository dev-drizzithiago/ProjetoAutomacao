# Manual do Usuário — pointRestaurations

Utilitário para automatizar a criação de Pontos de Restauração do Windows, com opção de disparo automático no logon.

## 1. Requisitos

- Windows 10/11 com o **Proteção do Sistema** (System Restore) habilitado para a unidade `C:`.
- Privilégios de **Administrador** — o app não funciona sem eles.

## 2. Como abrir

Execute `pointRestaurations.exe` (pasta `dist\pointRestaurations\`). Se a conta não estiver elevada, o Windows exibirá o prompt do **Controle de Conta de Usuário (UAC)** — clique em **Sim** para continuar. O app se relança automaticamente como Administrador e abre a interface.

> Copie a pasta `dist\pointRestaurations\` inteira ao distribuir — o `.exe` depende dos arquivos dentro de `_internal`.

## 3. Tela principal

No topo da janela fica um indicador (badge) de status:

| Badge | Significado |
|---|---|
| 🟢 **Administrador** | App rodando com privilégios elevados — todos os botões ficam habilitados. |
| 🔴 **Sem privilégios de Admin** | O app não conseguiu elevar. Todos os botões de ação ficam **desabilitados** até reabrir como Administrador. |

Abaixo do badge, uma linha de **status** mostra o resultado da última ação executada, com horário.

Na parte inferior, o painel **Histórico de Execução** lista os eventos registrados no log do dia (sucesso, avisos e erros), atualizado automaticamente após cada ação.

## 4. Os botões

### 4.1 "Criar Ponto de Restauração Agora"

Executa imediatamente o comando `Checkpoint-Computer` do Windows para criar um novo ponto de restauração.

- **O que esperar:** o botão fica desabilitado e muda para "Criando..." enquanto o comando roda (a criação pode levar alguns segundos).
- **Sucesso:** status muda para "Ponto de restauração criado com sucesso." e um evento `SUCCESS` aparece no histórico.
- **Aviso comum — restrição de 24h:** o Windows só permite **um** ponto de restauração criado por script/API a cada 24 horas. Se você já criou um recentemente (manualmente ou via este app), o botão vai retornar o aviso "Já existe um ponto de restauração criado nas últimas 24 horas" — isso é comportamento normal do sistema, não um erro do app.
- **Erro de permissão:** se aparecer "Permissão negada", feche o app e reabra-o confirmando o prompt do UAC.

### 4.2 "Instalar Tarefa no Logon"

Registra uma tarefa no **Agendador de Tarefas do Windows** (nome interno `pointRestaurations_LogonCheckpoint`) configurada para:

- Disparar automaticamente **toda vez que o usuário atual fizer logon**.
- Rodar com o nível de privilégio mais alto (`HIGHEST`), sem exibir prompt do UAC novamente.
- Chamar o app em modo silencioso (sem abrir a interface), apenas criando o ponto de restauração e gravando o resultado no log.

Use este botão **uma única vez** para configurar a automação diária. Se a tarefa já existir, ela é sobrescrita (`/F`) com a configuração atual.

- **Sucesso:** status "Tarefa agendada instalada com sucesso (dispara no logon)."
- **Falha:** normalmente indica que o app não está rodando como Administrador, ou que o Agendador de Tarefas está com alguma restrição de política local.

### 4.3 "Remover Tarefa" (botão vermelho)

Remove a tarefa agendada criada pelo botão anterior, desativando a criação automática no logon.

- **Sucesso:** status "Tarefa agendada removida com sucesso."
- Se a tarefa não existir (nunca foi instalada, ou já removida), o app retorna um aviso — não é um erro crítico.

> Não há confirmação antes de remover — a ação é imediata.

## 5. Onde ficam os registros (logs)

Todo evento (criação de ponto, instalação/remoção de tarefa, erros) é gravado em:

```
%UserProfile%\Documents\pointRestaurations\logs\execucao_AAAA-MM-DD.jsonl
```

Um arquivo por dia, em formato JSON Lines (uma linha JSON por evento: `timestamp`, `level`, `message`, `details`). Útil para auditoria ou depuração fora da interface gráfica.

## 6. Uso silencioso (avançado)

A tarefa agendada chama o app com o parâmetro `--run-silent`, que pula a interface gráfica e apenas executa a criação do ponto de restauração, registrando o resultado no log. Você pode rodar esse modo manualmente também:

```
pointRestaurations.exe --run-silent
```

## 7. Perguntas frequentes

**O app trava tentando reabrir depois do UAC?**
Verifique se o UAC não está desabilitado nas configurações do sistema de um jeito que impeça o `runas` de funcionar; nesse caso, clique com o botão direito no `.exe` e escolha "Executar como administrador".

**Criei um ponto de restauração pelo botão, mas ele não aparece no "Restaurar Sistema"?**
Confira se a Proteção do Sistema está habilitada para a unidade `C:` em Painel de Controle → Sistema → Proteção do Sistema.

**Posso rodar o app sem instalar a tarefa?**
Sim — o botão "Criar Ponto de Restauração Agora" funciona de forma independente, útil para criação manual e pontual.
