# Análise de Sessão — 2026-03-25

## O que foi feito

Rebuild completo da Ana (v1 → v2). Workflow anterior (`EVbZX91iB5moD6I4`, 32 nodes) foi descartado e reconstruído do zero como `S22OxWxT77a1geK8` (16 nodes), mais limpo e corrigido.

---

## Bugs Corrigidos

### 1. Google Sheets node `sheetName` — "Could not get parameter"
**Causa:** Node Google Sheets v4.x tem bug confirmado: o parâmetro `sheetName` nunca resolve via API, em nenhum modo (`url`, `id`, `name`, string literal). O workflow parava aqui e Ana não respondia nada.
**Fix:** Substituição por HTTP Request chamando a Sheets API v4 diretamente:
- `GET /spreadsheets/{id}/values/Conversas` para leitura
- `POST /spreadsheets/{id}/values/Conversas:append?valueInputOption=USER_ENTERED` para escrita

### 2. Ana repetia "Oi [Nome]" em toda mensagem
**Causa:** `Preparar Linhas` lia `$input.first().json` (que era a resposta da API WhatsApp), não o contexto da conversa. Salvava `undefined` como `conversationId` em todas as linhas → filtro de histórico nunca encontrava conversas anteriores → `isFirstMessage` sempre `true` → saudação toda vez.
**Fix:** `Preparar Linhas` agora lê `$('Preparar Resposta').first().json` explicitamente.

### 3. Prefixo legacy `scala_`
**Causa:** Histórico antigo tinha `conversationId = 'scala_556181292879'`. Novo código usa apenas `'556181292879'`.
**Fix:** Filtro aceita ambos: `.filter(r => r.json.conversationId === conversationId || r.json.conversationId === 'scala_' + conversationId)`

### 4. Meet link enviado duas vezes (duplicado)
**Causa:** `Detectar Agendamento` usava regex `/✅/i` que também batia no `✅ Gratuito e sem compromisso.` da mensagem de oferta de slots. Além disso, os próprios slots tinham o padrão `DD/MM às HH:MM` que passava no `dateMatch`. Resultado: criava evento no Calendar e mandava Meet link na mensagem de oferta, antes do lead confirmar qualquer horário.
**Fix:** Regex restrito a palavras que indicam confirmação explícita: `/marcado para|agendado para/i`

### 5. Meet link substituía a data na confirmação
**Causa:** `Montar Mensagem Final` substituía `✅[qualquer coisa]` pelo bloco de meet. Quando a confirmação era "Perfeito! ✅ Marcado para qui 26/03 às 09:00.", substituía por "Perfeito!\n\n✅ Gratuito e sem compromisso.\n🔗 link" — perdendo a data.
**Fix:** Simplificado para apenas fazer append: `aiResponse + '\n🔗 ' + meetLink`

---

## Novas Funcionalidades

### Google Calendar + Meet automático
- Quando Ana confirma agendamento com "Perfeito! ✅ Marcado para DD/MM às HH:MM."
- `Detectar Agendamento` extrai dia, mês, hora do texto via regex
- `Criar Evento Calendario` faz POST para Calendar API com `conferenceDataVersion=1`
- Evento criado em `primary` (ph.nunan@gmail.com), duração 20 min, timezone BRT
- Meet link extraído de `conferenceData.entryPoints[0].uri`
- `Montar Mensagem Final` appenda `🔗 [link]` à mensagem de confirmação
- Lead recebe: "Perfeito! ✅ Marcado para qui 26/03 às 09:00.\n🔗 https://meet.google.com/xxx"

### Delay de 3 segundos
- `Wait` node (typeVersion 1.1, `resume: timeInterval`, 3 segundos)
- Simula tempo de digitação humano antes de enviar

### Fluxo 8 passos (SPIN Selling adaptado)
Substituiu o prompt genérico anterior:
- P1: Conexão inicial (Variante A site / Variante B orgânico)
- P2: Identificação da trilha (Atendimento / Marketing / Comercial / Outra)
- P3: Reconhecimento da dor por trilha (bullets com exemplos)
- P4: Aprofundamento (2 perguntas específicas por trilha, uma por vez)
- P5: Transição e resumo personalizado da dor
- P6: Agendamento com 2 slots concretos
- P7: Confirmação + micro-compromisso ("salva meu contato como Ana | Scala")
- P8: Lembrete D-1 (pendente — requer workflow separado com cron)

### Negociação de horário
Se o lead não puder nos slots oferecidos, Ana pergunta qual dia da semana funciona e oferece slots compatíveis até confirmar.

### Desvios cobertos
Preço, resposta vaga, não-decisor, já tem solução, silêncio.

---

## Arquitetura Final (16 nodes)

```
a1  Webhook WhatsApp     — POST /whatsapp-ana, responseMode: onReceived
a2  Extrair Dados        — parse WhatsApp payload
a3  Buscar Histórico     — HTTP GET Sheets API
a4  Limitar 1 Item       — força 1 item de output
a5  Montar Contexto      — system prompt + slots dinâmicos
a6  GPT-4.1              — HTTP POST OpenAI
a7  Preparar Resposta    — extrai texto da resposta GPT
a8  Enviar WhatsApp      — WhatsApp node
a9  Preparar Linhas      — monta [userRow, aiRow] lendo de Preparar Resposta
a10 Salvar Conversa      — HTTP POST Sheets API :append
a11 Resposta Fallback    — fallback se GPT falhar
a12 Aguardar             — Wait 3s
a13 Detectar Agendamento — regex "marcado para|agendado para" + extrai datetime
a14 IF Agendamento       — $json.isBooking === true
a15 Criar Evento Calendario — HTTP POST Calendar API + conferenceData
a16 Montar Mensagem Final — append Meet link ao final
```

---

## Pendências

- **Passo 8 (Lembrete D-1):** workflow separado com cron diário que lê agendamentos do dia seguinte na planilha e dispara WhatsApp de lembrete.
- **CRM/Leads sheet:** o workflow v1 tinha um nó que salvava perfil do lead em aba "Leads". Não foi reimplementado no v2 — adicionar quando necessário.
