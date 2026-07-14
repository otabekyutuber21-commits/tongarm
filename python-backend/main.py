import os
import hmac
import hashlib
import urllib.parse
from fastapi import FastAPI, HTTPException, Header, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Import database module
import database

# Initialize FastAPI app
app = FastAPI(title="Gram 5000 Prize TMA Backend", version="1.0.0")

# Enable CORS for local testing and WebApp access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
BOT_TOKEN = os.getenv("BOT_TOKEN", "8991748929:AAFsX1ey49CBSDsC5Zah6ZFkG9QFDeYevjU")
LAUNCH_DATE_ISO = "2026-07-01T00:00:00Z"

# --- TELEGRAM WEBAPP INITDATA VALIDATION ---
def verify_telegram_webapp_signature(init_data: str) -> bool:
    """
    Validates Telegram WebApp initData against the bot token.
    Uses SHA-256 HMAC hashing.
    """
    if not init_data:
        return False
        
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        if "hash" not in parsed_data:
            return False
            
        received_hash = parsed_data.pop("hash")
        
        # Sort keys lexicographically and join with \n
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        # Calculate secret key
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        
        # Calculate local hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(calculated_hash, received_hash)
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

# --- PYDANTIC SCHEMAS ---

class UserRegisterRequest(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    language: Optional[str] = "uz"
    referrer_id: Optional[str] = None

class LanguageUpdateRequest(BaseModel):
    telegram_id: str
    language: str

class WithdrawalRequest(BaseModel):
    telegram_id: str
    amount: float
    wallet_address: str
    tx_hash: Optional[str] = ""

class AdminLoginRequest(BaseModel):
    password: str

class SettingItem(BaseModel):
    key: str
    value: str

class SaveSettingsRequest(BaseModel):
    settings: List[SettingItem]

class StatusUpdateRequest(BaseModel):
    status: str # approved or rejected

# --- API ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# 1. Get Live Stats (Gram automated counter + Global counts)
@app.get("/api/stats")
def get_stats():
    # Calculate automated Gram prize pool progress
    launch_time = datetime.fromisoformat(LAUNCH_DATE_ISO.replace("Z", "+00:00"))
    now = datetime.now(launch_time.tzinfo)
    hours_passed = int(max(0, (now - launch_time).total_seconds() // 3600))
    current_gram = 560 + hours_passed * 15
    
    settings = database.get_settings()
    
    # Simple count of users and referrals
    conn = database.get_db_connection()
    users_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
    referrals_count = conn.execute("SELECT COUNT(*) as count FROM referrals").fetchone()["count"]
    conn.close()
    
    return {
        "gram_stats": current_gram,
        "total_users": users_count,
        "total_referrals": referrals_count,
        "min_withdrawal": float(settings.get("min_withdrawal", "3.0")),
        "referral_bonus": float(settings.get("referral_bonus", "0.5")),
        "verification_fee": float(settings.get("verification_fee", "0.5")),
        "admin_wallet": settings.get("admin_wallet", "UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV"),
        "admin_id": settings.get("admin_id", "8939863862")
    }

# 2. Get/Create User Profile (includes referral linking)
@app.post("/api/user")
def get_or_create_user(req: UserRegisterRequest):
    user = database.get_user(req.telegram_id)
    is_new = False
    referral_applied = False
    
    if not user:
        is_new = True
        user = database.create_user(req.telegram_id, req.username or f"user_{req.telegram_id}", req.language or "uz")
        
        # Apply referral if a valid referrer exists and is not the user themselves
        if req.referrer_id and req.referrer_id != req.telegram_id:
            referrer = database.get_user(req.referrer_id)
            if referrer:
                referral_applied = database.add_referral(req.referrer_id, req.telegram_id)
                
    referrals_count = database.get_referral_count(req.telegram_id)
    return {
        "user": user,
        "referrals_count": referrals_count,
        "is_new": is_new,
        "referral_applied": referral_applied
    }

# 3. Update Language
@app.put("/api/user/lang")
def update_user_lang(req: LanguageUpdateRequest):
    user = database.get_user(req.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    database.update_user_language(req.telegram_id, req.language)
    return {"success": True, "language": req.language}

# 4. Get User Profile and Withdrawal History
@app.get("/api/user/{telegram_id}")
def get_user_profile(telegram_id: str):
    user = database.get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    referrals_count = database.get_referral_count(telegram_id)
    withdrawals = database.get_withdrawals_for_user(telegram_id)
    
    return {
        "user": user,
        "referrals_count": referrals_count,
        "withdrawals": withdrawals
    }

# 5. Get Leaderboard (TOP-10)
@app.get("/api/leaderboard")
def get_leaderboard():
    return database.get_leaderboard()

# 6. Submit Withdrawal Request
@app.post("/api/withdraw")
def request_withdrawal(req: WithdrawalRequest):
    user = database.get_user(req.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    min_withdrawal = float(database.get_setting("min_withdrawal") or "3.0")
    if req.amount < min_withdrawal:
        raise HTTPException(status_code=400, detail=f"Minimal yechish miqdori: {min_withdrawal} TON")
        
    if user["balance"] < req.amount:
        raise HTTPException(status_code=400, detail="Mablag' yetarli emas (Insufficient balance)")
        
    tx_id = database.create_withdrawal(req.telegram_id, req.amount, req.wallet_address, req.tx_hash)
    if not tx_id:
        raise HTTPException(status_code=500, detail="Tranzaksiyani yaratishda xatolik")
        
    updated_user = database.get_user(req.telegram_id)
    return {
        "success": True,
        "withdrawal_id": tx_id,
        "user": updated_user
    }

# --- ADMIN ENDPOINTS (Protected) ---

def verify_admin_auth(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != "bekborz47":
        raise HTTPException(status_code=401, detail="Unauthorized admin password required")
    return authorization

@app.post("/api/admin/login")
def admin_login(req: AdminLoginRequest):
    if req.password == "bekborz47":
        return {"success": True, "token": "bekborz47"}
    raise HTTPException(status_code=401, detail="Noto'g'ri parol (Incorrect password)")

@app.get("/api/admin/config")
def get_admin_config(admin: str = Depends(verify_admin_auth)):
    settings_dict = database.get_settings()
    conn = database.get_db_connection()
    users_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
    referrals_count = conn.execute("SELECT COUNT(*) as count FROM referrals").fetchone()["count"]
    withdrawals_count = conn.execute("SELECT COUNT(*) as count FROM withdrawals").fetchone()["count"]
    total_balance = conn.execute("SELECT SUM(balance) as total FROM users").fetchone()["total"] or 0.0
    conn.close()
    
    return {
        "settings": [{"key": k, "value": v} for k, v in settings_dict.items()],
        "users_count": users_count,
        "referrals_count": referrals_count,
        "withdrawals_count": withdrawals_count,
        "total_balance_pool": total_balance
    }

@app.post("/api/admin/settings")
def save_settings(req: SaveSettingsRequest, admin: str = Depends(verify_admin_auth)):
    for item in req.settings:
        database.set_setting(item.key, item.value)
    return {"success": True, "settings": database.get_settings()}

@app.get("/api/admin/withdrawals")
def get_admin_withdrawals(admin: str = Depends(verify_admin_auth)):
    return database.get_all_withdrawals()

@app.post("/api/admin/withdrawals/{id}/status")
async def update_withdrawal_status(id: str, req: StatusUpdateRequest, admin: str = Depends(verify_admin_auth)):
    if req.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be approved or rejected")
        
    tx = database.update_withdrawal_status(id, req.status)
    if not tx:
        raise HTTPException(status_code=404, detail="Tranzaksiya topilmadi")
        
    # Send Telegram message through AIogram bot if possible
    # In production, you would run a loop, or make a request/use import to notify user
    import requests
    bot_token = os.getenv("BOT_TOKEN", "8991748929:AAFsX1ey49CBSDsC5Zah6ZFkG9QFDeYevjU")
    
    message = ""
    user = database.get_user(tx["telegram_id"])
    lang = user["language"] if user else "uz"
    
    if req.status == "approved":
        message = (
            f"✅ Hurmatli foydalanuvchi, sizning {tx['amount']} TON miqdoridagi pul yechish so'rovingiz tasdiqlandi va hamyoningizga o'tkazib berildi!"
            if lang == "uz" else
            f"✅ Уважаемый пользователь, ваш запрос на вывод {tx['amount']} TON одобрен и отправлен на ваш кошелек!"
            if lang == "ru" else
            f"✅ Dear user, your withdrawal request for {tx['amount']} TON has been approved and sent to your wallet!"
        )
    else:
        message = (
            f"❌ Hurmatli foydalanuvchi, sizning {tx['amount']} TON miqdoridagi pul yechish so'rovingiz rad etildi. Mablag' balansingizga qaytarildi."
            if lang == "uz" else
            f"❌ Уважаемый пользователь, ваш запрос на вывод {tx['amount']} TON был отклонен. Средства возвращены на ваш баланс."
            if lang == "ru" else
            f"❌ Dear user, your withdrawal request for {tx['amount']} TON has been rejected. Funds returned to your balance."
        )
        
    # Call Telegram Bot API to notify user immediately
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": int(tx["telegram_id"]), "text": message}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to notify user over Telegram: {e}")
        
    return {
        "success": True,
        "withdrawal": tx,
        "notified": True
    }

if __name__ == "__main__":
    import uvicorn
    # In production, bind to port and run ASGI server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
