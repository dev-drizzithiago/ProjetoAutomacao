import os, json, msal, requests
from datetime import datetime, timedelta, timezone


# =========================
# Configurações (ENV VARS)
# =========================
TENANT_ID    = os.getenv("Organization")
CLIENT_ID    = os.getenv("CLIENT_ID")
PFX_PATH     = os.getenv("PATH_CERTIFICADO")            # ex.: C:\Temp\ExchangeOnlineAutomation.pfx
PFX_PASSWORD = os.getenv("PASSWORD")        # mesma senha que você usa no EXO
SHARED_UPN   = os.getenv("ORGANIZADOR_GRUPO")          # ex.: gti.inovacao@segeticonsultoria.com
TEAM_ID      = os.getenv("NOME_GRUPO")             # groupId da equipe (GTI – Inovação)
CHANNEL_ID   = os.getenv("CHANNEL_ID")          # 19:...@thread.tacv2 do canal (Área de Trabalho)


# Zona de horário do Windows usada pelo Exchange/Graph
# Ref: IDs de TZ do Windows nas chamadas de create event
TIMEZONE = "E. South America Standard Time"  # São Paulo (padrão). Ajuste se necessário.  [7](https://www.devhut.net/use-the-microsoft-graph-rest-api-to-create-an-event-in-the-users-calendar/)

GRAPH = "https://graph.microsoft.com/v1.0"
SCOPES = ["https://graph.microsoft.com/.default"]
