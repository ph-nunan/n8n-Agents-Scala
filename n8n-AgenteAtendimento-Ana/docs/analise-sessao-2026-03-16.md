# Análise Completa — Agente IA Scala (Ana) 24/7
**Data:** 16 de março de 2026
**Autor:** Paulo Nunan + Claude (Anthropic)
**Repositório:** https://github.com/ph-nunan/scala-whatsapp-agent

---

## 1. O QUE FOI CONSTRUÍDO

Um agente de atendimento 100% autônomo via WhatsApp para a Scala, capaz de:

- Atender leads 24 horas por dia, 7 dias por semana
- Qualificar leads usando metodologia SPIN Selling
- Verificar disponibilidade real no Google Agenda
- Agendar diagnósticos gratuitos (Google Meet com link automático)
- Salvar histórico de conversas no Google Sheets
- Bloquear sobreposição de reuniões automaticamente

---

## 2. STACK COMPLETA

| Componente | Tecnologia | Função |
|---|---|---|
| Orquestração | n8n (self-hosted) | Fluxo principal do agente |
| Canal | WhatsApp Business Cloud API (Meta oficial) | Receber e enviar mensagens |
| IA | OpenAI GPT-4o-mini | Geração de respostas + extração CRM |
| Memória | Google Sheets (aba Conversas) | Histórico de conversas |
| CRM | Google Sheets (aba Leads) | Perfis estruturados dos leads |
| Agenda | Google Calendar API (freeBusy + Events) | Verificar disponibilidade e criar eventos |
| Reunião | Google Meet (automático via Calendar) | Link gerado automaticamente |
| Persona | Ana — consultora da Scala | Identidade do agente |

---

## 3. ARQUITETURA DO WORKFLOW (20 nodes)

```
FLUXO PRINCIPAL (mensagem recebida):
┌─────────────────────────────────────────────────────────────────────┐
│ 1. WhatsApp Trigger                                                  │
│    ↓                                                                  │
│ 2. Extrair Dados (Code)                                              │
│    ↓                                                                  │
│ 3. Buscar Histórico (Google Sheets — aba Conversas, leitura)         │
│    ↓                                                                  │
│ 4. Buscar Disponibilidade (HTTP → Google Calendar freeBusy API)      │
│    ↓                                                                  │
│ 5. Formatar Slots (Code — injeta períodos OCUPADOS, lista livres)    │
│    ↓                                                                  │
│ 6. Montar Contexto (Code — prompt com histórico + ocupados)          │
│    ↓                                                                  │
│ 7. OpenAI GPT-4o-mini (HTTP Request)                                 │
│    ↓                                                                  │
│ 8. Delay Humano (5s — simula digitação)                              │
│    ↓                                                                  │
│ 9. Preparar Resposta (Code — extrai aiResponse)                      │
│    ↓                                                                  │
│ 10. Salvar Mensagem User (Google Sheets — append Conversas)          │
│    ↓                                                                  │
│ 11. Salvar Resposta Assistente (Google Sheets — append Conversas)    │
│    ↓                                                                  │
│ 12. Enviar Resposta WhatsApp                                         │
└─────────────────────────────────────────────────────────────────────┘

FLUXO DE AGENDAMENTO (bifurcação após envio):
┌─────────────────────────────────────────────────────────────────────┐
│ 13. Detectar Agendamento (IF — regex: "link.*agora/instantes/já")   │
│     │                                                                 │
│     ├── TRUE: agendamento detectado                                  │
│     │    ↓                                                            │
│     │ 14. Extrair Info Agendamento (Code — extrai data/hora)         │
│     │    ↓                                                            │
│     │ 15. Criar Evento Calendar (HTTP → Google Calendar API + Meet)  │
│     │    ↓                                                            │
│     │ 16. Enviar Link Meet (WhatsApp — 2ª mensagem com link)         │
│     │                                                                 │
│     └── FALSE: sem agendamento, workflow encerra                     │
└─────────────────────────────────────────────────────────────────────┘

FLUXO CRM (bifurcação paralela após salvar resposta, sempre executa):
┌─────────────────────────────────────────────────────────────────────┐
│ 17. CRM Extrair Lead (HTTP → GPT — extrai dados estruturados)       │
│    ↓                                                                  │
│ 18. CRM Formatar Lead (Code — formata datas, estrutura o objeto)    │
│    ↓                                                                  │
│ 19. CRM Validar Lead (IF — verifica se nome e negócio foram         │
│     identificados)                                                   │
│     │                                                                 │
│     ├── TRUE: dados suficientes para salvar                          │
│     │    ↓                                                            │
│     │ 20. CRM Salvar Lead (Google Sheets — appendOrUpdate aba Leads  │
│     │     com telefone como chave primária)                          │
│     │                                                                 │
│     └── FALSE: dados insuficientes, encerra CRM branch              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. IDs E CONFIGURAÇÕES DE PRODUÇÃO

| Campo | Valor |
|---|---|
| **Workflow ID** | `EVbZX91iB5moD6I4` |
| **Status** | ✅ ATIVO |
| **Webhook URL** | `https://n8n.paulonunan.com/webhook/a4d4b2c4-2099-4eb6-980d-df5274d1c1fc/webhook` |
| **Meta App ID** | `854431830954678` |
| **Phone Number ID** | `971782562694033` |
| **Número WhatsApp** | +55 61 8189-4189 |
| **WABA ID** | `1480192843700940` |
| **PIN do número** | `869531` |
| **Google Sheet ID (Conversas)** | `1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U` |
| **Google Sheet Leads** | Planilha "Scala Leads" — aba `Leads` |
| **Link WhatsApp** | https://wa.me/556181894189 |

---

## 5. CREDENCIAIS NO N8N

| Credencial | Tipo | ID | Usada em |
|---|---|---|---|
| WhatsApp OAuth account | whatsAppTriggerApi | `3Ucs5ITEFuzuPAJx` | Node 1 (Trigger) |
| WhatsApp account | whatsAppApi | `umUchtUGj2ZzikQ5` | Nodes 12, 16 (Enviar) |
| scala-agent | openAiApi | `LFnyHUsH7lj5FEvQ` | Node 7 (OpenAI) |
| Google Sheets - Paulo | googleSheetsOAuth2Api | `UeSaLFF10d9utrmA` | Nodes 3, 10, 11, 20 (CRM) |
| Google Calendar - Paulo | googleCalendarOAuth2Api | `QGp1FxkKTfYhYYJ0` | Nodes 4, 15 |

---

## 6. ERROS ENCONTRADOS E SOLUÇÕES

### Erro 1 — OTP não chegava no número
**Problema:** Meta armazenou o número como +55 61 8189-4189 (sem o 9). A API retornava erro de formato.
**Solução:** Registrar o número diretamente pela interface de developers.facebook.com, sem usar a API programaticamente.

---

### Erro 2 — Extrair Dados retornava 0 itens
**Problema:** O código esperava `entry[0].changes[0].value.messages`, mas o n8n WhatsApp Trigger já faz o parse dos dados e entrega em `payload.messages`.
**Solução:** Mudar para `$input.first().json.messages` (sem a cadeia de entry/changes).

---

### Erro 3 — Buscar Histórico parava o fluxo quando a planilha estava vazia
**Problema:** Google Sheets node retornava 0 items quando não havia histórico, interrompendo o workflow.
**Solução:** Adicionar `alwaysOutputData: true` no **nível do node** (não em `parameters.options`, que é o erro mais comum).

```json
// ERRADO — não funciona:
"parameters": { "options": { "alwaysOutputData": true } }

// CORRETO — funciona:
{ "alwaysOutputData": true }  // propriedade no nível do node
```

---

### Erro 4 — "Unable to sign without access token" no Salvar Mensagem User
**Problema:** Node estava usando credencial quebrada (`Hc1bnuxOvDFDiG3C`).
**Solução:** Trocar para `UeSaLFF10d9utrmA` (Google Sheets - Paulo).

---

### Erro 5 — Enviar WhatsApp: "Cannot read properties of undefined (reading 'replace')"
**Problema:** Após corrigir o Salvar Mensagem User, o node de envio não encontrava `aiResponse`/`phoneNumber` pois o mapping de dados foi alterado.
**Solução:** Usar referência explícita: `$('Preparar Resposta').first().json.phoneNumber` em vez de `$json.phoneNumber`.

---

### Erro 6 — Ana ativava "ligações" quando lead pedia reunião
**Problema:** A instrução `<ligacoes>` era ativada para qualquer pedido de "reunião" ou "marcar horário".
**Solução:** Restringir para palavras explícitas: "quero ligar", "pode me ligar", "me passa o telefone". Adicionar exclusão: "NUNCA use quando lead pedir reunião ou agendamento."

---

### Erro 7 — Ana repetia pergunta de horário após lead confirmar
**Problema:** Instrução de agendamento não era clara sobre confirmar imediatamente.
**Solução:** Adicionar: "NUNCA repita a pergunta de horário se o lead já deu um horário. NUNCA diga que vai verificar disponibilidade."

---

### Erro 8 — Webhook Meta retornando erro 2200 (404) na verificação
**Problema:** Workflow estava inativo quando Meta tentou verificar o webhook.
**Solução:** Ativar o workflow ANTES de registrar o webhook no Meta.

---

### Erro 9 — Meta rejeitando campo `phoneNumberId` na credencial WhatsApp
**Problema:** A API do n8n não aceita `phoneNumberId` como campo de credencial.
**Solução:** A credencial WhatsApp só precisa de `accessToken` + `businessAccountId`. O Phone Number ID vai no **parâmetro do node**, não na credencial.

---

### Erro 10 — OAuth Google retornando 403 access_denied
**Problema:** App OAuth em modo "Teste" mas o e-mail do usuário não estava na lista de testadores.
**Solução:** Google Cloud Console → APIs e serviços → Tela de permissão OAuth → Usuários de teste → Adicionar `ph.nunan@gmail.com`.

---

### Erro 11 — Ana em loop infinito de horários ("esse horário está ocupado")
**Problema (parte 1):** Slots gerados só iam até 19:30. Às 20:38, todos os slots do dia tinham expirado. Usuário propunha 21h, que não estava na lista → Ana dizia "ocupado".
**Problema (parte 2):** Lógica de injetar lista de slots livres era ruim: qualquer horário "fora da lista" era recusado, criando loop.
**Solução:** Inverter a lógica — injetar **os períodos ocupados** (lista curta) e instruir Ana a confirmar qualquer horário que NÃO conflite. Estender slots até 22h.

```
LÓGICA ERRADA:  injeta lista de slots LIVRES → "horário fora da lista = ocupado" → loop
LÓGICA CORRETA: injeta lista de slots OCUPADOS → "confirme qualquer horário sem conflito"
```

---

### Erro 12 — `Module 'luxon' is disallowed` nos Code nodes
**Problema:** Esta versão do n8n usa um task runner separado que bloqueia `require('luxon')` e outras libs externas.
**Solução:** Reescrever todos os Code nodes usando apenas `Date` nativo do JavaScript.

```javascript
// ERRADO — luxon bloqueado:
const { DateTime } = require('luxon');

// CORRETO — Date nativo:
const BRT_MS = 3 * 3600 * 1000; // Brasília = UTC-3
const brNow = new Date(new Date().getTime() - BRT_MS);
```

---

### Erro 13 — CRM Salvar Lead retornava "Unknown error"
**Problema:** Node Google Sheets configurado com operação `update` + `upsertData: true`. Falha silenciosa quando a aba está vazia (nenhuma linha para fazer update).
**Solução:** Trocar para operação `appendOrUpdate` com a coluna `telefone` como chave de match. Esta operação faz insert se não encontrar a linha, ou update se encontrar — comportamento correto para CRM.

```
ERRADO:  operation: "update" + upsertData: true → falha em aba vazia
CORRETO: operation: "appendOrUpdate" + matchingColumns: ["telefone"]
```

---

### Erro 14 — Datas no CRM em formato ISO (2026-03-16T22:52:30.886Z)
**Problema:** CRM Formatar Lead retornava timestamps ISO direto do `new Date().toISOString()`. Google Sheets exibia formato UTC sem conversão de fuso.
**Solução:** Criar função `formatBR()` que converte ISO para `dd/MM/yyyy HH:mm` no fuso Brasília (UTC-3).

```javascript
const BRT_MS = 3 * 3600 * 1000;
const pad = n => String(n).padStart(2, '0');
const formatBR = (isoStr) => {
  const br = new Date(new Date(isoStr).getTime() - BRT_MS);
  return pad(br.getUTCDate()) + '/' + pad(br.getUTCMonth()+1) + '/'
    + br.getUTCFullYear() + ' ' + pad(br.getUTCHours()) + ':' + pad(br.getUTCMinutes());
};
// Saída: "16/03/2026 19:52"
```

---

## 7. APRENDIZADOS TÉCNICOS

### 7.1 n8n — Comportamentos não óbvios

| Situação | Comportamento |
|---|---|
| WhatsApp Trigger | Já entrega dados parseados em `$input.first().json` (sem `entry.changes.value`) |
| `alwaysOutputData` | Deve ser propriedade do node, NÃO de `parameters.options` |
| Code nodes nesta versão | `require('luxon')` é bloqueado pelo task runner. Usar Date nativo |
| Credencial WhatsApp | Só aceita `accessToken` + `businessAccountId`. Phone Number ID vai no node |
| `n8n_update_partial_workflow` | `addConnection` é flat (sem wrapper `connection: {}`). IF usa `branch: "true"/"false"` |
| `updateNode` | Usa chave `updates` com dot notation, não `changes` |
| Google Sheets upsert | Usar `appendOrUpdate` com `matchingColumns`. Não usar `update + upsertData:true` (falha em aba vazia) |

### 7.2 Meta / WhatsApp Business API

| Situação | Solução |
|---|---|
| OTP não chega | Verificar formatação exata do número. Usar interface web se API falhar |
| Número não no WhatsApp | Chamar `POST /v21.0/{phoneNumberId}/register` com `{"messaging_product":"whatsapp","pin":"123456"}` |
| Webhook verificação falha (2200) | Workflow deve estar ATIVO antes de registrar webhook |
| Token de System User | Gerar via Meta Business Suite → Usuários do sistema → Token permanente (sem expiração) |
| Atualizar foto de perfil do WhatsApp Business | Ver seção 7.5 abaixo — fluxo de 3 etapas com Resumable Upload API |

### 7.5 Atualizar foto de perfil WhatsApp Business (Resumable Upload API)

**Fluxo correto (3 etapas via Node.js):**

```
Etapa 1: Criar sessão de upload
POST https://graph.facebook.com/v21.0/app/uploads
  ?file_name=logo.png&file_length={bytes}&file_type=image%2Fpng&access_token={TOKEN}
→ Retorna: { "id": "upload:MTp..." }

Etapa 2: Upload do arquivo
POST https://graph.facebook.com/v21.0/{session-id-completo-com-sig}
  Headers: Authorization: OAuth {TOKEN}, file_offset: 0, Content-Type: image/png
  Body: binário do arquivo
→ Retorna: { "h": "4:...handle1...\n4:...handle2...\n..." }

Etapa 3: Atualizar perfil
POST https://graph.facebook.com/v21.0/{phone-number-id}/whatsapp_business_profile
  Body: { "messaging_product": "whatsapp", "profile_picture_handle": "{h completo}" }
→ Retorna: { "success": true }
```

**Erros comuns e soluções:**

| Erro | Causa | Solução |
|---|---|---|
| `InvalidEndpointError` no upload | Tentativa de usar `rupload.facebook.com` | Usar `graph.facebook.com/v21.0/{session-id}` |
| `Invalid file handle provided` | Passando apenas o 1º handle (split por `\n`) | Passar o campo `h` COMPLETO (todos os handles separados por `\n`) |
| `Cannot parse access token` em Node.js | Variável de ambiente não exportada para o script | Usar `export TOKEN=...` antes do heredoc ou `process.env.TOKEN` |

**Exemplo funcional em Node.js:**

```javascript
const https = require('https');
const fs = require('fs');
const TOKEN = process.env.TOKEN;
const PHONE_ID = '971782562694033';

const file = fs.readFileSync('/caminho/logo.png');
const fileSize = file.length;

async function main() {
  // 1. Criar sessão
  const session = await post(`/v21.0/app/uploads?file_name=logo.png&file_length=${fileSize}&file_type=image%2Fpng&access_token=${TOKEN}`);

  // 2. Upload
  const upload = await postBinary(`/v21.0/${session.id}`, file, fileSize, TOKEN);

  // 3. Atualizar perfil — PASSAR handle COMPLETO (não split!)
  const result = await postJSON(`/v21.0/${PHONE_ID}/whatsapp_business_profile`, {
    messaging_product: 'whatsapp',
    profile_picture_handle: upload.h   // <- campo h inteiro, com todas as linhas
  }, TOKEN);

  console.log(result); // { success: true }
}
```

### 7.3 CRM com GPT + Google Sheets

| Situação | Solução |
|---|---|
| Extrair dados estruturados do histórico | Chamar GPT separado com `response_format: { type: 'json_object' }` e histórico resumido |
| Upsert confiável no Sheets | Usar `appendOrUpdate` com `matchingColumns: ["telefone"]` — funciona em aba vazia ou populada |
| Formatar datas para o Brasil | `new Date(new Date(iso).getTime() - 3*3600*1000)` → ler campos UTC como horário de Brasília |
| Quando atualizar o CRM | A cada mensagem recebida, sem esperar o agendamento — perfil vai sendo enriquecido progressivamente |

---

### 7.4 Google Calendar API

| Situação | Solução |
|---|---|
| Criar evento com Google Meet | Adicionar `conferenceDataVersion=1` na URL + `conferenceData.createRequest` no body |
| Google Calendar OAuth 403 | Adicionar e-mail em "Usuários de teste" no Google Cloud Console |
| freeBusy para verificar disponibilidade | `POST /v3/freeBusy` retorna períodos ocupados — mais simples que listar eventos |
| Timezone | Sempre passar `"timeZone": "America/Sao_Paulo"` no body do evento |

---

## 8. COMO REPLICAR DO ZERO

### Pré-requisitos
- n8n self-hosted (ou n8n Cloud)
- Conta Meta Business com app configurado
- Conta Google com acesso ao Google Cloud Console
- Número de telefone físico (SIM card) para WhatsApp Business

---

### Passo 1 — Meta (WhatsApp Business Cloud API)

1. Acesse **developers.facebook.com** → Meus apps → Criar app → Negócios
2. Adicione o produto **WhatsApp**
3. No painel WhatsApp:
   - Anote o **Phone Number ID** e o **WhatsApp Business Account ID**
4. Crie um **Usuário do sistema** em Meta Business Suite:
   - Configurações → Usuários do sistema → Adicionar
   - Permissões: `whatsapp_business_messaging`, `whatsapp_business_management`, `business_management`
   - Gere um **token permanente** (sem expiração)
5. Configure o número de telefone:
   - Adicione o número e verifique via OTP (SMS ou ligação)
   - Anote o PIN gerado
6. Registre o número via API:
```bash
curl -X POST "https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/register" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{"messaging_product":"whatsapp","pin":"{SEU_PIN}"}'
```

---

### Passo 2 — Google Cloud Console

1. Acesse **console.cloud.google.com**
2. Crie um projeto (ex: `n8n-agente`)
3. Ative as APIs:
   - **Google Sheets API**
   - **Google Calendar API**
4. Crie tela de consentimento OAuth:
   - Tipo: Externo
   - Adicione seu e-mail em **Usuários de teste**
5. Crie credencial **OAuth 2.0 para Aplicativo da Web**:
   - URI de redirecionamento: `https://SEU_N8N.com/rest/oauth2-credential/callback`
   - Anote o **Client ID** e **Client Secret**
6. Crie a planilha Google Sheets (ex: "Scala Leads") com **duas abas**:
   - Aba `Conversas`: `conversationId | role | content | pushName | timestamp`
   - Aba `Leads`: `telefone | nome | negocio | dor | classificacao | status | volume_leads | investimento_trafego | data_primeiro_contato | ultima_atualizacao`

---

### Passo 3 — n8n: Credenciais

Crie as seguintes credenciais em **Credentials**:

| Nome sugerido | Tipo | Dados necessários |
|---|---|---|
| WhatsApp Trigger | WhatsApp Trigger API | App Secret + Access Token |
| WhatsApp Sender | WhatsApp API | Access Token + WABA ID |
| OpenAI | OpenAI API | API Key |
| Google Sheets | Google Sheets OAuth2 | Client ID + Client Secret → autorizar |
| Google Calendar | Google Calendar OAuth2 | Client ID + Client Secret → autorizar |

---

### Passo 4 — n8n: Importar Workflow

1. Abra o n8n → Workflows → Import
2. Faça upload do arquivo `workflows/scala-whatsapp-ai-agent.json`
3. Substitua os IDs nos nodes:
   - **Google Sheets Conversas** (Buscar Histórico, Salvar User, Salvar Assistente): trocar Sheet ID + nome da aba
   - **Google Sheets CRM** (CRM Salvar Lead): trocar Sheet ID + nome da aba `Leads`
   - **Enviar WhatsApp** (nodes 12 e 16): trocar `phoneNumberId`
   - **Montar Contexto**: revisar system prompt com dados da empresa
4. Associe as credenciais criadas no Passo 3
5. **Ative** o workflow

---

### Passo 5 — Meta: Registrar Webhook

Com o workflow **ativo**:

1. No painel WhatsApp → Configuração → Webhooks
2. URL: `https://SEU_N8N.com/webhook/{WEBHOOK_ID}/webhook`
3. Token de verificação: qualquer string (ex: `meu-webhook-2026`)
4. Inscreva nos eventos: `messages`
5. Assine a WABA:
```bash
curl -X POST "https://graph.facebook.com/v21.0/{WABA_ID}/subscribed_apps" \
  -H "Authorization: Bearer {TOKEN}"
```

---

### Passo 6 — Teste Final

1. Envie uma mensagem para o número WhatsApp configurado
2. Verifique no n8n → Executions se o workflow rodou
3. Confirme que a resposta chegou no WhatsApp
4. Teste o fluxo de agendamento completo:
   - Peça um diagnóstico
   - Confirme um horário
   - Verifique se o link do Meet chegou
   - Verifique se o evento apareceu no Google Agenda
5. Verifique o CRM:
   - Após algumas mensagens, abra a aba `Leads` da planilha
   - Confirme que nome, negócio, dor e classificação foram extraídos
   - Envie uma segunda mensagem e confirme que o registro é atualizado (não duplicado)

---

## 9. ESTRUTURA DE ARQUIVOS

```
agenteIA-scala/
├── README.md                              # Overview e IDs de produção
├── docs/
│   ├── guia-configuracao.md               # Passo a passo detalhado de setup
│   ├── system-prompt.md                   # System prompt editável da Ana
│   └── analise-sessao-2026-03-16.md       # Este documento
└── workflows/
    └── scala-whatsapp-ai-agent.json       # JSON completo do workflow n8n
```

---

## 10. PONTOS DE MELHORIA FUTUROS

| Melhoria | Impacto | Complexidade |
|---|---|---|
| Notificação para Paulo quando reunião for agendada | Alto | Baixa |
| Enviar email de confirmação para o lead | Médio | Baixa |
| Limpar histórico antigo do Google Sheets automaticamente | Médio | Baixa |
| Dashboard de métricas (leads atendidos, taxa de agendamento) | Alto | Média |
| Suporte a mensagens de áudio (transcrição via Whisper) | Médio | Média |
| Follow-up automático 1h antes da reunião | Alto | Média |
| Detecção de intenção mais robusta via GPT para agendamento | Alto | Média |
| Rate limiting para evitar spam | Baixo | Baixa |

---

## 11. RESULTADO FINAL

O agente está **100% funcional e em produção** com três camadas:

**Atendimento:**
- ✅ Atendimento 24/7 via WhatsApp
- ✅ Contexto e memória de conversas (Google Sheets, últimas 20 mensagens)
- ✅ Delay de 5s simulando digitação humana

**Qualificação:**
- ✅ Metodologia SPIN Selling embutida no system prompt
- ✅ Classificação automática A/B/C/D por perfil de negócio
- ✅ Verificação real de disponibilidade (Google Calendar freeBusy)
- ✅ Agendamento automático com Google Meet
- ✅ Proteção contra sobreposição de reuniões
- ✅ Reuniões de 30 minutos, link enviado automaticamente via WhatsApp

**CRM:**
- ✅ Extração estruturada de dados do lead por GPT após cada mensagem
- ✅ Upsert na aba Leads com telefone como chave primária
- ✅ Campos: nome, negócio, dor principal, classificação, status, volume de leads, investimento em tráfego
- ✅ Datas em formato brasileiro (dd/MM/yyyy HH:mm, timezone Brasília)

**Custo estimado de operação:**
- n8n: infraestrutura existente
- OpenAI GPT-4o-mini: ~$0.00054 por mensagem trocada (~$0.007 por conversa completa de 10-15 msgs)
- WhatsApp Business: gratuito até 1.000 conversas iniciadas pelo negócio/mês
- Google APIs: gratuito dentro dos limites de uso

---

*Documento gerado em 16/03/2026 — Sessão de implementação Paulo Nunan + Claude Sonnet 4.6*
