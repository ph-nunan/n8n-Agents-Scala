# Plano Operacional — Meta Ads Scala

> Documento vivo. Atualizar sempre que mudar estratégia, orçamento ou aprender algo novo.
> Criado em: 2026-03-21

---

## Contexto da Conta

| Item | Valor |
|---|---|
| Ad Account ID (canônico) | `act_1605651367382391` |
| Ad Account ID (alias) | `act_120244137424200671` |
| Página | `1079796795206873` |
| Pixel ID | `1466153678449297` |
| Evento de conversão | `wa_button_click` |
| Destino dos anúncios | `https://portfolio-scala.vercel.app/` |

---

## Funil Atual

```
Anúncio (Meta)
    ↓
portfolio-scala.vercel.app  ←  qualifica o lead visualmente
    ↓
Botão WhatsApp (wa_button_click) ←  evento de conversão
    ↓
Ana (WhatsApp 24/7) ←  qualificação via SPIN Selling
    ↓
Diagnóstico Gratuito (Google Meet com Paulo)
    ↓
Fechamento
```

---

## Campanha Ativa

| Item | Valor |
|---|---|
| Campaign ID | `120244213653500671` |
| Campaign Name | `[LEADS] Conversão - Leads B2B - Gestores de Tráfego - Mar/26` |
| Objetivo | `OUTCOME_LEADS` |
| Ad Set ID | `120244272147020671` |
| Ad Set Name | `Broad Audience - Brasil - 25-55` |
| Orçamento | R$10/dia |
| Otimização | `LANDING_PAGE_VIEWS` |
| Bid Strategy | `LOWEST_COST_WITHOUT_CAP` |
| Público | Advantage+ Audience — Brasil, 25+ |
| Status | **ACTIVE** — no ar desde 2026-03-21 |
| Pagamento | PayPal `nunan38@gmail.com` |

### Anúncios Ativos

| Nome | Ad ID | Creative ID | Formato |
|---|---|---|---|
| Estático — Vendas no escuro | `120244272148560671` | `955974620281208` | Imagem única |
| Carrossel 1 — Funil quebrado | `120244272149010671` | `897804036413244` | Carrossel 5 cards |
| Carrossel 2 — Concorrente automatizou | `120244272149350671` | `2239822923454857` | Carrossel 5 cards |

### Image Hashes (conta `act_1605651367382391`)

| Arquivo | Hash |
|---|---|
| Estático `1.png` | `807918c0f6f5ce47adaf0e4ce830f37c` |
| Carrossel 1 — card 1 | `abebb1815222b5069fb51fddac067df7` |
| Carrossel 1 — card 2 | `3b7825048a1819ace6b1d4f1bb27fb5d` |
| Carrossel 1 — card 3 | `4a667e81e6d043ffb8fe6f036ac94d2e` |
| Carrossel 1 — card 4 (4.1.png) | `307895f152ec89821248abc76cdb066e` |
| Carrossel 1 — card 5 (ChatGPT) | `9d9a7c63c4ad1f7c6c7b9d113c99e43f` |
| Carrossel 2 — card 1 | `48782db817148befc51e14a742177c22` |
| Carrossel 2 — card 2 | `4c6925d9006720e24fa6384ee0f82337` |
| Carrossel 2 — card 3 | `811cbfcac814a42c8d6b9faf70af0b35` |
| Carrossel 2 — card 4 | `332d77f339372f4f0b995d37320ac86a` |
| Carrossel 2 — card 5 | `1fb433c441af6e07b1fdc872d7609106` |

---

## Copies dos Anúncios

### Estático — "Vendas no escuro"
**Texto principal:**
> Você sabe quantos leads chegaram essa semana?
> Quantos foram atendidos em menos de 5 minutos?
> Quantas reuniões foram marcadas?
> Qual campanha trouxe o lead que mais avançou no funil?
>
> Se você não sabe responder essas perguntas agora, você está gerenciando vendas no escuro.
>
> Tem uma forma diferente de operar. →

**Headline:** Pare de operar no escuro

---

### Carrossel 1 — "Funil quebrado"
**Texto principal:**
> Você investe em tráfego. Os leads chegam. E depois?
>
> A maioria das empresas tem um problema que não aparece no relatório de campanhas — e é exatamente esse problema que está limitando o crescimento.
>
> Deslize para entender.

**Cards:**
1. Tráfego bom. Funil quebrado.
2. Onde os seus leads somem
3. O custo que você não está calculando
4. O que separa quem escala
5. É isso que a Scala resolve

---

### Carrossel 2 — "Concorrente automatizou"
**Texto principal:**
> Seu concorrente não está trabalhando mais do que você.
> Ele só parou de fazer manualmente o que pode ser automatizado.
>
> Enquanto você responde lead no WhatsApp às 23h,
> o sistema dele já marcou 3 reuniões.
>
> Deslize para entender o que mudou. →

**Cards:**
1. Não é esforço. É sistema.
2. 23h. O sistema dele nunca dorme.
3. O que ele parou de fazer manualmente
4. Infraestrutura que vende enquanto você descansa
5. Monte o mesmo sistema

---

## Plano de Evolução da Campanha

### Fase 1 — Treinar o Pixel (atual)
- **Objetivo:** Landing Page Views
- **Orçamento:** R$10/dia
- **Duração:** Até atingir 500 eventos no pixel
- **Meta:** O algoritmo aprende quem visita o site e quem tem perfil de cliente

### Fase 2 — Ativar Conversões
- **Gatilho:** 500+ eventos totais no pixel (PageView + wa_button_click combinados)
- **Mudança:** Trocar `LANDING_PAGE_VIEWS` → `OFFSITE_CONVERSIONS`
- **Orçamento mínimo recomendado:** R$30-50/dia (precisa de 50 conversões/semana para sair do learning)
- **Ação:** Criar novo ad set (attribution window muda — não é possível editar o existente)

### Fase 3 — Escala com Lookalike
- **Gatilho:** 100+ conversões (`wa_button_click`) registradas no pixel
- **Ação:** Criar audiência Custom de quem converteu + Lookalike 1% Brasil
- **Novo ad set:** Lookalike separado do Broad para comparar CPL

---

## Regras de Análise de Criativos

### Princípio fundamental
> Nunca tome decisão sobre criativo com dados insuficientes.
> Com R$10/dia, cada criativo precisa de ~R$50 gastos antes de ser julgado.
> Isso representa aproximadamente 15 dias de campanha para cada criativo.

### Métricas e Benchmarks

| Métrica | Bom | Aceitável | Problema |
|---|---|---|---|
| CTR | > 1,5% | 0,8% – 1,5% | < 0,8% |
| CPV (Custo por LPV) | < R$1,50 | R$1,50 – R$3,00 | > R$3,00 |
| Frequência | < 2,0 | 2,0 – 3,0 | > 3,0 |

### Quando trocar a arte

**Trocar:** CTR < 0,8% **E** CPV > R$3,00 após R$50 gastos no criativo → problema confirmado no criativo.

**Não trocar ainda:**
- Só CTR baixo pode ser público ou posicionamento, não a arte
- CPV bom mas CTR mediano = Meta encontrando as pessoas certas, não mexa

**Nunca:** Pausar os 3 criativos ao mesmo tempo. Sempre mantém pelo menos 1 rodando.

### Breakdown de Carrossel

Analisar performance card a card no Gerenciador:
- Para no card 1 → problema no hook visual
- Chega ao card 3-4 → público engajado, copy funcionando
- Ninguém vê o card 5 → CTA nunca aparece, considerar antecipar CTA para card 4

---

## Calendário de Análise

| Semana | O que fazer |
|---|---|
| Semana 1 | Não analisa criativo. Confirma só que a campanha está entregando (impressões > 0). |
| Semana 2 | Primeiro olhar: qual criativo o Meta está priorizando? CTR por criativo. CPV geral. |
| Semana 3 | Decisão de criativo. Se um está claramente perdendo (CTR + CPV ruins), pausa e substitui por variação. |
| Semana 4+ | Dados suficientes para diagnóstico completo. Avalia se é problema de arte, público ou site. |

---

## Diagnóstico Rápido de Problemas

| Sintoma | Causa provável | Ação |
|---|---|---|
| Impressões baixas / zero | Bid muito baixo ou criativo reprovado | Verificar status no Gerenciador |
| CTR baixo | Hook visual fraco ou headline sem tensão | Testar novo primeiro frame/copy |
| CPV alto com CTR ok | Landing page lenta ou desalinhada com o anúncio | Testar velocidade do site, revisar alinhamento de mensagem |
| Frequência > 3 em 2 semanas | Público muito pequeno | Expandir targeting ou criar novo ad set com público diferente |
| CTR bom, zero conversões no site | Desalinhamento anúncio × site | Revisar se a promessa do anúncio é cumprida no site |

---

## Recomendações do Meta — como tratar

| Recomendação | Decisão | Motivo |
|---|---|---|
| Criativo Advantage+ (retoques automáticos, +3%) | ❌ Não aplicar | Perde controle da identidade visual. Meta modifica cores, textos e sobreposições. Ganho de 3% não compensa risco de distorção de marca. |
| Reels 9:16 com áudio (+8% de CPR) | ✅ Planejar para Fase 2 | Reels tem menor custo por resultado. Criar vídeo vertical da Scala (15-30s) e adicionar à campanha no próximo ciclo criativo. |

---

## Observações Técnicas

- **ID canônico da conta:** `act_1605651367382391` — usar este para criar criativos e ads. O `act_120244137424200671` é alias.
- **API version:** usar `v22.0` — `v19.0` foi descontinuada em fev/2026
- **Hashes de imagem** são vinculados à conta onde foram uploadados. Re-upload necessário ao trocar de conta.
- **`promoted_object` é imutável** após criação do ad set
- **Janela de atribuição é imutável** após criação do ad set — qualquer mudança exige novo ad set
- **Imagem estática:** 1024x1536 (2:3) — Meta faz crop automático. Substituir por 1:1 ou 4:5 no próximo ciclo.
- **Page Access Token:** obtido via `GET /{page_id}?fields=access_token` com o system user token
- **Permissão `pages_manage_metadata`** não está no token atual — foto de perfil da página precisa ser trocada manualmente no Facebook

---

## Regras de Ouro

1. **Pixel antes de tudo** — sem dados no pixel, qualquer otimização é chute
2. **Verba concentrada aprende mais rápido** — menos ad sets, mais orçamento por set
3. **Mudar uma variável por vez** — ao testar, troca só a imagem OU só o texto, nunca os dois juntos
4. **Não pausar por impulso** — espera R$50 por criativo antes de qualquer decisão
5. **Registrar tudo** — anotar aqui o que foi testado, resultado e decisão tomada

---

## Histórico de Testes

| Data | Criativo | CTR | CPV | Resultado | Decisão |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

> Preencher conforme os dados chegarem.
