# Jornada Scala — Documento Mestre de Decisões

> **Propósito:** Este documento é o registro histórico completo da construção da Scala Automate.
> Cada versão do site, cada decisão estratégica, cada número real coletado em produção está aqui.
> Use como contexto antes de qualquer decisão relevante. Se algo mudou, atualize aqui.

**Última atualização:** 31 de março de 2026
**Versão atual do site:** v2 (v3 em construção)
**Versão atual da Ana:** SPIN v1.1 (workflow `mLM22h2JylSrhCRE`)

---

## Índice

1. [O Negócio — Scala Automate](#1-o-negócio)
2. [A Infraestrutura](#2-a-infraestrutura)
3. [Os Produtos](#3-os-produtos)
4. [Fase 1 — Campanha LPV (21 Mar – 30 Mar 2026)](#4-fase-1)
5. [V1 — O Site Original (cold traffic)](#5-v1)
6. [Os Dados Reais de 700+ LPVs](#6-os-dados-reais)
7. [A Grande Revelação — 0% de Conversão](#7-a-grande-revelação)
8. [O Pivot — De LPV para CTWA](#8-o-pivot)
9. [V2 — O Redesign para Lead Quente](#9-v2)
10. [Tracking — Arquitetura Atual](#10-tracking)
11. [Aprendizados — Princípios para Decisões Futuras](#11-aprendizados)
12. [Próximas Versões Planejadas](#12-próximas-versões)

---

## 1. O Negócio

### O que é a Scala Automate

Scala é um serviço de implementação de automação de atendimento e vendas para agências de marketing digital, gestores de tráfego pago e empresas que geram leads via Meta Ads. O produto central é um ecossistema de automação que conecta WhatsApp, IA, CRM e relatórios em um sistema que opera 24/7 sem equipe adicional.

**Fundador:** Paulo Nunan — 5 anos em marketing digital, 3 anos em programação, especialista em n8n e IA. Brasília, DF.

**Dor que resolve:**
> Gestores de tráfego geram centenas de leads por dia e perdem a maioria por falta de velocidade no atendimento. O problema nunca foi o tráfego. Era o que acontecia depois do clique.

### Modelo de Precificação

| Item | Valor | Observação |
|------|-------|------------|
| Setup (implementação) | R$ 1.500 | Taxa única |
| Recorrência mensal | R$ 400/mês | Escalar para R$ 600–800 após 3–4 meses com resultados |
| LTV 12 meses | R$ 6.300 | R$ 1.500 + 12 × R$ 400 |

### Funil de Conversão Projetado

```
Meta Ads (LPV ou CTWA)
  ↓  6% taxa de conversão meta
Clique no WhatsApp
  ↓  60% qualificados pela Ana (agente IA)
Leads qualificados
  ↓  70% agendam reunião de diagnóstico
Reunião de diagnóstico (30 min, gratuita)
  ↓  35% fechamento
Cliente fechado
```

**Projeção por ciclo de 500 LPVs (base: R$ 25/dia × ~20 dias = ~R$ 500):**
- 500 LPVs → 30 cliques WA → 18 qualificados → 13 reuniões → **4–5 clientes**
- Receita: R$ 6.000–7.500 setup + R$ 1.600–2.000/mês recorrência
- **ROI sobre ads: 23–29×**

### Ponto de Equilíbrio

2 clientes ativos cobrem o custo de ads:
- 2 × R$ 400 = R$ 800/mês > R$ 750/mês em ads (R$ 25/dia)

### Clientes Reais (em produção)

| Cliente | Segmento | Cidade |
|---------|----------|--------|
| Hugo Borges | Gestor de Tráfego | Brasília, DF |
| H3imob | Imobiliária | Goiânia, GO |
| GoAlpha | Agência de Marketing Digital | São Paulo, SP |
| DonaSol | Energia Solar — Vendas B2C | Brasília, DF |

---

## 2. A Infraestrutura

### Stack Técnico

| Componente | Ferramenta | URL / ID |
|------------|------------|----------|
| Automação | n8n (self-hosted) | `https://n8n.paulonunan.com` |
| Site | Next.js 16 + Vercel | `https://portfolio-scala.vercel.app` |
| Repositório site | GitHub | `github.com/ph-nunan/portfolio-scala` |
| Analytics | GA4 | Property ID: `528936871` |
| Tag Manager | GTM | `GTM-TH5VGFDP` |
| Meta Pixel | Pixel Scala Site | `1466153678449297` |
| Monitoramento | Microsoft Clarity | (configurado via GTM) |
| Agente IA WhatsApp | n8n + GPT-4o-mini | Workflow: `S22OxWxT77a1geK8` |

### Meta Ads — Conta Principal

| Campo | Valor |
|-------|-------|
| Ad Account | `act_1605651367382391` — Scala-Conta-Anúncios |
| Business Manager | ID `1576433183439107` — Scala |
| Pixel | `1466153678449297` — Pixel Scala Site |
| WhatsApp | +55 61 8189-4189 |
| System User | `scala-user` (ID: `61579495951643`) — token permanente |
| Meta App ID | `854431830954678` |
| Phone Number ID | `971782562694033` |
| WhatsApp Business Account ID | `1480192843700940` |

### Variáveis de Ambiente (Vercel)

| Variável | Valor | Onde usada |
|----------|-------|-----------|
| `NEXT_PUBLIC_GTM_ID` | `GTM-TH5VGFDP` | layout.tsx — carrega GTM |
| `GOOGLE_SHEETS_WEBHOOK_URL` | [encriptado] | api/contact — formulário |

---

## 3. Os Produtos

### 3.1 Ana — Agente WhatsApp IA

**Papel no funil:** recebe leads 24/7, faz triagem e qualificação, agenda reunião de diagnóstico.

| Campo | Valor |
|-------|-------|
| Workflow n8n | `S22OxWxT77a1geK8` |
| Modelo atual | GPT-4o-mini |
| Google Sheet | `1yDex-TLsx3TCxQ2ZZObTn6X_4Ln83ClMEiZI47y6h5U` (aba: Conversas) |
| Link direto | `https://wa.me/556181894189` |

**Meta de performance:**
- >60% dos contatos qualificados
- >70% dos qualificados agendam reunião

**Upgrade planejado (v3):** GPT-4o-mini → Claude Sonnet 4.6 + SPIN Selling

---

### 3.2 AI Campaign Manager

Reports automatizados via n8n:
- **WF-02** — Meta Ads Reports → WhatsApp (multi-cliente)
- **WF-03** — Google Ads Reports → WhatsApp (via MCC `4323799990`)
- **WF-04** — Meta Leads → Google Sheets (pendente)

Google Sheet central: `1YweVU-kJjvjb5QLJpUu8xUpJS4g7QL0aL1CdKgFTt7A` (aba: Clientes)

---

### 3.3 Site — portfolio-scala.vercel.app

Ver seções [V1](#5-v1) e [V2](#9-v2) para histórico completo.

---

## 4. Fase 1 — Campanha LPV

### Campanha

| Campo | Valor |
|-------|-------|
| ID | `120244213653500671` |
| Nome | [LEADS] Conversão - Leads B2B - Advantage+ - Mar/26 |
| Adset ID | `120244272147020671` |
| Adset | Broad Audience - Brasil - 25-55 |
| Objetivo | LANDING_PAGE_VIEWS |
| Budget inicial | R$ 10/dia (21 Mar) |
| Budget ajustado | R$ 25/dia (23 Mar) |
| Budget final | R$ 20/dia (ajustado pelo Paulo) |
| Status | Pausada (30 Mar — pré-Fase 2) |
| Início | 21 de março de 2026 |
| Pausa | 30 de março de 2026 |

### Criativos

| Criativo | Formato | Gancho | Performance |
|---------|---------|--------|-------------|
| Carrossel 2 — Concorrente automatizou | Carrossel | FOMO competitivo | **97% do budget alocado pelo algoritmo** |
| Carrossel 1 — Funil quebrado | Carrossel | Dor operacional | 3% do budget — mal rodou |
| Estático — Vendas no escuro | Imagem estática | Dor de negócio | ~0% — praticamente ignorado |

**UTMs configurados:**
```
utm_source=facebook&utm_medium=paid_social&utm_campaign=leads_b2b_mar26
utm_content=carrossel2_concorrente (vencedor)
utm_content=carrossel1_funil_quebrado
utm_content=estatico_vendas_escuro
```

### Audiência

- Segmentação: Broad Audience, Brasil, 25–55 anos
- Advantage+ Audience (Meta decide a segmentação automaticamente)
- Plataformas: Instagram Feed + Facebook Feed + Stories

---

## 5. V1 — O Site Original

**Tag git:** `v1`
**Commit:** `63745dc`
**Período ativo:** 13 Mar – 30 Mar 2026

### Estrutura (19 seções)

```
Hero → SocialProof → PatternInterrupt → Problem → FunnelComparison →
MidCTA → HowItWorks → Services → ForWhom → Comparison → Results →
Cases → Testimonials → FuturePacing → KPIs → TechStack → Founder → FAQ → Contact
```

### Filosofia do V1

**Estratégia:** cold traffic converter. O anúncio leva o usuário ao site. O site tem que fazer o trabalho completo de:
1. Identificar quem é o visitante
2. Qualificar a dor
3. Apresentar a solução
4. Eliminar objeções
5. Converter para WhatsApp

19 seções foi a tentativa de cobrir cada etapa do funil completo dentro do próprio site.

### Características Técnicas do V1

| Métrica | Valor | Data |
|---------|-------|------|
| Lighthouse Score (mobile) | 75 | 24 Mar |
| LCP | 4.5s | 24 Mar |
| FCP | 1.7s | 24 Mar |
| TBT | 300ms (-59% após otimizações) | 24 Mar |
| CLS | 0.001 | 24 Mar |
| INP (Clarity) | 840ms → classificado como BAD | 30 Mar |

**Problemas técnicos identificados e corrigidos durante o V1:**
- Framer Motion no FloatingCTA causando INP 840ms → resolvido com CSS transitions
- Problem.tsx com LiveTicker (`setInterval`) consumindo main thread → removido na v2
- Hero server component com imports cliente no critical path → separado HeroCTAs + HeroLiveFeed
- GTM com tags duplicadas e triggers obsoletos → limpeza completa (25 Mar)
- CTA primário apontando para `#contact` (âncora interna) → WhatsApp direto (25 Mar)
- `data-section="hero"` duplicado → IntersectionObserver disparava eventos em dobro → corrigido
- FID depreciado (Mar 2024) ainda sendo medido → substituído por INP

### Linha do Tempo do V1 — Construção

| Data | Marco |
|------|-------|
| 13 Mar 2026 | Primeiros commits — branding e estrutura base |
| ~15 Mar | Implementação de todas as 19 seções |
| 16 Mar | Ana (agente WhatsApp) em produção — testada e validada |
| 21 Mar | Campanha Meta Ads lançada — R$ 10/dia, LPV |
| 22 Mar | GTM configurado e validado (v4 publicada) |
| 23 Mar | Budget aumentado para R$ 25/dia. UTMs configurados via API |
| 24 Mar | GA4 custom dimensions criadas. TBT 740ms → 300ms. Score 67 → 75 |
| 25 Mar | Primeiro ajuste importante (ver doc separado): CTA corrigido, copy hero, tracking |
| 30 Mar | 701 LPVs acumulados. Campanha pausada. Site redesenhado (v2) |

---

## 6. Os Dados Reais de 700+ LPVs

### Métricas da Campanha (21 Mar – 30 Mar)

| Métrica | Valor |
|---------|-------|
| Alcance total | ~4.200 pessoas |
| Impressões | ~5.500 |
| Cliques no link | ~180 |
| Landing Page Views | **701** |
| CTR médio | **2.91%** ✅ (meta: >1.5%) |
| CPC | **R$ 0,23** ✅ (meta: <R$ 0,80) |
| CPL (custo/LPV) | **R$ 0,29** ✅ (meta: <R$ 0,60) |
| Gasto total | ~R$ 200 |
| Período | 10 dias |
| LPVs/dia médio | ~70 |

**Por criativo (acumulado):**

| Criativo | Cliques | LPVs | CTR | Observação |
|---------|---------|------|-----|------------|
| Carrossel 2 — Concorrente | ~175 | ~680 | ~2.94% | Algoritmo alocou 97% do budget |
| Carrossel 1 — Funil quebrado | ~5 | ~21 | ~2.5% | Mal rodou |
| Estático — Vendas no escuro | 0 | 0 | ~0% | Ignorado pelo algoritmo |

### Dados do Microsoft Clarity (63 sessões analisadas — 25 Mar)

| Métrica | Valor | Interpretação |
|---------|-------|---------------|
| Scroll depth médio | **6.49%** | A maioria saiu sem sair do Hero |
| Bounce rate (GA4) | **81.3%** | Alto mas esperado para cold traffic |
| INP | **840ms** | BAD — cliques não registravam imediatamente |
| Sessões mobile | ~76% | Majoritariamente Instagram/Facebook in-app |
| In-app browser | **76%** | Instagram WebView — bloqueia cookies, wa.me tem fricção |

**Snapshot do scroll depth por sessão (Clarity):**
- 90%+ dos usuários saíram entre 0–15% de scroll
- Apenas ~3% chegaram até a seção Contact (seção 19 de 19)
- A maioria dos usuários nunca viu além do Hero

### Dados do GA4 (21 Mar – 30 Mar)

| Evento | Ocorrências | Observação |
|--------|-------------|------------|
| `page_view` | 701 | Confirma LPVs da Meta |
| `wa_button_click` | **12** | **Todos eram testes do Paulo — 0 orgânicos** |
| `scroll_depth_reached` (25%) | ~21 | Apenas 3% dos visitantes chegaram a 25% |
| `section_viewed` (hero) | registrado | Todos viram o Hero |
| `section_viewed` (contact) | ~0 | Quase nenhum chegou ao Contact |

**Conclusão crítica:** **Taxa de conversão real = 0,0%**

---

## 7. A Grande Revelação — 0% de Conversão

### O diagnóstico

Após pausar a campanha com 701 LPVs, análise completa revelou:

**Os 12 eventos `wa_button_click` no GA4 eram todos testes internos do Paulo.**

Isso significa que em 701 visitas de pessoas reais vindas do anúncio, **zero clicaram no WhatsApp.**

### As causas identificadas (por ordem de impacto)

#### Causa 1 — Scroll depth de 6.49% (crítico)
A maioria dos visitantes saiu dentro do Hero sem rolar a página. As CTAs secundárias (FunnelComparison, HowItWorks, Contact) nunca foram vistas. O único CTA que poderia converter era o Hero — e ele não convertia porque...

#### Causa 2 — INP 840ms (crítico)
O INP (Interaction to Next Paint) de 840ms significa que quando alguém clicava no botão, o site demorava 840ms para responder. Em in-app browser do Instagram, esse delay é percebido como "o botão não funcionou" e o usuário clica de novo ou desiste. **Cliques estavam sendo registrados no GA4 mas nenhum era de usuários reais.**

Causa técnica: Framer Motion (`AnimatePresence`) no FloatingCTA estava no bundle inicial, bloqueando o main thread.

#### Causa 3 — In-app browser do Instagram (importante)
76% do tráfego chegava pelo navegador interno do Instagram (WebView). Nesse ambiente:
- Links `wa.me` abrem com fricção (prompt "Abrir no WhatsApp?" + segunda ação)
- Cookies de sessão não persistem normalmente
- Eventos de clique podem não disparar por limitações do WebView

#### Causa 4 — Site não conectava em 8 segundos (importante)
O Hero original dizia "Do Anúncio ao Relatório. Tudo no Piloto Automático." — uma descrição de produto. O visitante que chegou por um anúncio com gancho emocional ("Seu concorrente já automatizou") encontrou uma página que falava sobre o produto, não sobre a dor que o trouxe até ali.

Regra dos 8 segundos: se o visitante não se identificar com o problema em até 8 segundos, sai.

#### Causa 5 — 19 seções = site longo demais para cold traffic
Com 6.49% de scroll médio, as seções 3 a 19 eram invisíveis para a maioria. Um site de cold traffic converter com 19 seções pressupõe que o visitante tem motivação para ler. Com tráfego pago de topo de funil, o visitante tem atenção mínima — quer validar em segundos se é para ele ou não.

### O que NÃO causou

- **Não foi o criativo:** CTR 2.91% é excelente. O anúncio convencia. O problema era no que acontecia depois.
- **Não foi o budget:** R$ 0,29/LPV é muito eficiente. Mais budget com 0% de conversão só significaria mais prejuízo.
- **Não foi a audiência:** 701 pessoas qualificadas chegaram à landing page.

---

## 8. O Pivot — De LPV para CTWA

### A decisão estratégica

**Insight central:** se o site com 19 seções converte 0% de cold traffic, a solução não é reescrever o site para cold traffic — é mudar onde acontece a conversão.

**CTWA = Click to WhatsApp Ads**

O anúncio Meta com objetivo "Mensagens" leva o clique diretamente para o WhatsApp, sem passar pelo site. A Ana (agente IA) faz a qualificação. O site vira um documento de credibilidade enviado pela Ana depois da qualificação — para um lead que já está engajado e quer saber mais.

**Vantagens do CTWA sobre LPV:**
1. Elimina o problema do in-app browser — o WhatsApp abre nativamente
2. Elimina o problema de INP — sem site intermediário para converter
3. Meta otimiza para conversas iniciadas, não LPVs — algoritmo aprende mais rápido
4. Feedback imediato — conversa real com a Ana em segundos

**Novo papel do site:**
- Não é mais um conversor de cold traffic
- É um documento de autoridade e credibilidade
- Enviado pela Ana após qualificação: "Enquanto verifico alguns detalhes, aqui está nosso site para você conhecer melhor o que fazemos"
- O visitante já foi qualificado, já falou com a Ana, já está aquecido

### Implicações para o site

Com a mudança de papel, as 19 seções de persuasão para cold traffic deixam de fazer sentido. O site precisa de:

1. **Autoridade** — confirmar que Paulo e a Scala são referência no assunto
2. **Prova** — resultados reais dos clientes existentes
3. **Clareza** — o que é, como funciona, por que confiar
4. **Conversão para reunião** — a Ana já qualificou, o site precisa fechar o agendamento do diagnóstico

Resultado: 19 seções → 8 seções.

---

## 9. V2 — O Redesign para Lead Quente

**Tag git:** `v2`
**Commits:** `cc45fe3` → `4b4ba87`
**Data:** 30 de março de 2026

### Estrutura (8 seções)

```
Hero → SocialProof → Problem → FunnelComparison →
HowItWorks → Testimonials → Founder → Contact
```

**Filosofia de cada seção:**

| # | Seção | Função psicológica |
|---|-------|-------------------|
| 1 | Hero | Identificação imediata com a dor (8 segundos) |
| 2 | SocialProof | Autoridade por números — sem ler mais nada, já viu a prova |
| 3 | Problem | Consciência — quantificar o problema que ele já sente |
| 4 | FunnelComparison | Desejo — o antes/depois concreto, 4.6× fechamentos |
| 5 | HowItWorks | Confiança no processo — desmistificar, mostrar o caminho |
| 6 | Testimonials | Voz humana — quem já passou pela transformação |
| 7 | Founder | Humanização — quem está por trás, por que confiar |
| 8 | Contact | Conversão — CTA final para lead que já está pronto |

### Copy Principal

**Hero:**
- H1: "Você gera leads."
- H2: "Ninguém responde a tempo."
- Sub: "A Scala implementa em 7 dias o sistema que atende leads em segundos via WhatsApp, qualifica automaticamente e agenda reuniões — sem você mover um dedo."
- Badge: "Para gestores de tráfego e agências"

**SocialProof (métricas no marquee):**

| Valor | Label |
|-------|-------|
| < 5s | resposta ao primeiro contato |
| 7 dias | do zero ao ecossistema ativo |
| 4.6× | mais fechamentos com o mesmo tráfego |
| 24/7 | operação sem interrupção |
| 30 dias | garantia ou reembolso total |
| R$ 0 | custo de equipe adicional |

**Problem (2 itens — era 4):**
- 78% dos leads não recebem resposta nos primeiros 5 minutos
- 35% das vendas são perdidas por falta de follow-up

**Testimonials (reescritos com dados reais):**

| Cliente | Result Badge | Dado concreto |
|---------|-------------|---------------|
| Hugo Borges | 4.6× mais fechamentos | Taxa de fechamento de 8% → 37% |
| H3imob | Zero lead sem resposta em 5 min | Nenhum lead > 5 segundos sem resposta |
| GoAlpha | 3 clientes novos sem nova contratação | Mais clientes sem aumentar equipe |
| DonaSol | Atendimento 24/7 sem equipe extra | Implementado em 6 dias |

**Contact:**
- Heading: "Confirme seu diagnóstico gratuito."
- WA message: "quero confirmar meu diagnóstico gratuito" (warm lead, não cold)

### Mudanças Técnicas do V2

| Arquivo | O que mudou | Por quê |
|---------|-------------|---------|
| `FloatingCTA.tsx` | Framer Motion → CSS transitions | INP 840ms → estimado <200ms |
| `Hero.tsx` | HeroLiveFeed → dynamic import | FM fora do bundle inicial, melhora TBT |
| `Problem.tsx` | LiveTicker removido, 4→2 itens | setInterval desnecessário, foco na dor principal |
| `HowItWorks.tsx` | `.hiw-visual { display:none }` no mobile | Mockups pesados ocultos onde não agregam |
| `Testimonials.tsx` | Reescrita com result badge + cargo + cidade | Credibilidade específica > genérica |
| `Contact.tsx` | Copy warm-lead, CTA "Confirmar Diagnóstico" | Visita vem de lead qualificado, não cold |
| `Analytics.tsx` | Scroll thresholds 5/10/15/20/50/75/100% | 6.49% médio revelou que 25% era muito alto |
| `Analytics.tsx` | Observer threshold 0.2 (era 0.4) | Seções longas no mobile não chegavam a 40% |
| `Navbar.tsx` | Links corrigidos (3 links mortos removidos) | #services, #results, #faq não existiam mais |
| `layout.tsx` | JSON-LD preços: R$450→R$1.500, R$1.200→R$400 | Preços estavam errados desde o início |
| 12 arquivos | Deletados (seções removidas) | Repo limpo — código morto aumenta risco |

---

## 10. Tracking — Arquitetura Atual

### Fluxo completo por evento

```
Visita ao site
  → fbq('track', 'PageView') [MetaPixel.tsx]
  → GTM carregado [strategy="afterInteractive"]

Clique em qualquer link wa.me
  → track('wa_button_click', { location, scroll_pct }) → dataLayer
    → GTM trigger "Custom Events — Analytics Scala" (regex)
      → GA4 Event Tag → GA4 Property 528936871
        → wa_button_click marcado como CONVERSÃO no GA4 ✅
  → GTM trigger "WhatsApp Button Click" (DOM click URL contém wa.me)
    → Meta Pixel tag: fbq('track','Lead', { content_name:'WhatsApp Diagnostico', content_category:'Conversion' })
  → MetaPixel.tsx global listener
    → fbq('trackCustom', 'wa_button_click')

Scroll
  → scroll_depth_reached com percent: 5, 10, 15, 20, 50, 75, 100

Seção visível por ≥2s
  → section_viewed com section name + scroll_pct

Seção saiu do viewport
  → section_time_spent com seconds

Tempo na página
  → time_milestone: 30s, 60s, 2min, 3min, 5min

Saída no topo (desktop)
  → exit_intent com scroll_pct

Saída da aba / fechamento
  → web_vitals: CLS + INP (via PerformanceObserver)

Carregamento
  → web_vitals: LCP, FCP
```

### GTM — Estrutura de Tags e Triggers

**Triggers:**

| Nome | Tipo | Condição | Tag que dispara |
|------|------|----------|-----------------|
| Custom Events — Analytics Scala | Custom Event | Regex: `^(wa_button_click\|cta_click\|nav_link_click\|time_milestone\|scroll_depth_reached\|exit_intent\|section_viewed\|section_time_spent\|web_vitals)$` | GA4 Event — Analytics Scala (universal) |
| WhatsApp Button Click | Clique — Apenas Links | Click URL contém `wa.me` | Meta Pixel — Lead (WhatsApp Click) |

**Tags:**

| Nome | Tipo | O que faz |
|------|------|-----------|
| GA4 Event — Analytics Scala (universal) | GA4 Event | Envia todos os custom events para GA4 |
| Meta Pixel — Lead (WhatsApp Click) | HTML customizado | `fbq('track','Lead', {content_name:'WhatsApp Diagnostico', content_category:'Conversion'})` |
| Meta Pixel — Base | (deduzido) | `fbq('init', '1466153678449297')` + `PageView` |
| GA4 — Configuração | GA4 Config | Configura GA4 com o Measurement ID |
| Microsoft Clarity | (deduzido) | Inicializa Clarity |

### CTAs com tracking completo (6/6)

| CTA | Localização | `wa_button_click` location |
|-----|------------|---------------------------|
| Hero primary | Hero section | `hero_primary` |
| FloatingCTA | Fixo inferior | `floating` |
| Navbar desktop | Nav superior | `navbar_desktop` |
| Navbar mobile | Menu hamburguer | `navbar_mobile` |
| FunnelComparison | Seção 4 | `funnel_comparison` |
| HowItWorks step 01 | Seção 5 | `how_it_works` |
| Contact | Seção 8 | `contact` |

### Meta Pixel — Estado verificado via API (30 Mar)

```json
{
  "id": "1466153678449297",
  "name": "Pixel Scala Site",
  "owner_business": { "name": "Scala" },
  "owner_ad_account": { "id": "act_1605651367382391" }
}
```

**Eventos nas últimas horas (30 Mar):** ~300 PageViews confirmados.
**Lead events:** zero — esperado, campanha pausada. Disparará quando CTWA for ao ar.

---

## 11. Aprendizados — Princípios para Decisões Futuras

### Sobre campanhas Meta

**1. CTR excelente não garante conversão**
CTR 2.91% com CPL R$ 0,29 — métricas de topo de funil perfeitas. Mas 0% de conversão. O anúncio convence o clique; o site tem que convencer a ação. São dois produtos separados.

**2. Algoritmo decide o criativo, não o gestor**
Três criativos lançados. O algoritmo alocou 97% do budget no Carrossel 2 espontaneamente. Não foi estratégia — foi aprendizado automático. Conclusão: lançar 2–3 criativos variados e deixar o algoritmo decidir. Não tentar forçar a distribuição.

**3. Nunca aumentar budget >20% após 50+ conversões**
Antes de 50 conversões (fase atual): pode escalar agressivamente sem riscos.
Depois de 50 conversões: aumentar >20% reinicia o aprendizado e CPL explode.

**4. Fase 2 tem prerequisitos não negociáveis**
OFFSITE_CONVERSIONS exige 50+ eventos/semana. Com 6% conversão, precisa de 833+ LPVs/semana (R$ 35+/dia) para sair da fase de aprendizado. Sem isso, o algoritmo nunca aprende e o CPL não converge.

---

### Sobre o site

**5. 6% de scroll depth é o problema, não a copy**
Se o usuário não rola, não importa o quanto a copy das seções 2–8 é boa. O Hero tem que:
- Identificar o visitante em <8 segundos
- Criar desejo de continuar lendo
- Ter CTA visível sem precisar scrollar

**6. INP 840ms mata conversões silenciosamente**
Cliques aconteciam mas o feedback visual demorava 840ms. Usuário pensava que o botão não funcionou. A Framer Motion no bundle inicial foi a causa. Solução: componentes com animações Framer Motion → dynamic imports ou substituição por CSS.

**7. In-app browser do Instagram é um ambiente hostil**
76% do tráfego de Meta Ads chega pelo in-app browser. Nesse ambiente:
- Cookies limitados
- Links `wa.me` têm fricção adicional
- JavaScript pesado tem performance degradada
- CTWA resolve esse problema completamente (abre WhatsApp nativo)

**8. Site de cold traffic vs site de credibilidade são produtos diferentes**
Um site que precisa converter tráfego frio precisa de persuasão completa (problema → solução → prova → objeções → conversão). Um site que recebe leads quentes (já qualificados pela Ana) precisa de autoridade e confirmação. Tentar usar o mesmo site para os dois propósitos resulta em nenhum dos dois bem.

---

### Sobre tracking

**9. Tracking é pré-condição de qualquer decisão**
Antes de qualquer otimização, verificar:
- GTM deployado e publicado?
- Eventos chegando ao dataLayer?
- GA4 recebendo eventos?
- Meta Pixel disparando Lead?

Sem tracking, qualquer análise é chute. Aprendemos isso na prática: o GTM tinha tags duplicadas e triggers obsoletos que capturavam menos da metade dos eventos.

**10. Scroll thresholds precisam ser calibrados para o site real**
Threshold de 25% como primeiro ponto de scroll ignorava 90% dos usuários (scroll médio 6.49%). Novos thresholds (5%, 10%, 15%, 20%) agora capturam dados de usuários reais antes que saiam.

**11. IDs duplicados no HTML quebram analytics**
Dois elementos com o mesmo `id` ou `data-section` fazem o IntersectionObserver disparar eventos duplicados. Sempre verificar se o wrapper em `page.tsx` já tem o atributo antes de adicionar em seções individuais.

**12. Nunca ter fbq Lead duplicado**
GTM dispara `fbq('track','Lead')` via DOM click em todo link `wa.me`. Se o código também disparar `fbq('track','Lead')` no onClick, Meta Pixel recebe 2 Lead events por clique — inflando métricas e potencialmente confundindo o algoritmo. Uma fonte por evento.

---

### Sobre o produto

**13. A dor real do cliente não é "operação de ads"**
A v1 tinha seções sobre relatórios de Meta Ads, gestão de Google Ads, KPIs de campanha. Os dados de scroll revelaram que ninguém chegava a essas seções. A dor que ressoa é simpler e mais direta: **"Você gera leads. Ninguém responde a tempo."** — essa frase conecta imediatamente com gestores de tráfego.

**14. Números concretos vencem argumentos abstratos**
"Melhora suas conversões" → ignorado.
"78% dos leads não recebem resposta em 5 minutos" → ativa medo e reconhecimento.
"4.6× mais fechamentos com o mesmo tráfego" → ativa desejo.
Cada claim precisa de um número. Números são âncoras mentais.

**15. Social proof falso é pior que nenhum social proof**
A v1 tinha "resultado médio dos clientes Scala após 30 dias" — o que seria falso se os números não fossem medidos individualmente em cada cliente. Em B2B, compradores sofisticados questionam. A correção foi citar os nomes reais dos 4 clientes sem afirmar números que não foram medidos.

---

## 12. Próximas Versões Planejadas

### Ana SPIN v1 — CONCLUÍDA (31 Mar 2026) ✅

**Workflow:** `mLM22h2JylSrhCRE` — 29 nodes | Supabase + GPT-4o + SPIN 5 fases

**O que foi entregue:**
- Substituição completa do Google Sheets por Supabase (Postgres real, REST API)
- Framework SPIN Selling com 5 fases modulares e prompts dinâmicos por fase e trilha
- JSON output estruturado do modelo → extração automática de dados do lead
- Guard pós-agendamento (na25): leads com `status=Agendado` nunca chamam o GPT novamente
- Bug na17 corrigido: `data_agendamento`, `link_meet` e `status` agora persistem corretamente
- Social proof com números específicos por trilha
- Link do portfólio inserido no fechamento da fase 3

**Em produção com conversas reais testadas e validadas.**

---

### V3 do Site — Site de Autoridade (planejado)

**Gatilho:** decisão tomada em 31 Mar 2026 com base no PDF estratégico

**O que muda:**
- Site deixa de ser landing page de aquisição → vira portfólio de autoridade técnica
- Visitante chegará pelo link enviado pela Ana nas fases 3 e 4 do SPIN (lead já qualificado)
- Novo objetivo: confirmar decisão já tomada, não convencer do zero
- CTA principal: "Confirmar meu diagnóstico gratuito →"

**8 novas seções** (substituem as 8 atuais):

| # | Seção | Gatilho |
|---|-------|---------|
| 1 | Hero — Declaração de Posicionamento | Reconhecimento |
| 2 | Ecossistema — 4 Módulos | Desejo de completude |
| 3 | Como Funciona — 4 Etapas | Redução de risco |
| 4 | Para Quem É — 3 Perfis | Identificação |
| 5 | Portfólio — 4 Projetos Técnicos | Prova de competência |
| 6 | Números de Mercado | Urgência competitiva |
| 7 | Por Que a Scala | Diferenciação |
| 8 | CTA Final | Escassez real |

**Regras do novo site:**
- Sem formulário, sem menu complexo, sem preços, sem depoimentos fabricados
- Sticky header com botão "Confirmar diagnóstico" sempre visível
- Evento GA4: `portfolio_site_cta_click` (separado de `wa_button_click`)
- Mobile-first (70%+ dos leads acessam direto do WhatsApp)
- URL: `/portfolio` ou domínio próprio (a Ana manda o link)

---

### V4 — Fase 2 da Campanha

**Gatilho:** Ana v3 validada + 50+ Lead events/semana no Meta Pixel

**O que muda:**
- Objetivo da campanha: LANDING_PAGE_VIEWS → objetivo Mensagens (CTWA)
- Budget: R$ 20/dia → R$ 30–50/dia
- Criativos: novos com gancho direto para WhatsApp
- Otimização: Meta otimiza para conversas iniciadas, não LPVs

**Prerequisitos não negociáveis:**
1. Ana qualificando bem (>60% dos contatos → reunião agendada)
2. Taxa de agendamento >40%
3. Meta Pixel com histórico de Lead events

---

### Modelo de Atualização deste Documento

**Atualizar sempre que:**
- Nova versão do site for ao ar (nova seção V)
- Campanha mudar de fase ou objetivo
- Métricas reais de conversão forem coletadas
- Decisão estratégica relevante for tomada
- Novo cliente for fechado

**Formato para novos registros:**
```markdown
## V[n] — [Nome da versão]

**Tag git:** `vN`
**Data:** DD MMM YYYY

### O que motivou a mudança
[Dado específico que gerou a decisão]

### O que mudou
[Tabela de mudanças]

### Resultado
[Dados coletados após a mudança]
```

---

---

## 13. Dashboard CRM (planejado)

**Objetivo:** visualizar o funil da Ana sem SQL manual

**Stack candidata:** Looker Studio conectado ao Supabase via connection string PostgreSQL (zero código, funcional em < 30 min)

**Métricas a exibir:**
- Leads por fase (1–5)
- Leads por classificação (Quente / Morno / Frio)
- Taxa de agendamento (leads que chegaram à fase 5 / total)
- Funil completo: contatos → qualificados → agendados → (fechados — manual)
- Histórico de conversas por lead

**Prerequisito:** Ana com pelo menos 30–50 leads no Supabase para o dashboard ter dados representativos.

---

*Documento criado em 30 de março de 2026. Última atualização: 31 de março de 2026.*
*Próxima atualização planejada: quando campanha CTWA for ao ar e primeiras métricas reais de conversão forem coletadas.*
