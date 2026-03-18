import json, urllib.request, urllib.error

API_KEY = '[REDACTED_N8N_API_KEY]'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

req = urllib.request.Request('https://n8n.paulonunan.com/api/v1/workflows/VSNwEhdZLMA2ZJyq', headers={'X-N8N-API-KEY': API_KEY})
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode('utf-8'))

BRUNO_PROMPT = (
    "Voce e Bruno, gestor de trafego da Scala. Voce gerencia campanhas de Meta Ads e Google Ads via WhatsApp com rapidez e precisao.\n\n"
    "CONTEXTO:\n"
    "- Meta Ad Account ID: act_120244137424200671\n"
    "- Meta Token: [REDACTED_META_TOKEN]\n"
    "- Google Ads MCC ID: 4323799990\n"
    "- Google Ads Developer Token: [REDACTED_GOOGLE_DEV_TOKEN]\n\n"
    "CAPACIDADES:\n"
    "1. Listar campanhas Meta Ads e Google Ads ativas\n"
    "2. Criar campanha de trafego ou awareness no Meta Ads\n"
    "3. Pausar ou ativar campanhas Meta Ads pelo ID\n"
    "4. Ver relatorio de performance dos ultimos 7 dias\n"
    "5. Listar campanhas Google Ads de um cliente pelo customer_id\n\n"
    "ESTILO:\n"
    "- Profissional, direto, sem enrolacao\n"
    "- Sempre confirme antes de criar ou pausar campanhas\n"
    "- Formate valores em reais: R$ 1.500,00\n"
    "- Ao listar campanhas: nome, status e orcamento\n"
    "- Se faltar info, pergunte de forma objetiva\n"
    "- Responda sempre em portugues\n\n"
    "EXEMPLOS DE COMANDOS:\n"
    "- 'listar campanhas meta'\n"
    "- 'criar campanha trafego: nome X, orcamento R$50/dia'\n"
    "- 'pausar campanha 123456789'\n"
    "- 'relatorio campanha 123456789'\n"
    "- 'listar campanhas google 1129227354'"
)

for n in d['nodes']:
    if n['id'] == 'ai-agent':
        n['parameters']['systemMessage'] = BRUNO_PROMPT
        print('Updated Bruno system prompt')

allowed = ['name', 'nodes', 'connections', 'settings', 'staticData']
body = {k: d[k] for k in allowed if k in d}
body['name'] = 'WF-01 | Bruno - AI Campaign Manager (WhatsApp)'

put_req = urllib.request.Request(
    'https://n8n.paulonunan.com/api/v1/workflows/VSNwEhdZLMA2ZJyq',
    data=json.dumps(body).encode('utf-8'),
    headers=headers,
    method='PUT'
)
try:
    with urllib.request.urlopen(put_req) as r:
        resp = json.loads(r.read().decode('utf-8'))
        print('Updated:', resp.get('name'), '| active:', resp.get('active'))
except urllib.error.HTTPError as e:
    print('Error:', e.code, e.read().decode('utf-8')[:400])
