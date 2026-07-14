import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { Database } from "./src/db.js";

Database.init();

const app = express();
app.use(express.json());

const PORT = 3000;

// Dynamic calculations for Gram 5000 prize statistic
const LAUNCH_DATE_MS = new Date("2026-07-14T14:00:00-07:00").getTime();

function calculateGramStats(): number {
  const now = Date.now();
  const minsPassed = Math.max(0, Math.floor((now - LAUNCH_DATE_MS) / (1000 * 60)));
  const total = 557 + Math.floor(minsPassed / 5) * 0.1;
  return Number(total.toFixed(1));
}

// --- API ENDPOINTS ---

// Get current stats (Gram live stats, global users, etc.)
app.get("/api/stats", (req, res) => {
  const currentGram = calculateGramStats();
  const totalUsers = Database.getUsers().length;
  const totalWithdrawals = Database.getWithdrawals().length;
  const totalReferrals = Database.getReferrals().length;

  res.json({
    gram_stats: currentGram,
    total_users: totalUsers,
    total_withdrawals: totalWithdrawals,
    total_referrals: totalReferrals,
    min_withdrawal: Number(Database.getSetting("min_withdrawal") || "3.0"),
    referral_bonus: Number(Database.getSetting("referral_bonus") || "0.5"),
    verification_fee: Number(Database.getSetting("verification_fee") || "0.5"),
    admin_wallet: Database.getSetting("admin_wallet") || "UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV",
    admin_id: Database.getSetting("admin_id") || "8939863862"
  });
});

// Create/Get user profiles
app.post("/api/user", (req, res) => {
  const { telegram_id, username, language, referrer_id } = req.body;

  if (!telegram_id) {
    return res.status(400).json({ error: "telegram_id is required" });
  }

  // Check if user is already registered
  const existingUser = Database.getUser(telegram_id);
  
  if (existingUser) {
    return res.json({
      user: existingUser,
      referrals_count: Database.getReferralsCount(telegram_id),
      is_new: false
    });
  }

  // Create new user
  const newUser = Database.createUser(telegram_id, username, language);
  let referralApplied = false;

  // Process referral if a valid referrer_id was provided
  if (referrer_id && referrer_id !== telegram_id) {
    const referrer = Database.getUser(referrer_id);
    if (referrer) {
      referralApplied = Database.addReferral(referrer_id, telegram_id);
    }
  }

  res.json({
    user: newUser,
    referrals_count: 0,
    is_new: true,
    referral_applied: referralApplied
  });
});

// Update language
app.put("/api/user/lang", (req, res) => {
  const { telegram_id, language } = req.body;
  if (!telegram_id || !language) {
    return res.status(400).json({ error: "telegram_id and language are required" });
  }

  const updated = Database.updateUserLanguage(telegram_id, language);
  if (!updated) {
    return res.status(404).json({ error: "User not found" });
  }

  res.json({ success: true, user: updated });
});

// Get user info and specific stats
app.get("/api/user/:telegram_id", (req, res) => {
  const { telegram_id } = req.params;
  const user = Database.getUser(telegram_id);

  if (!user) {
    return res.status(404).json({ error: "User not found" });
  }

  res.json({
    user,
    referrals_count: Database.getReferralsCount(telegram_id),
    withdrawals: Database.getWithdrawalsForUser(telegram_id)
  });
});

// Get leaderboard (TOP-10)
app.get("/api/leaderboard", (req, res) => {
  const users = Database.getUsers();
  const referrals = Database.getReferrals();

  // Map each user to their referral count
  const leaderboard = users.map((u) => {
    const count = referrals.filter((r) => r.referrer_id === u.telegram_id).length;
    const displayUsername = u.username || `user_${u.telegram_id}`;

    return {
      username: displayUsername,
      telegram_id_masked: u.telegram_id.length > 4 
        ? u.telegram_id.substring(0, 3) + "***" + u.telegram_id.substring(u.telegram_id.length - 2)
        : u.telegram_id,
      referrals_count: count,
      balance: u.balance
    };
  });

  // Sort by referrals count descending
  leaderboard.sort((a, b) => b.referrals_count - a.referrals_count);

  // Return Top 10
  res.json(leaderboard.slice(0, 10));
});

// Submit withdrawal request
app.post("/api/withdraw", (req, res) => {
  const { telegram_id, amount, wallet_address, tx_hash } = req.body;

  if (!telegram_id || !amount || !wallet_address) {
    return res.status(400).json({ error: "telegram_id, amount, and wallet_address are required" });
  }

  const user = Database.getUser(telegram_id);
  if (!user) {
    return res.status(404).json({ error: "User not found" });
  }

  const minWithdrawal = Number(Database.getSetting("min_withdrawal") || "3.0");
  if (amount < minWithdrawal) {
    return res.status(400).json({ error: `Minimum withdrawal is ${minWithdrawal} TON` });
  }

  if (user.balance < amount) {
    return res.status(400).json({ error: "Insufficient balance" });
  }

  // Create withdrawal request
  const tx = Database.createWithdrawal(telegram_id, amount, wallet_address, tx_hash);
  if (!tx) {
    return res.status(500).json({ error: "Failed to create withdrawal request" });
  }

  res.json({ success: true, withdrawal: tx, user });
});

// --- ADMIN API ENDPOINTS (Protected with simple basic/password auth check) ---

// Helper to verify admin authorization
const verifyAdmin = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || authHeader !== "bekborz47") {
    return res.status(401).json({ error: "Unauthorized admin password required" });
  }
  next();
};

// Admin authentication endpoint
app.post("/api/admin/login", (req, res) => {
  const { password } = req.body;
  if (password === "bekborz47") {
    res.json({ success: true, token: "bekborz47" });
  } else {
    res.status(401).json({ error: "Noto'g'ri parol (Incorrect password)" });
  }
});

// Get admin stats & settings
app.get("/api/admin/config", verifyAdmin, (req, res) => {
  res.json({
    settings: Database.getSettings(),
    users_count: Database.getUsers().length,
    referrals_count: Database.getReferrals().length,
    withdrawals_count: Database.getWithdrawals().length,
    total_balance_pool: Database.getUsers().reduce((sum, u) => sum + u.balance, 0)
  });
});

// Save settings
app.post("/api/admin/settings", verifyAdmin, (req, res) => {
  const { settings } = req.body; // Array of { key, value }
  if (!Array.isArray(settings)) {
    return res.status(400).json({ error: "Invalid settings format" });
  }

  settings.forEach((s) => {
    if (s.key && s.value !== undefined) {
      Database.setSetting(s.key, String(s.value));
    }
  });

  res.json({ success: true, settings: Database.getSettings() });
});

// Get all withdrawals
app.get("/api/admin/withdrawals", verifyAdmin, (req, res) => {
  const txs = Database.getWithdrawals();
  // Attach user details to withdrawals for easy auditing
  const detailedTxs = txs.map((tx) => {
    const u = Database.getUser(tx.telegram_id);
    return {
      ...tx,
      username: u ? u.username : "Unknown"
    };
  });
  res.json(detailedTxs);
});

// Update withdrawal status (Approve / Reject)
app.post("/api/admin/withdrawals/:id/status", verifyAdmin, (req, res) => {
  const { id } = req.params;
  const { status } = req.body; // "approved" or "rejected"

  if (status !== "approved" && status !== "rejected") {
    return res.status(400).json({ error: "Status must be approved or rejected" });
  }

  const updated = Database.updateWithdrawalStatus(id, status);
  if (!updated) {
    return res.status(404).json({ error: "Withdrawal not found" });
  }

  // Simulate Telegram bot notification sending
  const message = status === "approved" 
    ? `✅ Hurmatli foydalanuvchi, sizning ${updated.amount} TON miqdoridagi pul yechish so'rovingiz tasdiqlandi va hamyoningizga o'tkazib berildi!`
    : `❌ Hurmatli foydalanuvchi, sizning ${updated.amount} TON miqdoridagi pul yechish so'rovingiz rad etildi. Mablag' balansingizga qaytarildi.`;

  console.log(`[BOT NOTIFICATION SENT to User ${updated.telegram_id}]: ${message}`);

  res.json({ 
    success: true, 
    withdrawal: updated,
    simulated_bot_notification: message
  });
});

// Seed demo users and data to make preview extremely rich on first load
app.post("/api/admin/seed", (req, res) => {
  // Clear and force-seed high-quality TOP-10
  Database.seedDefaultData(true);

  // Seed a couple of withdrawals on these seeded users for the demo
  Database.createWithdrawal("10003", 5.0, "UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV", "0x5ae1bc21de4529f");
  Database.createWithdrawal("10001", 3.0, "EQA2B1cd9efGhiJklMnoPqrStuVwxYz1234567890abcdef", "0x3bc76b1daef5cde2");

  // Approve one, leave one pending
  const withdrawals = Database.getWithdrawals();
  if (withdrawals.length > 1) {
    Database.updateWithdrawalStatus(withdrawals[0].id, "approved");
  }

  res.json({ success: true, message: "Database successfully seeded with elegant TOP-10 crypto users!" });
});


// --- VITE MIDDLEWARE SETUP ---

async function startServer() {
  // Integrate Vite for dev
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    // Production serving of static files
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
