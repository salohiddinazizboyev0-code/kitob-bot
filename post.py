import os, sys, json, datetime, urllib.request, urllib.parse

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL = os.environ["CHANNEL"]
OWNER = os.environ["OWNER_ID"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
START = datetime.date(2026, 10, 16)  # 1-kitob chiqadigan sana
API = f"https://api.telegram.org/bot{TOKEN}/"


def tg(method, **params):
    data = {k: json.dumps(v) if isinstance(v, (dict, list)) else v
            for k, v in params.items()}
    req = urllib.request.Request(API + method, urllib.parse.urlencode(data).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)["result"]


def books():
    with open("books.txt", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def write_post(book):
    prompt = (
        f"Sen o'zbek tilidagi kitob kanali muharririsan. Kitob: {book}.\n"
        "Shu kitob haqida Telegram kanali uchun qisqa, qiziqarli post yoz (700 belgidan oshmasin).\n"
        "Qoidalar:\n"
        "- Faqat aniq va ishonchli ma'lumotlarni yoz. Aniq bilmasang, o'sha qismni tashlab ket.\n"
        "- Iqtibos, sana, raqam va syujet tafsilotlarini to'qima.\n"
        "- Syujetning oxirini ochib yuborma.\n"
        "- Format: faqat <b>qalin</b> va <i>qiya</i> teglari. Markdown (*, #, `) ishlatma.\n"
        "- Birinchi qatorda kitob nomi va muallifi (<b> ichida), keyin tavsif, "
        "oxirida 2-3 ta hashtag.\n"
        "- Faqat post matnini qaytar, boshqa izoh yozma."
    )
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        body,
        {"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY},
    )
    with urllib.request.urlopen(req) as r:
        text = json.load(r)["candidates"][0]["content"]["parts"][0]["text"]
    text = text.strip().replace("```html", "").replace("```", "").strip()
    return text.replace("&", "&amp;")


def buttons(i):
    return {"inline_keyboard": [[
        {"text": "✅ Yuborish", "callback_data": "ok"},
        {"text": "🔄 Qayta yozish", "callback_data": f"re:{i}"},
        {"text": "❌ Bekor", "callback_data": "no"},
    ]]}


def draft(i):
    book = books()[i % len(books())]
    tg("sendMessage", chat_id=OWNER, text=write_post(book),
       parse_mode="HTML", reply_markup=buttons(i))


def check():
    updates = tg("getUpdates", timeout=0)
    done = set()
    for u in updates:
        cq = u.get("callback_query")
        if not cq or str(cq["from"]["id"]) != OWNER:
            continue
        try:
            mid = cq["message"]["message_id"]
            act = cq["data"]
            if mid in done:
                continue
            label = None
            if act == "ok":
                tg("copyMessage", chat_id=CHANNEL, from_chat_id=OWNER, message_id=mid)
                done.add(mid)
                label = "✅ Kanalga yuborildi"
            elif act == "no":
                done.add(mid)
                label = "❌ Bekor qilindi"
            elif act.startswith("re:"):
                i = int(act[3:])
                book = books()[i % len(books())]
                tg("editMessageText", chat_id=OWNER, message_id=mid,
                   text=write_post(book), parse_mode="HTML", reply_markup=buttons(i))
            if label:
                tg("editMessageReplyMarkup", chat_id=OWNER, message_id=mid,
                   reply_markup={"inline_keyboard": [[{"text": label, "callback_data": "x"}]]})
        except Exception as e:
            print("Xato:", e)
        try:
            tg("answerCallbackQuery", callback_query_id=cq["id"])
        except Exception:
            pass
    if updates:
        tg("getUpdates", offset=updates[-1]["update_id"] + 1, timeout=0)


mode = sys.argv[1] if len(sys.argv) > 1 else "check"
if mode == "draft":
    day = (datetime.date.today() - START).days
    if day >= 0:
        draft(day)
else:
    check()
