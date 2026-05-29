import httpx
import re

r = httpx.get("https://hammer-finalsite.vercel.app/", timeout=20)
print("status", r.status_code)
m = re.search(r'src="(/assets/index-[^"]+\.js)"', r.text)
print("bundle", m.group(1) if m else "none")
if m:
    js = httpx.get("https://hammer-finalsite.vercel.app" + m.group(1), timeout=30).text
    needles = [
        "VoiceConversation",
        "No voice session setup strategy",
        "platform/web",
        "setSetupStrategy",
        "getElSignedUrl",
        "elevenlabs/token",
        "OpenAIRealtimeWebRTC",
        "RealtimeSession",
    ]
    for n in needles:
        print(n, "->", n in js)
