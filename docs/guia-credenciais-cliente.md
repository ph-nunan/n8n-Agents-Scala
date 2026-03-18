# Guia de Credenciais por Serviço

**Para uso interno — Scala Automações**
**Atualizado:** 2026-03-18

Este guia explica como obter cada credencial necessária para ativar um serviço para um novo cliente.

---

## Meta Access Token (para WF-02 — Relatórios Meta Ads)

O token permite que o workflow leia os dados de performance da conta de anúncios do cliente.

### Opção A — Melhor: Você como parceiro no BM do cliente

1. Pedir ao cliente que acesse o **Meta Business Manager** deles: business.facebook.com
2. Ir em: **Configurações → Parceiros → Adicionar parceiro**
3. Inserir o ID do seu BM: `[SEU_BUSINESS_MANAGER_ID]`
4. Dar permissão de **Anunciante** na conta de anúncios (`act_...`)
5. No seu BM → Usuários do sistema → `scala-user` → Gerar token
6. Selecionar a conta de anúncios do cliente → permissões: `ads_read`, `ads_management`
7. Copiar o token gerado → salvar na coluna `meta_access_token` da planilha

> ✅ **Vantagem:** Token permanente (System User). Não expira.
> ⚠️ **Pré-requisito:** Cliente precisa ter Business Manager configurado.

---

### Opção B — Rápida: Token pessoal do cliente

1. Pedir ao cliente que acesse: [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Selecionar: **App → Meta App for Business** (ou o app padrão)
3. Clicar em **Gerar Token de Acesso**
4. Conceder permissões: `ads_read`, `ads_management`, `read_insights`
5. Copiar o token → salvar na coluna `meta_access_token`

> ⚠️ **Desvantagem:** Expira em ~60 dias. Precisa renovar periodicamente.
> ✅ **Vantagem:** Mais rápido, não precisa de acesso ao BM.

---

### Opção C — Mais controle: Acesso à conta via seu BM

1. No seu BM, ir em: **Configurações → Contas de Anúncios → Adicionar**
2. Opção "Solicitar acesso à conta de anúncios"
3. Inserir o ID da conta do cliente
4. O cliente aprova o pedido em: Meta Business Manager → Notificações
5. No seu BM → Usuários do sistema → `scala-user` → Gerar token com acesso à conta

---

### Como encontrar o Meta Ad Account ID

- Cliente acessa: [business.facebook.com](https://business.facebook.com) → Contas de Anúncios
- O ID começa com `act_` (ex: `act_120244137424200671`)
- Ou no Ads Manager: URL do browser contém `act=120244137424200671` (adicionar `act_` na frente)

---

## Google Ads Customer ID (para WF-03 — Relatórios Google Ads)

O workflow usa o **seu MCC** para acessar qualquer conta vinculada. Você não precisa de token adicional — só do Customer ID do cliente.

### Como vincular a conta do cliente ao seu MCC

1. Acessar [Google Ads Manager](https://ads.google.com) com sua conta MCC (`4323799990`)
2. Ir em: **Contas → Adicionar conta existente**
3. Inserir o e-mail do cliente (ele receberá convite) ou o Customer ID se você já tiver acesso
4. O cliente acessa o Google Ads → Notificações → Aceitar convite
5. Pronto — o MCC agora tem acesso à conta do cliente

### Como encontrar o Google Ads Customer ID

- Cliente acessa: [ads.google.com](https://ads.google.com)
- No topo direito: mostra o Customer ID no formato `123-456-7890`
- **Usar sem hífens** na planilha: `1234567890`

> ✅ **Sem token adicional necessário.** O MCC + Developer Token do n8n já cobrem todos os clientes vinculados.

---

## Facebook Page ID (para WF-04 — Meta Leads)

### Método 1 — Mais fácil

1. Acessar a página do cliente no Facebook
2. Clicar em **Sobre** → rolar até o final
3. O Page ID aparece como número (ex: `123456789012345`)

### Método 2 — Via URL

1. Acessar a página do cliente no Facebook no browser
2. Se a URL for `facebook.com/pages/nome-da-pagina/123456789012345` → o número é o Page ID
3. Se usar URL amigável (ex: `facebook.com/empresaxyz`): usar [findmyfbid.in](https://findmyfbid.in) ou similar

### Método 3 — Via Meta Developer Console

1. Acessar [developers.facebook.com](https://developers.facebook.com)
2. App → Graph API Explorer
3. Query: `GET /me/accounts`
4. O Page ID aparece no campo `id` de cada página

---

## Como Registrar o Webhook no Meta (para WF-04)

1. Acessar: [developers.facebook.com](https://developers.facebook.com) → App `854431830954678` → Produtos → Webhooks
2. Selecionar objeto: **Page**
3. Clicar em **Adicionar URL de callback**:
   - URL: `https://n8n.paulonunan.com/webhook/meta-leads`
   - Verify Token: `scala2024` (ou qualquer string — não é validada pelo workflow)
4. O Meta vai verificar o URL (WF-04b responde automaticamente) → Status: Verificado ✅
5. Clicar em **Assinar** → selecionar campo: `leadgen`
6. **Assinar para a página do cliente específica:**
   - Ainda em Webhooks → clicar na página → Assinar

> **Atenção:** Um único webhook URL serve para TODOS os clientes. O roteamento é feito internamente pelo WF-04 via `meta_page_id`.

---

## Planilha de Leads por Cliente

Para cada novo cliente do serviço de Leads, criar uma planilha Google Sheets:

1. Criar nova planilha com nome: `[Nome do Cliente] — Leads`
2. Criar aba chamada **`Leads`** com as colunas na linha 1:
   ```
   nome_cliente | nome | email | telefone | lead_id | form_id | data_hora | status
   ```
3. **Compartilhar com: `ph.nunan@gmail.com` como Editor**
4. Copiar o Sheet ID: parte da URL entre `/d/` e `/edit`
   - URL: `https://docs.google.com/spreadsheets/d/XXXXXXXXXXX/edit`
   - Sheet ID = `XXXXXXXXXXX`
5. Salvar na coluna `leads_sheet_id` da planilha Clientes

---

## Referência Rápida — O que coletar por serviço

| Dado | Relatório Meta | Relatório Google | Leads Meta |
|------|:--------------:|:----------------:|:----------:|
| Nome do cliente | ✅ | ✅ | ✅ |
| WhatsApp | ✅ | ✅ | ✅ |
| Meta Ad Account ID (`act_...`) | ✅ | — | — |
| Meta Access Token | ✅ | — | — |
| Google Ads Customer ID | — | ✅ | — |
| Facebook Page ID | — | — | ✅ |
| Google Sheet ID (leads) | — | — | ✅ |

---

## Credenciais Fixas (suas — não mudam por cliente)

| Credencial | Valor | Onde é usada |
|-----------|-------|-------------|
| n8n Instance | `https://n8n.paulonunan.com` | Acesso à plataforma |
| Google Ads MCC ID | `4323799990` | WF-03 (login-customer-id header) |
| Google Ads Developer Token | Ver n8n credencial `2yQz1qh73JLxM3Rr` | WF-03 |
| WhatsApp Phone Number ID | `971782562694033` | WF-02, WF-03, WF-04 |
| Meta App ID | `854431830954678` | Registro de webhooks |
| Planilha Mestre (Clientes) | `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A` | WF-02, WF-03, WF-04 |
