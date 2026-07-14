# Gram 5000 Prize — Python Backend, Bot & Mini App Deploy Guide

Ushbu yo'riqnoma orqali siz loyihaning Python (FastAPI + SQLite) backend qismini va `aiogram` Telegram botini **Render** va **UptimeRobot**-ga mutlaqo bepul va xavfsiz deploy qilishingiz mumkin.

---

## 📁 Fayllar Strukturasi

```bash
/python-backend
  ├── main.py          # FastAPI Backend (TMA API endpoints, admin login, signature check)
  ├── bot.py           # aiogram v3 Telegram Bot (start buyrug'i, til tanlash, WebApp ochish)
  ├── database.py      # SQLite Ma'lumotlar bazasi logic (jadvallar va SQL so'rovlar)
  ├── requirements.txt # Python dependencies (aiogram, fastapi, uvicorn va h.k.)
  └── README.md        # Ushbu yo'riqnoma fayli
```

---

## ⚡ 1. Render-da Deploy qilish

Render platformasida bizga **ikkita** servis kerak bo'ladi (yoki bitta universal servis orqali barchasini birlashtirish ham mumkin). Eng oson va tejamkor usul - bitta Web Service yaratib, unda FastAPI backendni ishga tushirish, Telegram botni esa background task sifatida FastAPI-ga ulab yuborish.

### Qadamma-qadam ko'rsatma:

1. **GitHub Repozitoriya yaratish**:
   - Yangi GitHub repozitoriya yarating.
   - `/python-backend` ichidagi barcha fayllarni (yoki butun loyihani) ushbu GitHub repozitoriyaga yuklang (push qiling).

2. **Render-da Web Service yaratish**:
   - [Render.com](https://render.com) saytiga kiring va ro'yxatdan o'ting.
   - **New +** -> **Web Service** tanlang.
   - GitHub repozitoriyangizni ulang.

3. **Sozlamalarni kiritish**:
   - **Name**: `gram5000prize-backend`
   - **Root Directory**: `python-backend` (agar fayllar shu papkada bo'lsa, aks holda bo'sh qoldiring)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000` (agar bitta servisda botni ham qo'shib yubormoqchi bo'lsangiz, start commandga: `python bot.py & uvicorn main:app --host 0.0.0.0 --port 10000` yozishingiz mumkin!)

4. **Environment Variables (Atrof-muhit o'zgaruvchilari)**:
   Render sozlamalarida **Environment** bo'limiga kiring va quyidagi maxfiy o'zgaruvchilarni kiriting:
   - `BOT_TOKEN` = `8991748929:AAFsX1ey49CBSDsC5Zah6ZFkG9QFDeYevjU`
   - `WEBAPP_URL` = `Sizning frontend hosted URL-ingiz` (masalan, AI Studio dev/production URL yoki Render-dagi frontend manzili)
   - `PORT` = `10000`

5. **💾 SQLite Bazani Saqlab Qolish (Render Persistent Disk)**:
   Render-da bepul konteynerlar har safar qayta qurilganda (rebuild) SQLite fayllari o'chib ketadi. Buni oldini olish uchun:
   - Render Web Service sozlamalaridan **Disks** bo'limiga o'ting.
   - **Add Disk** tugmasini bosing.
   - **Name**: `database-storage`
   - **Mount Path**: `/data`
   - Keyin `database.py` faylida `DB_NAME = "/data/database.db"` deb o'zgartirib qo'ying. Shunda foydalanuvchilar va ularning balanslari har qanday o'chib-yonishda ham 100% omon qoladi!

---

## 🌐 2. UptimeRobot yordamida Botni 24/7 Aktiv ushlash

Render bepul rejasida (Free plan) agar servisga 15 daqiqa davomida hech qanday so'rov kelmasa, u "uyqu rejimiga" (Sleep mode) o'tadi. Bu esa botni o'chib qolishiga sabab bo'ladi. UptimeRobot orqali buni bartaraf etamiz:

1. [UptimeRobot.com](https://uptimerobot.com) saytiga kiring.
2. **Add New Monitor** tugmasini bosing.
3. **Monitor Type**: `HTTPS` tanlang.
4. **Friendly Name**: `Gram 5000 Health`
5. **URL (or IP)**: `https://sizning-render-web-servisingiz.onrender.com/api/health`
6. **Monitoring Interval**: Har `5 minutes` (har 5 daqiqada pingleydi).
7. **Create Monitor** bosing.

Shu orqali UptimeRobot har 5 daqiqada FastAPI-ning `/api/health` manziliga so'rov yuborib turadi va Render bepul konteyneri hech qachon uyquga ketmaydi, botingiz esa **24/7 uzluksiz** ishlaydi!

---

## 🔒 3. Admin Panel sozlamalari

Admin panelga kirish paroli: **`bekborz47`**
Admin panel orqali siz:
- Minimal yechish limitini va taklif uchun beriladigan bonuslarni o'zgartira olasiz.
- Kutilayotgan pul yechish so'rovlarini ko'rib, "Tasdiqlash" (Approve) va "Rad etish" (Reject) bosa olasiz.
- Tasdiqlanganda foydalanuvchiga Telegram bot orqali avtomatik ravishda chiroyli xabar boradi.

Hamyon manzilingiz: `UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV`
Foydalanuvchilar pul yechishdan oldin ushbu hamyonga **0.5 TON** o'tkazib, tranzaksiya isboti (Tx Hash) kiritishlari shart.
