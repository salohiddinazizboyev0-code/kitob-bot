import json, os, datetime, urllib.request, urllib.parse

TOKEN = os.environ[8846131575:AAG8_nexu66sbRcC8NljAirFv2o0LfdKEho]
CHANNEL = os.environ[@kitob_sarguzashtlari]
START = datetime.date(2026, 10, 9)   # 1-post chiqadigan sana

posts = json.load(open("posts.json", encoding="utf-8"))
day = (datetime.date.today() - START).days

if day < 0 or day >= len(posts):
    print("Bugun uchun post yo'q.")
    raise SystemExit

p = posts[day]
if p.get("photo"):
    method, data = "sendPhoto", {"chat_id": CHANNEL, "photo": p["photo"],
                                 "caption": p["text"], "parse_mode": "HTML"}
else:
    method, data = "sendMessage", {"chat_id": CHANNEL, "text": p["text"],
                                   "parse_mode": "HTML"}

url = f"https://api.telegram.org/bot{TOKEN}/{method}"
req = urllib.request.Request(url, urllib.parse.urlencode(data).encode())
print(urllib.request.urlopen(req).read().decode())
