import asyncio
import json
import httpx
import websockets

async def main():
    r = httpx.get("https://hammer-finalsite.vercel.app/api/elevenlabs/token", timeout=15)
    signed_url = r.json()["signed_url"]
    sep = "&" if "?" in signed_url else "?"
    url = f"{signed_url}{sep}source=js_sdk&version=1.8.0"
    print("connecting", url[:120], "...")
    try:
        async with websockets.connect(url, subprotocols=["convai"]) as ws:
            print("open")
            for i in range(5):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=8)
                    print("msg", i, str(msg)[:500])
                except asyncio.TimeoutError:
                    print("timeout waiting for msg", i)
                    break
    except Exception as e:
        print("error", type(e).__name__, e)

asyncio.run(main())
