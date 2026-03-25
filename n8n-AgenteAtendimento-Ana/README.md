# Agente IA Scala — Ana (WhatsApp 24/7) v2

Agente de atendimento IA para qualificação de leads e agendamento de diagnósticos gratuitos via WhatsApp, com integração ao Google Calendar e Google Meet automático.

## Stack

| Componente | Tecnologia |
|---|---|
| Orquestração | n8n (`n8n.paulonunan.com`) |
| Canal | WhatsApp Business Cloud API (Meta oficial) |
| Modelo de IA | GPT-4.1 (OpenAI) |
| Memória | Google Sheets (HTTP Request → Sheets API v4) |
| Agenda | Google Calendar API (criar evento + Meet link) |
| Reunião | Google Meet (link automático no evento) |
| Persona | Ana — consultora de automação da Scala |

## Workflow n8n

- **ID:** `S22OxWxT77a1geK8`
- **Nome:** Ana — Agente WhatsApp v2
- **Status:** ✅ ATIVO em produção
- **Nodes:** 16
- **Webhook URL:** `https://n8n.paulonunan.com/webhook/whatsapp-ana`

## IDs Meta

| Campo | Valor |
|---|---|
| Meta App ID | `854431830954678` |
| Phone Number (+55 61 8189-4189) | `971782562694033` |
| WhatsApp Business Account ID | `1480192843700940` |
| PIN do número | `869531` |
| Link WhatsApp | `https://wa.me/556181894189` |

## Google Sheets

- **Sheet ID:** `1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U`
- **Aba:** `Conversas`
- **Colunas:** `conversationId | role | content | pushName | timestamp`
- **Acesso:** HTTP Request → Google Sheets API v4 (contorna bug do node nativo v4.x)

## Google Calendar

- **Credencial n8n:** `Google Calendar - Paulo` (ID: `QGp1FxkKTfYhYYJ0`)
- **Calendário:** `primary` (ph.nunan@gmail.com)
- **Duração:** 20 min por reunião
- **Meet link:** gerado automaticamente via `conferenceData.createRequest`

## Arquitetura do Workflow (16 nodes)

```
Webhook WhatsApp (POST /whatsapp-ana, responseMode: onReceived)
  → Extrair Dados (Code)
  → Buscar Histórico (HTTP Request → Sheets API GET)
  → Limitar 1 Item (Code — força 1 item de saída)
  → Montar Contexto (Code — system prompt 8 passos + slots dinâmicos)
  → GPT-4.1 (HTTP Request → OpenAI)  [error → Resposta Fallback]
  → Preparar Resposta (Code)
  → Detectar Agendamento (Code — detecta "marcado para DD/MM às HH:MM")
  → IF Agendamento
      [true]  → Criar Evento Calendario (HTTP Request → Calendar API)
               → Montar Mensagem Final (Code — append Meet link)
               → Aguardar (Wait 3s)
               → Enviar WhatsApp
      [false] → Aguardar (Wait 3s)
               → Enviar WhatsApp
  → Preparar Linhas (Code — lê de Preparar Resposta, não do input)
  → Salvar Conversa (HTTP Request → Sheets API POST :append)

  Resposta Fallback → Aguardar → Enviar WhatsApp
```

## Fluxo de Atendimento da Ana (8 Passos)

| Passo | Objetivo |
|---|---|
| P1 — Conexão Inicial | Boas-vindas com nome + descobrir negócio (Variante A: site / Variante B: orgânico) |
| P2 — Identificação da Trilha | Mapear área: Atendimento / Marketing / Comercial / Outra |
| P3 — Reconhecimento da Dor | Mostrar exemplos específicos da trilha com bullets |
| P4 — Aprofundamento | 2 perguntas específicas por trilha, uma por vez |
| P5 — Transição e Resumo | Resumo personalizado da dor + criar antecipação para a reunião |
| P6 — Agendamento | Oferta de 2 slots concretos das disponibilidades |
| P7 — Confirmação | "Perfeito! ✅ Marcado para DD/MM às HH:MM." + micro-compromisso |
| P8 — Lembrete D-1 | *Pendente — workflow separado com cron* |

## Desvios Cobertos

- Preço → redireciona para valor do diagnóstico
- Resposta vaga → foca em uma dor
- Não é decisor → convida ambos
- Já tem solução → auditoria do ecossistema
- Silêncio → reengajamento

## Bugs Corrigidos (v2 — 2026-03-25)

| Bug | Causa | Fix |
|---|---|---|
| Google Sheets node `sheetName` error | Node v4.x nunca resolve via API (qualquer modo) | Substituído por HTTP Request → Sheets API v4 |
| Ana repetia "Oi [Nome]" em toda mensagem | `Preparar Linhas` lia `$input` (resposta WhatsApp) → salvava `undefined` como conversationId | Corrigido para ler `$('Preparar Resposta').first().json` |
| Meet link duplicado na oferta de slots | `Detectar Agendamento` usava `/✅/` que batia nos slots do fechamento | Regex restrito a `marcado para\|agendado para` |
| Meet link substituía data na confirmação | `Montar Mensagem Final` substituía `✅ Marcado para...` pelo bloco de meet | Corrigido: simplesmente appenda `\n🔗 [link]` ao final |

## Estrutura da Pasta

```
n8n-AgenteAtendimento-Ana/
├── README.md
├── docs/
│   ├── system-prompt.md              # System prompt completo editável (v2)
│   ├── guia-configuracao.md          # Setup completo passo a passo
│   ├── analise-sessao-2026-03-25.md  # Rebuild v2 — 8 passos + Calendar + fixes
│   ├── analise-sessao-2026-03-20-parte2.md
│   ├── analise-sessao-2026-03-20.md
│   ├── analise-sessao-2026-03-19.md
│   └── analise-sessao-2026-03-16.md
└── workflows/
    └── scala-whatsapp-ai-agent.json  # JSON do workflow n8n (sincronizado)
```

## Credenciais no n8n

| Credencial | Tipo | Usada em |
|---|---|---|
| `WhatsApp account` (id: `umUchtUGj2ZzikQ5`) | WhatsApp API | Enviar mensagens |
| `scala-agent` (id: `LFnyHUsH7lj5FEvQ`) | OpenAI API | GPT-4.1 |
| `Google Sheets - Paulo` (id: `UeSaLFF10d9utrmA`) | Google Sheets OAuth2 | Histórico de conversas |
| `Google Calendar - Paulo` (id: `QGp1FxkKTfYhYYJ0`) | Google Calendar OAuth2 | Criar eventos + Meet |

## Observações Técnicas

- **Google Sheets node v4.x** tem bug: `sheetName` nunca resolve via API. Usar HTTP Request → Sheets API v4 direto.
- **`Preparar Linhas`** deve sempre ler de `$('Preparar Resposta').first().json`, não de `$input` (que retorna a resposta da API WhatsApp).
- **`Detectar Agendamento`** usa regex restrito (`marcado para|agendado para`) — nunca `/✅/` que também aparece no fechamento.
- **`Montar Mensagem Final`** só executa quando `isBooking === true`. Apenas faz append do Meet link ao final da mensagem.
- **Webhook `responseMode: onReceived`**: responde 200 imediatamente ao Meta, continua processando em background — evita timeout de 20s do WhatsApp.
- **Legacy prefix**: histórico antigo tem `conversationId = 'scala_' + phoneNumber`. O filtro aceita ambos.
