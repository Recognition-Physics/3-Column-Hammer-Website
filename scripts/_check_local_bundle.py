from pathlib import Path

js = Path(r"c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge\demo\realtime-sales-demo\web\dist\assets").glob("index-*.js")
for p in js:
    text = p.read_text(encoding="utf-8")
    print(p.name)
    for s in [
        "No voice session setup strategy",
        "setSetupStrategy",
        "webSessionSetup",
        "VoiceSessionSetup",
        "platform/web",
    ]:
        print(f"  {s}: {text.find(s)}")
