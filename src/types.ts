export interface AppUser {
  telegram_id: string;
  username: string;
  language: string;
  balance: number;
  created_at: string;
}

export interface AppWithdrawal {
  id: string;
  telegram_id: string;
  amount: number;
  wallet_address: string;
  tx_hash?: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  username?: string;
}

export interface AppStats {
  gram_stats: number;
  total_users: number;
  total_withdrawals: number;
  total_referrals: number;
  min_withdrawal: number;
  referral_bonus: number;
  verification_fee: number;
  admin_wallet: string;
  admin_id: string;
}

export interface LeaderboardEntry {
  username: string;
  telegram_id_masked: string;
  referrals_count: number;
  balance: number;
}

export const TRANSLATIONS: Record<string, any> = {
  uz: {
    dashboard: "Asosiy",
    referrals: "Takliflar",
    leaderboard: "Reyting",
    withdraw: "Yechish",
    admin: "Admin",
    balance: "Joriy balans",
    invited_friends: "Taklif etilgan do'stlar",
    promo_info: "Aksiya shartlari",
    promo_desc: "Har 5 ta faol taklif etilgan do'stingiz uchun qo'shimcha 3 TON bonus oling!",
    ref_link: "Sizning taklifnomangiz (Referral Link)",
    copy: "Nusxalash",
    copied: "Nusxalandi!",
    share: "Telegramda ulashish",
    top_10: "TOP-10 Eng yaxshi taklifchilar",
    rank: "O'rin",
    username: "Foydalanuvchi",
    friends: "Do'stlar soni",
    withdraw_title: "Mablag'larni yechib olish",
    min_withdraw_desc: "Minimal yechish miqdori",
    verification_required: "Tasdiqlash to'lovi talab etiladi (0.5 TON)",
    verification_desc: "Efir va firg'ob botlarning oldini olish maqsadida, birinchi pul yechishdan oldin admin hamyoniga tasdiqlash to'lovini (0.5 TON) o'tkazishingiz kerak. Ushbu miqdor to'liqligicha tekshiriladi.",
    admin_wallet: "Admin TON Hamyoni",
    wallet_address_input: "Sizning TON Hamyon manzilingiz",
    tx_hash_input: "To'lov tranzaksiya havolasi / Tx Hash (ixtiyoriy)",
    withdraw_btn: "Yechib olishni so'rash",
    withdraw_history: "Yechib olish tarixi",
    status_pending: "Kutilmoqda",
    status_approved: "Tasdiqlangan",
    status_rejected: "Rad etilgan",
    insufficient_balance: "Balans yetarli emas",
    language_select: "Tilni tanlang",
    telegram_sim: "TMA Simulyatori",
    change_user: "Foydalanuvchini almashtirish",
    current_sim_user: "Simulyatordagi foydalanuvchi",
    gram_stats_title: "Gram Mukofot Jamg'armasi",
    gram_stats_desc: "Har soatda avtomatik ravishda 15 TON/Gram qo'shiladi!",
    next_increment: "Keyingi qo'shilish vaqti",
    seed_btn: "Demo ma'lumotlarni yuklash (TOP-10)",
    add_balance_btn: "+1 TON qo'shish",
    enter_ref_id: "Kim taklif qilgan (Referrer ID)?",
    simulation_settings: "Simulyatsiya sozlamalari",
    apply_ref: "Taklifni qo'llash",
    ton_sent_success: "Hamyon nusxalandi! Iltimos, tranzaksiyani bajaring.",
    withdraw_submitted: "So'rov muvaffaqiyatli qabul qilindi. Kutilmoqda...",
  },
  ru: {
    dashboard: "Главная",
    referrals: "Рефералы",
    leaderboard: "Рейтинг",
    withdraw: "Вывод",
    admin: "Админ",
    balance: "Текущий баланс",
    invited_friends: "Приглашенные друзья",
    promo_info: "Условия акции",
    promo_desc: "За каждых 5 активных друзей вы получите дополнительно 3 TON бонуса!",
    ref_link: "Ваша реферальная ссылка",
    copy: "Копировать",
    copied: "Скопировано!",
    share: "Поделиться в Telegram",
    top_10: "TOP-10 Лучших пригласителей",
    rank: "Место",
    username: "Пользователь",
    friends: "Друзья",
    withdraw_title: "Вывод средств",
    min_withdraw_desc: "Минимальная сумма вывода",
    verification_required: "Требуется верификационный платеж (0.5 TON)",
    verification_desc: "Во избежание ботов и накруток, перед первым выводом необходимо отправить верификационный платеж (0.5 TON) на кошелек администратора.",
    admin_wallet: "TON кошелек админа",
    wallet_address_input: "Ваш TON кошелек",
    tx_hash_input: "Ссылка/Хэш транзакции оплаты (необязательно)",
    withdraw_btn: "Запросить вывод",
    withdraw_history: "История выводов",
    status_pending: "Ожидание",
    status_approved: "Одобрено",
    status_rejected: "Отклонено",
    insufficient_balance: "Недостаточно баланса",
    language_select: "Выберите язык",
    telegram_sim: "Симулятор ТМА",
    change_user: "Сменить пользователя",
    current_sim_user: "Текущий пользователь",
    gram_stats_title: "Призовой Фонд Gram",
    gram_stats_desc: "Каждый час автоматически добавляется 15 TON/Gram!",
    next_increment: "До следующего пополнения",
    seed_btn: "Загрузить демо-данные",
    add_balance_btn: "Добавить +1 TON",
    enter_ref_id: "Кто пригласил (ID реферера)?",
    simulation_settings: "Настройки симуляции",
    apply_ref: "Применить реферал",
    ton_sent_success: "Кошелек скопирован! Пожалуйста, отправьте транзакцию.",
    withdraw_submitted: "Запрос успешно создан и отправлен на проверку.",
  },
  en: {
    dashboard: "Dashboard",
    referrals: "Referrals",
    leaderboard: "Leaderboard",
    withdraw: "Withdraw",
    admin: "Admin",
    balance: "Current Balance",
    invited_friends: "Invited Friends",
    promo_info: "Campaign Details",
    promo_desc: "Get an extra 3 TON reward for every 5 active friends you invite!",
    ref_link: "Your Referral Link",
    copy: "Copy",
    copied: "Copied!",
    share: "Share in Telegram",
    top_10: "TOP-10 Lead Referrers",
    rank: "Rank",
    username: "Username",
    friends: "Friends Invited",
    withdraw_title: "Withdraw Funds",
    min_withdraw_desc: "Minimum withdrawal limit",
    verification_required: "Verification payment required (0.5 TON)",
    verification_desc: "To prevent botting and abuse, before requesting your first withdrawal, you must submit a verification fee of 0.5 TON to the admin wallet.",
    admin_wallet: "Admin TON Wallet",
    wallet_address_input: "Your TON Wallet Address",
    tx_hash_input: "Transaction Hash / Tx Hash proof (optional)",
    withdraw_btn: "Request Withdrawal",
    withdraw_history: "Withdrawal History",
    status_pending: "Pending",
    status_approved: "Approved",
    status_rejected: "Rejected",
    insufficient_balance: "Insufficient balance",
    language_select: "Select Language",
    telegram_sim: "TMA Simulator",
    change_user: "Switch User",
    current_sim_user: "Simulated User",
    gram_stats_title: "Gram Reward Pool",
    gram_stats_desc: "Adds 15 TON/Gram automatically every hour!",
    next_increment: "Next hourly increment",
    seed_btn: "Load Demo Data (TOP-10)",
    add_balance_btn: "Add +1 TON",
    enter_ref_id: "Who invited you (Referrer ID)?",
    simulation_settings: "Simulation Control",
    apply_ref: "Apply Referral",
    ton_sent_success: "Wallet copied! Please complete transaction.",
    withdraw_submitted: "Withdrawal request submitted successfully. Pending...",
  }
};
