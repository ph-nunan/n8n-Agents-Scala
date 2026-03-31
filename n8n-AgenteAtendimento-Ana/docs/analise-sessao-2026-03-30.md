# Análise de Sessão — 2026-03-30

## O que foi feito

Ana v2 → **Ana v3**: estrutura completa e profissional para lançamento da campanha CTWA.

---

## Novas Funcionalidades

### 1. Salvar Agendamentos Estruturado (Nodes a17 + a18)

Quando um agendamento é confirmado no fluxo da Ana, dois novos nodes executam antes de enviar a mensagem ao lead:

**Node a17 — Preparar Agendamento (Code):**
- Extrai: conversationId, nome, telefone, startISO, endISO, meetLink, status="agendado", timestamp, lembrete_ts=""
- Monta a row no formato esperado pela aba "Agendamentos"

**Node a18 — Salvar Agendamento (HTTP POST):**
- Destino: `https://sheets.googleapis.com/v4/spreadsheets/1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U/values/Agendamentos:append`
- Credencial: Google Sheets - Paulo (id: UeSaLFF10d9utrmA)

**Schema da aba Agendamentos (9 colunas A–I):**
```
conversationId | nome | telefone | startISO | endISO | meetLink | status | timestamp | lembrete_ts
```

### 2. Notificar Paulo quando booking confirmado (Node a19)

**Node a19 — Notificar Paulo (WhatsApp):**
- Envia alerta para o número pessoal do Paulo imediatamente após salvar o agendamento
- Mensagem: 🔔 Novo agendamento! + nome + telefone + data/hora + Meet link
- **AÇÃO NECESSÁRIA:** Substituir `SUBSTITUA_PELO_SEU_NUMERO_PESSOAL` no campo `recipientPhoneNumber` pelo número pessoal com DDI (ex: `5561987654321`)

**Fluxo de booking após as mudanças:**
```
IF Agendamento (true)
  → Criar Evento Calendario
  → Montar Mensagem Final (agora inclui meetLink no JSON de output)
  → Preparar Agendamento
  → Salvar Agendamento (Sheets)
  → Notificar Paulo (WhatsApp)
  → Aguardar 3s
  → Enviar WhatsApp (lead recebe confirmação + Meet link)
```

### 3. WF-05 — Lembrete D-1 (ID: RJlG9D62UMddTe3N)

Workflow independente. Status: **ATIVO** ✅

**Fluxo:**
```
Cron 8h BRT (11:00 UTC)
  → Buscar Agendamentos (GET Sheets)
  → Filtrar Amanhã (Code: startISO = amanhã + lembrete_ts vazio)
  → Aguardar 2s
  → Enviar Lembrete (WhatsApp ao lead)
  → Marcar Enviado (PUT Sheets — atualiza coluna I com timestamp)
```

**Mensagem de lembrete:**
> "Oi, [nome]! 👋 Passando para lembrar que amanhã você tem o diagnóstico gratuito com o Paulo às [hora]. 😊 🔗 [meetLink] Se precisar reagendar ou tiver alguma dúvida, é só me chamar aqui! 😊"

**Lógica anti-duplicação:**
- Coluna `lembrete_ts` fica vazia quando criado
- WF-05 só processa linhas com `lembrete_ts` vazio
- Após envio: atualiza `lembrete_ts` com timestamp atual
- Mesmo se executado manualmente duas vezes, não duplica o envio

### 4. Upgrade de Modelo: GPT-4.1 → Claude Sonnet 4.6

**Mudanças no workflow:**

**Node a5 — Montar Contexto (Code):**
- Antes: retornava `{ messages: [{ role: 'system', ... }, ...history, { role: 'user', ... }] }`
- Agora: retorna `{ system: prompt, messages: [...cleanHistory, { role: 'user', ... }] }`
- Adicionada limpeza de histórico: remove roles consecutivos duplicados (Claude não aceita) e garante que começa com 'user'

**Node a6 — Renomeado para "Claude Sonnet 4.6" (HTTP Request):**
- URL: `https://api.anthropic.com/v1/messages`
- Headers: `x-api-key: {{ $env.ANTHROPIC_API_KEY }}`, `anthropic-version: 2023-06-01`
- Body: `{ model: "claude-sonnet-4-6", system: $json.system, messages: $json.messages, max_tokens: 1024, temperature: 0.75 }`

**Node a7 — Preparar Resposta (Code):**
- Adicionado parsing Claude: `gpt.content?.[0]?.text`
- Mantido fallback OpenAI: `gpt.choices?.[0]?.message?.content`

**AÇÃO NECESSÁRIA — API Key Anthropic:**
1. Acesse [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key
2. No n8n: Settings → Environment Variables → adicionar `ANTHROPIC_API_KEY=<sua_key>`
3. OU: substituir `{{ $env.ANTHROPIC_API_KEY }}` pelo valor direto no header do node "Claude Sonnet 4.6"

---

## Workflow de Setup (rodar uma vez)

**ID:** `b4HK6JkFHBivCoDp` — "SETUP — Criar Aba Agendamentos no Sheets"

**O que faz:**
1. Cria a aba "Agendamentos" no Google Sheet da Ana
2. Adiciona os headers: `conversationId | nome | telefone | startISO | endISO | meetLink | status | timestamp | lembrete_ts`

**Como rodar:**
- Abrir no n8n → clicar "Execute Workflow" → confirmar que a aba foi criada no Sheets

---

## Estado Final — Arquitetura Ana v3

```
Workflow: Ana — Agente WhatsApp v2 (ID: S22OxWxT77a1geK8)
Nodes: 19 | Status: ATIVO ✅

Fluxo principal (mensagem normal):
Webhook → Extrair Dados → Buscar Histórico → Limitar 1 Item
→ Montar Contexto → Claude Sonnet 4.6 → Preparar Resposta
→ Detectar Agendamento → IF Agendamento
  (false) → Aguardar 3s → Enviar WhatsApp → Preparar Linhas → Salvar Conversa
  (true)  → Criar Evento Calendario → Montar Mensagem Final
           → Preparar Agendamento → Salvar Agendamento → Notificar Paulo
           → Aguardar 3s → Enviar WhatsApp → Preparar Linhas → Salvar Conversa

Workflow: WF-05 — Lembrete D-1 (ID: RJlG9D62UMddTe3N)
Nodes: 6 | Status: ATIVO ✅

Cron 8h BRT → GET Agendamentos → Filtrar Amanhã
→ Aguardar 2s → Enviar Lembrete → Marcar Enviado
```

---

## Pendências (Ações do Usuário)

1. **Rodar o SETUP workflow** (ID: b4HK6JkFHBivCoDp) para criar a aba Agendamentos
2. **Preencher número pessoal** no node "Notificar Paulo" (campo recipientPhoneNumber)
3. **Configurar ANTHROPIC_API_KEY** no n8n para ativar Claude Sonnet 4.6
   - Sem a key, o workflow falhará no node "Claude Sonnet 4.6"
   - Alternativa temporária: reverter para GPT-4.1 até ter a key

---

## Arquitetura de Dados — Google Sheet Ana

**Sheet ID:** `1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U`

| Aba | Propósito | Colunas |
|-----|-----------|---------|
| Conversas | Histórico de mensagens | conversationId, role, content, pushName, timestamp |
| Agendamentos | CRM de agendamentos + D-1 tracking | conversationId, nome, telefone, startISO, endISO, meetLink, status, timestamp, lembrete_ts |
