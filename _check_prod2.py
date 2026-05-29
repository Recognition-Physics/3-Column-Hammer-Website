import httpx
import re

r = httpx.get("https://hammer-finalsite.vercel.app/", timeout=20)
m = re.search(r'src="(/assets/index-[^"]+\.js)"', r.text)
js = httpx.get("https://hammer-finalsite.vercel.app" + m.group(1), timeout=30).text
needles = [
    "preliminaryInputStream",
    "webSessionSetup",
    "wakeLock",
    "loadRawAudioProcessor",
    "MediaDeviceInput",
    "No voice session setup strategy",
    "signedUrl only supports websocket",
    "VoiceConversation",
]
for n in needles:
    print(n, "->", n in js)
