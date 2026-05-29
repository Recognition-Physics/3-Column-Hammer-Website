"""
Configures the ElevenLabs agent for dynamic per-call greeting variety and
routes all LLM calls through the Fly.io backend so session state persists.

- first_message is cleared so ElevenLabs calls our custom LLM at the start
  of every call instead of repeating a static line.
- initial_wait_time=1 is the minimum ElevenLabs allows; it fires the LLM
  call 1 second after connect (covers SIP handshake time).
- The custom LLM /_opening_greeting() picks randomly from PEN_CHALLENGE_GREETINGS
  on every call, giving full 12-variant rotation automatically.
- custom_llm_url points to Fly.io (NOT Vercel) so that fill_hammer_account_field
  session state persists reliably across all conversation turns. Vercel serverless
  /tmp files are NOT guaranteed to survive between invocations, which causes the
  AI to re-ask for fields already provided. Fly.io is a persistent process.

Run this script any time the ElevenLabs agent is reset or re-created.
"""
import httpx
import re
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "demo" / "realtime-sales-demo" / "server"))

env = open(
    r"c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge\demo\realtime-sales-demo\server\.env"
).read()
key = re.search(r"ELEVENLABS_API_KEY=(.+)", env).group(1).strip()
aid = re.search(r"ELEVENLABS_AGENT_ID=(.+)", env).group(1).strip()

r = httpx.patch(
    f"https://api.elevenlabs.io/v1/convai/agents/{aid}",
    headers={"xi-api-key": key, "Content-Type": "application/json"},
    json={
        "conversation_config": {
            "agent": {
                "first_message": "",
                "prompt": {
                    "llm": "custom-llm",
                    "custom_llm": {
                        "url": "https://hammer-voice-telephony.fly.dev/api/elevenlabs",
                    },
                },
            },
            "turn": {"initial_wait_time": 1},
        }
    },
    timeout=20,
)
import json
d = r.json()
cc = d.get("conversation_config", {})
print("status:", r.status_code)
print("first_message:", repr(cc.get("agent", {}).get("first_message")))
print("initial_wait_time:", cc.get("turn", {}).get("initial_wait_time"))
custom_llm = cc.get("agent", {}).get("prompt", {}).get("custom_llm", {})
print("custom_llm_url:", custom_llm.get("url"))
