"""Publica um episódio no YouTube pela API oficial (YouTube Data API v3).

Uso (no GitHub Actions): python scripts/publish_youtube.py queue/epNN.json
O JSON da fila tem: video (caminho do MP4 no repo), title, description, tags,
publish_at (ISO com fuso, ex. 2026-11-25T11:30:00-03:00). Espera até publish_at,
sobe o vídeo público, marca conteúdo sintético (IA) e grava published/epNN.json.

Credenciais (secrets do GitHub, nunca no repositório):
YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
"""
import json, os, sys, time, datetime as dt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

job_path = sys.argv[1]
job = json.load(open(job_path, encoding="utf-8"))
name = os.path.splitext(os.path.basename(job_path))[0]
out_path = f"published/{name}.json"
if os.path.exists(out_path):
    print(f"{name} já foi publicado ({out_path}); nada a fazer."); sys.exit(0)

# 1) espera o horário
when = dt.datetime.fromisoformat(job["publish_at"])
while True:
    left = (when - dt.datetime.now(dt.timezone.utc)).total_seconds()
    if left <= 0: break
    print(f"Aguardando {int(left)} s até {job['publish_at']}", flush=True)
    time.sleep(min(left, 300))

creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                    client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

body = {
    "snippet": {"title": job["title"], "description": job["description"], "tags": job.get("tags", []),
                "categoryId": str(job.get("category_id", "27")),
                "defaultLanguage": "pt-BR", "defaultAudioLanguage": "pt-BR"},
    "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "embeddable": True,
               "publicStatsViewable": True, "license": "youtube", "containsSyntheticMedia": True},
}

# 2) upload resumável com novas tentativas em erro temporário
video_id = None
for attempt in range(1, 7):
    try:
        req = yt.videos().insert(part="snippet,status", body=body, notifySubscribers=True,
                                 media_body=MediaFileUpload(job["video"], mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status: print(f"enviado {int(status.progress() * 100)}%", flush=True)
        video_id = resp["id"]; break
    except HttpError as e:
        code = e.resp.status
        print(f"tentativa {attempt}: HTTP {code} {e}", flush=True)
        if code not in (429, 500, 502, 503, 504) or attempt == 6: raise
        time.sleep(60 * attempt)
print("videoId:", video_id)

# 3) garante o selo de IA (alguns campos podem ser ignorados no insert)
v = yt.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
if not v.get("containsSyntheticMedia"):
    yt.videos().update(part="status", body={"id": video_id, "status": body["status"]}).execute()
    v = yt.videos().list(part="status", id=video_id).execute()["items"][0]["status"]

os.makedirs("published", exist_ok=True)
json.dump({"episode": name, "youtube_id": video_id, "url": f"https://www.youtube.com/shorts/{video_id}",
           "published_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "title": job["title"], "status": v}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok:", out_path)
