import os, json, msal, requests
from datetime import datetime, timedelta, timezone


# =========================
# Configurações (ENV VARS)
# =========================
TENANT_ID = os.getenv("Organization")            # Tenant
CLIENT_ID = os.getenv("AppId")                   # ID do aplicativo (App registration) que você já usa para CBA (certificado).
PFX_PATH = os.getenv("PATH_CERTIFICADO")        # ex.: C:\Temp\ExchangeOnlineAutomation.pfx
PFX_PASSWORD = os.getenv("PASSWORD")                # mesma senha que você usa no EXO

SHARED_UPN = os.getenv("ORGANIZADOR_GRUPO")       # ex.: gti.inovacao@segeticonsultoria.com
TEAM_ID = os.getenv("NOME_GRUPO")              # groupId da equipe (GTI – Inovação)
CHANNEL_ID = os.getenv("CHANNEL_ID")              # 19:...@thread.tacv2 do canal (Área de Trabalho)


# Zona de horário do Windows usada pelo Exchange/Graph
# Ref: IDs de TZ do Windows nas chamadas de create event
# São Paulo (padrão). Ajuste se necessário.
# [7](https://www.devhut.net/use-the-microsoft-graph-rest-api-to-create-an-event-in-the-users-calendar/)
TIMEZONE = "E. South America Standard Time"

GRAPH = "https://graph.microsoft.com/v1.0"
SCOPES = ["https://graph.microsoft.com/.default"]


def get_app_token():
    if not all([TENANT_ID, CLIENT_ID, PFX_PATH, PFX_PASSWORD]):
        raise SystemExit("Defina TENANT_ID, CLIENT_ID, PFX_PATH, PFX_PASSWORD como variáveis de ambiente.")
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential={
            "private_key_pfx_path": PFX_PATH,
            "passphrase": PFX_PASSWORD
        }
    )
    token = app.acquire_token_silent(SCOPES, account=None) or app.acquire_token_for_client(SCOPES)
    if "access_token" not in token:
        raise SystemExit(f"Falha ao obter token Graph: {token.get('error_description')}")
    return token["access_token"]

if __name__ == "__main__":
    access_token = get_app_token()
    print("✓ Token obtido com sucesso. Tamanho:", len(access_token))

    # Chamada GET simples para validar escopo e conectividade
    me_url = "https://graph.microsoft.com/v1.0/organization"
    resp = requests.get(me_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=15)
    print("GET /organization ->", resp.status_code)
    print(resp.text[:400], "...")



get_app_token()