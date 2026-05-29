import httpx
import re

r = httpx.get("https://hammer-finalsite.vercel.app/", timeout=15)
m = re.search(r'src="(/assets/index-[^"]+\.js)"', r.text)
print("bundle", m.group(1) if m else None)
if not m:
    raise SystemExit(1)
js = httpx.get("https://hammer-finalsite.vercel.app" + m.group(1), timeout=30).text
for s in [
    "No voice session setup strategy",
    "VoiceConversation",
    "/api/elevenlabs/token",
    "VITE_ENABLE_BROWSER_VOICE",
    "setSetupStrategy",
    "webSessionSetup",
]:
    print(s, js.find(s))
