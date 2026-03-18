import json, urllib.request, urllib.error

API_KEY = '[REDACTED_N8N_API_KEY]'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

req = urllib.request.Request('https://n8n.paulonunan.com/api/v1/workflows/EVbZX91iB5moD6I4', headers={'X-N8N-API-KEY': API_KEY})
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode('utf-8'))

for n in d['nodes']:
    if n['id'] == 'node-call-campaign-agent':
        # Fix body format - use bodyParameters instead of body object
        n['parameters'] = {
            'method': 'POST',
            'url': 'https://n8n.paulonunan.com/webhook/campaign-agent',
            'authentication': 'none',
            'sendBody': True,
            'contentType': 'json',
            'specifyBody': 'keypair',
            'bodyParameters': {
                'parameters': [
                    {'name': 'phoneNumber', 'value': '={{ $json.phoneNumber }}'},
                    {'name': 'messageText', 'value': '={{ $json.messageText }}'}
                ]
            },
            'options': {
                'response': {
                    'response': {
                        'neverError': True
                    }
                }
            }
        }
        print('Fixed Chamar Bruno node body parameters')

allowed = ['name', 'nodes', 'connections', 'settings', 'staticData']
body = {k: d[k] for k in allowed if k in d}

put_req = urllib.request.Request(
    'https://n8n.paulonunan.com/api/v1/workflows/EVbZX91iB5moD6I4',
    data=json.dumps(body).encode('utf-8'),
    headers=headers,
    method='PUT'
)
try:
    with urllib.request.urlopen(put_req) as r:
        resp = json.loads(r.read().decode('utf-8'))
        print('Updated:', resp.get('name'), '| active:', resp.get('active'))
except urllib.error.HTTPError as e:
    print('Error:', e.code, e.read().decode('utf-8')[:300])
