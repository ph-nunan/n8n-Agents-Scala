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
    wf = json.loads(resp.read())

print(f"Fetched workflow: {wf['name']}")
print(f"Nodes: {len(wf['nodes'])}, Active: {wf['active']}")

# ---- NEW NODES ----
new_nodes = [
    {
        "id": "node-buscar-sessao",
        "name": "Buscar Sessao",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [900, 60],
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": "UeSaLFF10d9utrmA",
                "name": "Google Sheets - Paulo"
            }
        },
        "alwaysOutputData": True,
        "parameters": {
            "operation": "read",
            "documentId": {"__rl": True, "value": "1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U", "mode": "id"},
            "sheetName": {"mode": "name", "value": "Sessoes"},
            "filtersUI": {
                "values": [
                    {
                        "lookupColumn": "phone",
                        "lookupValue": "={{ $json.phoneNumber }}"
                    }
                ]
            },
            "options": {
                "returnFirstMatch": True
            }
        }
    },
    {
        "id": "node-if-resetar-menu",
        "name": "IF Resetar Menu",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1120, -80],
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose"},
                "conditions": [
                    {
                        "id": "cond-menu-reset",
                        "leftValue": "={{ $('Extrair Dados').first().json.messageText.toLowerCase().trim() }}",
                        "rightValue": "menu",
                        "operator": {"type": "string", "operation": "equals"}
                    },
                    {
                        "id": "cond-voltar-reset",
                        "leftValue": "={{ $('Extrair Dados').first().json.messageText.toLowerCase().trim() }}",
                        "rightValue": "voltar",
                        "operator": {"type": "string", "operation": "equals"}
                    }
                ],
                "combinator": "or"
            },
            "options": {}
        }
    },
    {
        "id": "node-if-tem-sessao",
        "name": "IF Tem Sessao",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1340, -80],
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose"},
                "conditions": [
                    {
                        "id": "cond-has-session",
                        "leftValue": "={{ $json.agent }}",
                        "rightValue": "",
                        "operator": {"type": "string", "operation": "notEmpty"}
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        }
    },
    {
        "id": "node-route-by-session",
        "name": "Route by Session",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1560, -80],
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose"},
                "conditions": [
                    {
                        "id": "cond-route-bruno",
                        "leftValue": "={{ $json.agent.toLowerCase() }}",
                        "rightValue": "bruno",
                        "operator": {"type": "string", "operation": "equals"}
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        }
    },
    {
        "id": "node-salvar-sessao-bruno",
        "name": "Salvar Sessao Bruno",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [1780, 0],
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": "UeSaLFF10d9utrmA",
                "name": "Google Sheets - Paulo"
            }
        },
        "parameters": {
            "operation": "appendOrUpdate",
            "documentId": {"__rl": True, "value": "1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U", "mode": "id"},
            "sheetName": {"mode": "name", "value": "Sessoes"},
            "columns": {
                "mappingMode": "defineBelow",
                "value": {
                    "phone": "={{ $json.phoneNumber }}",
                    "agent": "Bruno",
                    "updated_at": "={{ new Date().toISOString() }}"
                },
                "matchingColumns": ["phone"],
                "schema": [
                    {"id": "phone", "displayName": "phone", "required": False, "defaultMatch": True, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False},
                    {"id": "agent", "displayName": "agent", "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False},
                    {"id": "updated_at", "displayName": "updated_at", "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False}
                ]
            },
            "options": {}
        }
    },
    {
        "id": "node-salvar-sessao-ana",
        "name": "Salvar Sessao Ana",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [1780, 140],
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": "UeSaLFF10d9utrmA",
                "name": "Google Sheets - Paulo"
            }
        },
        "parameters": {
            "operation": "appendOrUpdate",
            "documentId": {"__rl": True, "value": "1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U", "mode": "id"},
            "sheetName": {"mode": "name", "value": "Sessoes"},
            "columns": {
                "mappingMode": "defineBelow",
                "value": {
                    "phone": "={{ $json.phoneNumber }}",
                    "agent": "Ana",
                    "updated_at": "={{ new Date().toISOString() }}"
                },
                "matchingColumns": ["phone"],
                "schema": [
                    {"id": "phone", "displayName": "phone", "required": False, "defaultMatch": True, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False},
                    {"id": "agent", "displayName": "agent", "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False},
                    {"id": "updated_at", "displayName": "updated_at", "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False}
                ]
            },
            "options": {}
        }
    },
    {
        "id": "node-limpar-sessao",
        "name": "Limpar Sessao",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [1340, 80],
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": "UeSaLFF10d9utrmA",
                "name": "Google Sheets - Paulo"
            }
        },
        "parameters": {
            "operation": "update",
            "documentId": {"__rl": True, "value": "1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U", "mode": "id"},
            "sheetName": {"mode": "name", "value": "Sessoes"},
            "columns": {
                "mappingMode": "defineBelow",
                "value": {
                    "phone": "={{ $('Extrair Dados').first().json.phoneNumber }}",
                    "agent": "",
                    "updated_at": "={{ new Date().toISOString() }}"
                },
                "matchingColumns": ["phone"],
                "schema": [
                    {"id": "phone", "displayName": "phone", "required": False, "defaultMatch": True, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False},
                    {"id": "agent", "displayName": "agent", "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False},
                    {"id": "updated_at", "displayName": "updated_at", "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "display": True, "type": "string", "readOnly": False, "removed": False}
                ]
            },
            "options": {}
        }
    }
]

# Add new nodes to workflow
wf['nodes'].extend(new_nodes)

# ---- UPDATE CONNECTIONS ----
# 1. Change 'E Paulo?' output[0] from Switch Agente to Buscar Sessao
wf['connections']['E Paulo?'] = wf['connections'].pop('E Paulo?', wf['connections'].get('\u00c9 Paulo?', {}))

# Find the actual key for E Paulo? node
epaulokey = None
for k in wf['connections']:
    if 'Paulo' in k:
        epaulokey = k
        break

print(f"Found E Paulo key: {repr(epaulokey)}")
wf['connections'][epaulokey]['main'][0] = [{'node': 'Buscar Sessao', 'type': 'main', 'index': 0}]

# 2. Buscar Sessao -> IF Resetar Menu
wf['connections']['Buscar Sessao'] = {
    'main': [[{'node': 'IF Resetar Menu', 'type': 'main', 'index': 0}]]
}

# 3. IF Resetar Menu
#   [0]=TRUE -> Limpar Sessao
#   [1]=FALSE -> IF Tem Sessao
wf['connections']['IF Resetar Menu'] = {
    'main': [
        [{'node': 'Limpar Sessao', 'type': 'main', 'index': 0}],
        [{'node': 'IF Tem Sessao', 'type': 'main', 'index': 0}]
    ]
}

# 4. Limpar Sessao -> Enviar Menu
wf['connections']['Limpar Sessao'] = {
    'main': [[{'node': 'Enviar Menu', 'type': 'main', 'index': 0}]]
}

# 5. IF Tem Sessao
#   [0]=TRUE -> Route by Session
#   [1]=FALSE -> Switch Agente
wf['connections']['IF Tem Sessao'] = {
    'main': [
        [{'node': 'Route by Session', 'type': 'main', 'index': 0}],
        [{'node': 'Switch Agente', 'type': 'main', 'index': 0}]
    ]
}

# 6. Route by Session
#   [0]=TRUE (Bruno) -> Chamar Bruno directly (session already stored)
#   [1]=FALSE (Ana) -> Buscar Historico
wf['connections']['Route by Session'] = {
    'main': [
        [{'node': 'Chamar Bruno (Campaign Agent)', 'type': 'main', 'index': 0}],
        [{'node': 'Buscar Hist\u00f3rico', 'type': 'main', 'index': 0}]
    ]
}

# 7. Switch Agente
#   [0]=Bruno -> Salvar Sessao Bruno
#   [1]=Ana -> Salvar Sessao Ana
#   [2]=Menu -> Enviar Menu
wf['connections']['Switch Agente'] = {
    'main': [
        [{'node': 'Salvar Sessao Bruno', 'type': 'main', 'index': 0}],
        [{'node': 'Salvar Sessao Ana', 'type': 'main', 'index': 0}],
        [{'node': 'Enviar Menu', 'type': 'main', 'index': 0}]
    ]
}

# 8. Salvar Sessao Bruno -> Chamar Bruno
wf['connections']['Salvar Sessao Bruno'] = {
    'main': [[{'node': 'Chamar Bruno (Campaign Agent)', 'type': 'main', 'index': 0}]]
}

# 9. Salvar Sessao Ana -> Buscar Historico
wf['connections']['Salvar Sessao Ana'] = {
    'main': [[{'node': 'Buscar Hist\u00f3rico', 'type': 'main', 'index': 0}]]
}

# ---- UPDATE Chamar Bruno to use $('Extrair Dados') references ----
# So it works whether coming from Route by Session OR Salvar Sessao Bruno
for node in wf['nodes']:
    if node['id'] == 'node-call-campaign-agent':
        node['parameters']['bodyParameters']['parameters'] = [
            {"name": "phoneNumber", "value": "={{ $('Extrair Dados').first().json.phoneNumber }}"},
            {"name": "messageText", "value": "={{ $('Extrair Dados').first().json.messageText }}"}
        ]
        print("Updated Chamar Bruno parameters")
        break

print(f"\nFinal node count: {len(wf['nodes'])}")
print(f"Connection keys: {sorted(wf['connections'].keys())}")

# ---- SAVE BACKUP ----
backup_path = "C:/Users/nunan-pc/Documents/n8n builder/n8n-Agents-Scala/n8n-AgenteAtendimento-Ana/workflows/workflow_before_session.json"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print(f"\nBackup saved to {backup_path}")

# ---- DEPLOY via PUT ----
print("\nDeploying to n8n...")

# Build payload - n8n PUT requires specific fields
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
        print(f"SUCCESS! Workflow updated: {result['name']}")
        print(f"Active: {result['active']}")
        print(f"Updated at: {result['updatedAt']}")
        print(f"Node count: {len(result['nodes'])}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(e.read().decode('utf-8')[:2000])
except Exception as e:
    print(f"Error: {e}")
