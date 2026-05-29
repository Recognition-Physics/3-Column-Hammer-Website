from pathlib import Path
import httpx, re

def check(text, label):
    print("===", label, "===")
    for s in [
        "visibilitychange",
        "Register the web strategy",
        "setupStrategy",
        "No voice session setup strategy registered",
        "Failed to load the rawAudioProcessor worklet",
    ]:
        idx = text.find(s)
        print(f"  {s}: {idx}")

local = next(Path(r"c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge\demo\realtime-sales-demo\web\dist\assets").glob("index-*.js")).read_text(encoding="utf-8")
check(local, "local build")

r = httpx.get("https://hammer-finalsite.vercel.app/", timeout=15)
m = re.search(r'src="(/assets/index-[^"]+\.js)"', r.text)
prod = httpx.get("https://hammer-finalsite.vercel.app" + m.group(1), timeout=30).text
check(prod, "production")
