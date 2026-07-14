import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

# GitHub'dagi index.html faylini o'qish uchun sozlamalar
templates = Jinja2Templates(directory=".")

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://tongarm.onrender.com/")
# Siz uchun yaratgan rasmimizning to'g'ridan-to'g'ri havolasi
IMAGE_URL = "https://raw.githubusercontent.com/otabekturamirzayev/gram-ton-earn/main/71855220426954431.jpeg"  # Agar Github'ga rasmni yuklagan bo'lsangiz, shuni yoki pastdagi havolani qo'ying:
# Muqobil ravishda to'g'ridan-to'g'ri ushbu havolani ishlatsangiz ham bo'ladi:
IMAGE_URL = "https://i.ibb.co/3mN9Y7r/gram-ton-earn.jpg" # Biz yaratgan rasm havolasi

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/start"):
            # Inglizcha chiroyli va jozibador matn
            caption_text = (
                "👋 Welcome to GRAM TON EARN!\n\n"
                "The ultimate Telegram Mini App where you can earn real $TON coins just by inviting your friends and completing simple daily tasks! 💎\n\n"
                "🔥 How to Start?\n"
                "1️⃣ Tap the 'Launch App' button below.\n"
                "2️⃣ Complete easy social tasks.\n"
                "3️⃣ Invite 5 friends and get 3 TON instantly!\n\n"
                "🚀 *Fast, secure, and built on the TON Blockchain. Let's grow together!*"
            )
            
            # Mini App ochuvchi Inline Tugma
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
                            "url": "https://t.me/Gram5000prize_bot"  # O'z kanalingiz linkini qo'ysangiz ham bo'ladi
                        }
                    ]
                ]
            }
            
            # Telegram'ga rasm, matn va tugmani yuborish (sendPhoto)
            payload = {
                "chat_id": chat_id,
                "photo": IMAGE_URL,
                "caption": caption_text,
                "parse_mode": "Markdown",
                "reply_markup": reply_markup
            }
            
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            requests.post(telegram_url, json=payload)
            
    return {"status": "ok"}
