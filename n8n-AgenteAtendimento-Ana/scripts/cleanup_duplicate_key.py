import json, sys, urllib.request, urllib.error

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZGVmMTgwMi1kMGM2LTQ5MGYtYWRkOC1jZDZmNWM0YjYwNGQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWE5YTM4ODktYWFhZC00ZjM3LTliZDUtOTZhZjRhZGRlM2Y0IiwiaWF0IjoxNzczMTYyNjA1fQ.XkQZ_3dNwZlllA8bgdIyVLxZ7GjP2IhJvTdX-hBUacM"
BASE_URL = "https://n8n.paulonunan.com/api/v1"
WF_ID = "EVbZX91iB5moD6I4"

# Fetch current workflow
req = urllib.request.Request(
    f"{BASE_URL}/workflows/{WF_ID}",
    headers={"X-N8N-API-KEY": API_KEY}
)
with urllib.request.urlopen(req) as resp:
    raw = resp.read()
    wf = json.loads(raw)

print(f"Fetched: {wf['name']}")
print(f"Nodes: {len(wf['nodes'])}, Active: {wf['active']}")

# Find and remove the spurious "E Paulo?" key (ASCII version)
# Keep only the proper Unicode "É Paulo?" key
keys_to_remove = []
for k in list(wf['connections'].keys()):
    if k == 'E Paulo?':
        keys_to_remove.append(k)
        print(f"Removing spurious key: {repr(k)}")

for k in keys_to_remove:
    del wf['connections'][k]

print(f"\nConnection keys after cleanup:")
for k in wf['connections']:
    print(f"  {repr(k)}")

# Verify the correct E Paulo connection is intact
for k in wf['connections']:
    if 'Paulo' in k and k != 'E Paulo?':
        print(f"\nCorrect Paulo key: {repr(k)}")
        print(json.dumps(wf['connections'][k], ensure_ascii=False, indent=2))

# Deploy
print("\nDeploying cleaned workflow...")
payload = {
    "name": wf['name'],
    "nodes": wf['nodes'],
    "connections": wf['connections'],
    "settings": wf.get('settings', {}),
    "staticData": wf.get('staticData', None)
}

payload_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
put_req = urllib.request.Request(
    f"{BASE_URL}/workflows/{WF_ID}",
    data=payload_bytes,
    headers={
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    },
    method="PUT"
)

try:
    with urllib.request.urlopen(put_req) as resp:
        result = json.loads(resp.read())
        print(f"\nSUCCESS! Workflow updated: {result['name']}")
        print(f"Active: {result['active']}")
        print(f"Updated at: {result['updatedAt']}")
        print(f"Node count: {len(result['nodes'])}")
        # Verify no E Paulo? key
        for k in result['connections']:
            if 'Paulo' in k:
                print(f"Paulo connection key: {repr(k)} -> {result['connections'][k]['main'][0]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(e.read().decode('utf-8')[:2000])
except Exception as e:
    print(f"Error: {e}")
