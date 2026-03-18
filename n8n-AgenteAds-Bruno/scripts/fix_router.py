import json, urllib.request, urllib.error

API_KEY = '[REDACTED_N8N_API_KEY]'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

req = urllib.request.Request('https://n8n.paulonunan.com/api/v1/workflows/EVbZX91iB5moD6I4', headers={'X-N8N-API-KEY': API_KEY})
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode('utf-8'))

# Fix: correct n8n expression without any escaping
EXPR = '={{ $json.phoneNumber }}'
PHONE = '556181292879'

for n in d['nodes']:
    if n['id'] == 'node-router-gestor':
        n['parameters']['conditions']['conditions'][0]['leftValue'] = EXPR
        n['parameters']['conditions']['conditions'][0]['rightValue'] = PHONE
        print('leftValue set to:', repr(EXPR))
        print('rightValue set to:', PHONE)

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
