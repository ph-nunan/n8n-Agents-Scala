import urllib.request, json

TOKEN = "EAAMJGenE0rYBQZBLYp6hWbwsZBlSJqZAly0dV9f7EJRRIbZAfUISnr9usegZCSdAjgdhOenSO6Sf8ybj117D3q3cKT8fcxWZCgbFsAyUZCb5tCHTaJC1c99DGCuylr0y2RnFtqtmNpkqN1LmJqnasqkoDvrKUzdaejFSi37EL7vl4w7ZCd9zj8u1jQB198n9hLRXMgZDZD"
CAMPAIGN = "120244213653500671"
ADSET = "120244272147020671"

# Campanha total
url = f"https://graph.facebook.com/v22.0/{CAMPAIGN}/insights?fields=impressions,reach,clicks,spend,cpc,ctr,actions,date_start,date_stop&date_preset=maximum&access_token={TOKEN}"
r = json.loads(urllib.request.urlopen(url).read())

if "error" in r:
    print("ERRO:", r["error"])
else:
    d = r["data"][0]
    acts = {a["action_type"]: a["value"] for a in d.get("actions", [])}
    lpv = int(acts.get("landing_page_view", 0))
    gasto = float(d["spend"])
    print(f"=== CAMPANHA — {d['date_start']} a {d['date_stop']} ===")
    print(f"Alcance: {d['reach']} | Impressoes: {d['impressions']}")
    print(f"Cliques: {d['clicks']} | CTR: {float(d['ctr']):.2f}%")
    print(f"CPC: R${float(d['cpc']):.2f} | Gasto total: R${gasto:.2f}")
    print(f"LPVs: {lpv} / 500 meta ({lpv/5:.1f}%)")
    print(f"CPL (por LPV): R${gasto/lpv:.2f}" if lpv else "CPL: N/A")
    print(f"Leads pixel: {acts.get('lead', '0')}")

# Ads individuais
url2 = f"https://graph.facebook.com/v22.0/{ADSET}/ads?fields=name,status&access_token={TOKEN}"
ads_r = json.loads(urllib.request.urlopen(url2).read())
ad_ids = [(a["id"], a["name"]) for a in ads_r.get("data", [])]

print("\n=== ADS INDIVIDUAIS ===")
for aid, aname in ad_ids:
    url3 = f"https://graph.facebook.com/v22.0/{aid}/insights?fields=impressions,clicks,spend,ctr,actions&date_preset=maximum&access_token={TOKEN}"
    ar = json.loads(urllib.request.urlopen(url3).read())
    if ar.get("data"):
        a = ar["data"][0]
        aa = {x["action_type"]: x["value"] for x in a.get("actions", [])}
        print(f"\n{aname}")
        print(f"  Impressoes: {a['impressions']} | Cliques: {a['clicks']} | CTR: {float(a['ctr']):.2f}%")
        print(f"  Gasto: R${float(a['spend']):.2f} | LPV: {aa.get('landing_page_view', '0')}")
