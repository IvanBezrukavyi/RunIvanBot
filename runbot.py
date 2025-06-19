import os
import time
import threading
import schedule
from datetime import datetime
from dotenv import load_dotenv
import telebot
import pytz
import tracker

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

# === ЧАСОВА ЗОНА ===
ukraine_tz = pytz.timezone("Europe/Kyiv")

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
    now = datetime.now(ukraine_tz)
    warmup = warmup_links[now.day % len(warmup_links)]
    motivation = motivations[now.day % len(motivations)]

    tracker.log_training_day()

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

# === СУБОТА — ПРОГУЛЯНКА З СИНОМ ===
def saturday_walk():
    bot.send_message(USER_ID,
        "👣 Субота — активне відновлення!\n"
        "🚶‍♂️ Прогулянка на свіжому повітрі з сином 👶\n"
        "🌳 Просто ходи 20–40 хв без навантаження.\n"
        "🎧 Можеш послухати спокійну музику або подкаст.\n\n"
        "❤️ Турбота про сина — це теж інвестиція у твоє здоров'я!")

# === ПЕРЕВІРКА ПРОПУЩЕНИХ ДНІВ ===
def sunday_check():
    missed = tracker.check_missed_days()
    if missed:
        bot.send_message(USER_ID,
            f"📋 Ти пропустив тренування у: {', '.join(sorted(missed))}\n"
            f"💡 Спробуй надолужити або розплануй наступний тиждень!")
    else:
        bot.send_message(USER_ID, "✅ Усі тренування цього тижня виконано! Чудова робота!")
    tracker.reset_week_log()

# === ГРАФІК НА ТИЖДЕНЬ ===
schedule.every().tuesday.at("18:30").do(running_reminder)
schedule.every().wednesday.at("18:30").do(running_reminder)
schedule.every().thursday.at("18:30").do(running_reminder)
schedule.every().friday.at("18:30").do(running_reminder)
schedule.every().saturday.at("18:30").do(saturday_walk)
schedule.every().sunday.at("18:30").do(running_reminder)
schedule.every().sunday.at("21:00").do(sunday_check)

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
