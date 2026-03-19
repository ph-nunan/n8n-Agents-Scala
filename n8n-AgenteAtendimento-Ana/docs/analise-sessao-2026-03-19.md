# Análise Completa — Sessão 2026-03-19
**Agente:** Ana — WhatsApp AI Agent 24/7
**Workflow ID:** `EVbZX91iB5moD6I4`
**Autor:** Paulo Nunan + Claude Sonnet 4.6

---

## Contexto

Após a implementação inicial do agente Ana (documentada em `analise-sessao-2026-03-16.md`), esta sessão focou em duas frentes:

1. **Modo dono (Paulo):** implementar comportamento diferenciado quando Paulo (dono da empresa) envia mensagem, incluindo consulta à agenda do Google Calendar
2. **Correção definitiva do relatório de reuniões:** resolver por que o `<dados_reunioes>` sempre mostrava "Não foi possível carregar" mesmo quando o Calendar retornava dados corretos

---

## O Que Foi Construído / Modificado

### 1. Modo Dono para Paulo

**Objetivo:** quando Paulo mensagem (número `556181292879`), a Ana age como assistente executiva — não como vendedora. Pode consultar agenda, reuniões, métricas.

**Implementação no "Montar Contexto":**
- `const isPaulo = phoneNumber === '556181292879'`
- Se `isPaulo = true` → usa system prompt `<modo_dono>` (assistente executiva)
- Se `isPaulo = false` → usa system prompt de atendimento de leads (persona consultora de vendas)
- Detecção de intenção: `askingAboutMeetings` — regex sobre a mensagem para só injetar dados de reunião quando Paulo pergunta explicitamente

### 2. Adição do Node "Buscar Reuniões"

**Objetivo:** buscar todos os eventos do Google Calendar do mês atual para que Ana possa responder quantas reuniões foram realizadas.

**Node criado:** `Buscar Reuniões` (HTTP Request)
- Endpoint: `GET https://www.googleapis.com/calendar/v3/calendars/primary/events`
- Parâmetros: `timeMin` (início do mês), `timeMax` (fim do mês), `singleEvents=true`, `orderBy=startTime`
- Credencial: `Google Calendar - Paulo` (OAuth2)
- Posição na cadeia: após `Formatar Slots`, antes de `Montar Contexto`

### 3. Linearização da Cadeia de Nodes

**Problema:** a cadeia original tinha `Montar Contexto` com 2 inputs (Formatar Slots + Buscar Reuniões). Em n8n, um Code node com 2 inputs executa o código **uma vez por branch**, de forma independente. `$input.all()` só retorna os items do branch atual — nunca faz merge automático dos dois.

**Solução:** linearizar a cadeia para que `Montar Contexto` tenha exatamente 1 input:

```
ANTES (errado):
Buscar Disponibilidade → Formatar Slots ─────────────┐
                                                      ├→ Montar Contexto
Buscar Disponibilidade → Buscar Reuniões ─────────────┘
(2 inputs = código executa 2x independentemente)

DEPOIS (correto):
Buscar Disponibilidade → Formatar Slots → Buscar Reuniões → Montar Contexto
(1 input = $input.first().json = calendar#events da Buscar Reuniões)
```

**Como acessar dados dos nodes anteriores com 1 input:**
- `$input.first().json` → dados de `Buscar Reuniões` (calendar#events com items[])
- `$('Formatar Slots').first().json` → slots de disponibilidade (referência direta ao node)
- `$('Buscar Histórico').all()` → histórico de conversas

---

## Erros Encontrados e Soluções

### Erro 1 — SyntaxError: Identifier 'messageText' has already been declared

**Problema:** n8n usa um task runner (JsTaskRunner) que reutiliza o contexto de VM entre execuções. Ao usar `const` no escopo raiz de um Code node, a variável persiste na VM. Na próxima execução do mesmo node, o `const` tenta redeclarar → `SyntaxError`.

**Fix:** envolver todo o código num IIFE (Immediately Invoked Function Expression):

```javascript
// ERRADO — const no escopo raiz persiste na VM:
const messageText = ...;
return [...];

// CORRETO — IIFE isola o escopo:
return (() => {
  const messageText = ...;
  return [...];
})();
```

---

### Erro 2 — `n8n_update_partial_workflow` removeConnection falhando

**Problema:** ao tentar remover conexão individual de um node com múltiplos outputs via `removeConnection`, a ferramenta retornava "No connections found from 'Buscar Disponibilidade'".

**Fix:** usar `n8n_update_full_workflow` para reescrever as conexões inteiras do workflow de forma atômica, eliminando a ambiguidade.

**Aprendizado:** `removeConnection` e `addConnection` são frágeis quando o node tem múltiplos outputs. Para reestruturações maiores, preferir `replaceConnections` ou reescrita completa das conexões.

---

### Erro 3 — Calendar retornava 0 eventos apesar de dados corretos

**Problema:** `Montar Contexto` tinha 2 inputs (Formatar Slots + Buscar Reuniões). Como n8n executa o código por branch, quando o branch do `Formatar Slots` chegava primeiro (rápido, ~17ms), o código executava com `$input.all()` contendo apenas os slots — sem os dados do Calendar. Quando o branch do `Buscar Reuniões` chegava (~300ms depois), o código executava novamente mas não encontrava `kind: 'calendar#events'` porque estava processando o segundo branch separadamente.

**Fix:** linearizar a cadeia (ver seção acima). Com 1 único input vindo de `Buscar Reuniões`, o `$input.first().json` é sempre `calendar#events`.

---

### Erro 4 — `<dados_reunioes>` sempre mostrava "Não foi possível carregar" (bug crítico da data)

**Problema:** mesmo após linearizar, o catch block continuava sendo ativado. A causa raiz estava na função `getEventDate`:

```javascript
// CÓDIGO ANTIGO (buggy):
const getEventDate = (e) => new Date(e.start.dateTime - 3 * 60 * 60 * 1000).toISOString().split('T')[0];
//                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//                                   PROBLEMA: e.start.dateTime é string!
//                                   "2026-03-17T08:00:00-03:00" - 10800000 = NaN
//                                   new Date(NaN).toISOString() → throws TypeError
//                                   → catch captura → fallback "Não foi possível carregar"
```

`e.start.dateTime` é uma string ISO com timezone (ex: `"2026-03-17T08:00:00-03:00"`). Em JavaScript, `string - number = NaN`. `new Date(NaN).toISOString()` lança `TypeError: Invalid time value`. O catch capturava esse erro silenciosamente e exibia a mensagem de fallback.

**Fix:**

```javascript
// CÓDIGO CORRETO:
const toDate = (e) => new Date(e.start.dateTime);
// new Date("2026-03-17T08:00:00-03:00") → parseia corretamente (timezone já está na string)
// Não precisa subtrair horas — o JavaScript já lida com o offset -03:00
```

**Resultado após o fix:**

> *"Tivemos 3 reuniões esse mês. Destas, 2 já foram realizadas e 1 está agendada para o dia 23/03 às 21:00."*

---

## Arquitetura Final do Workflow (32 nodes)

```
ROTEAMENTO (Paulo vs Lead):
WhatsApp Trigger → Extrair Dados → É Paulo? (IF)
    │                                   │
    │ true (Paulo)                       │ false (lead)
    ▼                                   ▼
Buscar Sessao                     Buscar Histórico ──────────────────┐
    ↓                                                                  │
IF Resetar Menu                                                        │
    ├── sim → Limpar Sessao → Enviar Menu                             │
    └── não → IF Tem Sessao                                           │
                  ├── sim → Route by Session                          │
                  │              ├── Bruno → Chamar Bruno             │
                  │              └── Ana ──────────────────────────→ Buscar Histórico
                  └── não → Switch Agente                             │
                                 ├── Bruno → Salvar Sessao Bruno →  Chamar Bruno
                                 ├── Ana   → Salvar Sessao Ana ──→ Buscar Histórico
                                 └── menu  → Enviar Menu            │
                                                                      │
FLUXO ANA (todos os caminhos chegam aqui):                           ▼
                                              Buscar Disponibilidade (Google Calendar freeBusy)
                                                      ↓
                                              Formatar Slots (Code — lista horários livres)
                                                      ↓
                                              Buscar Reuniões (Google Calendar events do mês)
                                                      ↓
                                              Montar Contexto (Code — detecta Paulo, injeta reuniões se perguntado)
                                                      ↓
                                              OpenAI GPT-4o-mini
                                                      ↓
                                              Delay Humano (5s)
                                                      ↓
                                              Preparar Resposta
                                                      ↓
                                    ┌─────── Salvar Mensagem User ────────┐
                                    │         Salvar Resposta Assistente  │
                                    │                  ↓                  │
                                    │         Enviar Resposta WhatsApp    │ CRM Preparar Request
                                    │                  ↓                  │ CRM Extrair Perfil
                                    │         Detectar Agendamento (IF)   │ CRM Formatar Lead
                                    │         ├── sim: Extrair → Criar    │ CRM Salvar Lead
                                    │         │   Evento → Enviar Meet    └──────────────────
                                    │         └── não: fim
                                    └─────────────────────────────────────────────────────────
```

---

## Comportamento do Modo Dono (Paulo)

Quando `phoneNumber === '556181292879'`:

| Paulo pergunta sobre | Comportamento da Ana |
|---|---|
| Reuniões / agenda | Injeta `<dados_reunioes>` com contagem, realizadas e próximas do mês |
| Qualquer outra coisa | Responde diretamente como assistente executiva, sem dados de calendário |
| Leads / clientes | Responde com informações disponíveis no contexto |

**Detecção de intenção (regex):**
```
/reuni[aã]o?s?|agenda|diagn[oó]stico|marcamos|agendamos|agendou|marcou|hor[aá]rios?|quan(tos?|tas?)|hoje|semana|m[eê]s/i
```

---

## Aprendizados Técnicos

### n8n — Comportamentos críticos descobertos

| Comportamento | Detalhe |
|---|---|
| Code node com múltiplos inputs | O código executa **uma vez por input branch**, de forma independente. `$input.all()` NÃO faz merge automático. Solução: linearizar para 1 input. |
| Task runner e `const` no escopo raiz | O JsTaskRunner reutiliza o contexto de VM entre execuções. `const` no topo → `SyntaxError: already declared` na 2ª execução. Sempre usar IIFE. |
| `n8n_update_partial_workflow` format | A operação `updateNode` usa `{ type, nodeName, updates: { "parameters.jsCode": "..." } }` com dot notation. Não usar `changes`. |
| `$('NodeName')` | Funciona para referenciar qualquer node que rodou na mesma execução, independente da topologia de conexões. Útil para acessar dados "de trás" na cadeia linearizada. |

### JavaScript — Armadilha de tipo com datas

```javascript
// ARMADILHA:
const dateStr = "2026-03-17T08:00:00-03:00";
const date = new Date(dateStr - 3600000); // dateStr - number = NaN → Invalid Date

// CORRETO — dateTime ISO já tem timezone offset:
const date = new Date(dateStr); // parseia corretamente
```

---

## Estado Final (2026-03-19)

| Componente | Status |
|---|---|
| Atendimento de leads (Ana) | ✅ Funcionando |
| Modo dono (Paulo) | ✅ Funcionando |
| Relatório de reuniões do mês | ✅ Funcionando — retorna contagem, realizadas e próximas |
| Agendamento via Google Meet | ✅ Funcionando |
| CRM (extração de dados do lead) | ✅ Funcionando |
| Roteamento Ana ↔ Bruno | ✅ Funcionando |
| Workflow ativo em produção | ✅ `n8n.paulonunan.com` |

---

*Documento gerado em 19/03/2026 — Sessão Paulo Nunan + Claude Sonnet 4.6*
