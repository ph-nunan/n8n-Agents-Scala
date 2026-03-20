# Bruno — Análise de Sessão 2026-03-19
**Sessão:** Pixel Meta + Primeira Campanha + Capacitação Ads Completa do Bruno
**Status ao final:** Setup 100% funcional. Pixel ativo. Campanha criada. Bruno capacitado para criar estrutura completa autonomamente.

---

## 1. Objetivo da Sessão

- Identificar e corrigir o Pixel Meta do site portfolio-scala
- Instalar o pixel corretamente no Next.js
- Criar a primeira campanha de conversão no Meta Ads
- Capacitar Bruno para criar campanha + ad set + anúncios autonomamente
- Validar o funil completo: Anúncio → Site → WhatsApp → Ana

---

## 2. Meta Pixel — Descoberta e Correção

### Problema encontrado
O ID `854431830954678` estava documentado como "Meta Pixel" em todos os arquivos do projeto. Na verdade, é o **App ID** do app "Scala Agent" (o app WhatsApp/Meta que roda os workflows do n8n).

**Confirmação via API:**
```
GET https://graph.facebook.com/v19.0/854431830954678
→ {"id": "854431830954678", "name": "Scala Agent"}
```

### Solução
Criação de um pixel real via API:
```
POST /act_1605651367382391/adpixels
→ Pixel ID criado: 1466153678449297
```

### Arquivos corrigidos
- `portfolio-scala/README.md` — Pixel ID atualizado
- `portfolio-scala/ANALISE_SITE.md` — Pixel ID atualizado

---

## 3. Instalação do Pixel no Next.js

### Componente criado: `components/MetaPixel.tsx`
```tsx
"use client"
const PIXEL_ID = "1466153678449297"

export default function MetaPixel() {
  useEffect(() => {
    // Captura todos os cliques em links wa.me e dispara wa_button_click
    const handleClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest("a")
      if (target?.href?.includes("wa.me") && typeof window.fbq === "function") {
        window.fbq("trackCustom", "wa_button_click")
      }
    }
    document.addEventListener("click", handleClick)
    return () => document.removeEventListener("click", handleClick)
  }, [])

  return (
    <Script id="meta-pixel" strategy="afterInteractive">
      {`...fbq('init','${PIXEL_ID}'); fbq('track','PageView');`}
    </Script>
  )
}
```

**Por que direto no Next.js (não via GTM)?**
- O GTM interface fechava a página ao tentar avançar durante a configuração
- Implementação direta é mais robusta para evento customizado `wa_button_click`
- Menos dependências externas, carregamento mais rápido

### Integração em `app/layout.tsx`
```tsx
import MetaPixel from "@/components/MetaPixel"
// Dentro de <body>:
<MetaPixel />
```

### Página de privacidade criada
- **URL:** `https://portfolio-scala.vercel.app/privacidade`
- **Arquivo:** `app/privacidade/page.tsx`
- **Necessária para:** Meta App publicar em modo Live (requisito de conformidade)

### Validação com Meta Pixel Helper
Ao rolar e clicar em todos os botões do site:
- `PageView` — Active ✅ (dispara ao carregar a página)
- `wa_button_click` — Active ✅ (dispara em cada clique em link wa.me)
- `SubscribedButtonClick` — Automatically Detected (Meta detecta automaticamente, bonus)

---

## 4. Meta App em Modo Live

### Problema
Ao tentar criar ad creatives via API, erro:
```
Error subcode 1885183: "O post do criativo dos anúncios foi criado por um app que está em modo de desenvolvimento"
```

### Solução
Usuário publicou o app "Scala Agent" em modo Live via `developers.facebook.com → Publicar`.

---

## 5. Primeira Campanha de Conversão

### Estrutura criada em produção

**CAMPANHA**
| Campo | Valor |
|-------|-------|
| ID | `120244213653500671` |
| Nome | `[LEADS] Conversão - Leads B2B - Gestores de Tráfego - Mar/26` |
| Objetivo | `OUTCOME_LEADS` |
| Tipo de compra | `AUCTION` |
| Status | `PAUSED` |

**CONJUNTO DE ANÚNCIOS**
| Campo | Valor |
|-------|-------|
| ID | `120244213653710671` |
| Nome | `Broad Audience - Brasil - 25-55` |
| Objetivo de otimização | `OFFSITE_CONVERSIONS` |
| Destination type | `WEBSITE` |
| Orçamento diário | R$30 (3000 centavos) |
| Billing event | `IMPRESSIONS` |
| Pixel | `1466153678449297` |
| Evento de conversão | `wa_button_click` |
| Page ID | `1079796795206873` |
| Targeting | Brasil, age_min 25, Advantage+ ON |
| Status | `PAUSED` |

**ANÚNCIOS**
| ID | Nome | Copy (resumo) |
|----|------|---------------|
| `120244213654860671` | Ad1 - Dor - Tempo no Atendimento | "Seu time gasta horas respondendo sempre as mesmas perguntas?" |
| `120244213655060671` | Ad2 - Prova Social - 7 dias | "Em 7 dias seu atendimento já funciona no piloto automático" |
| `120244213654890671` | Ad3 - CTA Direto - Diagnóstico | "Quantos leads você perde por demora no primeiro contato?" |

Todos os anúncios: PAUSED, image_hash placeholder `850b86ce7876a024f5c2d4e17054ca1c` (logo Scala), link `https://portfolio-scala.vercel.app`.

---

## 6. Funil de Conversão (arquitetura validada)

```
Anúncio Meta (3 variações)
  ↓
https://portfolio-scala.vercel.app
  (site qualifica o lead — 20 seções, calculadora ROI, prova social)
  ↓
Clique no botão WhatsApp
  (Pixel wa_button_click dispara → Meta registra conversão)
  ↓
WhatsApp +55 61 8189-4189
  ↓
Ana (agente IA de atendimento — WF-01 EVbZX91iB5moD6I4)
  ↓
Diagnóstico gratuito agendado
```

**Por que OUTCOME_LEADS + OFFSITE_CONVERSIONS?**
- `OUTCOME_LEADS` = objetivo da campanha (gerar leads)
- `OFFSITE_CONVERSIONS` = Meta otimiza para encontrar pessoas propensas a fazer a conversão definida no pixel (wa_button_click no site)
- Não é Lead Ads form (que fica dentro do Meta) — é conversão real no site

---

## 7. Novos Tools Adicionados ao Bruno

### `criar_conjunto_anuncios_meta`
Tool HTTP Request — `POST /act_1605651367382391/adsets`

Parâmetros:
- `campaign_id` — modelRequired
- `name` — modelRequired
- `daily_budget` — modelRequired (centavos)
- `optimization_goal` — modelRequired
- `destination_type` — modelRequired (**novo — crítico para rastreamento**)
- `targeting` — modelRequired (JSON string)
- `promoted_object` — modelRequired (JSON string)
- `billing_event` — fixo: IMPRESSIONS
- `status` — fixo: PAUSED

### `criar_anuncio_meta`
Tool HTTP Request — `POST /act_1605651367382391/ads`

Parâmetros:
- `adset_id` — modelRequired
- `name` — modelRequired
- `creative` — modelRequired (JSON string com `object_story_spec`)
- `status` — fixo: PAUSED
- `access_token` — fixo (token do scala-user)

Formato do creative:
```json
{
  "object_story_spec": {
    "page_id": "1079796795206873",
    "link_data": {
      "image_hash": "850b86ce7876a024f5c2d4e17054ca1c",
      "link": "https://portfolio-scala.vercel.app",
      "message": "COPY_DO_ANUNCIO",
      "name": "HEADLINE",
      "call_to_action": {
        "type": "LEARN_MORE",
        "value": {"link": "https://portfolio-scala.vercel.app"}
      }
    }
  }
}
```

### `upload_imagem_meta`
Tool Code — `@n8n/n8n-nodes-langchain.toolCode`

Upload binário multipart via `$fromAI()`. Funciona para fazer upload de imagens e retornar o `image_hash`.

**WORKAROUND ATUAL:** O upload via Code tool tem instabilidades no ambiente sandbox do n8n. O hash `850b86ce7876a024f5c2d4e17054ca1c` (logo Scala) está pre-carregado como placeholder padrão. Bruno usa direto sem chamar upload, a menos que Paulo forneça URL de imagem personalizada.

---

## 8. Erros e Soluções da Meta Marketing API

### E1: Upload de imagem bloqueado via URL parameter
```
POST /act_.../adimages?url=https://...
→ Error code 3: "Application does not have the capability to make this API call"
```
**Causa:** Meta bloqueia upload via URL em apps novos/sem histórico.
**Solução:** Upload binário multipart (baixar imagem + enviar como form-data).

### E2: App em modo Development bloqueia criação de ad creative
```
Error subcode 1885183: app em modo de desenvolvimento
```
**Solução:** Publicar o Meta App em modo Live.

### E3: Conta sem forma de pagamento
```
Error subcode 1359188: "Nenhuma forma de pagamento"
```
**Solução:** Adicionar cartão de crédito na conta de anúncios.

### E4: `promoted_object` sem `page_id` para OFFSITE_CONVERSIONS
```
Error 1815437: para OFFSITE_CONVERSIONS, page_id precisa ser válido
```
**Solução:** Incluir `page_id: "1079796795206873"` no promoted_object.

### E5: `LEAD_GENERATION` incompatível com OUTCOME_LEADS + pixel
```
Error subcode 2490408: A meta de desempenho não está disponível
```
**Causa:** `LEAD_GENERATION` é para Lead Ads form nativo. Com pixel de site, usar `OFFSITE_CONVERSIONS`.
**Solução:** Mudar optimization_goal para `OFFSITE_CONVERSIONS`.

### E6: `promoted_object` imutável após criação
```
Error subcode 1885090: O objeto promovido é imutável
```
**Solução:** Deletar o ad set e criar um novo com o promoted_object correto desde o início.

### E7: Advantage+ rejeita `age_max` < 65
```
Error subcode 1870189: Com Advantage+, age_max não pode ser < 65
```
**Causa:** Com Advantage+ ON, restrições de idade viram "sugestões" — Meta exige ao menos 65 como teto.
**Solução:** Com advantage_audience=1, usar apenas `age_min` (sem age_max). O Meta usa o age_min como piso de segmentação.

### E8: Advantage+ requer flags de automação
```
Error subcode 1359202: Não é possível desabilitar opções do Advantage
```
**Causa:** Ao habilitar advantage_audience=1, Meta exige que as outras flags de automação (lookalike, detailed targeting, custom audience) também permaneçam habilitadas.
**Solução:** Usar `targeting={"age_min":25, "geo_locations":{...}, "targeting_automation":{"advantage_audience":1}}` sem incluir as outras flags explicitamente.

### E9: `destination_type` ausente causa rastreamento incorreto
**Sintoma:** Ad set criado com `destination_type: UNDEFINED`.
**Impacto:** Meta não associa corretamente o tráfego como destino website.
**Solução:** Sempre incluir `destination_type=WEBSITE` ao criar ad sets de conversão no site.

---

## 9. Configurações Corrigidas no Ad Set de Produção

Após criar o ad set via Bruno, duas correções foram necessárias via API direta:

```bash
# Fix 1: destination_type
PATCH /120244213653710671
  destination_type=WEBSITE

# Fix 2: Advantage+ Audience
PATCH /120244213653710671
  targeting={"age_min":25,"geo_locations":{...},"targeting_automation":{"advantage_audience":1}}
```

**Essas correções foram incorporadas ao Bruno** para que ele faça corretamente desde a criação:
- `destination_type` agora é parâmetro obrigatório no tool `criar_conjunto_anuncios_meta`
- System prompt atualizado com regras explícitas sobre Advantage+ e age_max
- Seção `<setup_padrao_meta_ads>` adicionada com configuração validada em produção

---

## 10. Atualizações no System Prompt do Bruno

### Seção `<funil_scala>` — nova
Documenta o funil completo para que Bruno entenda por que o link deve ser sempre o site (nunca WhatsApp direto) e por que `wa_button_click` é a conversão correta.

### Seção `<setup_padrao_meta_ads>` — nova
Configuração padrão validada em produção para campanhas de conversão:
- Campanha: OUTCOME_LEADS, AUCTION
- Ad Set: OFFSITE_CONVERSIONS, WEBSITE, Advantage+ ON, age_min 25
- Ad: image_hash placeholder, link ao site, LEARN_MORE

### Regra adicionada às `<regras_absolutas>`
> "Para criar ad set: SEMPRE incluir destination_type=WEBSITE em campanhas de conversão no site."
> "O link de destino dos anúncios é SEMPRE o site da Scala, nunca direto para WhatsApp."

### Correção crítica na tool `criar_anuncio_meta`
**Antes:** Descrição dizia "FLUXO OBRIGATORIO: 1) Chame upload_imagem_meta"
**Depois:** Descrição diz "Use image_hash 850b86ce7876a024f5c2d4e17054ca1c diretamente. NÃO chame upload_imagem_meta."

Isso resolvia o loop: Bruno tentava fazer upload → upload falhava → Bruno reportava erro → nunca criava os anúncios.

---

## 11. Roadmap para Escala (documentado para Bruno)

Quando a campanha tiver 50+ conversões, sequência recomendada:

1. **Retargeting** — Custom Audience: visitantes do site que não clicaram no WhatsApp
2. **Lookalike 1%** — baseado em números de clientes que fecharam (lista manual por enquanto)
3. **Interesses** — Gestores de tráfego, Marketing digital, Meta Ads (quando tiver verba maior)
4. **Aumento de budget** — só com 3-5 dias de dados, +20% por vez
5. **CBO** — quando tiver 2+ ad sets com dados, migrar para Campaign Budget Optimization

---

## 12. Estado Final ao Encerrar a Sessão

| Item | Estado |
|------|--------|
| Pixel `1466153678449297` | ✅ Instalado e validado no site |
| Evento `wa_button_click` | ✅ Disparando corretamente |
| Meta App em Live mode | ✅ |
| Campanha PAUSED | ✅ IDs documentados |
| Ad set com config correta | ✅ WEBSITE + Advantage+ |
| 3 anúncios com copy + link correto | ✅ Aguardando imagens reais |
| Bruno capacitado para criar tudo do zero | ✅ |
| Bruno tool `destination_type` | ✅ |
| Bruno system prompt com funil e setup padrão | ✅ |

**Próximo passo:** Paulo cria os criativos no Canva → fornece URLs → upload via API → substituir `image_hash` nos 3 anúncios → ativar campanha.
