"""
Setup GTM + GA4 Admin
- GTM: troca trigger do Microsoft Clarity de All Pages → Timer 5000ms
- GA4: registra custom dimensions percent_scrolled, section_name, time_seconds
"""
import sys, os, json, time
sys.stdout.reconfigure(encoding='utf-8')

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/analytics.edit",
]

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "setup_token.json")

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

# Auth
credentials = None
if os.path.exists(TOKEN_FILE):
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print("Renovando token...")
        credentials.refresh(Request())
    else:
        print("Abrindo autenticacao no browser...")
        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
        credentials = flow.run_local_server(port=8080, open_browser=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())

print("Autenticado!\n")

gtm = googleapiclient.discovery.build("tagmanager", "v2", credentials=credentials)
ga4 = googleapiclient.discovery.build("analyticsadmin", "v1beta", credentials=credentials)

# ─── GTM ──────────────────────────────────────────────────────────────────────
print("=" * 56)
print("GTM — Microsoft Clarity → Timer 5000ms")
print("=" * 56)

# 1. Encontrar account + container GTM-TH5VGFDP
accounts = gtm.accounts().list().execute()
account_id = None
container_id = None
container_path = None

for acc in accounts.get("account", []):
    containers = gtm.accounts().containers().list(parent=acc["path"]).execute()
    for c in containers.get("container", []):
        if c.get("publicId") == "GTM-TH5VGFDP":
            account_id = acc["accountId"]
            container_id = c["containerId"]
            container_path = c["path"]
            print(f"Container encontrado: {c['name']} ({c['publicId']})")

if not container_path:
    print("ERRO: container GTM-TH5VGFDP nao encontrado")
    sys.exit(1)

# 2. Workspace default
workspaces = gtm.accounts().containers().workspaces().list(parent=container_path).execute()
workspace = workspaces["workspace"][0]
workspace_path = workspace["path"]
print(f"Workspace: {workspace['name']} ({workspace_path})")

# 3. Encontrar tag Microsoft Clarity
tags = gtm.accounts().containers().workspaces().tags().list(parent=workspace_path).execute()
clarity_tag = None
for tag in tags.get("tag", []):
    if "clarity" in tag.get("name", "").lower() or "clarity" in str(tag.get("type", "")).lower():
        clarity_tag = tag
        print(f"Tag Clarity encontrada: {tag['name']} (ID: {tag['tagId']})")
        break

if not clarity_tag:
    # Tentar por tipo de tag
    for tag in tags.get("tag", []):
        print(f"  Tag disponivel: {tag['name']} — tipo: {tag.get('type','?')}")
    print("AVISO: tag Clarity nao encontrada pelo nome. Verifique o nome acima.")
    sys.exit(1)

# 4. Verificar se ja existe trigger Timer 5000ms (por tipo/intervalo ou por nome)
triggers = gtm.accounts().containers().workspaces().triggers().list(parent=workspace_path).execute()
timer_trigger = None
for t in triggers.get("trigger", []):
    is_timer_type = t.get("type") == "TIMER"
    is_timer_name = "timer" in t.get("name", "").lower() and "5000" in t.get("name", "").lower()
    interval = next((p["value"] for p in t.get("parameter", []) if p["key"] == "interval"), None)
    if is_timer_type and (interval == "5000" or is_timer_name):
        timer_trigger = t
        print(f"Trigger Timer 5000ms ja existe: {t['name']} (ID: {t['triggerId']})")
        break
    elif is_timer_name:
        timer_trigger = t
        print(f"Trigger Timer ja existe (por nome): {t['name']} (ID: {t['triggerId']})")
        break

# 5. Criar trigger Timer se nao existir
if not timer_trigger:
    print("Criando trigger Timer 5000ms...")
    timer_trigger = gtm.accounts().containers().workspaces().triggers().create(
        parent=workspace_path,
        body={
            "name": "Timer - 5000ms",
            "type": "TIMER",
            "parameter": [
                {"type": "TEMPLATE", "key": "interval", "value": "5000"},
                {"type": "TEMPLATE", "key": "limit", "value": "1"},
                {"type": "BOOLEAN", "key": "firingId", "value": "true"},
            ],
        }
    ).execute()
    print(f"Trigger criado: {timer_trigger['name']} (ID: {timer_trigger['triggerId']})")

# 6. Atualizar tag Clarity para usar o Timer trigger
print(f"Atualizando tag Clarity para usar Timer trigger...")
clarity_tag["firingTriggerId"] = [timer_trigger["triggerId"]]

updated_tag = gtm.accounts().containers().workspaces().tags().update(
    path=clarity_tag["path"],
    body=clarity_tag
).execute()
print(f"Tag atualizada: {updated_tag['name']} — trigger: {updated_tag.get('firingTriggerId')}")

# 7. Criar versao e publicar
print("Criando versao do workspace...")
version_resp = gtm.accounts().containers().workspaces().create_version(
    path=workspace_path,
    body={"name": "Clarity Timer 5000ms", "notes": "Troca trigger Clarity de All Pages para Timer 5000ms — melhora LCP"}
).execute()

container_path_base = f"accounts/{account_id}/containers/{container_id}"

# Debug: mostrar estrutura da resposta
cv = version_resp.get("containerVersion", {})
version_id = cv.get("containerVersionId")
version_path_from_cv = cv.get("path", "")
print(f"  containerVersionId: {version_id}")
print(f"  path retornado: {version_path_from_cv}")

# Buscar versoes disponiveis via version_headers
headers_resp = gtm.accounts().containers().version_headers().list(
    parent=container_path_base
).execute()
headers = headers_resp.get("containerVersionHeader", [])
print(f"  Versoes encontradas: {[(h.get('containerVersionId'), h.get('name')) for h in headers[:5]]}")

# Publicar a versao mais recente
latest_version_id = headers[0].get("containerVersionId") if headers else version_id
publish_path = f"{container_path_base}/versions/{latest_version_id}"
print(f"Publicando versao {latest_version_id} ({publish_path})...")
published = gtm.accounts().containers().versions().publish(path=publish_path).execute()
print(f"GTM publicado com sucesso!")

# ─── GA4 CUSTOM DIMENSIONS ────────────────────────────────────────────────────
print()
print("=" * 56)
print("GA4 — Registrando Custom Dimensions")
print("=" * 56)

PROPERTY = "properties/528936871"
dimensions = [
    {"displayName": "Percent Scrolled",  "parameterName": "percent_scrolled", "scope": "EVENT"},
    {"displayName": "Section Name",      "parameterName": "section_name",      "scope": "EVENT"},
    {"displayName": "Time Seconds",      "parameterName": "time_seconds",      "scope": "EVENT"},
]

# Verificar quais ja existem
existing = ga4.properties().customDimensions().list(parent=PROPERTY).execute()
existing_params = [d.get("parameterName") for d in existing.get("customDimensions", [])]
print(f"Custom dimensions ja existentes: {existing_params or 'nenhuma'}")

for dim in dimensions:
    if dim["parameterName"] in existing_params:
        print(f"  SKIP (ja existe): {dim['parameterName']}")
        continue
    result = ga4.properties().customDimensions().create(
        parent=PROPERTY,
        body=dim
    ).execute()
    print(f"  CRIADA: {result.get('displayName')} ({result.get('parameterName')})")

print()
print("=" * 56)
print("TUDO CONCLUIDO")
print("  GTM: Clarity agora dispara apos 5s (nao bloqueia LCP)")
print("  GA4: Custom dimensions registradas e prontas para reportar")
print("=" * 56)
