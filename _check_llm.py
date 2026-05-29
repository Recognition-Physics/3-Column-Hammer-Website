import httpx

body = {
    "model": "gpt-4o",
    "stream": True,
    "messages": [{"role": "user", "content": "Hello"}],
    "elevenlabs_extra_body": {"voice_scenario": "hammer"},
}
r = httpx.post(
    "https://hammer-finalsite.vercel.app/api/elevenlabs/chat/completions",
    json=body,
    timeout=60,
)
print("HTTP", r.status_code)
print(r.text[:500])

body2 = {
    "model": "gpt-4o",
    "stream": True,
    "messages": [{"role": "user", "content": "Hello"}],
    "elevenlabs_extra_body": {"voice_scenario": "pen"},
}
r2 = httpx.post(
    "https://hammer-finalsite.vercel.app/api/elevenlabs/chat/completions",
    json=body2,
    timeout=60,
)
print("pen HTTP", r2.status_code)
print(r2.text[:500])
