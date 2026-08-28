# Manual — Módulo Watchdog (Auto-Restart de Aplicativo)

Este manual descreve como integrar uma função de **auto-restart** ao seu utilitário Python já existente, permitindo escolher um app e garantir que ele seja reaberto automaticamente sempre que for fechado (acidental ou manualmente).

> **Escopo:** este módulo reinicia o processo quando ele deixa de existir. Ele **não** impede o fechamento em si (isso exigiria hooks de sistema de baixo nível, o que não é recomendável) — ele neutraliza o efeito, reabrindo o app em poucos segundos.

---

## 1. Pré-requisitos

```bash
pip install psutil
```

`psutil` é usado para verificar processos por nome de forma confiável (mais robusto que `tasklist` via subprocess).

---

## 2. Estrutura de configuração

Sugestão de arquivo `config.json` para que seu utilitário salve qual app deve ser monitorado, sem precisar hardcodar:

```json
{
  "watchdog_apps": [
    {
      "name": "3CXDesktopApp",
      "exe_path": "C:\\Users\\usuario\\AppData\\Local\\3CXDesktopApp\\3CXDesktopApp.exe",
      "check_interval_seconds": 30,
      "enabled": true
    }
  ]
}
```

Como seu utilitário já tem uma interface para "escolher o app", ele só precisa gravar `name` (nome do processo, sem `.exe`) e `exe_path` (caminho completo do executável) nesse formato. Múltiplos apps podem ser adicionados na lista.

---

## 3. Módulo core — `watchdog_core.py`

```python
import psutil
import subprocess
import time
import json
import logging
from pathlib import Path

logging.basicConfig(
    filename="watchdog.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def is_running(process_name: str) -> bool:
    """Verifica se existe um processo com esse nome rodando."""
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and process_name.lower() in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def restart_app(exe_path: str):
    """Inicia o executável informado."""
    try:
        subprocess.Popen([exe_path], shell=False)
        logging.info(f"App reiniciado: {exe_path}")
    except Exception as e:
        logging.error(f"Falha ao reiniciar {exe_path}: {e}")

def load_config(config_path: str = "config.json") -> list:
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("watchdog_apps", [])

def monitor_loop(config_path: str = "config.json"):
    """Loop principal: verifica todos os apps configurados em ciclos."""
    while True:
        apps = load_config(config_path)
        for app in apps:
            if not app.get("enabled", True):
                continue
            if not is_running(app["name"]):
                logging.warning(f"{app['name']} não está rodando. Reiniciando...")
                restart_app(app["exe_path"])
        # Usa o menor intervalo configurado entre os apps ativos
        intervals = [a["check_interval_seconds"] for a in apps if a.get("enabled", True)]
        sleep_time = min(intervals) if intervals else 30
        time.sleep(sleep_time)

if __name__ == "__main__":
    monitor_loop()
```

**Pontos importantes:**
- `is_running` usa correspondência parcial de nome (`in`), o que cobre casos em que o processo tem sufixos variáveis. Se preferir correspondência exata, troque por `==`.
- O loop lê o `config.json` a cada ciclo — isso permite que seu utilitário adicione/remova apps monitorados **sem precisar reiniciar o watchdog**.
- Todo evento vai para `watchdog.log`, útil para auditoria (ex: mostrar quantas vezes o app caiu num turno).

---

## 4. Integração com seu utilitário existente

Se seu utilitário já tem uma tela/CLI para "escolher o app", basta que, ao selecionar um app, ele:

1. Descubra o `exe_path` (pode usar um file picker, ou `psutil.Process(pid).exe()` se o app já estiver aberto no momento da seleção).
2. Grave a entrada no `config.json` conforme o formato acima.
3. Garanta que o `watchdog_core.py` esteja rodando (veja seção 5).

Exemplo de função para adicionar um app via seu utilitário:

```python
def add_watched_app(name: str, exe_path: str, interval: int = 30, config_path: str = "config.json"):
    config_file = Path(config_path)
    data = {"watchdog_apps": []}
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    data.setdefault("watchdog_apps", [])
    data["watchdog_apps"] = [a for a in data["watchdog_apps"] if a["name"] != name]  # evita duplicado
    data["watchdog_apps"].append({
        "name": name,
        "exe_path": exe_path,
        "check_interval_seconds": interval,
        "enabled": True
    })

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## 5. Fazendo o watchdog rodar sempre (persistência)

O script Python precisa estar sempre ativo para funcionar. Duas formas comuns no Windows:

### Opção A — Tarefa Agendada (mais simples)

1. Empacote ou aponte diretamente para o interpretador Python:
   - Programa: `C:\Python3x\pythonw.exe` (o `pythonw.exe`, não `python.exe`, evita abrir janela de console)
   - Argumentos: `C:\Scripts\watchdog_core.py`
2. Disparador: **No logon** (ou "Ao iniciar o sistema" se quiser rodar mesmo sem login).
3. Configure para reiniciar em caso de falha (aba **Configurações** → "Se a tarefa falhar, reiniciar cada: 1 minuto").

### Opção B — Compilar como serviço Windows (mais robusto)

Se quiser que o watchdog sobreviva mesmo a logoff, use `pywin32` para registrar como serviço:

```bash
pip install pywin32
```

Isso é mais avançado — se fizer sentido para o seu caso (várias estações, gestão centralizada), posso detalhar em um manual separado.

---

## 6. Testando

1. Adicione o 3CX (ou o app desejado) via seu utilitário.
2. Confirme que `config.json` foi atualizado corretamente.
3. Rode `python watchdog_core.py` manualmente no terminal primeiro (antes de agendar) para validar o comportamento.
4. Feche o app manualmente e observe se ele reabre dentro do `check_interval_seconds` configurado.
5. Verifique `watchdog.log` para confirmar o registro do evento.

---

## 7. Limitações e observações

- Não impede o fechamento em si — apenas reabre o app rapidamente. Se o app exigir login manual (ex: 3CX sem "lembrar sessão"), o reinício abrirá a tela de login, e não a sessão ativa anterior.
- Se múltiplas instâncias do mesmo executável puderem rodar (ex: várias janelas), ajuste `is_running` para uma lógica mais específica (por PID, título de janela, etc.), evitando reaberturas duplicadas.
- Recomenda-se revisar o log periodicamente — reincidência alta pode indicar necessidade de investigar a causa raiz do fechamento (crash, ação do usuário, política de energia, etc.), e não só mitigar o efeito.
