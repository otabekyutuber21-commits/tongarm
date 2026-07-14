import fs from "fs";
import path from "path";

export interface DBUser {
  telegram_id: string;
  username: string;
  language: string;
  balance: number; // TON or Gram
  created_at: string;
}

export interface DBReferral {
  referrer_id: string;
  referred_id: string;
  status: "active" | "pending";
  created_at: string;
}

export interface DBWithdrawal {
  id: string;
  telegram_id: string;
  amount: number;
  wallet_address: string;
  tx_hash?: string; // transaction hash of the 0.5 TON payment
  status: "pending" | "approved" | "rejected";
  created_at: string;
}

export interface DBSetting {
  key: string;
  value: string;
}

export interface DatabaseSchema {
  users: DBUser[];
  referrals: DBReferral[];
  withdrawals: DBWithdrawal[];
  settings: DBSetting[];
}

const DB_PATH = path.join(process.cwd(), "database.json");

export class Database {
  private static data: DatabaseSchema = {
    users: [],
    referrals: [],
    withdrawals: [],
    settings: [
      { key: "min_withdrawal", value: "3.0" },
      { key: "referral_bonus", value: "0.5" },
      { key: "verification_fee", value: "0.5" },
      { key: "admin_wallet", value: "UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV" },
      { key: "admin_id", value: "8939863862" }
    ]
  };

  public static init() {
    try {
      if (fs.existsSync(DB_PATH)) {
        const fileContent = fs.readFileSync(DB_PATH, "utf-8");
        Database.data = JSON.parse(fileContent);
        // Ensure defaults if settings are empty
        if (!Database.data.settings || Database.data.settings.length === 0) {
          Database.data.settings = [
            { key: "min_withdrawal", value: "3.0" },
            { key: "referral_bonus", value: "0.5" },
            { key: "verification_fee", value: "0.5" },
            { key: "admin_wallet", value: "UQCnXBuJgIKK7UjEQrd5atPNxQcyqe2uAA4HbbU8V9NtenYV" },
            { key: "admin_id", value: "8939863862" }
          ];
        }
      } else {
        Database.save();
      }
      
      // Automatically seed beautiful TOP-10 data on initialization
      Database.seedDefaultData();
    } catch (error) {
      console.error("Database initialization failed, using in-memory:", error);
    }
  }

  public static seedDefaultData(force: boolean = false) {
    // Check if we already have the core seed users to avoid duplicate seeding
    const hasSeed = Database.data.users.some(u => u.telegram_id === "10001");
    if (hasSeed && !force) return;

    // Filter out any older mock users or referred_sim_ users to keep it absolutely pristine
    Database.data.users = Database.data.users.filter(u => !u.telegram_id.startsWith("100") && !u.telegram_id.startsWith("referred_sim_"));
    Database.data.referrals = Database.data.referrals.filter(r => !r.referrer_id.startsWith("100") && !r.referred_id.startsWith("referred_sim_"));

    const demoUsers = [
      { id: "10001", name: "ton_whale", lang: "en", balance: 12.0, refs: 24 },
      { id: "10002", name: "sherzod_crypto", lang: "uz", balance: 9.0, refs: 18 },
      { id: "10003", name: "olga_queen", lang: "ru", balance: 7.5, refs: 15 },
      { id: "10004", name: "alisher_tma", lang: "uz", balance: 6.0, refs: 12 },
      { id: "10005", name: "alex_crypto", lang: "en", balance: 5.0, refs: 10 },
      { id: "10006", name: "dilshod_ton", lang: "uz", balance: 4.0, refs: 8 },
      { id: "10007", name: "dmitry_ton", lang: "ru", balance: 3.0, refs: 6 },
      { id: "10008", name: "madina_m", lang: "uz", balance: 2.0, refs: 4 },
      { id: "10009", name: "maxim_trade", lang: "ru", balance: 1.0, refs: 2 },
      { id: "10010", name: "lola_mining", lang: "uz", balance: 0.5, refs: 1 },
    ];

    demoUsers.forEach((du) => {
      // Create user
      Database.createUser(du.id, du.name, du.lang);
      // Directly set their balance (so it precisely matches referral_bonus * refs)
      const userObj = Database.getUser(du.id);
      if (userObj) {
        userObj.balance = du.balance;
      }

      // Add realistic referred users
      for (let i = 0; i < du.refs; i++) {
        const referredId = `referred_sim_${du.id}_${i}`;
        const refName = du.lang === "uz" 
          ? `foydalanuvchi_uzb_${du.id.slice(-2)}_${i}` 
          : du.lang === "ru"
            ? `polzovatel_rus_${du.id.slice(-2)}_${i}`
            : `user_eng_${du.id.slice(-2)}_${i}`;

        // Create the dummy referred user
        Database.createUser(referredId, refName, du.lang);
        
        // Add the referral link
        Database.data.referrals.push({
          referrer_id: du.id,
          referred_id: referredId,
          status: "active",
          created_at: new Date().toISOString()
        });
      }
    });

    Database.save();
  }

  private static save() {
    try {
      fs.writeFileSync(DB_PATH, JSON.stringify(Database.data, null, 2), "utf-8");
    } catch (error) {
      console.error("Failed to save database:", error);
    }
  }

  // --- Users ---
  public static getUsers(): DBUser[] {
    return Database.data.users;
  }

  public static getUser(telegram_id: string): DBUser | undefined {
    return Database.data.users.find((u) => u.telegram_id === telegram_id);
  }

  public static createUser(telegram_id: string, username: string, language: string): DBUser {
    let user = Database.getUser(telegram_id);
    if (!user) {
      user = {
        telegram_id,
        username: username || `user_${telegram_id}`,
        language: language || "en",
        balance: 0,
        created_at: new Date().toISOString()
      };
      Database.data.users.push(user);
      Database.save();
    }
    return user;
  }

  public static updateUserBalance(telegram_id: string, amount: number): DBUser | undefined {
    const user = Database.getUser(telegram_id);
    if (user) {
      user.balance = Number((user.balance + amount).toFixed(4));
      Database.save();
    }
    return user;
  }

  public static updateUserLanguage(telegram_id: string, language: string): DBUser | undefined {
    const user = Database.getUser(telegram_id);
    if (user) {
      user.language = language;
      Database.save();
    }
    return user;
  }

  // --- Referrals ---
  public static getReferrals(): DBReferral[] {
    return Database.data.referrals;
  }

  public static getReferralsCount(telegram_id: string): number {
    return Database.data.referrals.filter((r) => r.referrer_id === telegram_id).length;
  }

  public static addReferral(referrer_id: string, referred_id: string): boolean {
    // Check if referral already exists
    const exists = Database.data.referrals.some(
      (r) => r.referred_id === referred_id
    );
    if (exists || referrer_id === referred_id) return false;

    Database.data.referrals.push({
      referrer_id,
      referred_id,
      status: "active",
      created_at: new Date().toISOString()
    });

    // Award bonus to referrer
    const bonus = Number(Database.getSetting("referral_bonus") || "0.5");
    Database.updateUserBalance(referrer_id, bonus);

    Database.save();
    return true;
  }

  // --- Withdrawals ---
  public static getWithdrawals(): DBWithdrawal[] {
    return Database.data.withdrawals;
  }

  public static getWithdrawalsForUser(telegram_id: string): DBWithdrawal[] {
    return Database.data.withdrawals.filter((w) => w.telegram_id === telegram_id);
  }

  public static createWithdrawal(
    telegram_id: string,
    amount: number,
    wallet_address: string,
    tx_hash?: string
  ): DBWithdrawal | null {
    const user = Database.getUser(telegram_id);
    if (!user || user.balance < amount) return null;

    // Deduct user balance
    Database.updateUserBalance(telegram_id, -amount);

    const withdrawal: DBWithdrawal = {
      id: "tx_" + Math.random().toString(36).substring(2, 11),
      telegram_id,
      amount,
      wallet_address,
      tx_hash: tx_hash || "",
      status: "pending",
      created_at: new Date().toISOString()
    };

    Database.data.withdrawals.push(withdrawal);
    Database.save();
    return withdrawal;
  }

  public static updateWithdrawalStatus(
    id: string,
    status: "approved" | "rejected"
  ): DBWithdrawal | null {
    const tx = Database.data.withdrawals.find((w) => w.id === id);
    if (!tx) return null;

    tx.status = status;

    // If rejected, refund user's balance
    if (status === "rejected") {
      Database.updateUserBalance(tx.telegram_id, tx.amount);
    }

    Database.save();
    return tx;
  }

  // --- Settings ---
  public static getSettings(): DBSetting[] {
    return Database.data.settings;
  }

  public static getSetting(key: string): string | undefined {
    return Database.data.settings.find((s) => s.key === key)?.value;
  }

  public static setSetting(key: string, value: string) {
    const setting = Database.data.settings.find((s) => s.key === key);
    if (setting) {
      setting.value = value;
    } else {
      Database.data.settings.push({ key, value });
    }
    Database.save();
  }
}
