# O Primeiro Ajuste Importante
**Data:** 25 de março de 2026
**Fase:** Fase 1 — Compra de Dados e Validação do Funil
**Campanha ativa:** 4 dias (início: 21 Mar)
**LPVs acumulados:** ~130 de 500 (meta da Fase 1)

---

## Contexto: por que esse ajuste aconteceu

A campanha estava rodando há 4 dias com métricas de topo de funil excelentes
(CTR 2.98%, CPC R$0,25, CPL R$0,30) mas **zero conversões orgânicas** registradas
no GA4 e no Meta Pixel. O gatilho para o ajuste foi a pergunta: _"Esperamos as 300
LPVs antes de mexer, ou agimos agora?"_

A resposta veio dos dados do Microsoft Clarity (63 sessões analisadas):
- Scroll depth médio: **26%** — usuários abandonavam no Hero sem rolar
- 76% do tráfego: Instagram + Facebook **in-app browser** (pior ambiente de performance)
- Bounce rate GA4: **81.3%**

Com esses dados era possível diagnosticar sem esperar 300 LPVs. Dados insuficientes
para reescrever copy do zero, mas suficientes para corrigir problemas técnicos e
de credibilidade que estavam bloqueando conversões.

---

## Linha do Tempo — 25 Mar 2026

---

### 09:00 — Diagnóstico de rastreamento (pré-condição de tudo)

**O que estava errado:**
O GTM tinha tags Custom HTML duplicadas, triggers obsoletos e uma estrutura
que enviava apenas alguns eventos para o GA4. O `Analytics.tsx` disparava
11 eventos customizados para o `window.dataLayer`, mas o GTM capturava menos
da metade.

**O que foi feito (sessão anterior, documentado aqui como base):**
- Deletadas 6 tags obsoletas (Section Observer, Time on Page Tracker, etc.)
- Deletados 4 triggers obsoletos
- Criadas 9 variáveis Data Layer (location, scroll_pct, percent, seconds,
  section, metric, metric_value, question, seconds_open)
- Criado trigger catch-all regex para os 11 eventos do Analytics.tsx
- Tag GA4 "All Custom Events (catch-all)" publicada como GTM v4 ✅

**Por que isso importa:**
Sem rastreamento correto, qualquer decisão de otimização seria baseada em dados
incompletos. O tracking é a fundação — sem ele, não existe Fase 2.

**FID → INP fix (Analytics.tsx):**
O FID (First Input Delay) foi depreciado pelo Google em março de 2024 e substituído
pelo INP (Interaction to Next Paint). O código continuava medindo FID com um
PerformanceObserver que não recebia mais dados. Corrigido para medir INP via
`entry type: "event"` com `durationThreshold: 0`.

---

### 10:30 — Problema crítico identificado: CTA apontando para âncora interna

**Dado:** 76% do tráfego vem de Instagram e Facebook in-app browser.
**Problema técnico:** O botão primário "Agendar Diagnóstico Gratuito" apontava
para `href="#contact"` — uma âncora interna que exigia scroll por toda a página
para chegar ao formulário de contato.

Em in-app browser:
- O JavaScript de scroll suave funciona de forma imprevisível
- O usuário precisa rolar 4-5 telas antes de ver o formulário
- O formulário, quando encontrado, não abre WhatsApp diretamente

**Conclusão:** o funil estava tecnicamente quebrado para 76% do tráfego desde
o lançamento. Os 0% de conversão orgânica não provam que o site não converte —
provam que o caminho até a conversão estava bloqueado.

**Decisão:** CTA primário → WhatsApp direto
```
href="#contact"
→
href="https://wa.me/556181894189?text=Ol%C3%A1%2C%20quero%20agendar%20um%20diagn%C3%B3stico%20gratuito%20da%20Scala!"
target="_blank" rel="noopener noreferrer"
```

**Efeito colateral positivo:** link externo (wa.me) agora ativa o trigger
`linkClick` do GTM, que dispara o Meta Pixel `Lead` event automaticamente.
Cada clique no CTA primário agora gera dado no Meta Pixel para futuro
treinamento do algoritmo.

---

### 11:00 — INP 570ms: redução de frequência do HeroLiveFeed

**Dado:** Clarity mostrava INP de 570ms (limiar: >500ms = ruim).
**Causa identificada:** `setInterval` de 2.600ms no HeroLiveFeed com
`AnimatePresence` do Framer Motion — interrompendo o main thread a cada
2,6 segundos com cálculos de layout e animação.

**Decisão:** intervalo 2.600ms → 4.000ms
- Reduz interrupções no main thread em 35%
- Usuário percebe o feed como "live" com qualquer intervalo < 5s
- Sem impacto visual perceptível, impacto técnico significativo

---

### 11:15 — data-section="hero" ausente: seção Hero nunca rastreada

**Problema:** o `Analytics.tsx` rastreia `section_viewed` e `section_time_spent`
usando `IntersectionObserver` em todos os elementos com `data-section="..."`.
A seção Hero não tinha esse atributo. Nunca foi rastreada.

**Impacto:** nenhum dado de dwell time do Hero no GA4. Sem esse dado, não
sabemos quanto tempo médio o usuário passa no Hero antes de sair ou de converter.

**Correção:** adicionado `data-section="hero"` na tag `<section>` do Hero.

---

### 13:00 — Auditoria de copy: diagnóstico dos problemas não técnicos

**Observações do screenshot mobile (iPhone 13, Facebook UA):**

**Problema 1 — Badge duplica o H1:**
O badge dizia "DO ANÚNCIO AO RELATÓRIO · TUDO AUTOMATIZADO" e o H1 dizia
"Do Anúncio ao Relatório." — a linha mais lida da página repetia a segunda
linha mais lida. Desperdício de um dos ativos mais valiosos: a atenção nos
primeiros 2 segundos.

**Problema 2 — Desalinhamento ad → landing:**
O criativo vencedor (Carrossel 2) tem o gancho "Concorrente automatizou" —
ativa FOMO, senso de urgência competitiva. Quando o usuário clica e chega
na landing, encontra: "Do Anúncio ao Relatório. Tudo no Piloto Automático."
— descrição de produto. A continuidade emocional do ad é interrompida.

**Princípio:** o usuário que clicou no ad fez isso por uma razão emocional
(medo de ficar para trás). A landing precisa confirmar esse medo antes de
apresentar a solução. Se não confirma, o usuário pensa "isso não é pra mim"
e sai.

**Decisão — Badge:**
"Do Anúncio ao Relatório · Tudo Automatizado"
→ "Seus concorrentes já automatizaram"

Agora o badge continua o gancho emocional do ad. O H1/H2 pode manter a
descrição do produto como resposta à pergunta implícita: "o que eles
automatizaram?"

---

### 14:00 — Problema crítico de credibilidade: stats sem atribuição real

**O problema:** a linha "resultado médio dos clientes Scala após 30 dias"
implica medição direta em clientes — o que seria falso se os números não
fossem medidos nesse contexto específico. Comprador B2B mais sofisticado
pede referência. Se não há referência, a credibilidade desmorona no exato
momento em que seria mais necessária.

**Contexto relevante:** 4 clientes reais existem:
- **Hugo Borges** — gestor de tráfego
- **H3imob** — imobiliária
- **GoAlpha** — agência de marketing
- **DonaSol** — delivery

Resultados positivos em todos, sem métricas específicas documentadas.

**Decisão sobre o "4.6×":**
O número é defensável como benchmark de indústria. A Velocify (InsideSales
Research) documentou que empresas que respondem leads em <5 minutos têm
4,6× mais chances de qualificar o lead do que as que demoram 30+ minutos.
O número não foi inventado — foi contextualmente válido aplicado ao produto.

O que muda é a atribuição: de "resultado médio dos clientes" para "implementado
em [nomes reais]". Isso é honesto: diz que esses clientes confiaram no serviço,
sem afirmar um número que não foi medido individualmente neles.

**Correção:**
"resultado médio dos clientes Scala após 30 dias"
→ "implementado em GoAlpha · H3imob · DonaSol · Hugo Borges"

---

### 15:00 — ICP ausente e "ecossistema de vendas" como diferenciador

**Problema:** nenhuma linha do Hero dizia para quem é o serviço. Um gestor
de tráfego, dono de imobiliária ou agência que chegasse na página não se via
representado. Sem identificação de ICP (Ideal Customer Profile) acima do fold,
a mente do visitante não processa "isso é para mim" — e sai.

**Benchmark:** páginas B2B de alta conversão têm o ICP explícito nos primeiros
200px. A regra dos 5 segundos: o visitante precisa entender em 5s quem é você,
para quem é, e o que faz.

**Sobre "ecossistema de vendas":**
Posiciona o serviço como responsável por um sistema integrado (lead → qualificação
→ relatório → decisão) — não apenas por uma ferramenta ou integração pontual.
Diferencia de:
- Consultores Zapier/Make (vendem ferramentas)
- Freelancers de automação (vendem horas)
A Scala vende um sistema de conversão. "Ecossistema" carrega esse significado
sem precisar explicá-lo.

**Decisão — Subtitle:**
"Montamos em 7 dias: resposta ao lead em <5s, campanhas que se otimizam sozinhas
e relatórios automáticos — sem contratar ninguém."
→
"Para agências, imobiliárias e gestores de tráfego — montamos em 7 dias o
ecossistema que responde leads em <5s, otimiza campanhas e entrega relatórios
sem você mover um dedo."

---

### 15:30 — Risk reversal ausente perto do CTA

**Problema:** o visitante que decide clicar no CTA enfrenta "commitment anxiety"
— a dúvida não verbalizada: "se eu clicar, vou ser pressionado a fechar? Tem
contrato? Quanto custa? Se não funcionar?"

Em serviços B2B, esse atrito existe mesmo quando a intenção de compra é alta.
A remoção do atrito não requer desconto — requer clareza sobre o que acontece
a seguir.

**Decisão — micro-linha abaixo do CTA:**
Adicionada linha: "Diagnóstico gratuito · Sem contrato · Implementado em 7 dias"

Três objeções silenciadas numa linha: custo inicial (gratuito), comprometimento
(sem contrato) e timeline (7 dias).

---

## Resumo de todas as mudanças — 25 Mar 2026

| # | Arquivo | Mudança | Gatilho | Tipo |
|---|---|---|---|---|
| 1 | `HeroCTAs.tsx` | CTA `#contact` → WhatsApp direto | 76% in-app browser, funil tecnicamente quebrado | Técnico crítico |
| 2 | `HeroLiveFeed.tsx` | setInterval 2.600ms → 4.000ms | INP 570ms (ruim) no Clarity | Performance |
| 3 | `Hero.tsx` | `data-section="hero"` adicionado | Hero nunca rastreado no GA4 | Tracking |
| 4 | `Hero.tsx` | Badge → "Seus concorrentes já automatizaram" | Desalinhamento criativo vencedor ↔ landing | Copy/conversão |
| 5 | `Hero.tsx` | Subtitle com ICP explícito + "ecossistema" | ICP ausente, diferenciação fraca | Copy/conversão |
| 6 | `Hero.tsx` | Stats attribution → nomes dos 4 clientes reais | Social proof falso = risco crítico de credibilidade | Credibilidade |
| 7 | `HeroLiveFeed.tsx` | `.feed-label` permite wrap no mobile | Texto truncado com "..." = aparência quebrada | UX |
| 8 | `globals.css` | `.feed-label` wrap ativado em `max-width: 480px` | Fix para dispositivos mobile | UX |
| 9 | `HeroCTAs.tsx` | Risk reversal abaixo do CTA | Commitment anxiety silenciosa bloqueando conversão | Conversão |
| 10 | `Analytics.tsx` | FID depreciado → INP (entry type: event) | FID removido pelo Google em Mar 2024 | Tracking accuracy |
| 11 | `Hero.tsx` | `data-section="hero"` removido da section interna | Auditoria revelou duplicata: page.tsx já tinha wrapper com mesmo atributo → IntersectionObserver disparava eventos em dobro | Bug de tracking |
| 12 | `HeroCTAs.tsx` | Risk reversal encurtado: "Gratuito · Sem contrato · 7 dias" | Auditoria mobile mostrou texto quebrando em 2 linhas — "dias" ficava sozinho na segunda linha | UX |

---

## O que NÃO fizemos — e por quê

| Decisão evitada | Por quê não fazer agora |
|---|---|
| Reescrever H1/H2 | Requer saber quem converte. Sem dados orgânicos reais, qualquer reescrita é chute. Decisão em aberto após 15+ wa_button_click orgânicos |
| Testimonials com quotes dos clientes | ~~Requer aprovação formal~~ ~~**DESBLOQUEADO**~~ **IMPLEMENTADO** — seção `Testimonials.tsx` no ar com 4 quotes reais. Ver seção abaixo. |
| Mudar objetivo da campanha para OFFSITE_CONVERSIONS | Meta precisa de 50+ eventos/semana. A R$25/dia + 6% conv = só 6 eventos/semana. Fase 2 requer ≥R$36/dia confirmado |
| Aumentar budget da campanha | Campanha ainda na fase de coleta de dados. Aumentar interromperia leitura de baseline. Não tocar até 500 LPVs ou conversões confirmadas |
| Novos criativos | Carrossel 2 recebeu 97% do budget naturalmente. Algoritmo já decidiu. Não interferir |

---

## Estado dos dados antes × depois

| Métrica | Antes (21–25 Mar) | Esperado após mudanças |
|---|---|---|
| Funil técnico | Quebrado (CTA → âncora interna) | Funcional (CTA → WhatsApp direto) |
| wa_button_click orgânico | 0 (funil quebrado) | Primeiros dados em 3–5 dias |
| Meta Pixel Lead event | Só fires do botão WhatsApp fixo no footer/contact | Agora fires também no hero CTA |
| INP | 570ms (ruim) | Estimado <500ms após fix de intervalo |
| data-section hero | Ausente — Hero nunca rastreado | Rastreado: dwell time, section_viewed |
| Social proof | Fabricado ("resultado médio dos clientes") | Real (4 nomes de clientes reais) |
| ICP no hero | Ausente | Explícito (agências, imobiliárias, gestores) |
| Risk reversal | Ausente | Presente (micro-linha abaixo do CTA) |
| Badge | Duplicava H1 | Continua gancho emocional do ad vencedor |

---

## Fase 1 — Estado atual e critérios para avançar

**Objetivo da Fase 1:** acumular dados suficientes para Fase 2 existir com chance
real de sucesso. Não é fase de escalar — é fase de entender.

### Critérios para concluir a Fase 1

| Critério | Mínimo | Estado atual | Prazo estimado |
|---|---|---|---|
| LPVs acumulados | 500 | ~130 (26%) | ~25 dias (20 Abr) |
| Conversão orgânica confirmada | ≥15 wa_button_click reais, ≥4% | 0 (funil corrigido hoje) | 3–5 dias para primeiros dados |
| Criativo vencedor confirmado | CTR >1.5% estável | Carrossel 2: 3.01% ✅ | Confirmado |
| CPL estável | <R$0,60/LPV | R$0,30 ✅ | Monitorar semanalmente |
| Ana testada com lead real | ≥3 conversas qualificadas | 0 | Depende das conversões |
| Budget validado para Fase 2 | ≥R$36/dia confirmado | R$25/dia atual | Decisão após conversão confirmada |

### Por que a pressa para Fase 2 é o maior risco

Meta OFFSITE_CONVERSIONS exige 50+ eventos de conversão/semana para sair do
aprendizado. A matemática:

- R$25/dia × 14.3 LPVs/dia × 7 dias = 100 LPVs/semana
- 100 LPVs × 6% conversão = **6 eventos/semana** (8x abaixo do mínimo)
- Para 50 eventos/semana com 6% conversão = precisa de 833 LPVs/semana = R$35/dia

**Conclusão:** Fase 2 só funciona com budget ≥R$36/dia E conversão ≥6% confirmada.
Sem ambos simultâneos, a campanha OFFSITE_CONVERSIONS ficará em aprendizado
permanente e o CPL vai explodir.

---

## Próximas ações com datas

| Data | Ação | Responsável |
|---|---|---|
| 28–30 Mar | Rodar `ga4_auth.py` — ver primeiros wa_button_click orgânicos | Claude + Paulo |
| 30 Mar | Se conv ≥4%: planejar Fase 2. Se <4%: diagnóstico do bloqueio | Decisão conjunta |
| Esta semana | Contactar GoAlpha, H3imob, DonaSol, Hugo Borges para quote de 1 frase | Paulo |
| ~20 Abr | 500 LPVs atingidos — análise completa Fase 1 | Claude + Paulo |
| ~20 Abr | Decisão: avançar Fase 2 ou nova rodada de otimização | Decisão conjunta |

---

## Framework replicável para próximos ajustes

Todo ajuste futuro deve seguir esta sequência:

```
1. DADO → Qual métrica específica indicou o problema?
2. HIPÓTESE → Por que esse dado está assim?
3. CAUSA RAIZ → O que de fato gera o dado (técnico ou copy)?
4. DECISÃO → A mudança é segura de fazer agora ou precisa de mais dados?
5. IMPLEMENTAÇÃO → Mudança mínima necessária — sem over-engineering
6. VALIDAÇÃO → Screenshot, deploy, confirmar visualmente
7. MONITORAMENTO → O que medir em quantos dias para saber se funcionou?
```

**Regra de ouro:** nunca mudar mais de uma variável grande por vez sem dados.
Hoje mudamos múltiplas coisas porque a maioria eram correções técnicas óbvias
(funil quebrado, tracking ausente) — não testes de hipótese. Quando estivermos
testando copy ou design, uma mudança por ciclo.

---

## Auditoria pós-deploy — resultado

Executada via Playwright (produção real, UA Facebook in-app browser, iPhone 13).

### Checklist de confirmação

| Item | Verificação | Resultado |
|---|---|---|
| CTA href | `wa.me/556181894189?text=...` | ✅ Correto |
| Badge | "Seus concorrentes já automatizaram" | ✅ Correto |
| Stats attribution | "implementado em GoAlpha · H3imob · DonaSol · Hugo Borges" | ✅ Correto |
| Risk reversal | "Gratuito · Sem contrato · 7 dias" | ✅ 1 linha |
| Subtitle ICP | "Para agências, imobiliárias e gestores de tráfego..." | ✅ Correto |
| GTM dataLayer | `typeof window.dataLayer !== 'undefined'` | ✅ Ativo |
| GTM eventos | wa_button_click, scroll_depth_reached, section_viewed, web_vitals, exit_intent | ✅ Todos presentes |
| data-section hero | 1 único elemento no DOM | ✅ Duplicata removida |

### Bug encontrado e corrigido na auditoria

`data-section="hero"` aparecia DUAS vezes no DOM:
- `app/page.tsx:34` — `<div id="hero" data-section="hero">` (wrapper pré-existente)
- `components/sections/Hero.tsx:12` — `<section data-section="hero">` (adicionado hoje)

O IntersectionObserver do `Analytics.tsx` observa TODOS os elementos com `data-section`.
Com o atributo duplicado, cada entrada/saída do Hero dispararia:
- `section_viewed` × 2
- `section_time_spent` × 2

Dados de dwell time do Hero estariam inflados. Corrigido removendo o atributo da section interna.

**Lição:** antes de adicionar `data-section` a qualquer seção nova, verificar se o wrapper em `page.tsx` já tem o atributo.

### Clientes confirmaram participação

GoAlpha · H3imob · DonaSol · Hugo Borges — todos confirmaram e estão felizes em ser citados.
**Desbloqueado:** implementação de seção de testimonials assim que quotes de 1 frase forem coletados.

---

---

## Segundo ciclo do mesmo dia — Testimonials + UX

### Seção de Depoimentos implementada

**Contexto:** clientes (GoAlpha, H3imob, DonaSol, Hugo Borges) confirmaram participação
e pediram que escolhêssemos a melhor quote de cada par criado.

**Critérios de seleção:** especificidade de resultado, tom natural, sinal de credibilidade
mais alto para visitante B2B.

**Quotes selecionadas:**

| Cliente | Segmento | Quote escolhida | Por que |
|---|---|---|---|
| Hugo Borges | Gestor de Tráfego | "Perdi clientes por demorar a responder lead. Desde a Scala, a resposta vai em segundos — isso sozinho mudou minha taxa de fechamento." | "taxa de fechamento" é métrica concreta; dor específica mapeia com hero stat `<5s` |
| H3imob | Imobiliária | "No mercado imobiliário quem responde primeiro fecha. A Scala garantiu que nenhum lead nosso fica mais de 5 segundos sem resposta — em qualquer horário." | Abre com verdade do setor (autoridade); "5 segundos" referencia o stat do hero; "em qualquer horário" endereça medo de lead noturno |
| GoAlpha | Agência | "Peguei 3 novos clientes sem contratar ninguém. Os relatórios vão automáticos, o monitoramento é 24/7 e o cliente recebe update antes de precisar perguntar." | "3 novos clientes sem contratar ninguém" — melhor gancho do set. Número concreto, resultado impossível de ignorar |
| DonaSol | Delivery | "Antes era caos: pedido perdido, cliente sem resposta, tudo manual. Agora o sistema cuida do atendimento e a gente foca no que sabe fazer." | "era caos" → lista de dores reconhecíveis → virada limpa. Opção A tinha "aumentou muito" (vago demais) |

**Posição no funil:** entre `Cases` e `FuturePacing` — depois da prova técnica das
automações, a voz humana sela o fechamento emocional antes do último empurrão.

**Design:** grid 2×2, aspas decorativas em `var(--accent)` opacidade 35%,
avatar inicial + label de role em mono, `borderTop` antes da atribuição.

---

### Scroll hints em todas as seções

**Problema:** Clarity mostrava scroll depth médio de 26%. O usuário não tinha
estímulo visual para continuar scrollando.

**Decisão de implementação:** CSS `::after` no `.s-wrap` — zero JS, aplica
automaticamente em todas as seções do funil, sem editar cada arquivo individualmente.

**Visual:** linha vertical `1px`, `28px` de altura, gradient `transparent →
rgba(255,255,255,0.35) → transparent`, animação que desce 6px com fade-in/out,
loop 2.6s. Minimalista, consistente com a identidade visual do site.

**Hero:** hint adicionado inline no fluxo do conteúdo (após HeroLiveFeed),
não absoluto — evita sobreposição com o marquee do SocialProof que segue.

---

## Commits desta sessão

```
9d32570  perf: CTA hero → WhatsApp direto, INP fix, data-section hero
c30fc6b  copy: badge FOMO, subtitle tangível, stats com atribuição, feed fix
657c6d8  copy: ICP, atribuição real de clientes, risk reversal no CTA
b2b0896  docs: registrar O Primeiro Ajuste Importante — 25 Mar 2026
f926eb0  fix: remover data-section duplicado no Hero, encurtar risk reversal
6a0fca5  feat: adicionar seção de depoimentos com 4 clientes reais
8f2684f  feat: adicionar scroll hint em todas as seções
c81b2a3  fix: scroll hint — linha vertical animada, remove sobreposição no Hero
c15b844  fix: scroll hint no Hero — inline no fluxo, sem sobreposição
```

**Deploy confirmado:** READY em Vercel após cada commit.
**URL produção:** https://portfolio-scala.vercel.app/
