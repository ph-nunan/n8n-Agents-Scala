# Análise de Sessão — 2026-03-20 (Parte 2)
**Agente:** Ana — WhatsApp AI Agent 24/7
**Workflow ID:** `EVbZX91iB5moD6I4`
**Foco:** Transformação de Ana em consultora de vendas com SPIN Selling

---

## Contexto

Após corrigir os bugs da Parte 1 (Calendar + encoding), sessão focada em capacitar a Ana para fazer qualificação de leads e vendas consultivas em vez de simplesmente agendar reuniões. O ponto de partida era uma Ana que tentava agendar o diagnóstico logo na primeira mensagem — comportamento de chatbot.

**Mensagem de entrada do lead (via botão do site):**
> "Oi! Estou interessado, queria saber mais como funciona!"

---

## Problema Identificado

O system prompt anterior tinha Ana focada em:
1. Apresentar a empresa e serviços
2. Agendar o diagnóstico o mais rápido possível
3. Quebrar objeções de forma reativa

**Resultado:** Ana parecia um chatbot de agendamento, não uma consultora. Não qualificava o lead, não entendia a dor, não criava valor antes de propor o diagnóstico.

---

## Solução: SPIN Selling + Qualificação

### O que é SPIN Selling
Metodologia de vendas consultivas criada por Neil Rackham. Baseada em 4 tipos de perguntas que guiam o lead a reconhecer e articular sua própria necessidade:

| Fase | Objetivo | Exemplo |
|------|----------|---------|
| **S — Situação** | Entender o contexto atual | "Quanto você investe em ads por mês?" |
| **P — Problema** | Identificar a dor real | "Em quanto tempo vocês respondem um lead novo?" |
| **I — Implicação** | Fazer o lead calcular o impacto | "O que representa perder esses leads em reais?" |
| **N — Necessidade** | Lead articula o que quer | "Se respondesse em segundos, como mudaria seus fechamentos?" |

### Por que SPIN funciona no WhatsApp
- Uma pergunta por vez = conversa natural, não interrogatório
- O lead chega à conclusão por conta própria = menos resistência
- Cria valor antes de qualquer oferta = diagnóstico se torna desejável

---

## Novo System Prompt — Estrutura Completa

### Arquivo atualizado
`n8n-AgenteAtendimento-Ana/docs/system-prompt.md`

### Seções adicionadas/reescritas

#### `<missao>` — nova
Define explicitamente que o objetivo NÃO é fechar pelo WhatsApp, mas qualificar e tornar o diagnóstico inevitável.

#### `<spin_selling>` — nova
As 4 fases com exemplos de perguntas para cada fase. Ana usa como guia para conduzir a conversa progressivamente.

#### `<qualificacao>` — nova
Critérios de qualificação da Scala:
- Investimento em tráfego: R$3.000+/mês
- Volume de leads: 50+/mês
- Problema real (atendimento lento, perda de leads, sem escala)
- Tomador de decisão
- Não busca o mais barato

**Nível de consciência do lead:**
- BAIXO → mais perguntas S e P
- MÉDIO → aprofundar implicações
- ALTO → avançar para necessidade + diagnóstico

**Se não qualifica:** Ana diz honestamente que a Scala pode não ser o fit certo agora.

#### `<fluxo_ideal>` — nova
Guia de fluxo por estágio da conversa. Evita que Ana ofereça o diagnóstico na primeira mensagem.

#### `<tom_de_voz>` — reescrito completamente
12 regras, com destaque para:
- **UMA PERGUNTA POR VEZ** (regra mais importante)
- OUÇA E REFLITA antes de ir pra próxima pergunta
- NÃO MENCIONE PREÇOS até lead estar qualificado

#### `<objecoes>` — reescrito
5 objeções com respostas que redirecionam para perguntas, não para defesa da empresa:
- "É caro" → pergunta sobre investimento atual em tráfego
- "Já tentei chatbot" → diferencia IA conversacional de fluxo fixo
- "Preciso pensar" → diagnóstico facilita a conversa interna
- "Não tenho tempo" → 20 minutos, quando seria bom essa semana?
- "Já tenho solução" → pergunta sobre taxa de resposta atual

#### `<agendamento>` — atualizado
Posicionamento mudou de "diagnóstico gratuito" para "análise real da operação" — menos vendedor, mais consultivo.

---

## Parâmetros do Modelo Atualizados

| Parâmetro | Antes | Depois | Motivo |
|-----------|-------|--------|--------|
| `max_tokens` | 300 | 450 | Respostas consultivas precisam de mais espaço |
| `temperature` | 0.7 | 0.75 | Tom mais natural e variado |

---

## Comportamento Esperado Após a Mudança

**Conversa típica antes (❌):**
```
Lead: Oi! Estou interessado, queria saber mais como funciona!
Ana:  Oi! Sou a Ana da Scala. Trabalhamos com automação de atendimento,
      relatórios, CRM... Os planos começam em R$600/mês. Posso agendar
      um diagnóstico gratuito de 15 min? Tenho horário terça às 10h ou
      quarta às 14h.
```

**Conversa típica depois (✅):**
```
Lead: Oi! Estou interessado, queria saber mais como funciona!
Ana:  Oi! Que bom que você chegou aqui. Pra eu entender melhor o que
      faz sentido pra você — você trabalha com tráfego pago pro seu
      próprio negócio ou pra clientes?

Lead: Pro meu negócio, gestão de tráfego pra uma loja.
Ana:  Entendi. E como funciona o atendimento dos leads que chegam hoje?
      Tem alguém dedicado a isso ou você mesmo responde?

Lead: Eu mesmo respondo, mas às vezes demoro.
Ana:  Faz sentido, é difícil estar disponível 100% do tempo. Quando
      um lead chega fora do horário, o que acontece normalmente?

[... conversa continua até lead sentir a dor e pedir o diagnóstico ...]
```

---

## Estado do Workflow (2026-03-20 Parte 2)

| Componente | Status |
|---|---|
| Atendimento de leads — modo chatbot | ❌ Substituído |
| Atendimento de leads — SPIN Selling consultivo | ✅ Ativo |
| Qualificação por nível de consciência | ✅ |
| Fluxo de 4 fases SPIN | ✅ |
| 5 quebras de objeção | ✅ |
| Modo dono (Paulo) | ✅ Sem alteração |
| Relatório de reuniões | ✅ Sem alteração |
| Workflow ativo em produção | ✅ `n8n.paulonunan.com` |
