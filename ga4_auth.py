"""
GA4 Data API — Analise de conversao do site Scala
Property ID: 528936871
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, OrderBy,
    FilterExpression, Filter
)

PROPERTY_ID = "528936871"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "ga4_token.json")

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

credentials = None

# Carregar token salvo se existir
if os.path.exists(TOKEN_FILE):
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

# Renovar ou autenticar
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print("Renovando token...")
        credentials.refresh(Request())
    else:
        print("Abrindo autenticação Google no browser...")
        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
        credentials = flow.run_local_server(port=8080, open_browser=True)

    # Salvar token para próximas execuções
    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())

print("✅ Autenticado com sucesso!\n")

client = BetaAnalyticsDataClient(credentials=credentials)
DATE_RANGE = [DateRange(start_date="2026-03-21", end_date="today")]

def run(req):
    try:
        return client.run_report(req)
    except Exception as e:
        print(f"  [ERRO] {e}\n")
        return None

# ── 1. Visão Geral ────────────────────────────────────────────────────────────
print("=" * 60)
print("1. VISAO GERAL (21/03 ate hoje)")
print("=" * 60)
r = run(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=DATE_RANGE,
    metrics=[
        Metric(name="sessions"),
        Metric(name="activeUsers"),
        Metric(name="bounceRate"),
        Metric(name="averageSessionDuration"),
        Metric(name="engagementRate"),
    ]
))
if r and r.rows:
    v = [x.value for x in r.rows[0].metric_values]
    print(f"  Sessoes:              {v[0]}")
    print(f"  Usuarios ativos:      {v[1]}")
    print(f"  Bounce rate:          {float(v[2])*100:.1f}%  (meta: <70%)")
    print(f"  Duracao media:        {float(v[3]):.0f}s  ({float(v[3])/60:.1f}min)  (meta: >90s)")
    print(f"  Engagement rate:      {float(v[4])*100:.1f}%")
else:
    print("  Sem dados — GTM provavelmente nao esta configurado no Vercel")

# ── 2. Todos os eventos ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. TODOS OS EVENTOS (o que o GA4 esta recebendo)")
print("=" * 60)
r2 = run(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=DATE_RANGE,
    dimensions=[Dimension(name="eventName")],
    metrics=[Metric(name="eventCount")],
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
))
if r2 and r2.rows:
    for row in r2.rows:
        name = row.dimension_values[0].value
        count = row.metric_values[0].value
        marker = " <<< CONVERSAO" if name == "wa_button_click" else ""
        print(f"  {name:<40} {count:>5}{marker}")
else:
    print("  Sem eventos registrados")

# ── 3. Scroll depth (metrica nativa do GA4) ───────────────────────────────────
print("\n" + "=" * 60)
print("3. SCROLL DEPTH (GA4 Enhanced Measurement nativo)")
print("=" * 60)
r3 = run(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=DATE_RANGE,
    dimensions=[Dimension(name="percentScrolled")],
    metrics=[Metric(name="eventCount")],
    dimension_filter=FilterExpression(
        filter=Filter(
            field_name="eventName",
            string_filter=Filter.StringFilter(value="scroll")
        )
    ),
))
if r3 and r3.rows:
    for row in r3.rows:
        pct = row.dimension_values[0].value
        count = row.metric_values[0].value
        print(f"  {pct}% scrolled: {count} usuarios")
else:
    print("  Sem dados de scroll (Enhanced Measurement pode nao estar ativo)")

# ── 4. Dispositivos ───────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. DISPOSITIVOS")
print("=" * 60)
r4 = run(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=DATE_RANGE,
    dimensions=[Dimension(name="deviceCategory")],
    metrics=[
        Metric(name="sessions"),
        Metric(name="bounceRate"),
        Metric(name="averageSessionDuration"),
    ],
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
))
if r4 and r4.rows:
    for row in r4.rows:
        device = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        bounce = float(row.metric_values[1].value) * 100
        duration = float(row.metric_values[2].value)
        print(f"  {device:<12} {sessions} sessoes  bounce: {bounce:.1f}%  duracao: {duration:.0f}s")
else:
    print("  Sem dados de dispositivo")

# ── 5. Fonte de trafego ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("5. FONTE DE TRAFEGO")
print("=" * 60)
r5 = run(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=DATE_RANGE,
    dimensions=[
        Dimension(name="sessionSource"),
        Dimension(name="sessionMedium"),
    ],
    metrics=[Metric(name="sessions"), Metric(name="engagementRate")],
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
))
if r5 and r5.rows:
    for row in r5.rows:
        source = row.dimension_values[0].value
        medium = row.dimension_values[1].value
        sessions = row.metric_values[0].value
        engagement = float(row.metric_values[1].value) * 100
        print(f"  {source}/{medium:<25} {sessions} sessoes  engagement: {engagement:.1f}%")
else:
    print("  Sem dados de fonte")

# ── 6. Landing pages ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("6. LANDING PAGES")
print("=" * 60)
r6 = run(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=DATE_RANGE,
    dimensions=[Dimension(name="landingPage")],
    metrics=[
        Metric(name="sessions"),
        Metric(name="bounceRate"),
        Metric(name="averageSessionDuration"),
    ],
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
))
if r6 and r6.rows:
    for row in r6.rows:
        page = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        bounce = float(row.metric_values[1].value) * 100
        duration = float(row.metric_values[2].value)
        print(f"  {page:<35} {sessions} sessoes  bounce: {bounce:.1f}%  duracao: {duration:.0f}s")
else:
    print("  Sem dados de landing page")

print("\n" + "=" * 60)
print("ANALISE CONCLUIDA")
print("=" * 60)
