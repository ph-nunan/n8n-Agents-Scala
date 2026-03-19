# n8n-Agents-Scala
## Sistema Completo de Automação e IA — Scala Automações

> **Atualizado:** 2026-03-19
> **Instância n8n:** `https://n8n.paulonunan.com`
> **Status:** PRODUÇÃO — todos os sistemas ativos

---

## Visão Geral

Este repositório centraliza todos os agentes de IA e workflows de automação da **Scala Automações** (Brasília/DF), construídos em n8n. O sistema possui dois agentes principais operando pelo mesmo número de WhatsApp (`+55 61 8189-4189`), com roteamento automático por remetente.

```
WhatsApp +55 61 8189-4189
          │
          ├── Paulo (61981292879) → Bruno (gestor de tráfego IA)
          │
          └── Qualquer outro número → Ana (atendimento de clientes)
```

---

## Agentes

### Ana — Atendimento 24/7
Atende clientes da Scala via WhatsApp. Responde dúvidas, qualifica leads, agenda reuniões via Google Calendar.

- **Pasta:** [n8n-AgenteAtendimento-Ana/](n8n-AgenteAtendimento-Ana/)
- **Workflow:** `EVbZX91iB5moD6I4`
- **Persona:** Ana, consultora de automação da Scala
- **Docs:** [n8n-AgenteAtendimento-Ana/README.md](n8n-AgenteAtendimento-Ana/README.md)

### Bruno — Gestor de Tráfego IA (exclusivo para Paulo)
Gerencia campanhas de Meta Ads e Google Ads via WhatsApp. Conduz qualificação estratégica antes de recomendar qualquer ação, executa comandos diretos na API do Meta e Google.

- **Pasta:** [n8n-AgenteAds-Bruno/](n8n-AgenteAds-Bruno/)
- **Workflow principal:** `VSNwEhdZLMA2ZJyq`
- **Persona:** Bruno, gestor de tráfego sênior com 10 anos de experiência
- **Docs:** [n8n-AgenteAds-Bruno/README.md](n8n-AgenteAds-Bruno/README.md)

---

## Serviços de Relatórios (multi-cliente)

Relatórios automáticos semanais enviados via WhatsApp para cada cliente cadastrado na planilha mestre.

| Workflow | ID | Horário | Função |
|----------|----|---------|--------|
| WF-02 Meta Reports | `dLr5lDWj7rtLgbGk` | Seg 8h00 | Relatório Meta Ads → WhatsApp do cliente |
| WF-03 Google Reports | `ndMNpUBlGhfd6CO2` | Seg 8h05 | Relatório Google Ads → WhatsApp do cliente |
| WF-04 Meta Leads | `rfYBkXnh37JltJxN` | Sempre ativo (webhook) | Lead Meta → Sheets do cliente + WhatsApp |
| WF-04b Verificação | `a1rk1RB4F0MRRyHK` | Sempre ativo | Responde desafio de verificação do Meta |

**Planilha mestre de clientes:** `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A`
**Onboarding:** [docs/sop-onboarding-cliente.md](docs/sop-onboarding-cliente.md)
**Credenciais por serviço:** [docs/guia-credenciais-cliente.md](docs/guia-credenciais-cliente.md)

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    WhatsApp Business                     │
│              +55 61 8189-4189 (Cloud API)                │
└────────────────────────┬────────────────────────────────┘
                         │ webhook
                         ▼
┌─────────────────────────────────────────────────────────┐
│        SCALA WORKFLOW (EVbZX91iB5moD6I4)                 │
│                                                          │
│  Router: phoneNumber == "556181292879"?                  │
│     SIM → POST localhost:5678/webhook/campaign-agent     │
│     NÃO → Ana AI Agent                                   │
└──────────────────┬──────────────────┬───────────────────┘
                   │                  │
          ┌────────▼───────┐  ┌───────▼────────┐
          │  BRUNO WF-01   │  │  ANA (inline)  │
          │ VSNwEhdZLMA2ZJyq│  │  GPT + Sheets  │
          │ GPT-4o-mini     │  │  Calendar      │
          │ Meta API        │  └────────────────┘
          │ Google Ads API  │
          └────────────────┘

┌─────────────────────────────────────────────────────────┐
│              RELATÓRIOS AUTOMÁTICOS                      │
│                                                          │
│  WF-02 (seg 8h)  → Google Sheets → Meta API → WhatsApp  │
│  WF-03 (seg 8h05)→ Google Sheets → Google API → WhatsApp│
│  WF-04 (webhook) → Meta Lead → Sheets cliente → WhatsApp│
└─────────────────────────────────────────────────────────┘
```

---

## Contas e IDs Principais

| Recurso | Valor |
|---------|-------|
| n8n URL | `https://n8n.paulonunan.com` |
| WhatsApp Phone Number ID | `971782562694033` |
| WhatsApp Business Account ID | `1480192843700940` |
| Meta App ID | `854431830954678` |
| Meta Ad Account (Scala) | `act_1605651367382391` |
| Google Ads MCC | `4323799990` |
| Planilha Mestre de Clientes | `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A` |
| Google Sheet Ana (Conversas) | `1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U` |

---

## Estrutura do Repositório

```
n8n-Agents-Scala/
├── README.md                          ← Este arquivo
├── docs/
│   ├── sop-onboarding-cliente.md      ← SOP completo de onboarding (3 serviços)
│   └── guia-credenciais-cliente.md    ← Como obter cada credencial por serviço
├── n8n-AgenteAtendimento-Ana/
│   ├── README.md                      ← Documentação completa da Ana
│   └── workflows/
│       └── scala-whatsapp-ai-agent.json
└── n8n-AgenteAds-Bruno/
    ├── README.md                      ← Documentação completa do Bruno
    ├── workflows/
    │   ├── bruno-ads-manager.json     ← JSON atual do Bruno (sincronizado)
    │   ├── wf02_meta_reports.json
    │   └── wf03_google_reports.json
    └── scripts/
        └── *.py                       ← Scripts utilitários de desenvolvimento
```

---

## Serviços Disponíveis para Clientes

| Código | Descrição | Workflow | Preço sugerido |
|--------|-----------|----------|----------------|
| `reports_meta` | Relatório semanal Meta Ads → WhatsApp | WF-02 | R$ 250/mês |
| `reports_google` | Relatório semanal Google Ads → WhatsApp | WF-03 | R$ 250/mês |
| `leads` | Captura Meta Lead Ads → Google Sheets + alerta | WF-04 | R$ 300/mês |
| `full` | Todos os serviços | WF-02+03+04 | R$ 650/mês |

**Onboarding de novo cliente:** adicionar 1 linha na planilha mestre → ~15-30 min de setup.
**Offboarding:** setar `ativo=FALSE` na planilha → 2 minutos.
