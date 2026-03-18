# SOP — Onboarding de Clientes: Automações de Ads

**Versão:** 1.0 | **Atualizado:** 2026-03-18
**Instância n8n:** `https://n8n.paulonunan.com`
**Planilha Mestre:** [Clientes — Google Sheets](https://docs.google.com/spreadsheets/d/1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A)

---

## Serviços Disponíveis

| Código | Serviço | Workflow n8n | Preço sugerido |
|--------|---------|-------------|----------------|
| `reports_meta` | Relatório semanal Meta Ads → WhatsApp | WF-02 (`dLr5lDWj7rtLgbGk`) | R$ 250/mês |
| `reports_google` | Relatório semanal Google Ads → WhatsApp | WF-03 (`ndMNpUBlGhfd6CO2`) | R$ 250/mês |
| `leads` | Captura Meta Lead Ads → Google Sheets | WF-04 (`rfYBkXnh37JltJxN`) | R$ 300/mês |
| `full` | Todos os serviços acima | WF-02 + WF-03 + WF-04 | R$ 650/mês |

---

## Arquitetura (como funciona para múltiplos clientes)

```
Planilha "Clientes" (Google Sheets)
  └─ Uma linha por cliente
  └─ ativo = TRUE/FALSE → liga/desliga todos os serviços

WF-02 (toda segunda, 08h) → loop em todos os clientes com meta_ad_account_id + meta_access_token
WF-03 (toda segunda, 08h05) → loop em todos os clientes com google_customer_id
WF-04 (webhook sempre ativo) → roteia por meta_page_id → salva na planilha do cliente
```

**Onboarding = adicionar 1 linha na planilha. Offboarding = setar `ativo=FALSE`.**

---

## Schema da Planilha "Clientes"

| Coluna | Exemplo | Obrigatório para |
|--------|---------|-----------------|
| `nome_cliente` | `Empresa XYZ` | Todos |
| `whatsapp` | `5511987654321` | Todos (recebe relatórios/alertas) |
| `ativo` | `TRUE` | Todos |
| `meta_ad_account_id` | `act_120244137424200671` | reports_meta |
| `meta_access_token` | `EAAJ...` | reports_meta |
| `google_customer_id` | `1234567890` | reports_google |
| `leads_sheet_id` | `1ABC...XYZ` | leads |
| `meta_page_id` | `123456789012345` | leads |
| `plano` | `full` | Controle interno |
| `data_inicio` | `2026-03-18` | Controle interno |
| `observacoes` | `Cliente VIP` | Controle interno |

---

## SERVIÇO 1 — Relatórios Meta Ads → WhatsApp

### O que o cliente recebe
Toda segunda-feira às 8h: mensagem WhatsApp com performance de cada campanha Meta dos últimos 7 dias (alcance, impressões, cliques, CTR, CPC, investimento).

### O que você precisa coletar do cliente
- [ ] Nome da empresa/cliente
- [ ] Número WhatsApp (com DDI — ex: `5511987654321`)
- [ ] Meta Ad Account ID (ex: `act_120244137424200671`)
- [ ] Acesso ao Meta Business Manager (para gerar o token — ver Guia de Credenciais)

### Passo a passo de setup

1. **Conseguir o Meta Access Token do cliente**
   - Veja o [Guia de Credenciais](./guia-credenciais-cliente.md) — Seção "Meta Access Token"
   - Token válido por tempo indeterminado (System User) ou ~60 dias (token pessoal)

2. **Adicionar linha na planilha Clientes**
   - Abrir [planilha mestre](https://docs.google.com/spreadsheets/d/1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A)
   - Adicionar nova linha com:
     - `nome_cliente`, `whatsapp`, `ativo=TRUE`
     - `meta_ad_account_id`, `meta_access_token`
     - `plano=reports_meta`, `data_inicio=hoje`

3. **Testar**
   - Abrir n8n → WF-02 → botão "Execute Workflow"
   - Verificar se o cliente recebeu o WhatsApp
   - Se der erro: verificar token e ad account ID (ver troubleshooting abaixo)

4. **Confirmar com o cliente**
   - Aguardar a segunda-feira seguinte ou executar manual novamente para demonstração

### Troubleshooting
| Erro | Causa | Solução |
|------|-------|---------|
| `Invalid OAuth access token` | Token expirado ou inválido | Gerar novo token (ver guia credenciais) |
| `Unsupported get request` | Ad Account ID errado | Verificar formato: deve começar com `act_` |
| Cliente não recebe mensagem | Número WhatsApp errado | Verificar DDI (55) + DDD + número |
| Cliente filtrado | `ativo=FALSE` ou token vazio | Verificar colunas na planilha |

### Offboarding
1. Na planilha Clientes, setar `ativo=FALSE` na linha do cliente
2. O cliente deixa de receber relatórios na próxima execução
3. Opcional: deletar a linha se quiser limpeza

---

## SERVIÇO 2 — Relatórios Google Ads → WhatsApp

### O que o cliente recebe
Toda segunda-feira às 8h05: mensagem WhatsApp com performance de cada campanha Google Ads dos últimos 7 dias (impressões, cliques, custo em R$, CTR, CPC médio, conversões).

### O que você precisa coletar do cliente
- [ ] Nome da empresa/cliente
- [ ] Número WhatsApp (com DDI)
- [ ] Google Ads Customer ID (10 dígitos, ex: `1234567890`)

### Passo a passo de setup

1. **Vincular conta Google Ads ao seu MCC**
   - Você tem um MCC (Manager Account) ID: `4323799990`
   - O cliente precisa aceitar o convite de gerenciamento
   - Veja o [Guia de Credenciais](./guia-credenciais-cliente.md) — Seção "Google Ads via MCC"

2. **Adicionar linha na planilha Clientes**
   - `nome_cliente`, `whatsapp`, `ativo=TRUE`
   - `google_customer_id` (apenas os números, sem hífens)
   - `plano=reports_google`, `data_inicio=hoje`

3. **Testar**
   - Abrir n8n → WF-03 → "Execute Workflow"
   - Verificar recebimento do WhatsApp

4. **Confirmar com o cliente**

### Troubleshooting
| Erro | Causa | Solução |
|------|-------|---------|
| `PERMISSION_DENIED` | MCC não vinculado à conta | Solicitar aceite do convite |
| `INVALID_CUSTOMER_ID` | Customer ID errado | Verificar no painel Google Ads: Ferramentas → Conta |
| Valores zerados | Sem campanhas ativas no período | Normal se conta sem campanha ativa |

### Offboarding
- Setar `ativo=FALSE` na planilha OU remover `google_customer_id`
- Opcional: remover o cliente do MCC pelo Google Ads Manager

---

## SERVIÇO 3 — Captura de Leads Meta → Google Sheets

### O que o cliente recebe
Cada lead que preenche o formulário de Lead Ad do cliente é automaticamente salvo em uma planilha Google Sheets exclusiva do cliente + notificação WhatsApp em tempo real.

### O que você precisa coletar do cliente
- [ ] Nome da empresa/cliente
- [ ] Número WhatsApp (para receber alertas de novos leads)
- [ ] Facebook Page ID (ID numérico da página — ver guia credenciais)
- [ ] Acesso ao Meta Developer Console (para registrar webhook) OU acesso de admin à página

### Passo a passo de setup

1. **Criar planilha Google Sheets para o cliente**
   - Criar nova planilha: `[Nome do Cliente] — Leads`
   - Criar aba chamada `Leads` com as colunas:
     `nome_cliente | nome | email | telefone | lead_id | form_id | data_hora | status`
   - Compartilhar a planilha com a conta Google `ph.nunan@gmail.com` (editor)
   - Copiar o Sheet ID (parte da URL após `/d/` e antes de `/edit`)

2. **Obter o Facebook Page ID do cliente**
   - Ver [Guia de Credenciais](./guia-credenciais-cliente.md) — Seção "Facebook Page ID"

3. **Adicionar linha na planilha Clientes**
   - `nome_cliente`, `whatsapp`, `ativo=TRUE`
   - `leads_sheet_id` = ID da planilha criada no passo 1
   - `meta_page_id` = ID numérico da página Facebook
   - `plano=leads`, `data_inicio=hoje`

4. **Registrar webhook no Meta**
   - Acessar: Meta Developer Console → App `854431830954678` → Webhooks
   - Subscription: `leadgen`
   - Callback URL: `https://n8n.paulonunan.com/webhook/meta-leads`
   - Verify Token: qualquer string (não é usado no workflow)
   - Selecionar a página do cliente
   > WF-04b responde automaticamente ao desafio de verificação (está sempre ativo)

5. **Ativar WF-04 no n8n** (se ainda não estiver ativo)
   - n8n → WF-04 → toggle para ativar

6. **Testar**
   - Submeter lead de teste pelo formulário da página
   - Verificar: lead apareceu na planilha do cliente? WhatsApp chegou?

### Troubleshooting
| Erro | Causa | Solução |
|------|-------|---------|
| Lead não salvo | `meta_page_id` errado na planilha | Verificar ID da página vs. o que Meta envia |
| Webhook não verificado | WF-04b inativo | Ativar WF-04b no n8n |
| `leads_sheet_id` inválido | Planilha não compartilhada ou ID errado | Verificar compartilhamento e ID |
| Nenhum campo no lead | Formulário com campos diferentes | Ajustar o Code node "Set Lead Data" |

### Offboarding
1. Na planilha Clientes, setar `ativo=FALSE`
2. No Meta Developer Console: remover webhook da página do cliente (ou deixar — não vai salvar pois `ativo=FALSE`)
3. Opcional: parar de compartilhar a planilha de leads

---

## Checklist Rápido — Novo Cliente (Todos os Serviços)

```
ANTES DA REUNIÃO:
[ ] Preparar Google Form ou template de briefing

NA REUNIÃO / POR EMAIL:
[ ] Coletar: nome, WhatsApp, plano contratado
[ ] Meta Ads: coletar Ad Account ID + dar acesso ao BM ou pedir token
[ ] Google Ads: coletar Customer ID + enviar convite MCC
[ ] Lead Ads: coletar Page ID + combinar acesso ao Meta Developer Console

SETUP (você faz internamente, ~15-30 min):
[ ] Gerar Meta Access Token (se relatório Meta)
[ ] Criar planilha de leads (se serviço leads) + compartilhar
[ ] Adicionar linha na planilha Clientes (ativo=TRUE)
[ ] Registrar webhook Meta (se serviço leads)
[ ] Executar workflow manualmente para teste
[ ] Confirmar recebimento com o cliente

ENTREGA:
[ ] Enviar mensagem de confirmação ao cliente
[ ] Explicar quando os relatórios chegam (toda segunda, 8h)
[ ] Combinar ponto de contato para dúvidas
```

---

## Fluxo para Cliente que Sai (Offboarding)

1. Setar `ativo=FALSE` na planilha Clientes
2. Para leads: remover webhook da página no Meta Developer Console
3. Opcional: remover linha da planilha (ou manter para histórico)
4. **Tempo total: 2 minutos**

---

## Notas sobre Hosting

- Todos os clientes rodam na **mesma instância n8n** (`n8n.paulonunan.com`)
- Custo adicional por cliente: zero
- Limite prático: centenas de clientes (o loop processa um por vez)
- Para clientes enterprise que exijam isolamento: criar instância n8n separada (VPS ~R$50/mês) ou indicar n8n Cloud (~USD 20/mês)
