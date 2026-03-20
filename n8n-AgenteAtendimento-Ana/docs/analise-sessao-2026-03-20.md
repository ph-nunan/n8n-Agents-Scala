# Análise de Sessão — 2026-03-20
**Agente:** Ana — WhatsApp AI Agent 24/7
**Workflow ID:** `EVbZX91iB5moD6I4`

---

## Contexto

Sessão focada em debug: após adicionar o menu de seleção de agentes (Ana/Bruno) e o sistema de sessão, Ana parou de responder consultas de agenda. Dois bugs distintos foram identificados e corrigidos.

---

## Bugs Encontrados e Corrigidos

### Bug 1 — Aba `Sessoes` com erro 500 do Google Sheets (falso positivo)

**Sintoma:** execuções do workflow com erro no nó `Buscar Sessao`:
```
NodeApiError: The service was not able to process your request
500 - {"error":{"code":500,"message":"Internal error encountered.","status":"INTERNAL"}}
```

**Diagnóstico inicial:** erro 500 do Google Sheets ao tentar ler a aba `Sessoes`. Suspeitou-se que a aba não existia.

**Diagnóstico real:** a aba `Sessoes` já existia na planilha (`1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U`) e já tinha dados gravados (`phone: 556181292879, agent: Ana`). O erro 500 foi **transitório** do lado do Google Sheets API — se resolveu sozinho.

**Estrutura da aba Sessoes (confirmada em produção):**
| Coluna | Valor exemplo |
|--------|--------------|
| `phone` | `556181292879` |
| `agent` | `Ana` ou `Bruno` (vazio = sem sessão) |
| `updated_at` | `2026-03-20T01:19:20.771Z` |

**Função da aba:** persiste qual agente Paulo escolheu (Ana ou Bruno) para que mensagens subsequentes sejam roteadas diretamente, sem precisar passar pelo menu novamente. `Limpar Sessao` zera o campo `agent` quando Paulo digita "menu".

---

### Bug 2 — `Montar Contexto` ignorando dados do Calendar (bug crítico)

**Sintoma:** Ana respondia "Não tenho os dados da agenda disponíveis no momento" mesmo quando o Google Calendar retornava os dados corretamente.

**Diagnóstico via execução 802 (sucesso):**
- `Buscar Reuniões` → SUCCESS, retornou 3 eventos (`calendar#events`)
- `Montar Contexto` → SUCCESS, mas `<dados_reunioes>` continha a mensagem de erro

**Root cause — exceção silenciosa no try/catch:**

O código de `Montar Contexto` tinha a seguinte função:

```javascript
// BUGADO — subtrai número de string de data:
const getEventDate = (e) => new Date(e.start.dateTime - 3 * 60 * 60 * 1000).toISOString().split('T')[0];
//                                    ^^^^^^^^^^^^^^^^^
//                                    string ISO - number = NaN
//                                    new Date(NaN).toISOString() → lança RangeError
```

`e.start.dateTime` é uma string como `"2026-03-17T08:00:00-03:00"`. Subtrair um número de uma string em JavaScript resulta em `NaN`. `new Date(NaN)` é uma data inválida. Chamar `.toISOString()` em uma data inválida lança `RangeError: Invalid time value`.

Esse erro era capturado pelo `catch` que então escrevia `"Não foi possível carregar os dados da agenda neste momento."` — mascarando completamente o problema.

**Fix aplicado:**

```javascript
// CORRETO — usa .getTime() do objeto Date já parseado:
const getEventDate = (e) => new Date(getEventDateTime(e).getTime() - 3 * 60 * 60 * 1000).toISOString().split('T')[0];
//                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//                                    getEventDateTime() retorna Date válido
//                                    .getTime() retorna número (timestamp ms)
//                                    Date(number) funciona corretamente
```

---

### Bug 3 — Referência de nó sem acento quebra execução

**Sintoma:** após o fix do Bug 2, nova exceção no `Montar Contexto`:
```
Error: Referenced node doesn't exist
TypeError: Cannot assign to read only property 'name' of object 'Error: Referenced node doesn't exist'
```

**Root cause:** ao reescrever o código do nó para corrigir o Bug 2, os acentos foram removidos dos textos para evitar problemas de encoding. Porém, a referência ao nó `$('Buscar Histórico')` teve o acento removido acidentalmente:

```javascript
// ERRADO — nó não existe com este nome:
const allRows = $('Buscar Historico').all();

// CORRETO — nome exato do nó no workflow:
const allRows = $('Buscar Histórico').all();
//                          ^
//                          acento 'ó' obrigatório — deve bater exatamente com o nome do nó
```

**Fix aplicado:** restaurar o acento no nome do nó usando escape Unicode `\u00f3` para garantir encoding correto no JSON da API:

```javascript
const allRows = $('Buscar Hist\u00f3rico').all();
```

**Regra geral:** `$('NomeDoNo')` em n8n é case-sensitive e acento-sensitive. O nome deve ser **idêntico** ao nome configurado no nó.

---

## Resultado Final

Após os 3 fixes, Ana respondeu corretamente:

> *"Tivemos um total de 3 reuniões este mês. Destas, 2 já foram realizadas e 1 está programada para o dia 23/03 às 21:00."*

Dados que o Calendar retornou (validados):
- Diagnóstico Gratuito Scala - Paulo Nunan → 17/03 08:00 (realizada)
- Diagnóstico Gratuito Scala - Iago → 17/03 08:30 (realizada)
- Diagnóstico Gratuito Scala - Paulo Nunan → 23/03 21:00 (futura)

---

## Aprendizados Técnicos

| Problema | Causa | Solução |
|----------|-------|---------|
| `string - number = NaN` | JS não converte string ISO para number automaticamente | Usar `new Date(str).getTime()` para obter timestamp numérico |
| `new Date(NaN).toISOString()` lança exceção | Date inválida não tem representação ISO | Sempre parsear a string primeiro com `new Date(str)` |
| `catch` mascarando bugs | O erro era capturado silenciosamente e substituído por mensagem genérica | Logar `err.message` no catch para diagnóstico: `'Erro: ' + err.message` |
| `$('Nome')` exige nome exato | n8n resolve referências de nó por nome literal | Usar `\uXXXX` escape ou manter acentos exatos |
| Erro 500 transitório do Google Sheets | Instabilidade momentânea da API | Não tratar como erro estrutural — verificar se persiste antes de corrigir |

---

## Estado do Workflow (2026-03-20)

| Componente | Status |
|---|---|
| Atendimento de leads (Ana) | ✅ |
| Modo dono (Paulo) | ✅ |
| Relatório de reuniões do mês | ✅ Corrigido nesta sessão |
| Menu de seleção Ana/Bruno | ✅ |
| Sistema de sessão (aba Sessoes) | ✅ |
| Roteamento para Bruno | ✅ |
| Agendamento Google Calendar | ✅ |
| Workflow ativo em produção | ✅ `n8n.paulonunan.com` |
