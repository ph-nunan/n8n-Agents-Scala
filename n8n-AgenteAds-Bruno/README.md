# Bruno — AI Campaign Manager (WhatsApp)
## Documentação Completa

> **Atualizado:** 2026-03-19
> **Status:** PRODUÇÃO — todos os workflows ativos e funcionando
> **Workflow n8n:** `VSNwEhdZLMA2ZJyq`

---

## 1. VISÃO GERAL

Bruno é um agente de IA que permite a **Paulo** (gestor da Scala) gerenciar campanhas de Meta Ads e Google Ads inteiramente pelo WhatsApp. Ele não é um assistente genérico — age como gestor de tráfego sênior com 10 anos de experiência, pensa como sócio, e só recomenda ações após diagnosticar corretamente a situação.

### O que Bruno faz

**Estratégia e planejamento:**
- Antes de qualquer plano, conduz protocolo de qualificação (objetivo, produto, ticket, pixel, budget, audiência)
- Entrega plano de execução estruturado com 8 seções (diagnóstico, metas, campanhas, criativos, pré-requisitos, cronograma 30 dias, KPIs, próximos passos)
- Adapta estratégia ao estágio de maturidade da conta (Zero / Iniciante / Intermediário / Avançado)

**Ações executáveis via API:**
- Criar campanhas Meta Ads (sempre com status PAUSED para revisão)
- Listar campanhas Meta Ads ativas
- Pausar ou ativar campanha pelo ID
- Relatório de métricas dos últimos 7 dias (impressões, cliques, CTR, CPC, gasto)
- Listar campanhas Google Ads de qualquer conta vinculada ao MCC

**Inteligência de decisão:**
- Não executa pedidos que não vão funcionar sem antes alertar e propor alternativa
- Prioriza problemas por impacto financeiro (rastreamento > budget desperdiçado > LP > criativos > estrutura)
- Honesto sobre limitações de dados — nunca decide com menos de 3 dias ou R$100 gasto

---

## 2. ARQUITETURA

```
Paulo (WhatsApp pessoal: 61981292879)
         │
         ▼
[SCALA WORKFLOW - EVbZX91iB5moD6I4]
    Nó "Router Gestor": IF phoneNumber == "556181292879"
         │
         ▼ (SIM — é Paulo)
    Chamar Bruno: POST http://localhost:5678/webhook/campaign-agent
         │
         ▼
[WF-01 BRUNO - VSNwEhdZLMA2ZJyq]
    Webhook Trigger → Extract Message → AI Campaign Manager (GPT-4o-mini)
         │ (tools disponíveis: Meta API + Google Ads API)
         ▼
    Enviar Resposta WhatsApp → Paulo
```

> **Por que `localhost:5678`?** O n8n roda em Docker. Chamadas internas devem usar `localhost:5678` (não o domínio público) para evitar ECONNREFUSED ao tentar resolver o domínio dentro do container.

---

## 3. CONTAS DE ADS

### Meta Ads
| Campo | Valor |
|-------|-------|
| Ad Account ID | `act_1605651367382391` (Scala-Conta-Anúncios) |
| Meta App ID | `854431830954678` |
| WhatsApp Business Account ID | `1480192843700940` |
| WhatsApp Phone Number ID | `971782562694033` |
| System User | `scala-user` (ID: `61579495951643`) |
| Access Token | `[REDACTED — token permanente, System User, não expira]` |
| API Version | v19.0 |

### Google Ads
| Campo | Valor |
|-------|-------|
| MCC (Manager Account) ID | `4323799990` |
| Developer Token | `[REDACTED — ver credencial n8n ID: 2yQz1qh73JLxM3Rr]` |
| Credencial n8n | `googleAdsOAuth2Api` (ID: `2yQz1qh73JLxM3Rr`) |
| API Version | v19 |

---

## 4. CREDENCIAIS N8N

| ID | Tipo | Nome | Uso |
|----|------|------|-----|
| `umUchtUGj2ZzikQ5` | `whatsAppApi` | WhatsApp account | Envio de mensagens (todos os workflows) |
| `3Ucs5ITEFuzuPAJx` | `whatsAppTriggerApi` | WhatsApp OAuth account | Recebimento (Scala workflow) |
| `IhMcXCpYHHMLb5Gh` | `openAiApi` | OpenAi account 2 | GPT-4o-mini do Bruno (WF-01) |
| `LFnyHUsH7lj5FEvQ` | `openAiApi` | scala-agent | OpenAI da Ana (Scala) |
| `2yQz1qh73JLxM3Rr` | `googleAdsOAuth2Api` | Google Ads account | Google Ads API (WF-01 e WF-03) |
| `UeSaLFF10d9utrmA` | `googleSheetsOAuth2Api` | Google Sheets - Paulo | Sheets dos clientes (WF-02 e WF-03) |

---

## 5. WORKFLOWS

### WF-01 — Bruno, AI Campaign Manager
- **ID:** `VSNwEhdZLMA2ZJyq`
- **Status:** ATIVO
- **Trigger:** Webhook em `http://localhost:5678/webhook/campaign-agent`
- **Modelo:** GPT-4o-mini (`IhMcXCpYHHMLb5Gh`)
- **responseMode:** `onReceived` (responde 200 imediatamente, processa async)

**Nós:**
| # | Nome | Tipo | Função |
|---|------|------|--------|
| 1 | Webhook Trigger | webhook | Recebe POST `{phoneNumber, messageText}` |
| 2 | Extract Message | set | Extrai campos do body |
| 3 | AI Campaign Manager | agent (toolsAgent) | Agente principal com GPT |
| 4 | OpenAI GPT-4o-mini | lmChatOpenAi | Modelo de linguagem |
| 5 | Listar Campanhas Meta | toolHttpRequest | GET `/act_1605651367382391/campaigns` |
| 6 | Criar Campanha Meta | toolHttpRequest | POST `/act_1605651367382391/campaigns` |
| 7 | Pausar Ativar Campanha Meta | toolHttpRequest | POST `/{campaign_id}` |
| 8 | Relatório Meta Campanha | toolHttpRequest | GET `/{campaign_id}/insights` |
| 9 | Listar Campanhas Google | toolHttpRequest | POST `/{customer_id}/googleAds:search` |
| 10 | Enviar Resposta WhatsApp | whatsApp | Envia resposta para Paulo |

### WF-02 — Meta Ads Reports → WhatsApp
- **ID:** `dLr5lDWj7rtLgbGk`
- **Schedule:** Toda segunda-feira às 8h00
- **Função:** Loop em todos os clientes ativos com `meta_ad_account_id` → Relatório semanal Meta → WhatsApp

### WF-03 — Google Ads Reports → WhatsApp
- **ID:** `ndMNpUBlGhfd6CO2`
- **Schedule:** Toda segunda-feira às 8h05
- **Função:** Loop em todos os clientes ativos com `google_customer_id` → Relatório semanal Google → WhatsApp

### WF-04 — Meta Lead Ads → Google Sheets (multi-cliente)
- **ID:** `rfYBkXnh37JltJxN`
- **Webhook:** `https://n8n.paulonunan.com/webhook/meta-leads`
- **Função:** Recebe lead do Meta, roteia por `meta_page_id`, salva na planilha do cliente + notifica WhatsApp

### WF-04b — Verificação do Webhook Meta
- **ID:** `a1rk1RB4F0MRRyHK`
- **Função:** Responde ao desafio de verificação do Meta (sempre ativo)

---

## 6. SYSTEM PROMPT DO BRUNO — EVOLUÇÃO

O system prompt do Bruno passou por várias iterações. A versão atual (`2026-03-19`) é a mais completa.

### Estrutura atual do system prompt

```
<identity>           Quem é Bruno, com quem fala, contas que gerencia
<personality>        Direto, proativo, honesto, orientado a dados
<compliance_absoluto> Políticas Meta/Google — regras que nunca violam
<core_knowledge>     Frameworks: diagnóstico 7D, estágios de maturidade,
                     métricas (3 níveis), benchmarks Brasil 2026,
                     otimização, criativos, landing page
<qualification_protocol> Protocolo obrigatório antes de qualquer plano
<execution_plan_format>  Template de plano com 8 seções estruturadas
<response_format>    Formato por tipo de pedido (campanha, análise, otimização)
<decision_intelligence>  Como agir quando pedido está errado, dados insuficientes,
                         problema crítico não solicitado, priorização de problemas
<platform_knowledge_2026> Meta (3 fases, CBO vs ABO, Breakdown Effect, fatigue),
                           Google (separação obrigatória, lances por estágio,
                           Quality Score, Performance Max, Search Terms),
                           Rastreamento completo (hierarquia, CAPI, diagnóstico)
<context_about_current_account> Contexto fixo da Scala (contas, serviços, regra
                                 de clarificar conta própria vs cliente)
<capacidades_bruno>  O que Bruno pode executar via API e limitações atuais
<regras_absolutas>   13 regras inegociáveis
```

### O que mudou em cada sessão

**2026-03-18 (criação inicial):**
- System prompt base com identidade, personalidade, conhecimento técnico
- Compliance Meta/Google
- Protocolo de qualificação (12 perguntas em 3 blocos)
- Frameworks de métricas, criativos, landing page, otimização

**2026-03-19 (upgrades desta sessão):**

1. **Fix crítico — Ad Account ID incorreto**
   - Problema: nodes `Criar Campanha Meta` e `Listar Campanhas Meta` usavam `act_120244137424200671` (conta de relatórios)
   - Correto: `act_1605651367382391` (Scala-Conta-Anúncios — única conta com permissão de escrita)
   - Root cause: token do System User `scala-user` só tem acesso de escrita à conta `act_1605651367382391`
   - Fix: 3 nodes atualizados (Criar Campanha Meta, Listar Campanhas Meta, system prompt da `<identity>`)
   - **Teste:** Campanha "Campanha Teste de Tráfego" criada com sucesso (R$10/dia, objetivo Tráfego)

2. **Protocolo de qualificação — enforcement obrigatório**
   - Antes: protocolo existia mas não era enforçado (Bruno dava respostas sem qualificar)
   - Depois: regra absoluta #13 — nunca entregar plano/estratégia sem completar Blocos 1 e 2
   - Gatilhos ampliados: "plano", "estratégia", "como anunciar" também ativam o protocolo

3. **Template de Plano de Execução (8 seções)**
   - Seção `<execution_plan_format>` adicionada
   - Quando tem todas as informações, entrega: diagnóstico → metas com números → estrutura por funil (70/20/10%) → criativos necessários + hooks → pré-requisitos → cronograma semana a semana → KPIs e gatilhos → próximos passos

4. **Decision Intelligence**
   - Seção `<decision_intelligence>` adicionada (baseada no PDF de frameworks de elite)
   - Como agir quando Paulo pede algo que não vai funcionar (não executa cegamente)
   - Honestidade sobre dados insuficientes (nunca decide com < 3 dias / < R$100)
   - Alerta proativo quando identifica problema crítico não solicitado
   - Hierarquia de priorização: rastreamento > budget > LP > criativos > estrutura

5. **CBO vs ABO + Breakdown Effect**
   - Regra clara: ABO para testar, CBO para escalar
   - Nunca pausar o ad de maior gasto só por CPA alto (Breakdown Effect)

6. **Rastreamento completo**
   - Hierarquia de 5 pontos (GTM → conversão → CAPI → GA4 → micro-conversões)
   - Diagnóstico: painel vs CRM, diferença ideal < 10%
   - CAPI: recupera 15-30% conversões perdidas por iOS, essencial > R$3.000/mês
   - Quality Score Google: fatores, meta QS 7+, ação quando < 5
   - Performance Max: quando usar (50+ conv/mês, rastreamento sólido) e quando não usar

7. **Context about current account**
   - Seção `<context_about_current_account>` com dados fixos da Scala
   - Regra: sempre clarificar se pergunta é sobre conta própria (`act_1605651367382391`) ou cliente

---

## 7. ROTEAMENTO WHATSAPP

- **Número Scala:** `+55 61 8189-4189` (Phone Number ID: `971782562694033`)
- **Número Paulo:** `61981292879` → no Cloud API vira `556181292879` (sem o nono dígito)

```
Mensagem recebida no Scala Workflow
  → "Router Gestor": IF $json.phoneNumber == "556181292879"
      SIM → Chamar Bruno: POST http://localhost:5678/webhook/campaign-agent
             Body: { phoneNumber, messageText }
      NÃO → Fluxo da Ana (atendimento de clientes)
```

---

## 8. GOOGLE SHEETS — PLANILHA MESTRE DE CLIENTES

- **Sheet ID:** `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A`
- **Aba:** `Clientes`

| Coluna | Descrição | Obrigatório para |
|--------|-----------|-----------------|
| `nome_cliente` | Nome para personalizar mensagem | Todos |
| `whatsapp` | Número com DDI (ex: `5511987654321`) | Todos |
| `ativo` | `TRUE`/`FALSE` — liga/desliga todos os serviços | Todos |
| `meta_ad_account_id` | Ex: `act_120244137424200671` | WF-02 (Meta Reports) |
| `meta_access_token` | Token do cliente (não o token da Scala) | WF-02 (Meta Reports) |
| `google_customer_id` | 10 dígitos sem hífens | WF-03 (Google Reports) |
| `leads_sheet_id` | ID da planilha de leads do cliente | WF-04 (Meta Leads) |
| `meta_page_id` | ID numérico da página Facebook do cliente | WF-04 (Meta Leads) |
| `plano` | `reports_meta` / `reports_google` / `leads` / `full` | Controle |
| `data_inicio` | Data de início do serviço | Controle |
| `observacoes` | Notas internas | Controle |

---

## 9. PROBLEMAS E SOLUÇÕES (para referência futura)

### P1: HTTP 500 OAuthException code 1 ao criar campanha
- **Sintoma:** `POST /act_.../campaigns` retorna `{"error": {"message": "An unknown error has occurred.", "type": "OAuthException", "code": 1}}`
- **Causa:** Ad Account ID errado. O token do System User `scala-user` só tem permissão de escrita em `act_1605651367382391`, não em `act_120244137424200671`
- **Diagnóstico:** Testar token com `GET /debug_token` e conta com `GET /act_ID?fields=account_status`
- **Solução:** Usar `act_1605651367382391` em todos os nodes do WF-01

### P2: ECONNREFUSED ao chamar webhook interno
- **Sintoma:** `connect ECONNREFUSED 127.0.1.1:443`
- **Causa:** n8n em Docker chamava domínio público que resolvia para localhost na porta 443 (HTTPS)
- **Solução:** Usar `http://localhost:5678/webhook/...` para chamadas internas

### P3: "No Respond to Webhook node found"
- **Causa:** `responseMode: "responseNode"` exige nó "Respond to Webhook"
- **Solução:** Usar `responseMode: "onReceived"`

### P4: "Could not get parameter" no lmChatOpenAi
- **Causa:** `typeVersion: 1.2` usa model como string; versão atual exige `typeVersion: 1.3` com model como objeto
- **Solução:** `typeVersion: 1.3`, `model: {__rl: true, value: "gpt-4o-mini", mode: "list"}`

### P5: Router não identifica Paulo
- **Causa:** Cloud API envia `556181292879` (sem nono dígito), não `5561981292879`
- **Solução:** Comparar com `556181292879`

### P6: `$json.phoneNumber` undefined após nós intermediários
- **Causa:** Após passar por nós de Google Sheets ou IFs, `$json` perde os dados originais
- **Solução:** Referenciar sempre `$('Extrair Dados').first().json.phoneNumber` em vez de `$json.phoneNumber`

### P7: Bruno não seguia protocolo de qualificação
- **Causa:** Protocolo existia mas sem enforcement — Bruno respondia sem qualificar
- **Solução:** Regra absoluta #13 adicionada + gatilhos ampliados para incluir "plano", "estratégia", etc.

### P8: Placeholder misconfigured nos tool nodes
- **Causa:** `={placeholder}` é tratado como expressão JS pelo n8n
- **Solução:** Usar `{placeholder}` sem `=`, e formato `parametersQuery.values[{name, valueProvider}]`

---

## 10. MODELO E PARÂMETROS

| Parâmetro | Valor atual | Recomendado (PDF) |
|-----------|-------------|-------------------|
| Modelo | GPT-4o-mini | Claude Sonnet (melhor seguimento de prompts longos) |
| Temperature | 0.3 | 0.3 |
| Max tokens | 2048 | 2048 |

> **Decisão (2026-03-19):** Manter GPT-4o-mini por enquanto. Se Bruno começar a ignorar partes do protocolo ou dar respostas inconsistentes com o framework, o upgrade de modelo é o primeiro passo (trocar para GPT-4o ou Claude Sonnet no nó LLM do WF-01).

---

## 11. COMO USAR O BRUNO

Paulo envia mensagens do número `61981292879` para o WhatsApp `+55 61 8189-4189`.

### Exemplos de uso

**Pedir um plano:**
> "Bruno, quero criar campanhas para gerar leads no meu site"
→ Bruno vai perguntar: objetivo, produto, ticket, pixel, budget, audiência → depois entrega plano completo

**Ações diretas:**
```
listar campanhas meta
criar campanha trafego: nome [X], orcamento R$[Y]/dia
pausar campanha [campaign_id]
ativar campanha [campaign_id]
relatorio campanha [campaign_id]
listar campanhas google [customer_id]
```

**Análise:**
> "Minha campanha está com CPA de R$120 mas meu target é R$50"
→ Bruno diagnostica o gargalo (anúncio, LP ou audiência) antes de recomendar ação

---

## 12. ARQUIVOS DESTA PASTA

```
n8n-AgenteAds-Bruno/
├── README.md                         ← Este arquivo
├── workflows/
│   ├── bruno-ads-manager.json        ← JSON atual do WF-01 (sincronizado com n8n)
│   ├── wf01_campaign_agent.json      ← Versão inicial do WF-01 (histórico)
│   ├── wf02_meta_reports.json        ← JSON WF-02 Meta Reports
│   ├── wf02_current.json             ← JSON WF-02 versão intermediária
│   └── wf03_google_reports.json      ← JSON WF-03 Google Reports
└── scripts/
    ├── fix_call_agent.py             ← Fix do nó Chamar Bruno (body format)
    ├── fix_router.py                 ← Fix do Router Gestor (expression)
    ├── update_wf01_bruno.py          ← Atualizações via n8n API
    └── update_bruno_prompt.py        ← Script com prompt completo (histórico)
```

> **NOTA:** `bruno-ads-manager.json` é o estado atual em produção.
> Para obter sempre a versão mais recente: `GET https://n8n.paulonunan.com/api/v1/workflows/VSNwEhdZLMA2ZJyq`

---

## 13. REFERÊNCIAS TÉCNICAS

### n8n toolHttpRequest — Formato Correto
```json
{
  "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
  "typeVersion": 1.1,
  "parameters": {
    "name": "nome_da_tool",
    "description": "Descrição para o AI",
    "method": "POST",
    "url": "https://api.exemplo.com/{placeholder}",
    "sendQuery": true,
    "parametersQuery": {
      "values": [
        {"name": "param_fixo", "valueProvider": "fieldValue", "value": "valor"},
        {"name": "param_dinamico", "valueProvider": "modelRequired"}
      ]
    },
    "placeholderDefinitions": {
      "values": [
        {"name": "placeholder", "description": "Descrição", "type": "string"}
      ]
    }
  }
}
```

### Meta Graph API — Endpoints usados
- Base: `https://graph.facebook.com/v19.0`
- `GET /act_1605651367382391/campaigns` — listar campanhas
- `POST /act_1605651367382391/campaigns` — criar campanha (parâmetros: `name`, `objective`, `daily_budget`, `status=PAUSED`, `special_ad_categories=[]`)
- `POST /{campaign_id}` — atualizar status (`status=PAUSED` ou `status=ACTIVE`)
- `GET /{campaign_id}/insights?date_preset=last_7d` — métricas

### Google Ads API — Endpoint usado
- Base: `https://googleads.googleapis.com/v19`
- `POST /customers/{customer_id}/googleAds:search`
- Headers: `developer-token`, `login-customer-id: 4323799990`
- GAQL: `SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, metrics.average_cpc, metrics.conversions FROM campaign WHERE segments.date DURING LAST_7_DAYS AND campaign.status != 'REMOVED'`
- Conversão: `cost_micros / 1_000_000 = BRL`
