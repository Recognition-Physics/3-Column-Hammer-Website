from pathlib import Path
js = Path(r"c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge\demo\realtime-sales-demo\web\dist\assets").glob("index-*.js")
path = next(js)
text = path.read_text(encoding="utf-8")
needles = [
    "preliminaryInputStream",
    "webSessionSetup",
    "wakeLock",
    "loadRawAudioProcessor",
    "MediaDeviceInput",
    "No voice session setup strategy",
    "signedUrl only supports websocket",
]
for n in needles:
    print(n, "->", n in text)
print("file", path.name, "size", len(text))
