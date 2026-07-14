import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Import our database helpers
import database

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants (Get from environment variables or use user's credentials)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8991748929:AAFsX1ey49CBSDsC5Zah6ZFkG9QFDeYevjU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://ais-dev-k3wrrledwzbczwm3zf3zbe-942978833980.asia-southeast1.run.app")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Simple FSM States to store temporary referrer id before language is chosen
class RegistrationStates(StatesGroup):
    choosing_language = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    username = message.from_user.username or f"user_{user_id}"
    
    # Check if referral link parameter exists (e.g., t.me/bot?start=12345)
    referrer_id = None
    parts = message.text.split()
    if len(parts) > 1:
        referrer_id = parts[1]
        
    # Check if user is already in database
    existing_user = database.get_user(user_id)
    if existing_user:
        # If user already exists, skip language selection and show main web app button
        lang = existing_user["language"]
        await send_welcome_back_message(message.chat.id, username, lang)
        return
        
    # User is new, ask to choose language first
    await state.set_state(RegistrationStates.choosing_language)
    await state.update_data(referrer_id=referrer_id, username=username)
    
    # Language keyboard
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")
    kb.adjust(1)
    
    await message.answer(
        "👋 Assalomu alaykum! Gram 5000 Prize botiga xush kelibsiz.\n"
        "Iltimos, muloqot tilini tanlang:\n\n"
        "👋 Здравствуйте! Добро пожаловать в бот Gram 5000 Prize.\n"
        "Пожалуйста, выберите язык общения:\n\n"
        "👋 Hello! Welcome to Gram 5000 Prize bot.\n"
        "Please choose your preferred language:",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("lang_"), RegistrationStates.choosing_language)
async def process_language_selection(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1] # uz, ru, en
    user_id = str(callback.from_user.id)
    
    # Retrieve stored state data
    data = await state.get_data()
    username = data.get("username", f"user_{user_id}")
    referrer_id = data.get("referrer_id")
    
    # Register user in SQLite
    user = database.create_user(user_id, username, lang_code)
    
    # Apply referral link if applicable
    referral_applied = False
    if referrer_id and referrer_id != user_id:
        referrer = database.get_user(referrer_id)
        if referrer:
            referral_applied = database.add_referral(referrer_id, user_id)
            # Notify referrer via Telegram
            bonus = database.get_setting("referral_bonus") or "0.5"
            try:
                ref_msg = (
                    f"🎉 Yangi taklif! Siz yuborgan havola orqali @{username} qo'shildi va balansingizga +{bonus} TON qo'shildi!"
                    if referrer["language"] == "uz" else
                    f"🎉 Новый реферал! @{username} присоединился по вашей ссылке, и ваш баланс пополнен на +{bonus} TON!"
                    if referrer["language"] == "ru" else
                    f"🎉 New referral! @{username} joined via your link, and your balance has been credited with +{bonus} TON!"
                )
                await bot.send_message(chat_id=int(referrer_id), text=ref_msg)
            except Exception as e:
                logger.error(f"Failed to notify referrer: {e}")
                
    await state.clear()
    
    # Delete the language choosing message and send main welcome
    await callback.message.delete()
    await send_new_user_welcome_message(callback.message.chat.id, username, lang_code, referral_applied)

# Send welcome back for returning users
async def send_welcome_back_message(chat_id: int, username: str, lang: str):
    text = ""
    btn_text = ""
    
    if lang == "uz":
        text = (
          f"🚀 Qaytganingizdan xursandmiz, @{username}!\n\n"
          "Gram 5000 Prize Mini App hamyoni orqali balansingizni tekshirishingiz, "
          "do'stlaringizni taklif qilishingiz va TON pul yechish so'rovlarini boshqarishingiz mumkin.\n"
          "Boshlash uchun quyidagi tugmani bosing 👇"
        )
        btn_text = "💎 Mini App-ni ochish"
    elif lang == "ru":
        text = (
          f"🚀 Рады видеть вас снова, @{username}!\n\n"
          "Через мини-приложение Gram 5000 Prize вы можете проверить свой баланс, "
          "пригласить друзей и запросить вывод средств TON.\n"
          "Нажмите кнопку ниже, чтобы начать 👇"
        )
        btn_text = "💎 Открыть Mini App"
    else:
        text = (
          f"🚀 Welcome back, @{username}!\n\n"
          "Through Gram 5000 Prize Mini App, you can manage your balance, "
          "invite friends, and request TON withdrawals.\n"
          "Press the button below to start 👇"
        )
        btn_text = "💎 Open Mini App"
        
    kb = InlineKeyboardBuilder()
    kb.button(text=btn_text, web_app=types.WebAppInfo(url=WEBAPP_URL))
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=kb.as_markup())

# Send welcome message for brand new users
async def send_new_user_welcome_message(chat_id: int, username: str, lang: str, referral_applied: bool):
    text = ""
    btn_text = ""
    
    ref_part = ""
    if referral_applied:
        ref_part = (
            "\n🎁 Siz taklifnoma orqali ro'yxatdan o'tdingiz!"
            if lang == "uz" else
            "\n🎁 Вы успешно зарегистрировались по приглашению!"
            if lang == "ru" else
            "\n🎁 You successfully registered via invitation!"
        )
        
    if lang == "uz":
        text = (
          f"🎉 Muvaffaqiyatli ro'yxatdan o'tdingiz, @{username}!{ref_part}\n\n"
          "💎 Gram 5000 Prize - bu 100% shaffof va oson taklifnomalar (referral) tizimi bo'lib, "
          "u yerda siz do'stlaringizni taklif qilib mutlaqo bepul TON ishlashingiz mumkin.\n\n"
          "📊 Har 5 ta faol do'stingiz uchun qo'shimcha 3 TON mukofoti taqdim etiladi!\n"
          "Yashirin to'lovlar va komissiyalar mutlaqo yo'q.\n\n"
          "Boshlash va shaxsiy havolangizni olish uchun quyidagi tugmani bosing 👇"
        )
        btn_text = "💎 Mini App-ni ochish"
    elif lang == "ru":
        text = (
          f"🎉 Вы успешно зарегистрировались, @{username}!{ref_part}\n\n"
          "💎 Gram 5000 Prize — это 100% прозрачная реферальная система, "
          "где вы можете зарабатывать TON совершенно бесплатно, приглашая друзей.\n\n"
          "📊 Получите дополнительный бонус 3 TON за каждые 5 активных друзей!\n"
          "Никаких скрытых платежей и комиссий.\n\n"
          "Нажмите кнопку ниже, чтобы начать и получить реферальную ссылку 👇"
        )
        btn_text = "💎 Открыть Mini App"
    else:
        text = (
          f"🎉 Registration successful, @{username}!{ref_part}\n\n"
          "💎 Gram 5000 Prize is a 105% honest and transparent referral program "
          "allowing you to earn TON absolutely free by inviting friends.\n\n"
          "📊 Get an additional 3 TON reward for every 5 active friends you invite!\n"
          "Absolutely zero upfront payments or hidden commissions.\n\n"
          "Click the button below to start and get your link 👇"
        )
        btn_text = "💎 Open Mini App"
        
    kb = InlineKeyboardBuilder()
    kb.button(text=btn_text, web_app=types.WebAppInfo(url=WEBAPP_URL))
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=kb.as_markup())

# Function to send simulated notifications to users (used by admin approval flow)
async def send_admin_notification_to_user(telegram_id: str, message_text: str):
    try:
        await bot.send_message(chat_id=int(telegram_id), text=message_text)
        return True
    except Exception as e:
        logger.error(f"Failed to send admin notification to user {telegram_id}: {e}")
        return False

# Main poll function
async def main():
    database.init_db()
    print("Bot is polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
