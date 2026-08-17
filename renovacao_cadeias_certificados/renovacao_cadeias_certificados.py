from __future__ import annotations

"""
Instalador de Certificados Itau (GlobalSign R46) - com interface grafica.

Funcionalidades:
- Selecionar o .zip baixado do Developer Portal Itau, uma pasta ja extraida,
  ou certificados .cer/.crt avulsos.
- Escolher quais certificados instalar e em qual repositorio do Windows
  (Autoridades Raiz Confiaveis / Autoridades Intermediarias).
- Instalar os certificados marcados (via Import-Certificate do PowerShell).
- Ao terminar a instalacao sem erros, testa automaticamente a conexao
  com os endpoints da Itau. Tambem da pra testar a qualquer momento.

Requisitos: Windows 10/11 ou Windows Server, Python 3.8+ (Tkinter ja vem
junto no instalador oficial do python.org para Windows).

O programa pede elevacao de Administrador sozinho ao iniciar (UAC).
"""

import ctypes
import hashlib
import os
import subprocess
import sys
import threading
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


# --------------------------------------------------------------------------
# Elevacao / utilitarios de sistema
# --------------------------------------------------------------------------

def is_admin() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relancar_como_admin() -> None:
    script = os.path.abspath(sys.argv[0])
    argumentos = " ".join(f'"{a}"' for a in sys.argv[1:])
    linha_comando = f'"{script}" {argumentos}'.strip()
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, linha_comando, None, 1
    )


def run_powershell(comando: str, timeout: int = 60) -> tuple[bool, str]:
    resultado = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", comando],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    saida = (resultado.stdout + resultado.stderr).strip()
    return resultado.returncode == 0, saida


# --------------------------------------------------------------------------
# Deteccao e classificacao de certificados
# --------------------------------------------------------------------------

def classificar(nome_arquivo: str) -> tuple[str, bool]:
    """Sugere (repositorio, marcado_por_padrao) a partir do nome do arquivo."""
    nome = nome_arquivo.lower()
    if "root" in nome:
        return "Root", True
    if " ca " in f" {nome} " or nome.endswith("ca.cer") or "ca 20" in nome or "-ca" in nome:
        return "CA", True
    # provavelmente um certificado final (leaf) do proprio servidor -
    # nao e obrigatorio pelo tutorial oficial, entao fica desmarcado
    return "CA", False


def escanear_pasta(pasta: Path) -> list[dict]:
    encontrados: list[dict] = []
    vistos_hash: set[str] = set()
    caminhos = sorted(pasta.rglob("*.cer")) + sorted(pasta.rglob("*.crt"))
    for arquivo in caminhos:
        try:
            dados = arquivo.read_bytes()
        except Exception:
            continue
        h = hashlib.sha256(dados).hexdigest()
        if h in vistos_hash:
            continue
        vistos_hash.add(h)
        repositorio, marcado = classificar(arquivo.name)
        encontrados.append({"caminho": arquivo, "repositorio": repositorio, "marcado": marcado})
    return encontrados


# --------------------------------------------------------------------------
# Interface grafica
# --------------------------------------------------------------------------

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Instalador de Certificados Itau - GlobalSign R46")
        root.geometry("780x580")
        root.minsize(680, 480)

        self.certificados: list[dict] = []
        self.vars_marcado: dict[Path, tk.BooleanVar] = {}
        self.vars_repo: dict[Path, tk.StringVar] = {}

        self._montar_interface()

    # ---------------- construcao da UI ----------------

    def _montar_interface(self) -> None:
        topo = ttk.Frame(self.root, padding=10)
        topo.pack(fill="x")

        ttk.Button(topo, text="Selecionar .zip da Itau", command=self.selecionar_zip).pack(side="left", padx=4)
        ttk.Button(topo, text="Selecionar pasta extraida", command=self.selecionar_pasta).pack(side="left", padx=4)
        ttk.Button(topo, text="Adicionar certificado(s) avulso(s)", command=self.adicionar_avulsos).pack(side="left", padx=4)

        self.label_origem = ttk.Label(self.root, text="Nenhuma origem selecionada.", padding=(10, 4))
        self.label_origem.pack(fill="x")

        frame_lista = ttk.LabelFrame(self.root, text="Certificados encontrados", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=8)

        canvas = tk.Canvas(frame_lista, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
        self.frame_itens = ttk.Frame(canvas)
        self.frame_itens.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame_itens, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_acoes = ttk.Frame(self.root, padding=10)
        frame_acoes.pack(fill="x")

        self.btn_instalar = ttk.Button(frame_acoes, text="Instalar selecionados", command=self.instalar_thread)
        self.btn_instalar.pack(side="left", padx=4)

        self.btn_testar = ttk.Button(frame_acoes, text="Testar conexao", command=self.testar_thread)
        self.btn_testar.pack(side="left", padx=4)

        frame_log = ttk.LabelFrame(self.root, text="Log", padding=6)
        frame_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_widget = ScrolledText(frame_log, height=12, state="disabled", wrap="word")
        self.log_widget.pack(fill="both", expand=True)

    def log(self, texto: str) -> None:
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", texto + "\n")
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    # ---------------- selecao de origem ----------------

    def selecionar_zip(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecione o .zip de certificados da Itau",
            filetypes=[("Arquivo ZIP", "*.zip")],
        )
        if not caminho:
            return
        zip_path = Path(caminho)
        destino = zip_path.parent / zip_path.stem
        try:
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(destino)
        except Exception as erro:
            messagebox.showerror("Erro ao extrair", str(erro))
            return
        self.label_origem.config(text=f"Origem: {zip_path.name}  (extraido em: {destino})")
        self._carregar_certificados(destino)

    def selecionar_pasta(self) -> None:
        caminho = filedialog.askdirectory(title="Selecione a pasta com os certificados (.cer/.crt)")
        if not caminho:
            return
        self.label_origem.config(text=f"Origem: {caminho}")
        self._carregar_certificados(Path(caminho))

    def adicionar_avulsos(self) -> None:
        caminhos = filedialog.askopenfilenames(
            title="Selecione um ou mais certificados",
            filetypes=[("Certificados", "*.cer *.crt"), ("Todos os arquivos", "*.*")],
        )
        if not caminhos:
            return
        hashes_atuais = {
            hashlib.sha256(item["caminho"].read_bytes()).hexdigest() for item in self.certificados
        }
        for c in caminhos:
            p = Path(c)
            try:
                dados = p.read_bytes()
            except Exception:
                continue
            h = hashlib.sha256(dados).hexdigest()
            if h in hashes_atuais:
                continue
            hashes_atuais.add(h)
            repositorio, marcado = classificar(p.name)
            self.certificados.append({"caminho": p, "repositorio": repositorio, "marcado": marcado})
        self._renderizar_lista()

    def _carregar_certificados(self, pasta: Path) -> None:
        encontrados = escanear_pasta(pasta)
        if not encontrados:
            messagebox.showwarning("Nada encontrado", "Nenhum certificado (.cer/.crt) foi encontrado nessa origem.")
            return
        self.certificados = encontrados
        self._renderizar_lista()
        self.log(f"{len(encontrados)} certificado(s) encontrado(s) em: {pasta}")

    def _renderizar_lista(self) -> None:
        for widget in self.frame_itens.winfo_children():
            widget.destroy()
        self.vars_marcado.clear()
        self.vars_repo.clear()

        ttk.Label(self.frame_itens, text="Instalar", width=8, font=("", 9, "bold")).grid(row=0, column=0, padx=4, pady=4)
        ttk.Label(self.frame_itens, text="Certificado", font=("", 9, "bold")).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(self.frame_itens, text="Repositorio destino", font=("", 9, "bold")).grid(row=0, column=2, padx=4)

        for i, item in enumerate(self.certificados, start=1):
            caminho: Path = item["caminho"]
            var_marcado = tk.BooleanVar(value=item["marcado"])
            var_repo = tk.StringVar(value=item["repositorio"])
            self.vars_marcado[caminho] = var_marcado
            self.vars_repo[caminho] = var_repo

            ttk.Checkbutton(self.frame_itens, variable=var_marcado).grid(row=i, column=0)
            texto = caminho.name
            if item["repositorio"] == "CA" and not item["marcado"]:
                texto += "   (certificado final do servidor - opcional)"
            ttk.Label(self.frame_itens, text=texto).grid(row=i, column=1, sticky="w", padx=4)
            combo = ttk.Combobox(
                self.frame_itens, textvariable=var_repo, values=["Root", "CA"], width=8, state="readonly"
            )
            combo.grid(row=i, column=2, padx=4, pady=2)

    # ---------------- instalacao ----------------

    def instalar_thread(self) -> None:
        selecionados = [item for item in self.certificados if self.vars_marcado[item["caminho"]].get()]
        if not selecionados:
            messagebox.showinfo("Nada selecionado", "Marque ao menos um certificado para instalar.")
            return
        self.btn_instalar.config(state="disabled")
        self.btn_testar.config(state="disabled")
        threading.Thread(target=self._instalar, args=(selecionados,), daemon=True).start()

    def _instalar(self, selecionados: list[dict]) -> None:
        self.log("\n=== Instalando certificados selecionados ===")
        falhas = 0
        for item in selecionados:
            caminho: Path = item["caminho"]
            repositorio = self.vars_repo[caminho].get()
            comando = (
                f'Import-Certificate -FilePath "{caminho}" '
                f'-CertStoreLocation Cert:\\LocalMachine\\{repositorio}'
            )
            ok, saida = run_powershell(comando)
            status = "OK" if ok else "FALHOU"
            self.log(f"[{status}] ({repositorio}) {caminho.name}")
            if saida:
                self.log(f"    {saida}")
            if not ok:
                falhas += 1

        self.root.after(0, self._pos_instalacao, falhas)

    def _pos_instalacao(self, falhas: int) -> None:
        self.btn_instalar.config(state="normal")
        self.btn_testar.config(state="normal")
        if falhas == 0:
            self.log("\nInstalacao concluida sem erros. Iniciando teste de conexao automaticamente...")
            self.testar_thread()
        else:
            messagebox.showwarning(
                "Instalacao com falhas",
                f"{falhas} certificado(s) falharam ao instalar. Veja o log para detalhes.",
            )

    # ---------------- teste ----------------

    def testar_thread(self) -> None:
        self.btn_testar.config(state="disabled")
        self.btn_instalar.config(state="disabled")
        threading.Thread(target=self._testar, daemon=True).start()

    def _testar(self) -> None:
        self.log("\n=== Testando conexao com endpoints Itau ===")
        script_ps = r'''
$endpoints = @(
    "https://secure.gateway.api.itau/healthcheckbalance",
    "https://api.gateway.itau.com.br/healthcheckbalance",
    "https://api-bin.gateway.itau.com.br/healthcheckbalance",
    "https://sts.itau.com.br"
)
foreach ($url in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
        Write-Output "[OK] $url - HTTP $($r.StatusCode)"
    } catch {
        Write-Output "[ERRO] $url - $($_.Exception.Message)"
    }
}
'''
        _, saida = run_powershell(script_ps, timeout=90)
        linhas = saida.splitlines() if saida else []
        problema_certificado = False
        for linha in linhas:
            self.log(linha)
            if linha.startswith("[ERRO]"):
                minusc = linha.lower()
                if any(p in minusc for p in ["ssl", "tls", "certificate", "trust", "certificado", "confiança", "confianca"]):
                    problema_certificado = True

        self.root.after(0, self._pos_teste, problema_certificado, bool(linhas))

    def _pos_teste(self, problema_certificado: bool, teve_saida: bool) -> None:
        self.btn_testar.config(state="normal")
        self.btn_instalar.config(state="normal")
        if not teve_saida:
            self.log("Nao foi possivel executar o teste (sem saida do PowerShell).")
            return
        if problema_certificado:
            self.log("\n>>> Ainda ha falha relacionada a certificado/TLS. Confira o log acima.")
            messagebox.showwarning("Teste concluido", "Ainda ha falha de certificado/TLS. Veja o log.")
        else:
            self.log(
                "\n>>> Nenhuma falha de certificado/TLS detectada. Erros de HTTP "
                "(401/403/404) sao esperados sem um token de autenticacao valido - "
                "o que importa aqui e que o handshake TLS funcionou."
            )
            messagebox.showinfo(
                "Teste concluido",
                "Sem falhas de certificado/TLS. A cadeia parece corretamente instalada.",
            )


def main() -> None:
    if os.name != "nt":
        print("Este programa deve ser executado no Windows.")
        sys.exit(1)

    if not is_admin():
        raiz_temp = tk.Tk()
        raiz_temp.withdraw()
        messagebox.showinfo(
            "Elevacao necessaria",
            "Este programa precisa ser executado como Administrador.\n"
            "Vou reabrir com permissao de administrador agora (aceite o aviso do Windows).",
        )
        raiz_temp.destroy()
        try:
            relancar_como_admin()
        except Exception as erro:
            print(f"Falha ao elevar: {erro}")
        sys.exit(0)

    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()