import asyncio
from playwright.async_api import async_playwright

async def test_site(url: str):
    errors = []
    logs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            permissions=["microphone"],
            locale="en-US",
        )
        page = await context.new_page()
        page.on("console", lambda msg: logs.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2000)

        # Open nav panel
        how = page.locator('[data-panel="how"]').first
        if await how.count():
            await how.click()
            await page.wait_for_timeout(800)

        btn = page.locator("#navPanelFootVoiceBtn")
        print("nav btn count", await btn.count())
        if not await btn.count():
            print("No nav panel voice button found")
            await browser.close()
            return

        cls_before = await btn.get_attribute("class")
        print("class before", cls_before)
        await btn.click()
        await page.wait_for_timeout(8000)
        cls_after = await btn.get_attribute("class")
        hint = await page.locator(".nav-panel__foot-hint").inner_text()
        eyebrow = await page.locator(".nav-panel__foot-eyebrow").inner_text()
        print("class after", cls_after)
        print("eyebrow", eyebrow)
        print("hint", hint)
        print("--- console ---")
        for line in logs[-40:]:
            print(line)
        print("--- page errors ---")
        for line in errors:
            print(line)
        await browser.close()

asyncio.run(test_site("https://hammer-finalsite.vercel.app/"))
