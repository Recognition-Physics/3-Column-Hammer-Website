from pathlib import Path

for label, glob in [
    ("local", r"c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge\demo\realtime-sales-demo\web\dist\assets\index-*.js"),
    ("prod", None),
]:
    if label == "prod":
        import httpx, re
        r = httpx.get("https://hammer-finalsite.vercel.app/", timeout=15)
        m = re.search(r'src="(/assets/index-[^"]+\.js)"', r.text)
        text = httpx.get("https://hammer-finalsite.vercel.app" + m.group(1), timeout=30).text
    else:
        text = next(Path(r"c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge\demo\realtime-sales-demo\web\dist\assets").glob("index-*.js")).read_text(encoding="utf-8")
    print("===", label, "===")
    for s in [
        "preliminaryInputStream",
        "voiceIsolation",
        "rawAudioProcessor",
        "loadRawAudioProcessor",
        "MediaDeviceInput",
        "wakeLock",
        "convai",
    ]:
        print(f"  {s}: {text.find(s)}")
