/**
 * Auditoria completa de tracking — portfolio-scala.vercel.app
 * Verifica: hrefs, dataLayer events, Meta Pixel, CTAs corretos
 * UA: Facebook in-app browser (representa 76% do tráfego real)
 */

const { chromium } = require("playwright")

const URL = "https://portfolio-scala.vercel.app/"
const WA_NUMBER = "556181894189"
const EXPECTED_LOCATIONS = [
  "hero_primary", "navbar_desktop", "navbar_mobile", "floating",
  "funnel_comparison", "for_whom", "comparison", "how_it_works",
  "results", "mid_cta", "services_plan", "services_pricing",
  "services_bottom", "future_pacing", "faq", "contact"
]

const FB_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/16.0;FBSS/3;FBID/phone;FBLC/pt_BR;FBOP/5]"

async function clickAndCapture(page, clickFn, waitMs = 400) {
  const before = await page.evaluate(() => window.__auditDL.length)
  await clickFn()
  await page.waitForTimeout(waitMs)
  const after = await page.evaluate(() => window.__auditDL.slice())
  const newEvents = after.slice(before)
  const waEvent = newEvents.find(e => e.event === "wa_button_click")
  return { fired: !!waEvent, location: waEvent?.location || "—" }
}

async function run() {
  const browser = await chromium.launch({ headless: true })
  const ctx = await browser.newContext({
    userAgent: FB_UA,
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
  })
  const page = await ctx.newPage()

  // Intercepta navegação para wa.me (não abre o WhatsApp de verdade)
  await ctx.route("**://wa.me/**", route => route.abort())
  await ctx.route("**://api.whatsapp.com/**", route => route.abort())

  // ── PASSAGEM 1: coletar todos os links ──────────────────────────
  console.log("\n══════════════════════════════════════════════")
  console.log("AUDITORIA 1 — Scan completo de hrefs")
  console.log("══════════════════════════════════════════════")

  await page.goto(URL, { waitUntil: "networkidle", timeout: 30000 })
  await page.waitForTimeout(2000)

  // Inject dataLayer capture
  await page.evaluate(() => {
    window.__auditDL = []
    const orig = window.dataLayer || []
    window.dataLayer = new Proxy(orig, {
      get(target, prop) {
        if (prop === "push") {
          return (...args) => {
            window.__auditDL.push(...args)
            return Array.prototype.push.apply(target, args)
          }
        }
        return target[prop]
      }
    })
  })

  // Scroll para 500px para ativar FloatingCTA (visível quando scrollY > 320)
  await page.evaluate(() => window.scrollTo(0, 500))
  await page.waitForTimeout(800)

  // Abrir menu mobile para expor navbar_mobile CTA
  await page.evaluate(() => {
    const hamburger = document.querySelector("button[aria-label='Menu']")
    if (hamburger) hamburger.click()
  })
  await page.waitForTimeout(500)

  // Coletar TODOS os links (incluindo FloatingCTA e navbar_mobile agora visíveis)
  const links = await page.evaluate(() => {
    return Array.from(document.querySelectorAll("a[href]")).map(a => ({
      href: a.href,
      text: a.textContent.trim().substring(0, 60),
      hasTarget: a.target === "_blank",
      hasRel: a.rel.includes("noopener"),
      inNav: !!a.closest("nav, footer, header"),
    }))
  })

  // Fechar menu mobile
  await page.evaluate(() => {
    const hamburger = document.querySelector("button[aria-label='Menu']")
    if (hamburger) hamburger.click()
  })
  await page.waitForTimeout(300)

  // Scroll de volta ao topo
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(500)

  // Classificar
  const waLinks = links.filter(l => l.href.includes("wa.me"))
  // Só flagga #contact fora de nav/footer (CTAs que esquecemos de migrar)
  const contactLinks = links.filter(l => l.href.includes("#contact") && !l.inNav)
  const otherLinks = links.filter(l =>
    !l.href.includes("wa.me") &&
    !l.href.includes("#contact") &&
    !l.href.startsWith("javascript") &&
    l.href !== URL &&
    !l.href.endsWith("#") &&
    !l.href.endsWith(URL + "#")
  )

  console.log(`\n✅ Links wa.me encontrados: ${waLinks.length}`)
  waLinks.forEach(l => {
    const hasNumber = l.href.includes(WA_NUMBER)
    const hasTarget = l.hasTarget
    const hasRel = l.hasRel
    const status = hasNumber && hasTarget && hasRel ? "✅" : "❌"
    console.log(`  ${status} "${l.text}" → ${l.href.substring(0, 80)}`)
    if (!hasNumber) console.log(`     ⚠️  NÚMERO ERRADO — esperado ${WA_NUMBER}`)
    if (!hasTarget) console.log(`     ⚠️  SEM target="_blank"`)
    if (!hasRel)    console.log(`     ⚠️  SEM rel="noopener noreferrer"`)
  })

  console.log(`\n${contactLinks.length > 0 ? "❌" : "✅"} CTAs #contact remanescentes (fora de nav/footer): ${contactLinks.length}`)
  if (contactLinks.length > 0) {
    contactLinks.forEach(l => console.log(`  ❌ "${l.text}"`))
  }

  console.log(`\nℹ️  Outros links internos/externos: ${otherLinks.length}`)
  otherLinks.forEach(l => console.log(`  · "${l.text}" → ${l.href.substring(0, 70)}`))

  // ── PASSAGEM 2: simular scroll + verificar GTM dataLayer ────────
  console.log("\n══════════════════════════════════════════════")
  console.log("AUDITORIA 2 — GTM dataLayer por evento")
  console.log("══════════════════════════════════════════════")

  // Scroll completo para disparar todos os section_viewed
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
  await page.waitForTimeout(1500)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(500)

  // Coletar eventos acumulados no dataLayer
  const captured = await page.evaluate(() => window.__auditDL || [])
  const waEvents = captured.filter(e => e.event === "wa_button_click")
  const scrollEvents = captured.filter(e => e.event === "scroll_depth_reached")
  const sectionEvents = captured.filter(e => e.event === "section_viewed")
  const vitalsEvents = captured.filter(e => e.event === "web_vitals")

  console.log(`\n  wa_button_click: ${waEvents.length} (esperado: 0 sem clique real)`)
  console.log(`  scroll_depth_reached: ${scrollEvents.length} eventos`)
  scrollEvents.forEach(e => console.log(`    · ${e.percent}%`))
  console.log(`  section_viewed: ${sectionEvents.length} seções`)
  sectionEvents.forEach(e => console.log(`    · ${e.section}`))
  console.log(`  web_vitals: ${vitalsEvents.length} métricas`)
  vitalsEvents.forEach(e => console.log(`    · ${e.metric}: ${e.metric_value}`))

  // Verificar GTM carregado
  const gtmLoaded = await page.evaluate(() => typeof window.dataLayer !== "undefined" && window.dataLayer.some(e => e["gtm.start"]))
  console.log(`\n  GTM carregado: ${gtmLoaded ? "✅" : "❌"}`)

  // Verificar Meta Pixel
  const pixelLoaded = await page.evaluate(() => typeof window.fbq === "function")
  console.log(`  Meta Pixel (fbq): ${pixelLoaded ? "✅" : "❌"}`)

  // ── PASSAGEM 3: clicar em cada wa.me e verificar evento ─────────
  console.log("\n══════════════════════════════════════════════")
  console.log("AUDITORIA 3 — Cliques reais + evento dataLayer")
  console.log("══════════════════════════════════════════════")

  // Limpar eventos anteriores
  await page.evaluate(() => { window.__auditDL = [] })

  const results = []

  // ── 3a. CTAs estáticos da página (menu fechado, scroll 0) ────────
  const staticSelectors = await page.evaluate(() => {
    // Exclui: FloatingCTA (.floating-cta-wrap), NavBar mobile (.nav-mobile-menu), NavBar desktop (.nav-cta-desktop)
    return Array.from(document.querySelectorAll("a[href*='wa.me']"))
      .filter(a => !a.closest(".floating-cta-wrap") && !a.closest(".nav-mobile-menu") && !a.closest(".nav-cta-desktop"))
      .map((a, i) => ({ index: i, text: a.textContent.trim().substring(0, 50) }))
  })

  for (const btn of staticSelectors) {
    await page.evaluate((idx) => {
      const els = Array.from(document.querySelectorAll("a[href*='wa.me']"))
        .filter(a => !a.closest(".floating-cta-wrap") && !a.closest(".nav-mobile-menu") && !a.closest(".nav-cta-desktop"))
      els[idx]?.scrollIntoView({ block: "center" })
    }, btn.index)
    await page.waitForTimeout(300)

    const result = await clickAndCapture(page, () => page.evaluate((idx) => {
      const els = Array.from(document.querySelectorAll("a[href*='wa.me']"))
        .filter(a => !a.closest(".floating-cta-wrap") && !a.closest(".nav-mobile-menu") && !a.closest(".nav-cta-desktop"))
      els[idx]?.click()
    }, btn.index))

    results.push({ text: btn.text, ...result })
  }

  // ── 3b. NavBar desktop (sem scroll necessário) ────────
  const navDesktopText = await page.evaluate(() => {
    const el = document.querySelector(".nav-cta-desktop a[href*='wa.me']")
    return el ? el.textContent.trim().substring(0, 50) : null
  })
  if (navDesktopText) {
    const result = await clickAndCapture(page, () => page.evaluate(() => {
      document.querySelector(".nav-cta-desktop a[href*='wa.me']")?.click()
    }))
    results.push({ text: navDesktopText, ...result })
  }

  // ── 3c. NavBar mobile (requer abrir menu) ────────
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(300)
  await page.evaluate(() => {
    const hamburger = document.querySelector("button[aria-label='Menu']")
    if (hamburger) hamburger.click()
  })
  await page.waitForTimeout(400)

  const navMobileText = await page.evaluate(() => {
    const el = document.querySelector(".nav-mobile-menu a[href*='wa.me']")
    return el ? el.textContent.trim().substring(0, 50) : null
  })
  if (navMobileText) {
    const result = await clickAndCapture(page, () => page.evaluate(() => {
      document.querySelector(".nav-mobile-menu a[href*='wa.me']")?.click()
    }))
    results.push({ text: navMobileText, ...result })
  }

  // Fechar menu
  await page.evaluate(() => {
    const hamburger = document.querySelector("button[aria-label='Menu']")
    const menuOpen = document.querySelector(".nav-mobile-menu")
    if (hamburger && menuOpen) hamburger.click()
  })
  await page.waitForTimeout(300)

  // ── 3d. FloatingCTA (requer scroll > 320) ────────
  await page.evaluate(() => window.scrollTo(0, 600))
  await page.waitForTimeout(700)

  const floatingText = await page.evaluate(() => {
    const el = document.querySelector(".floating-cta-wrap a[href*='wa.me']")
    return el ? el.textContent.trim().substring(0, 50) : null
  })
  if (floatingText) {
    const result = await clickAndCapture(page, () => page.evaluate(() => {
      document.querySelector(".floating-cta-wrap a[href*='wa.me']")?.click()
    }))
    results.push({ text: floatingText, ...result })
  } else {
    results.push({ text: "FloatingCTA (não encontrado no DOM)", fired: false, location: "—" })
    console.log("  ⚠️  FloatingCTA não apareceu no DOM em scrollY=600. Verificar useEffect.")
  }

  // ── Resultados ────────────────────────────────────────────────
  console.log("")
  let allPassed = true
  results.forEach(r => {
    const ok = r.fired
    if (!ok) allPassed = false
    console.log(`  ${ok ? "✅" : "❌"} "${r.text}" → location: ${r.location}`)
  })

  // Verificar se todas as locations esperadas foram cobertas
  const firedLocations = results.filter(r => r.fired).map(r => r.location)
  const missing = EXPECTED_LOCATIONS.filter(loc => !firedLocations.includes(loc))

  console.log("\n══════════════════════════════════════════════")
  console.log("RESUMO FINAL")
  console.log("══════════════════════════════════════════════")
  console.log(`  Total links wa.me: ${waLinks.length}`)
  console.log(`  CTAs #contact remanescentes: ${contactLinks.length} ${contactLinks.length === 0 ? "✅" : "❌"}`)
  console.log(`  CTAs com evento disparado: ${results.filter(r => r.fired).length}/${results.length} ${allPassed ? "✅" : "❌"}`)
  console.log(`  GTM: ${gtmLoaded ? "✅" : "❌"} | Meta Pixel: ${pixelLoaded ? "✅" : "❌"}`)
  if (missing.length > 0) {
    console.log(`  ⚠️  Locations sem cobertura: ${missing.join(", ")}`)
  } else {
    console.log(`  Cobertura de locations: ✅ todas cobertas`)
  }

  console.log(allPassed && contactLinks.length === 0 ? "\n✅ TRACKING PERFEITO — APROVADO" : "\n❌ FALHAS ENCONTRADAS — VER ACIMA")

  await browser.close()
}

run().catch(e => { console.error(e); process.exit(1) })
