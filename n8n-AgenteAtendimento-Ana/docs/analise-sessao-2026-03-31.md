# Análise de Sessão — 2026-03-31

## O que foi feito

Rebuild completo da Ana + correção de dois bugs críticos encontrados em produção + melhorias no prompt.

---

## Contexto

A sessão anterior (30/03) tinha construído a Ana v3 (Google Sheets). Esta sessão substituiu completamente a arquitetura por **Supabase + SPIN Selling + GPT-4o + JSON output estruturado**, resultando no workflow `mLM22h2JylSrhCRE` — "Nova Ana — Agente WhatsApp SPIN v1".

---

## O que foi construído (v1 → v1.1)

### Nova Ana SPIN v1 — Workflow `mLM22h2JylSrhCRE`

**Workflow anterior desativado:** `S22OxWxT77a1geK8`

Stack completa:
- **Modelo IA:** GPT-4o (`gpt-4o-2024-08-06`) via OpenAI API
- **Database:** Supabase — projeto `scala-ana` (ID: `euqvaadojakgplotvzvt`)
- **Tabelas:** `leads` (upsert por telefone), `conversas` (histórico 30 msgs), `agendamentos`
- **Calendar:** Google Calendar primary + Meet link automático
- **WhatsApp:** Cloud API — Phone ID `971782562694033`

Fluxo SPIN com 5 fases:
- Fase 1: Recepção / rapport — identifica negócio e origem
- Fase 2: Situação — identifica área travada (Atendimento / Marketing / Comercial / Outra)
- Fase 3: SPIN completo — 4 perguntas sequenciais por trilha + fechamento com social proof + slots
- Fase 5: Agendamento — confirma slot, cria evento no Calendar com Meet link
- Pós-booking: handler dedicado sem chamada ao GPT

Saída do modelo em JSON estruturado:
```json
{ "message": "...", "fase_nova": 3, "dados": { "negocio": "...", "trilha": "Marketing", "dor_principal": "..." } }
```

---

## Bugs corrigidos em produção

### Bug 1 — Double booking (crítico)

**Sintoma:** Lead enviou "tudo bem!" após já ter confirmado o horário. O sistema criou um **segundo evento no Google Calendar** e um segundo registro em `agendamentos`.

**Root cause:** O guard `leadJaAgendado = status === 'Agendado'` existia no node `Parsear Resposta` (na7), mas o GPT já havia sido chamado antes. O GPT, lendo o histórico com "Marcado para..." na fase 5, repetiu a confirmação exata e disparou `isBooking = true` novamente.

**Fix implementado:** Adicionado `IF Pos Agendado` (na25) **antes** do Buscar Histórico e GPT. Se `status === 'Agendado'` → rota para handler pós-booking dedicado (na26–na29) sem chamar o modelo.

### Bug 2 — na17 não persistia dados do agendamento (silencioso)

**Sintoma:** Após booking confirmado, o campo `status`, `data_agendamento` e `link_meet` da tabela `leads` permaneciam com os valores padrão (`"Em conversa"`, `null`, `null`).

**Root cause:** O node `Salvar Agendamento` (na16) usa `Prefer: return=minimal`, retornando 204 No Content = `{}`. O node seguinte `Atualizar Lead Agendado` (na17) usava `$json.phoneNumber`, `$json.startISO` e `$json.meetLink` — todos `undefined` por conta do `{}`. O PATCH resultante não acertava nenhuma linha (URL com `telefone=eq.undefined`).

**Fix implementado:** na17 agora referencia `$node['Preparar Confirmacao'].json` diretamente:
```javascript
url: "={{ 'https://.../leads?telefone=eq.' + $node['Preparar Confirmacao'].json.phoneNumber }}"
body: { status: 'Agendado', data_agendamento: $node['Preparar Confirmacao'].json.startISO, link_meet: $node['Preparar Confirmacao'].json.meetLink, fase: 5 }
```

---

## Melhorias implementadas (v1.1)

### Handler Pós-Agendamento (na26–na29)

Quando `status === 'Agendado'`, Ana responde com mensagem quente e curta sem acionar o modelo:

```
"Boa, Paulo! Tudo confirmado para 01/04 as 10:00. 😊

Link da reunião: https://meet.google.com/...

Qualquer dúvida até lá, é só chamar aqui! Até mais 👋"
```

Data e link são lidos diretamente do Supabase via `data_agendamento` e `link_meet`.

### Social Proof com Números Específicos

Substituídos os stories genéricos por versões com métricas concretas por trilha:
- **Atendimento:** clínica odontológica, 60% leads perdidos fora do horário → 8s resposta, agendamentos triplicaram em 3 semanas
- **Marketing:** agência de performance, 40% redução CPL com alertas automáticos
- **Comercial:** SaaS, 31% mais fechamento com follow-up automatizado, 48h de resposta

### Link do Portfólio no Fechamento da Fase 3

Adicionado antes dos slots de agendamento, como "prova de competência técnica" (conforme estratégia do PDF do site de autoridade):
```
"Enquanto isso, da uma olhada nos sistemas que ja montamos: https://portfolio-scala.vercel.app 👆"
```

---

## Estado Final do Workflow

| Node | Função | Status |
|------|--------|--------|
| na1–na9 | Webhook → Upsert → Histórico → Prompt → GPT → Parsear → Atualizar Lead | ✅ |
| na10–na21 | IF Booking → Calendar → WA → Supabase | ✅ Bug na17 corrigido |
| na22–na24 | Fallback GPT error | ✅ |
| **na25** | **IF Pos Agendado (NOVO)** | ✅ Guard double-booking |
| **na26–na29** | **Handler pós-booking sem IA (NOVO)** | ✅ |

**Total:** 29 nodes | **Arquivo:** `workflows/nova-ana-spin-v1.json`

---

## Decisões técnicas registradas

| Decisão | Motivo |
|---------|--------|
| Manter GPT-4o (não migrar para Claude Sonnet 4.6 ainda) | GPT-4o performou bem em produção. Migração futura quando houver critério claro (ver project_bruno_model.md) |
| Supabase ao invés de Google Sheets | Postgres real, REST API nativa, sem limites de requisições, dashboard visual |
| JSON output estruturado do modelo | Extração automática de dados do lead sem regex frágil |
| Prompt modular por fase | Elimina contexto monolítico de ~2000 tokens, cada fase recebe apenas o necessário |

---

## Próximos passos para a Ana

- [ ] Dashboard CRM — Looker Studio conectado ao Supabase para visualizar o funil
- [ ] Migrar WF-05 Lembrete D-1 de Google Sheets para Supabase
- [ ] Após 50+ conversas: avaliar troca de GPT-4o para Claude Sonnet 4.6
