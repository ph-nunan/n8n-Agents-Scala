# Agente IA Scala — WhatsApp 24/7

Agente de atendimento IA para qualificação de leads e agendamento de diagnósticos gratuitos via WhatsApp, com integração real ao Google Agenda e Google Meet.

## Stack

| Componente | Tecnologia |
|---|---|
| Orquestração | n8n (`n8n.paulonunan.com`) |
| Canal | WhatsApp Business Cloud API (Meta oficial) |
| Modelo de IA | GPT-4o-mini (OpenAI) |
| Memória | Google Sheets |
| Agenda | Google Calendar API (freeBusy + Events) |
| Reunião | Google Meet (link automático) |
| Persona | Ana — consultora de automação da Scala |

## Workflow n8n

- **ID:** `EVbZX91iB5moD6I4`
- **Nome:** Scala — WhatsApp AI Agent (Ana) 24/7
- **Status:** ✅ ATIVO em produção (ativado 2026-03-16, atualizado 2026-03-19)
- **Nodes:** 32

## IDs Meta (atualizado 2026-03-16)

| Campo | Valor |
|---|---|
| Meta App ID | `854431830954678` |
| Phone Number (+55 61 8189-4189) | `971782562694033` |
| WhatsApp Business Account ID | `1480192843700940` |
| Webhook Verify Token | `scala-webhook-2026` |
| Webhook URL (produção) | `https://n8n.paulonunan.com/webhook/a4d4b2c4-2099-4eb6-980d-df5274d1c1fc/webhook` |
| PIN do número | `869531` |
| System User Token | permanente (sem expiração) — gerado 2026-03-16 |
| Link WhatsApp | `https://wa.me/556181894189` |

## Google Sheets

- **Sheet ID:** `1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U`
- **Aba:** `Conversas`
- **Colunas:** `conversationId | role | content | pushName | timestamp`

## Google Calendar

- **Credencial n8n:** `Google Calendar - Paulo` (ID: `QGp1FxkKTfYhYYJ0`)
- **Calendário:** `primary` (ph.nunan@gmail.com)
- **Duração de cada reunião:** 30 minutos
- **Proteção contra sobreposição:** freeBusy API bloqueia automaticamente

## Fluxo do Agente

```
WhatsApp Trigger → Extrair Dados → É Paulo? (IF)
   ├── Paulo (dono): Buscar Sessao → [menu / Bruno / Ana]
   └── Lead: Buscar Histórico (Sheets)
         ↓
   Buscar Disponibilidade (Google Calendar freeBusy)
         ↓
   Formatar Slots (horários livres até 22h, sem domingos)
         ↓
   Buscar Reuniões (Google Calendar events do mês — para modo dono)
         ↓
   Montar Contexto (detecta Paulo vs lead; injeta reuniões se perguntado)
         ↓
   OpenAI GPT-4o-mini → Delay 5s → Preparar Resposta
         ↓
   Salvar no Sheets → Enviar WhatsApp
   ├── Detectar Agendamento (IF)?
   │   ├── SIM: Extrair Info → Criar Evento (Meet) → Enviar Link Meet
   │   └── NÃO: fim
   └── CRM: Extrair Perfil → Formatar → Salvar Lead (paralelo)
```

### Modo Dono (Paulo)

Quando Paulo (`556181292879`) mensageia, a Ana age como **assistente executiva** (não vendedora):
- Detecta se a mensagem é sobre reuniões/agenda via regex
- Se sim: injeta `<dados_reunioes>` com contagem do mês, realizadas e próximas
- Se não: responde diretamente sem dados de calendário

## Estrutura da Pasta

```
n8n-AgenteAtendimento-Ana/
├── README.md                              # Este arquivo
├── docs/
│   ├── guia-configuracao.md               # Setup completo passo a passo
│   ├── system-prompt.md                   # System prompt editável da Ana
│   ├── analise-sessao-2026-03-16.md       # Implementação inicial — 14 erros e soluções
│   └── analise-sessao-2026-03-19.md       # Modo dono + fix relatório de reuniões
└── workflows/
    └── scala-whatsapp-ai-agent.json       # JSON completo do workflow n8n (sincronizado)
```

## Documentação

- Setup completo: [`docs/guia-configuracao.md`](docs/guia-configuracao.md)
- System prompt editável: [`docs/system-prompt.md`](docs/system-prompt.md)
- Implementação inicial (2026-03-16): [`docs/analise-sessao-2026-03-16.md`](docs/analise-sessao-2026-03-16.md)
- **Modo dono + fix reuniões (2026-03-19):** [`docs/analise-sessao-2026-03-19.md`](docs/analise-sessao-2026-03-19.md)

## Credenciais no n8n

| Credencial | Tipo | Usada em |
|---|---|---|
| WhatsApp OAuth account | WhatsApp Trigger API | Trigger (receber mensagens) |
| WhatsApp account | WhatsApp API | Enviar respostas e link Meet |
| scala-agent | OpenAI API | GPT-4o-mini |
| Google Sheets - Paulo | Google Sheets OAuth2 | Histórico de conversas |
| Google Calendar - Paulo | Google Calendar OAuth2 | Disponibilidade + criar eventos |

## Observações Técnicas Importantes

- **`require('luxon')` é bloqueado** nesta versão do n8n (task runner separado). Todos os Code nodes usam `Date` nativo.
- **`alwaysOutputData`** deve ser propriedade do node, NÃO de `parameters.options`.
- **Phone Number ID** vai no parâmetro do node WhatsApp, não na credencial.
- A lógica de disponibilidade injeta os **períodos ocupados** (não os livres) para Ana não entrar em loop.
- **Code node com múltiplos inputs:** n8n executa o código uma vez por branch — nunca faz merge. Sempre linearizar para 1 input quando precisar de dados de múltiplos nodes.
- **`const` no escopo raiz do Code node:** o task runner reutiliza o contexto de VM. Sempre usar IIFE: `return (() => { ... })();`
- **`e.start.dateTime` do Google Calendar é string:** `new Date(dateString)` parseia corretamente (já tem timezone). NÃO subtrair números de strings de data (`string - number = NaN`).
- **`updateNode` no `n8n_update_partial_workflow`:** usa `{ nodeName, updates: { "parameters.jsCode": "..." } }` com dot notation. Não usar `changes`.
