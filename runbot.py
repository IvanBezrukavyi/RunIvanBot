import os
import time
import threading
import schedule
from datetime import datetime
from dotenv import load_dotenv
import telebot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")
if USER_ID is None:
    raise ValueError("USER_ID environment variable not set")
try:
    USER_ID = int(USER_ID)
except ValueError as exc:
    raise ValueError("USER_ID environment variable is not a valid integer") from exc
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = telebot.TeleBot(BOT_TOKEN)

# === СТАНИ ===
pushups_count = 13

# === РОЗМИНКА (відео YouTube до 2 хв) ===
warmup_links = [
    "https://www.youtube.com/watch?v=Gf7nqxkY0yU",  # 2 хв
    "https://www.youtube.com/watch?v=nph81YymVqg",  # 1:30 хв
    "https://www.youtube.com/watch?v=K-CrEi0ymMg",  # 2 хв йога
]

# === МОТИВАЦІЯ ===
motivations = [
    "💪 Пам'ятай, ти робиш це для себе і свого здоров'я!",
    "🏃‍♂️ Кожен крок наближає тебе до цілі — 10 км!",
    "🔥 Рух — життя. Ти вже на правильному шляху!",
    "✅ Кожне тренування — цеглинка у твоєму новому тілі!",
]

# === ОСНОВНІ КОМАНДИ ===
@bot.message_handler(commands=['start', 'test'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Бот активний! Готовий допомагати тобі в тренуваннях.")

# === НАГАДУВАННЯ НА БІГ І ВІДТИСКАННЯ ===
def running_reminder():
    global pushups_count
    today = datetime.now().strftime("%A")
    warmup = warmup_links[datetime.now().day % len(warmup_links)]
    motivation = motivations[datetime.now().day % len(motivations)]
    bot.send_message(USER_ID,
        f"🏃‍♂️ Час на пробіжку!\n"
        f"🔸 Зроби розминку: {warmup}\n"
        f"🔸 Відтиснись {pushups_count} раз(ів)\n"
        f"🔸 Потім — пробіжка!\n\n"
        f"{motivation}")
    pushups_count += 1

# === ЩОТИЖНЕВИЙ ТРЕКЕР ВАГИ ===
def weight_checkin():
    bot.send_message(USER_ID, "⚖️ Час зважування! Вкажи свою вагу у кг.")

# === НАСТРІЙ ===
def mood_checkin():
    bot.send_message(USER_ID, "🧠 Як настрій сьогодні? (від 1 до 10 або короткий опис)")

# === ГРАФІК НА ТИЖДЕНЬ (біг: вт-ср-чт-пт-нд) ===
schedule.every().tuesday.at("18:30").do(running_reminder)
schedule.every().wednesday.at("18:30").do(running_reminder)
schedule.every().thursday.at("18:30").do(running_reminder)
schedule.every().friday.at("18:30").do(running_reminder)
schedule.every().sunday.at("18:30").do(running_reminder)

# === ТРЕКЕРИ ===
schedule.every().monday.at("07:30").do(weight_checkin)
schedule.every().day.at("20:30").do(mood_checkin)

# === ПОТОКИ ===
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot polling error: {e}")
        time.sleep(5)