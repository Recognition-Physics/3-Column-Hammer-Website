import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(permissions=["microphone"])
        page = await context.new_page()
        await page.goto("https://hammer-finalsite.vercel.app/", wait_until="networkidle")
        result = await page.evaluate("""async () => {
          const out = {};
          try {
            const s1 = await navigator.mediaDevices.getUserMedia({ audio: true });
            out.basic = 'ok';
            s1.getTracks().forEach(t => t.stop());
          } catch (e) {
            out.basic = e.name + ': ' + e.message;
          }
          try {
            const s2 = await navigator.mediaDevices.getUserMedia({
              audio: {
                voiceIsolation: true,
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                channelCount: { ideal: 1 },
                sampleRate: { ideal: 16000 },
              }
            });
            out.full = 'ok';
            s2.getTracks().forEach(t => t.stop());
          } catch (e) {
            out.full = e.name + ': ' + e.message;
          }
          try {
            const ctx = new AudioContext({ sampleRate: 16000 });
            out.audioContext = 'ok';
            await ctx.audioWorklet.addModule('data:application/javascript,registerProcessor("x",class extends AudioWorkletProcessor{process(){return true}})');
            out.worklet = 'ok';
            await ctx.close();
          } catch (e) {
            out.worklet = e.name + ': ' + e.message;
          }
          try {
            await navigator.permissions.query({ name: 'microphone' });
            out.perm = 'ok';
          } catch (e) {
            out.perm = e.name + ': ' + e.message;
          }
          return out;
        }""")
        print(result)
        await browser.close()

asyncio.run(main())
