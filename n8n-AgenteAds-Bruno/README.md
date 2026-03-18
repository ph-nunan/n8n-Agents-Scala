# Sistema de Gestão de Anúncios com IA — Scala
## Documentação Completa para Contexto de IA

> **Data de criação:** 2026-03-18
> **Projeto:** Sistema completo de gestão de Meta Ads + Google Ads via WhatsApp, usando n8n + IA
> **Status:** PRODUÇÃO — todos os workflows ativos e funcionando

---

## 1. VISÃO GERAL DO SISTEMA

O sistema permite que **Paulo** (gestor da Scala) gerencie campanhas de Meta Ads e Google Ads inteiramente pelo WhatsApp, usando um agente de IA chamado **Bruno**. O sistema também envia relatórios semanais automáticos de performance para cada cliente.

### Arquitetura Geral

```
WhatsApp (número +55 61 8189-4189)
         │
         ▼
[SCALA WORKFLOW - EVbZX91iB5moD6I4]
    Ana: atende clientes normais
    Bruno: atende Paulo (gestor) — roteado por número de telefone
         │ (se phoneNumber == 556181292879)
         ▼
[WF-01 BRUNO - VSNwEhdZLMA2ZJyq]
    AI Agent (GPT-4o) com tools Meta Ads + Google Ads
         │
         ▼
    Resposta via WhatsApp → Paulo
```

```
Toda segunda-feira, 8h00
[WF-02 META REPORTS - dLr5lDWj7rtLgbGk]
    Lê aba "Clientes" do Google Sheets
    Para cada cliente com meta_ad_account_id:
        Chama Meta Insights API
        Formata relatório semanal
        Envia via WhatsApp para o cliente

Toda segunda-feira, 8h05
[WF-03 GOOGLE REPORTS - ndMNpUBlGhfd6CO2]
    Lê aba "Clientes" do Google Sheets
    Para cada cliente com google_customer_id:
        Chama Google Ads API (GAQL)
        Formata relatório semanal
        Envia via WhatsApp para o cliente
```

---

## 2. INSTÂNCIA N8N

- **URL:** `https://n8n.paulonunan.com`
- **API Key (JWT sem expiração):** `[REDACTED — configurado em N8N_API_KEY no MCP Server]`
- **Ambiente:** Docker/VPS auto-hospedado com proxy reverso (domínio próprio)
- **IMPORTANTE:** Chamadas internas entre workflows devem usar `http://localhost:5678` (não o domínio público — causa ECONNREFUSED)

---

## 3. CREDENCIAIS CONFIGURADAS NO N8N

| ID | Tipo | Nome | Uso |
|----|------|------|-----|
| `umUchtUGj2ZzikQ5` | `whatsAppApi` | WhatsApp account | Envio de mensagens WhatsApp (todos os workflows) |
| `3Ucs5ITEFuzuPAJx` | `whatsAppTriggerApi` | WhatsApp OAuth account | Recebimento de mensagens (Scala workflow) |
| `IhMcXCpYHHMLb5Gh` | `openAiApi` | OpenAi account 2 | Modelo GPT-4o do Bruno (WF-01) |
| `LFnyHUsH7lj5FEvQ` | `openAiApi` | scala-agent | Modelo OpenAI da Ana (Scala) |
| `2yQz1qh73JLxM3Rr` | `googleAdsOAuth2Api` | Google Ads account | Google Ads API (WF-01 e WF-03) |
| `UeSaLFF10d9utrmA` | `googleSheetsOAuth2Api` | Google Sheets - Paulo | Sheets dos clientes (WF-02 e WF-03) |
| `QGp1FxkKTfYhYYJ0` | `googleCalendarOAuth2Api` | Google Calendar - Paulo | Agenda (Scala workflow) |

---

## 4. CONTAS DE ADS

### Meta Ads
- **Ad Account ID:** `act_120244137424200671`
- **Access Token (permanente, System User):** `[REDACTED — configurado como credencial n8n]`
- **Meta App ID:** `854431830954678`
- **WhatsApp Business Account ID:** `1480192843700940`
- **WhatsApp Phone Number ID:** `971782562694033`
- **System User:** `scala-user` (ID: `61579495951643`)
- **API Version em uso:** v19.0

### Google Ads
- **MCC (Manager Account) ID:** `4323799990`
- **Developer Token:** `[REDACTED — configurado como header no n8n]`
- **OAuth2 Client ID:** `[REDACTED — ver n8n credencial ID: 2yQz1qh73JLxM3Rr]`
- **OAuth2 Client Secret:** `[REDACTED — ver n8n credencial ID: 2yQz1qh73JLxM3Rr]`
- **Credencial n8n:** `googleAdsOAuth2Api` (ID: `2yQz1qh73JLxM3Rr`)
- **API Version em uso:** v19

---

## 5. WHATSAPP E ROTEAMENTO

- **Número WhatsApp:** `+55 61 8189-4189` (Phone Number ID: `971782562694033`)
- **IMPORTANTE:** Este número é compartilhado entre a Ana (atendimento) e o Bruno (gestão)
- **Roteamento por número do remetente** no nó "Router Gestor" do Scala workflow

### Lógica de Roteamento
```
Se phoneNumber == "556181292879"  (número pessoal de Paulo, sem o 9 extra)
    → Chamar Bruno (Campaign Agent)
    → POST http://localhost:5678/webhook/campaign-agent
    → Body: { phoneNumber, messageText }
Senão
    → Ana (atendimento normal de clientes)
```

### Número de Paulo
- **Número pessoal:** `61981292879`
- **Formato no WhatsApp (sem o 9 extra):** `556181292879`
- **ATENÇÃO:** WhatsApp Business Cloud API envia `556181292879` (10 dígitos após 55), não `5561981292879`

---

## 6. WORKFLOWS — DETALHAMENTO COMPLETO

### 6.1 SCALA — WhatsApp AI Agent (Ana) 24/7
- **ID:** `EVbZX91iB5moD6I4`
- **Status:** ATIVO
- **Função:** Atendimento automatizado de clientes da Scala + roteamento para Bruno
- **Trigger:** WhatsApp Trigger (recebe mensagens do número +55 61 8189-4189)
- **Webhook de recebimento:** Configurado via Meta Business Suite no App ID `854431830954678`

**Nós principais:**
1. `WhatsApp Trigger` — recebe mensagens
2. `Extrair Dados` — extrai phoneNumber, messageText, pushName
3. `Router Gestor` — IF phoneNumber == "556181292879"
4. `Chamar Bruno (Campaign Agent)` — HTTP POST para `http://localhost:5678/webhook/campaign-agent`
5. `Buscar Histórico` / `Ana AI` / `Enviar Resposta` — fluxo normal de atendimento

**FIXES aplicados (críticos para referência futura):**
- URL interna: `http://localhost:5678/webhook/campaign-agent` (não o domínio público)
- Router usa expression `={{ $json.phoneNumber }}` com rightValue `556181292879`

---

### 6.2 WF-01 — Bruno, AI Campaign Manager
- **ID:** `VSNwEhdZLMA2ZJyq`
- **Status:** ATIVO
- **Função:** Agente de IA para gestão de campanhas Meta Ads e Google Ads via WhatsApp
- **Trigger:** Webhook em `http://localhost:5678/webhook/campaign-agent` (responseMode: onReceived)
- **Modelo:** GPT-4o (typeVersion: 1.3) com credencial `IhMcXCpYHHMLb5Gh`

**Nós:**
1. `Webhook Trigger` — recebe POST com `{ phoneNumber, messageText }`
2. `Extract Message` — extrai phoneNumber e messageText do body
3. `AI Campaign Manager` — AI Agent (toolsAgent, promptType: define, text: `={{ $json.messageText }}`)
4. `OpenAI GPT-4o-mini` → `OpenAI GPT-4o` — modelo de linguagem

**AI Tools conectados ao agente:**
| Tool ID | Nome | Endpoint Meta API | Função |
|---------|------|-------------------|--------|
| `tool-list-meta-campaigns` | Listar Campanhas Meta | GET `/act_120244137424200671/campaigns` | Lista campanhas ativas |
| `tool-create-meta-campaign` | Criar Campanha Meta | POST `/act_120244137424200671/campaigns` | Cria nova campanha |
| `tool-pause-meta-campaign` | Pausar Ativar Campanha Meta | POST `/{campaign_id}` | Pausa ou ativa campanha |
| `tool-meta-insights` | Relatório Meta Campanha | GET `/{campaign_id}/insights` | Relatório últimos 7 dias |
| `tool-list-google-campaigns` | Listar Campanhas Google | POST `/{customer_id}/googleAds:search` | Lista campanhas Google |

**FIXES críticos no WF-01 (para referência futura):**
1. **responseMode:** Deve ser `onReceived` (não `responseNode`) — sem nó Respond to Webhook
2. **promptType:** Deve ser `define` no AI Agent — sem isso usa Chat Trigger (que não existe)
3. **lmChatOpenAi typeVersion:** Deve ser `1.3` com model como objeto `{__rl: true, value: "gpt-4o", mode: "list"}` — versão 1.2 com string simples falha com "Could not get parameter"
4. **Tool node format:** n8n versão atual usa `parametersQuery.values[{name, valueProvider}]` — NÃO `queryParameters.parameters[{name, value}]` para toolHttpRequest nodes
5. **Placeholders em tool nodes:** Usar `{placeholder}` sem `=` prefixo — `={placeholder}` é tratado como expressão n8n, não placeholder

---

### 6.3 WF-02 — Meta Ads Reports → WhatsApp
- **ID:** `dLr5lDWj7rtLgbGk`
- **Status:** ATIVO
- **Função:** Envia relatório semanal de Meta Ads para cada cliente ativo
- **Schedule:** Toda segunda-feira às 8h00 (`0 8 * * 1`)
- **Google Sheet:** `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A` (aba: `Clientes`)

**Fluxo:**
```
Schedule Trigger (seg 8h)
  → Read Clients (Google Sheets - aba Clientes)
  → Filter Active Clients (ativo=TRUE AND meta_ad_account_id not empty)
  → SplitInBatches (1 cliente por vez)
  → Meta Insights API (GET /{act_id}/insights)
  → Code Node (formata mensagem)
  → Send WhatsApp (envia para cliente)
  → loop volta ao SplitInBatches
```

**Estrutura esperada no Google Sheets (aba Clientes):**
```
nome_cliente | whatsapp | ativo | meta_ad_account_id | google_customer_id
```

**Meta API call:**
- URL: `https://graph.facebook.com/v19.0/{meta_ad_account_id}/insights`
- Params: `fields=campaign_name,impressions,clicks,spend,ctr,cpc,actions`, `date_preset=last_7d`
- Auth: access_token no query param

---

### 6.4 WF-03 — Google Ads Reports → WhatsApp
- **ID:** `ndMNpUBlGhfd6CO2`
- **Status:** ATIVO
- **Função:** Envia relatório semanal de Google Ads para cada cliente ativo
- **Schedule:** Toda segunda-feira às 8h05 (`5 8 * * 1`)
- **Google Sheet:** `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A` (mesmo sheet do WF-02)

**Fluxo:**
```
Schedule Trigger (seg 8h05)
  → Read Clients (Google Sheets - aba Clientes)
  → Filter Active Clients (ativo=TRUE AND google_customer_id not empty)
  → SplitInBatches (1 cliente por vez)
  → Google Ads API (POST /{customer_id}/googleAds:search)
  → Code Node (formata mensagem, converte micros → BRL)
  → Send WhatsApp (envia para cliente)
  → loop volta ao SplitInBatches
```

**Google Ads API call:**
- URL: `https://googleads.googleapis.com/v19/customers/{google_customer_id}/googleAds:search`
- Headers: `developer-token: [REDACTED_GOOGLE_DEV_TOKEN]`, `login-customer-id: 4323799990`
- Body GAQL: `SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, metrics.average_cpc, metrics.conversions FROM campaign WHERE segments.date DURING LAST_7_DAYS AND campaign.status != 'REMOVED'`
- Auth: `googleAdsOAuth2Api` credential (OAuth2)
- **IMPORTANTE:** `cost_micros / 1_000_000 = valor em BRL`

---

## 7. PROBLEMAS ENCONTRADOS E SOLUÇÕES (para referência futura)

### P1: ECONNREFUSED ao chamar webhook interno
- **Sintoma:** `connect ECONNREFUSED 127.0.1.1:443`
- **Causa:** n8n rodando em Docker chamava o domínio público que resolvia para localhost na porta 443 (HTTPS), mas internamente não tem HTTPS
- **Solução:** Usar `http://localhost:5678/webhook/...` para chamadas internas entre workflows

### P2: "No Respond to Webhook node found"
- **Sintoma:** Webhook retorna erro mesmo sendo ativado
- **Causa:** `responseMode: "responseNode"` exige um nó "Respond to Webhook", que não existia
- **Solução:** Usar `responseMode: "onReceived"` — responde 200 imediatamente e processa async

### P3: Placeholder "status" misconfigured
- **Sintoma:** `Misconfigured placeholder 'status' - defined but not used anywhere`
- **Causa:** n8n versão atual usa formato `parametersQuery.values[]` com `valueProvider`, não `queryParameters.parameters[]`. Usar `={placeholder}` é tratado como expressão JS.
- **Solução:** Usar formato `parametersQuery.values[{name: "x", valueProvider: "modelRequired"}]` para valores dinâmicos e `{name: "x", valueProvider: "fieldValue", value: "..."}` para valores fixos

### P4: "Could not get parameter" no lmChatOpenAi
- **Sintoma:** AI Agent falha com "Error in sub-node OpenAI GPT-4o-mini"
- **Causa 1:** `typeVersion: 1.2` usa `model: "gpt-4o-mini"` (string simples), mas versão atual exige `typeVersion: 1.3` com `model: {__rl: true, value: "gpt-4o", mode: "list"}`
- **Causa 2:** AI Agent com `promptType` não definido usa modo Chat Trigger por padrão
- **Solução:** Definir `typeVersion: 1.3`, formato objeto no model, e `promptType: "define"` no AI Agent

### P5: Router não identifica o número de Paulo
- **Sintoma:** Mensagens de Paulo não eram roteadas para Bruno
- **Causa:** WhatsApp Business Cloud API envia o número sem o nono dígito: `556181292879` (não `5561981292879`)
- **Solução:** Usar `556181292879` como valor de comparação no Router

### P6: Expression `={{ $json.phoneNumber }}` corrompida
- **Sintoma:** Expression aparecia como `={{ \.phoneNumber }}`
- **Causa:** Python inline `-c` com aspas simples escapava caracteres
- **Solução:** Sempre usar scripts Python em arquivo separado (nunca `-c`)

---

## 8. ARQUIVOS DESTA PASTA

```
n8n-metaAds-GoogleAds/
├── README.md                        ← Este arquivo (documentação completa)
├── workflows/
│   ├── wf01_campaign_agent.json     ← JSON original WF-01 (versão inicial antes fixes)
│   ├── wf02_meta_reports.json       ← JSON WF-02 Meta Reports
│   ├── wf02_current.json            ← JSON WF-02 versão atual
│   └── wf03_google_reports.json     ← JSON WF-03 Google Reports
└── scripts/
    ├── fix_call_agent.py            ← Fix do nó Chamar Bruno (body format)
    ├── fix_router.py                ← Fix do Router Gestor (expression)
    ├── update_wf01_bruno.py         ← Script para atualizar system prompt do Bruno
    └── update_bruno_prompt.py       ← Script final com prompt completo do Bruno (18.643 chars)
```

> **NOTA:** O estado atual e definitivo dos workflows está no n8n em produção.
> Os JSONs nesta pasta refletem versões intermediárias do desenvolvimento.
> Para obter o estado atual: `GET https://n8n.paulonunan.com/api/v1/workflows/{id}`

---

## 9. COMO INTERAGIR COM O SISTEMA (guia de uso)

Paulo envia mensagens para o WhatsApp `+55 61 8189-4189` do seu número pessoal `61981292879`.

### Comandos reconhecidos pelo Bruno:
```
listar campanhas meta
listar campanhas google 1129227354
criar campanha trafego: nome [X], orcamento R$[Y]/dia
pausar campanha [campaign_id]
ativar campanha [campaign_id]
relatorio campanha [campaign_id]
[qualquer pergunta sobre estratégia, diagnóstico, otimização]
```

### Clientes recebem automaticamente (toda segunda-feira):
- 8h00: Relatório de Meta Ads (se cadastrado com `meta_ad_account_id`)
- 8h05: Relatório de Google Ads (se cadastrado com `google_customer_id`)

### Para adicionar cliente aos relatórios:
Adicionar linha na aba `Clientes` do Google Sheet `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A`:
```
nome_cliente | whatsapp | ativo | meta_ad_account_id | google_customer_id
Empresa X    | 5511...  | TRUE  | act_123456789      | 1234567890
```

---

## 10. CONTEXTO DO NEGÓCIO

- **Empresa:** Scala — agência de automação e marketing digital
- **Localização:** Brasília/DF
- **Proprietário:** Paulo Nunan
- **Contato WhatsApp Scala:** `https://wa.me/556181894189`
- **Número de telefone registrado:** `+55 61 8189-4189`

### Personas do sistema:
- **Ana** — atendente IA da Scala, atende clientes que chegam pela página
- **Bruno** — gestor de tráfego IA, exclusivo para Paulo gerenciar campanhas

---

## 11. PRÓXIMOS PASSOS PENDENTES

- [ ] Criar aba `Clientes` no Google Sheet com os dados reais dos clientes
- [ ] Criar aba `Leads` para WF-04 (captura de leads do Meta Lead Ads)
- [ ] WF-04: Meta Lead Ads webhook → Google Sheets + notificação WhatsApp
  - Webhook URL a registrar: `https://n8n.paulonunan.com/webhook/meta-leads`
  - Registrar no Facebook Developer Console para subscription `leadgen`
- [ ] Testar relatórios WF-02 e WF-03 com dados reais de clientes
- [ ] Considerar adicionar memória de contexto ao Bruno (Google Sheets com histórico por conversa)
- [ ] Considerar migrar Bruno para Claude claude-sonnet-4-6 (melhor seguimento de prompts longos)

---

## 12. REFERÊNCIAS TÉCNICAS

### n8n API
- Base URL: `https://n8n.paulonunan.com/api/v1`
- Autenticação: Header `X-N8N-API-KEY: {API_KEY}`
- Endpoints usados:
  - `GET /workflows/{id}` — obter workflow
  - `PUT /workflows/{id}` — atualizar workflow (campos permitidos: name, nodes, connections, settings, staticData)
  - `GET /executions?workflowId={id}&limit={n}` — listar execuções
  - `GET /executions/{id}?includeData=true` — detalhe de execução com dados
  - `GET /credentials` — listar credenciais

### Meta Graph API
- Base: `https://graph.facebook.com/v19.0`
- Auth: `access_token` como query param
- Endpoints usados:
  - `GET /act_{account_id}/campaigns` — listar campanhas
  - `POST /act_{account_id}/campaigns` — criar campanha
  - `POST /{campaign_id}` — atualizar status da campanha
  - `GET /{campaign_id}/insights` — métricas

### Google Ads API
- Base: `https://googleads.googleapis.com/v19`
- Auth: OAuth2 Bearer + headers `developer-token` e `login-customer-id`
- Endpoint usado: `POST /customers/{customer_id}/googleAds:search` (GAQL)
- Conversão: `cost_micros / 1_000_000 = BRL`

### n8n toolHttpRequest — Formato Correto (versão atual)
```json
{
  "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
  "typeVersion": 1.1,
  "parameters": {
    "name": "nome_da_tool",
    "description": "Descrição para o AI",
    "method": "GET",
    "url": "https://api.exemplo.com/{placeholder_na_url}",
    "sendQuery": true,
    "parametersQuery": {
      "values": [
        {"name": "param_fixo", "valueProvider": "fieldValue", "value": "valor_fixo"},
        {"name": "param_dinamico", "valueProvider": "modelRequired"}
      ]
    },
    "placeholderDefinitions": {
      "values": [
        {"name": "placeholder_na_url", "description": "Descrição", "type": "string"},
        {"name": "param_dinamico", "description": "Descrição", "type": "string"}
      ]
    }
  }
}
```

### n8n AI Agent — Configuração Correta
```json
{
  "type": "@n8n/n8n-nodes-langchain.agent",
  "typeVersion": 1.7,
  "parameters": {
    "agent": "toolsAgent",
    "promptType": "define",
    "text": "={{ $json.messageText }}",
    "systemMessage": "... system prompt ...",
    "options": {"returnIntermediateSteps": false}
  }
}
```

### n8n lmChatOpenAi — Configuração Correta (typeVersion 1.3)
```json
{
  "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
  "typeVersion": 1.3,
  "parameters": {
    "model": {
      "__rl": true,
      "value": "gpt-4o",
      "mode": "list",
      "cachedResultName": "gpt-4o"
    },
    "options": {"temperature": 0.3}
  },
  "credentials": {
    "openAiApi": {"id": "IhMcXCpYHHMLb5Gh", "name": "OpenAi account 2"}
  }
}
```
