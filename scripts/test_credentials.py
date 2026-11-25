"""Testa as credenciais da API do YouTube sem publicar nada: renova o token e lê o canal."""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
    print(k, "configurado" if os.environ.get(k) else "FALTANDO")
creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                    client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
ch = yt.channels().list(part="snippet,statistics", mine=True).execute()["items"][0]
print("Canal autorizado:", ch["id"], "-", ch["snippet"]["title"], "-", ch["statistics"]["subscriberCount"], "inscritos")
assert ch["id"] == "UCg5q7pGWh7lto5HeZcbL6uw", "O token é de OUTRO canal!"
print("Escopos do token:", creds.scopes)
v = yt.videos().list(part="status", id="vu8LSF5MfLk").execute()["items"][0]["status"]
print("Leitura do Ep 5 ok:", v.get("privacyStatus"), "containsSyntheticMedia =", v.get("containsSyntheticMedia"))
print("TUDO CERTO: credenciais funcionando.")
