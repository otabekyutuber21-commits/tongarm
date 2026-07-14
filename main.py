import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx  # Tezroq va asinxron ishlash uchun requests o'rniga httpx

app = FastAPI()

# index.html faylini o'qish uchun sozlamalar
templates = Jinja2Templates(directory=".")

BOT_TOKEN = os.getenv("8991748929:AAFsX1ey49CBSDsC5Zah6ZFkG9QFDeYevjU")
MINI_APP_URL = os.getenv "https://tongarm.onrender.com/"
IMAGE_URL = "https://i.ibb.co/3mN9Y7r/gram-ton-earn.jpg" # Biz yaratgan rasm havolasi

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Webhook manzili endi aniq '/webhook' bo'ldi
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"status": "invalid json"}
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/start"):
            caption_text = (
                "👋 *Welcome to GRAM TON EARN!*\n\n"
                "The ultimate Telegram Mini App where you can earn real *$TON* coins just by inviting your friends and completing simple daily tasks! 💎\n\n"
                "🔥 *How to Start?*\n"
                "1️⃣ Tap the *'Launch App'* button below.\n"
                "2️⃣ Complete easy social tasks.\n"
                "3️⃣ Invite 5 friends and get *3 TON* instantly!\n\n"
                "🚀 _Fast, secure, and built on the TON Blockchain. Let's grow together!_"
            )
            
            reply_markup = {
                "inline_keyboard": [
                    [
                        {
                            "text": "🚀 Launch App",
                            "web_app": {"url": MINI_APP_URL}
                        }
                    ],
                    [
                        {
                            "text": "📢 Join Community",
                            "url": "https://t.me/Gram5000prize_bot"
                        }
                    ]
                ]
            }
            
            payload = {
                "chat_id": chat_id,
                "photo": IMAGE_URL,
                "caption": caption_text,
                "parse_mode": "Markdown",
                "reply_markup": reply_markup
            }
            
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            # Asinxron so'rov yuboramiz
            async with httpx.AsyncClient() as client:
                await client.post(telegram_url, json=payload)
            
    return {"status": "ok"}import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx  # Tezroq va asinxron ishlash uchun requests o'rniga httpx

app = FastAPI()

# index.html faylini o'qish uchun sozlamalar
templates = Jinja2Templates(directory=".")

BOT_TOKEN = os.getenv("8991748929:AAFsX1ey49CBSDsC5Zah6ZFkG9QFDeYevjU")
MINI_APP_URL = os.getenv "https://tongarm.onrender.com/"
IMAGE_URL = "https://i.ibb.co/3mN9Y7r/gram-ton-earn.jpg" # Biz yaratgan rasm havolasi

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Webhook manzili endi aniq '/webhook' bo'ldi
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"status": "invalid json"}
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/start"):
            caption_text = (
                "👋 *Welcome to GRAM TON EARN!*\n\n"
                "The ultimate Telegram Mini App where you can earn real *$TON* coins just by inviting your friends and completing simple daily tasks! 💎\n\n"
                "🔥 *How to Start?*\n"
                "1️⃣ Tap the *'Launch App'* button below.\n"
                "2️⃣ Complete easy social tasks.\n"
                "3️⃣ Invite 5 friends and get *3 TON* instantly!\n\n"
                "🚀 _Fast, secure, and built on the TON Blockchain. Let's grow together!_"
            )
            
            reply_markup = {
                "inline_keyboard": [
                    [
                        {
                            "text": "🚀 Launch App",
                            "web_app": {"url": MINI_APP_URL}
                        }
                    ],
                    [
                        {
                            "text": "📢 Join Community",
                            "url": "https://t.me/Gram5000prize_bot"
                        }
                    ]
                ]
            }
            
            payload = {
                "chat_id": chat_id,
                "photo": IMAGE_URL,
                "caption": caption_text,
                "parse_mode": "Markdown",
                "reply_markup": reply_markup
            }
            
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            # Asinxron so'rov yuboramiz
            async with httpx.AsyncClient() as client:
                await client.post(telegram_url, json=payload)
            
    return {"status": "ok"}
if name == "main":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
