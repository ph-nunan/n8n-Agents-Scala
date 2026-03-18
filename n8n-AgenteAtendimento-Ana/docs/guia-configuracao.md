# Guia de Configuração — Scala WhatsApp AI Agent

**Workflow n8n:** `EVbZX91iB5moD6I4`
**Modelo de IA:** GPT-4o-mini (OpenAI)
**Canal:** WhatsApp Business Cloud API (Meta oficial)
**Memória:** Google Sheets

---

## Pré-requisitos

- Conta Meta Business verificada
- Número de telefone que **não** está em uso no WhatsApp pessoal
- Conta OpenAI com créditos
- Google Sheets (conta Google)

---

## PASSO 1 — Criar Conta de Desenvolvedor Meta

1. Acesse [developers.facebook.com](https://developers.facebook.com) e faça login
2. Clique em **"My Apps" → "Create App"**
3. Tipo: **"Business"**
4. Preencha:
   - App Name: `Scala WhatsApp Agent`
   - App Contact Email: seu email
   - Business Account: selecione ou crie um Meta Business
5. Na tela do app → **"Add Product"** → adicione **"WhatsApp"**

---

## PASSO 2 — Configurar WhatsApp Business no Meta

1. No app → **WhatsApp → Getting Started**
2. Anote o **Phone Number ID** do número de teste fornecido pela Meta
3. **Gerar Access Token permanente:**
   - Meta Business Manager → **System Users** → crie um System User (role Admin)
   - Gere token com permissões: `whatsapp_business_messaging`, `whatsapp_business_management`
   - **Guarde este token** (não será exibido novamente)
4. Anote também o **WhatsApp Business Account ID** (visível em WhatsApp → Configuration)

---

## PASSO 3 — Criar Google Sheet para Histórico

1. Crie uma planilha nova em [sheets.google.com](https://sheets.google.com)
2. Renomeie a aba para **`Conversas`**
3. Adicione estes cabeçalhos na linha 1:

| A | B | C | D | E |
|---|---|---|---|---|
| conversationId | role | content | pushName | timestamp |

4. Copie o **Sheet ID** da URL:
   `https://docs.google.com/spreadsheets/d/`**`<SHEET_ID>`**`/edit`

---

## PASSO 4 — Configurar Credenciais no n8n

Acesse n8n → **Settings → Credentials → Add Credential**

### 4.1 WhatsApp Business Cloud API
- Tipo: `WhatsApp Business Cloud API`
- **Access Token:** token do Passo 2.3
- **Phone Number ID:** ID do Passo 2.2
- **WhatsApp Business Account ID:** ID do Passo 2.4

### 4.2 OpenAI
- Tipo: `OpenAI`
- **API Key:** obtenha em [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 4.3 Google Sheets OAuth2
- Tipo: `Google Sheets OAuth2 API`
- Siga o fluxo OAuth2 do n8n (autorizar com a conta Google dona da planilha)

---

## PASSO 5 — Configurar Nós do Workflow

Abra o workflow **"Scala — WhatsApp AI Agent (Ana) 24/7"** no n8n.

| Nó | O que configurar |
|---|---|
| **WhatsApp Trigger** | Selecionar credencial WhatsApp |
| **Buscar Histórico** | Credencial Google Sheets + Sheet ID do Passo 3.4 |
| **OpenAI GPT-4o-mini** | Credencial OpenAI (Authentication → Predefined Credential Type → OpenAI) |
| **Salvar Mensagem User** | Credencial Google Sheets + Sheet ID |
| **Salvar Resposta Assistente** | Credencial Google Sheets + Sheet ID |
| **Enviar Resposta WhatsApp** | Credencial WhatsApp + selecionar Phone Number na lista |

Nos nós Google Sheets: substituir `SEU_GOOGLE_SHEET_ID_AQUI` pelo Sheet ID real.

---

## PASSO 6 — Registrar Webhook na Meta

1. No nó **WhatsApp Trigger** → copiar a **Webhook URL de teste**
2. Meta App Dashboard → **WhatsApp → Configuration → Webhook → Edit**
3. Preencher:
   - **Callback URL:** URL copiada do n8n
   - **Verify Token:** string aleatória (ex: `scala-webhook-2026`) — insira o mesmo valor na credencial WhatsApp do n8n
4. Ativar o campo **`messages`** em Webhook Fields

---

## PASSO 7 — Testar

1. Clicar em **"Test workflow"** no n8n (não ativar ainda)
2. Enviar mensagem WhatsApp para o número de teste da Meta
   - Obs: seu número precisa estar adicionado como teste em WhatsApp → Getting Started → "To"
3. Verificar se cada nó processou corretamente
4. Verificar se a resposta chegou no WhatsApp
5. Verificar se as linhas foram salvas no Google Sheets

---

## PASSO 8 — Ativar em Produção

1. Quando os testes passarem → clicar em **"Activate"** no workflow
2. O n8n troca automaticamente para a URL de produção
3. **Importante:** a Meta permite apenas 1 webhook por app. Ao ativar, a URL de teste para de funcionar.
   Para testar novamente: desativar o workflow temporariamente.

---

## Arquitetura do Workflow

```
[WhatsApp Trigger]          recebe mensagem via Meta Cloud API
        ↓
[Extrair Dados]             extrai phone, texto, nome; filtra grupos/status/não-texto
        ↓
[Buscar Histórico]          lê todas as mensagens do Google Sheets
        ↓
[Montar Contexto]           filtra por conversationId, monta messages[] + system prompt
        ↓
[OpenAI GPT-4o-mini]        chamada API OpenAI — max_tokens: 300, temperature: 0.7
        ↓
[Delay Humano 5s]           simula digitação humana
        ↓
[Preparar Resposta]         extrai texto da resposta da OpenAI
        ↓
[Salvar Mensagem User]      append no Google Sheets (role: user)
        ↓
[Salvar Resp. Assistente]   append no Google Sheets (role: assistant)
        ↓
[Enviar Resposta WhatsApp]  envia via Meta Cloud API
```

---

## Custos Estimados

| Item | Valor |
|---|---|
| GPT-4o-mini input | ~$0,00015 / 1k tokens |
| GPT-4o-mini output | ~$0,0006 / 1k tokens |
| Por conversa completa (15 trocas) | ~$0,01–0,03 USD |
| 100 conversas/mês | ~$1–3 USD |
| Meta Cloud API | Gratuito até 1.000 conversas/mês iniciadas pelo usuário |

---

## Limitação Importante: Janela de 24h da Meta

A Meta permite enviar mensagens livres apenas dentro de **24h após o último contato do usuário**.
Fora dessa janela, só é possível enviar templates pré-aprovados.
Para um agente receptivo (usuário sempre inicia), isso não é problema.

---

## Próximos Passos Sugeridos

1. **Notificação de lead QUENTE:** detectar classificação e notificar o dono da Scala
2. **Google Calendar:** agendamento automático quando a IA confirmar uma reunião
3. **Dashboard:** conectar Google Sheets ao Looker Studio para visualizar conversas e conversões
4. **Migrar para número real:** substituir número de teste da Meta por número de produção
