import urllib.request, json

req = urllib.request.Request(
    "https://api.vercel.com/v6/deployments?projectId=prj_s29RA7iViyWfG2IDxsDLOLqw9VLk&teamId=team_L1tmVcQ2MeXEiZsXEy5yFN9B&limit=1",
    headers={"Authorization": "Bearer <VERCEL_API_TOKEN>"}  # token em CLAUDE.md
)
r = json.loads(urllib.request.urlopen(req).read())
d = r["deployments"][0]
print(d["state"], d.get("url", ""))
