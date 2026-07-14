import sqlite3
from datetime import datetime
import os

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id TEXT PRIMARY KEY,
        username TEXT,
        language TEXT DEFAULT 'uz',
        balance REAL DEFAULT 0.0,
        created_at TEXT
    )
    """)
    
    # 2. Referrals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        referrer_id TEXT,
        referred_id TEXT PRIMARY KEY,
        status TEXT DEFAULT 'active',
        created_at TEXT,
        FOREIGN KEY (referrer_id) REFERENCES users (telegram_id),
        FOREIGN KEY (referred_id) REFERENCES users (telegram_id)
    )
    """)
    
    # 3. Withdrawals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS withdrawals (
        id TEXT PRIMARY KEY,
        telegram_id TEXT,
        amount REAL,
        wallet_address TEXT,
        tx_hash TEXT,
        status TEXT DEFAULT 'pending', -- pending, approved, rejected
        created_at TEXT,
        FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
    )
    """)
    
    # 4. Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # Pre-seed default settings if they do not exist
    defaults = [
        ("min_withdrawal", "3.0"),
        ("referral_bonus", "0.5"),
        ("verification_fee", "0.5"),
        ("admin_wallet", "UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV"),
        ("admin_id", "8939863862")
    ]
    for key, value in defaults:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
        
    conn.commit()
    conn.close()
    print("SQLite database initialized successfully.")

# --- Helper DB Functions ---

def get_user(telegram_id: str):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(telegram_id: str, username: str, language: str):
    conn = get_db_connection()
    created_at = datetime.utcnow().isoformat()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, language, balance, created_at) VALUES (?, ?, ?, 0.0, ?)",
            (telegram_id, username, language, created_at)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating user: {e}")
    conn.close()
    return get_user(telegram_id)

def update_user_balance(telegram_id: str, amount: float):
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET balance = ROUND(balance + ?, 4) WHERE telegram_id = ?",
        (amount, telegram_id)
    )
    conn.commit()
    conn.close()

def update_user_language(telegram_id: str, language: str):
    conn = get_db_connection()
    conn.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (language, telegram_id))
    conn.commit()
    conn.close()

def get_referral_count(telegram_id: str):
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ?", (telegram_id,)).fetchone()
    conn.close()
    return count["count"] if count else 0

def add_referral(referrer_id: str, referred_id: str):
    if referrer_id == referred_id:
        return False
        
    conn = get_db_connection()
    # Check if this referred user is already registered under a referrer
    exists = conn.execute("SELECT 1 FROM referrals WHERE referred_id = ?", (referred_id,)).fetchone()
    if exists:
        conn.close()
        return False
        
    created_at = datetime.utcnow().isoformat()
    try:
        conn.execute(
            "INSERT INTO referrals (referrer_id, referred_id, status, created_at) VALUES (?, ?, 'active', ?)",
            (referrer_id, referred_id, created_at)
        )
        # Credit referrer
        bonus = float(get_setting("referral_bonus") or "0.5")
        conn.execute(
            "UPDATE users SET balance = ROUND(balance + ?, 4) WHERE telegram_id = ?",
            (bonus, referrer_id)
        )
        conn.commit()
        success = True
    except sqlite3.Error as e:
        print(f"Error adding referral: {e}")
        success = False
    conn.close()
    return success

def create_withdrawal(telegram_id: str, amount: float, wallet_address: str, tx_hash: str):
    conn = get_db_connection()
    # Double check balance
    user = conn.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    if not user or user["balance"] < amount:
        conn.close()
        return None
        
    tx_id = f"tx_{os.urandom(4).hex()}"
    created_at = datetime.utcnow().isoformat()
    
    try:
        # Deduct balance
        conn.execute("UPDATE users SET balance = ROUND(balance - ?, 4) WHERE telegram_id = ?", (amount, telegram_id))
        # Insert withdrawal record
        conn.execute(
            "INSERT INTO withdrawals (id, telegram_id, amount, wallet_address, tx_hash, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (tx_id, telegram_id, amount, wallet_address, tx_hash, created_at)
        )
        conn.commit()
        ret = tx_id
    except sqlite3.Error as e:
        print(f"Error creating withdrawal: {e}")
        ret = None
    conn.close()
    return ret

def get_withdrawals_for_user(telegram_id: str):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM withdrawals WHERE telegram_id = ? ORDER BY created_at DESC", (telegram_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_withdrawals():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT w.*, u.username 
        FROM withdrawals w 
        JOIN users u ON w.telegram_id = u.telegram_id 
        ORDER BY w.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_withdrawal_status(tx_id: str, status: str):
    conn = get_db_connection()
    tx = conn.execute("SELECT * FROM withdrawals WHERE id = ?", (tx_id,)).fetchone()
    if not tx:
        conn.close()
        return None
        
    conn.execute("UPDATE withdrawals SET status = ? WHERE id = ?", (status, tx_id))
    
    # Refund balance if rejected
    if status == "rejected":
        conn.execute(
            "UPDATE users SET balance = ROUND(balance + ?, 4) WHERE telegram_id = ?",
            (tx["amount"], tx["telegram_id"])
        )
        
    conn.commit()
    updated_tx = conn.execute("SELECT * FROM withdrawals WHERE id = ?", (tx_id,)).fetchone()
    conn.close()
    return dict(updated_tx)

def get_settings():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

def get_setting(key: str):
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None

def set_setting(key: str, value: str):
    conn = get_db_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT u.telegram_id, u.username, u.balance, COUNT(r.referred_id) as referrals_count
        FROM users u
        LEFT JOIN referrals r ON u.telegram_id = r.referrer_id
        GROUP BY u.telegram_id
        ORDER BY referrals_count DESC, u.balance DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    
    leaderboard = []
    for r in rows:
        username = r["username"] or "Foydalanuvchi"
        # Mask username for privacy
        masked_username = username[:3] + "***" if len(username) > 3 else username + "***"
        masked_tg_id = r["telegram_id"][:3] + "***" + r["telegram_id"][-2:] if len(r["telegram_id"]) > 5 else "user***"
        
        leaderboard.append({
            "username": masked_username,
            "telegram_id_masked": masked_tg_id,
            "referrals_count": r["referrals_count"],
            "balance": r["balance"]
        })
    return leaderboard
