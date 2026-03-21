# Sessão 2026-03-21 — Primeira Campanha Meta Ads ao Vivo

## Resumo
Sessão completa de setup e lançamento da primeira campanha Meta Ads da Scala.
Upload de 11 imagens, criação de 3 anúncios, definição do plano operacional e campanha ativada.

---

## O que foi feito

### 1. Upload de imagens para o Meta
- 11 imagens uploadadas: 1 estática + 5 do Carrossel 1 + 5 do Carrossel 2
- Pasta local: `C:\Users\nunan-pc\Pictures\SCALA\ADS SCALA\`
- **Carrossel 1:** usados 1.png, 2.png, 3.png, 4.1.png (sem o 4.png), ChatGPT Image
- Todos os hashes salvos no plano operacional

### 2. Copies criadas e aprovadas
- Textos principais: fornecidos por Paulo
- Títulos dos cards: sugeridos e aprovados (ver plano operacional para copies completas)

### 3. Criação dos 3 anúncios
Processo teve vários aprendizados técnicos (ver seção Erros abaixo):

| Anúncio | Creative ID | Ad ID |
|---|---|---|
| Estático — Vendas no escuro | `955974620281208` | `120244272148560671` |
| Carrossel 1 — Funil quebrado | `897804036413244` | `120244272149010671` |
| Carrossel 2 — Concorrente automatizou | `2239822923454857` | `120244272149350671` |

### 4. Novo ad set criado
O ad set original (`120244213653710671`) foi arquivado porque:
- Tinha `bid_strategy: LOWEST_COST_WITH_BID_CAP` com cap de R$10 (ruim para R$10/dia)
- Attribution window imutável após criação — não dá pra trocar optimization_goal sem recriar

**Novo ad set:** `120244272147020671`
- Otimização: `LANDING_PAGE_VIEWS`
- Bid: `LOWEST_COST_WITHOUT_CAP`
- Budget: R$1.000 cents = R$10/dia

### 5. Plano operacional definido
- Arquivo: `plano-operacional-meta-ads.md`
- Framework de análise: CTR/CPV benchmarks, calendário semanal, regra dos R$50 por criativo
- Plano de evolução: Fase 1 (LPV) → Fase 2 (Conversões) → Fase 3 (Lookalike)

### 6. Campanha ativada
- Status: **ACTIVE** desde 2026-03-21
- Todos os 3 anúncios: **ACTIVE**
- Links verificados: todos apontando para `https://portfolio-scala.vercel.app/`

### 7. Foto de perfil da página Facebook
- Atualizada manualmente para o logo Scala (S metálico fundo preto)
- Arquivo: `C:\Users\nunan-pc\Pictures\SCALA\assets scala\logo-icon.png.png`
- Não foi possível via API — requer permissão `pages_manage_metadata` não incluída no token do system user

---

## Erros e aprendizados técnicos

### API v19.0 estava depreciada
- **Problema:** Toda chamada de criação de criativo retornava erro `1487390` sem mensagem clara
- **Causa:** API v19.0 foi depreciada em fevereiro de 2026 (janela de 2 anos encerrou)
- **Fix:** Usar `v22.0` em todas as chamadas

### Ad Account ID canônico diferente do alias
- **Problema:** `act_120244137424200671` funcionava para upload de imagens mas não para criar criativos
- **Causa:** É um alias. O ID canônico real é `act_1605651367382391`
- **Fix:** Sempre usar `act_1605651367382391` para criar criativos e ads
- **Importante:** Imagens uploadadas para o alias não ficam disponíveis na conta canônica — re-upload necessário

### Carrossel precisa de `call_to_action` em cada card
- **Problema:** Criativo carousel era criado com sucesso mas o ad retornava erro `1443225` ("imagem ausente")
- **Causa:** Imagens uploadadas para conta errada (alias vs canônico)
- **Fix secundário:** Além de re-fazer o upload para conta correta, adicionar `call_to_action: {type: LEARN_MORE}` em cada `child_attachment` e também no nível do `link_data`

### Attribution window imutável
- **Problema:** Ao tentar trocar `OFFSITE_CONVERSIONS` → `LANDING_PAGE_VIEWS`, erro `1885559`
- **Causa:** A janela de atribuição (`attribution_spec`) não pode ser alterada após criação do ad set
- **Fix:** Criar novo ad set do zero com a configuração correta

### `promoted_object` imutável
- **Problema:** Tentei adicionar `promoted_object` com pixel ao novo ad set após criação
- **Causa:** Campo imutável após criação
- **Conclusão:** Para LPV não é necessário — pixel continua alimentando via site normalmente

### `pages_manage_metadata` ausente no token
- **Problema:** Não foi possível trocar a foto de perfil da página via API
- **Causa:** O system user token foi configurado apenas para Ads e WhatsApp
- **Fix:** Paulo fez a alteração manualmente pelo Facebook

---

## Estado final da conta

| Item | Valor |
|---|---|
| Campanha | ACTIVE `120244213653500671` |
| Ad Set | ACTIVE `120244272147020671` — R$10/dia, LPV, sem bid cap |
| Ads | 3 × ACTIVE |
| Pixel | Ativo, recebendo PageView |
| Pagamento | PayPal `nunan38@gmail.com` |
| Foto da página | Logo Scala atualizada |

---

## Próximos passos
- **Semana 1:** Confirmar que impressões estão chegando
- **Semana 2:** Analisar CTR e CPV por criativo
- **Semana 3:** Decisão sobre criativos com base nos dados
- **Fase 2:** Quando pixel atingir 500 eventos `wa_button_click`, criar novo ad set com `OFFSITE_CONVERSIONS`
