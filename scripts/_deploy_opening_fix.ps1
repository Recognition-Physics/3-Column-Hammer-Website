$repo = "c:\Users\tbenn\Desktop\SellMeAPenChallenge\Hammer-Sell-me-a-pen-challenge"
git -C $repo add demo/realtime-sales-demo/server/elevenlabs_agent.py
git -C $repo commit -m "fix(voice): detect opening turn by absence of assistant messages not user speech"
git -C $repo push hammerfinalsite main
$env:Path = "$env:USERPROFILE\.fly\bin;$env:Path"
Set-Location $repo
fly deploy --config demo/realtime-sales-demo/fly.toml --app hammer-voice-telephony
