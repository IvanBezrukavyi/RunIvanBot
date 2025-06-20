import os
import time
import threading
import logging
from datetime import datetime, date
from dotenv import load_dotenv
import telebot
import schedule
import pytz
import tracker

ukraine_tz = pytz.timezone("Europe/Kyiv")


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

if BOT_TOKEN is None:
    logging.error("Fatal error: BOT_TOKEN environment variable not set")
    raise ValueError("BOT_TOKEN environment variable not set")

try:
    USER_ID = int(USER_ID)
except (ValueError, TypeError):
    logging.error("Fatal error: USER_ID is invalid or not set")
    raise ValueError("USER_ID environment variable is not a valid integer")

bot = telebot.TeleBot(BOT_TOKEN)

# === СТАНИ ===
pushups_count = 13
goal_date = datetime(2025, 9, 15, tzinfo=ukraine_tz)

# === РОЗМИНКА ===
warmup_links = [
    "https://www.youtube.com/watch?v=Gf7nqxkY0yU",
    "https://www.youtube.com/watch?v=nph81YymVqg",
    "https://www.youtube.com/watch?v=K-CrEi0ymMg",
]

motivations = [
    "💪 Пам'ятай, ти робиш це для себе і свого здоров'я!",
    "🏃‍♂️ Кожен крок наближає тебе до цілі — 10 км!",
    "🔥 Рух — життя. Ти вже на правильному шляху!",
    "✅ Кожне тренування — цеглинка у твоєму новому тілі!",
]

# === ТРЕНУВАЛЬНЕ НАГАДУВАННЯ ===
def running_reminder():
    global pushups_count
    today = datetime.now(ukraine_tz)
    warmup = warmup_links[today.day % len(warmup_links)]
    motivation = motivations[today.day % len(motivations)]
    days_left = (goal_date - today).days

    intervals = "🏃 3 хв біг / 1.5 хв хода (повтори 4 рази)"
    if days_left < 60:
        intervals = "🏃 6 хв біг / 1 хв хода (повтори 3 рази)"
    if days_left < 30:
        intervals = "🏃‍♂️ Біжи в стабільному темпі 7:45–8:30 хв/км до 6–8 км"

    bot.send_message(USER_ID,
        f"🏃‍♂️ Час на пробіжку!\n"
        f"🔸 Залишилось {days_left} днів до 10 км\n"
        f"🔸 Зроби розминку: {warmup}\n"
        f"🔸 Відтиснись {pushups_count} раз(ів)\n"
        f"🔸 Біг сьогодні: {intervals}\n"
        f"🔸 Оптимальний темп: 7:45–8:30 хв/км (зона жироспалення)\n\n"
        f"{motivation}"
    )
    tracker.log_training_day()
    pushups_count += 1

# === СИЛОВІ ТРЕНУВАННЯ ===
def strength_training():
    tracker.send_strength_reminder(bot, USER_ID)

# === ЩОТИЖНЕВА ЗВІТНІСТЬ ===
def send_weekly_report():
    path = tracker.generate_weekly_report_pdf()
    with open(path, 'rb') as f:
        bot.send_document(USER_ID, f)

# === ЩОТИЖНЕВЕ ЗВАЖУВАННЯ ===
def weight_checkin():
    bot.send_message(USER_ID, "⚖️ Час зважування! Вкажи свою вагу у кг.")

# === НАСТРІЙ ===
def mood_checkin():
    bot.send_message(USER_ID, "🧠 Як настрій сьогодні? (від 1 до 10 або короткий опис)")

# === КОМАНДИ ===
@bot.message_handler(commands=['start', 'test'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Бот активний! Готовий допомагати тобі в тренуваннях.")

@bot.message_handler(commands=['goal'])
def send_goal(message):
    today = datetime.now(ukraine_tz)
    days_left = (goal_date - today).days
    bot.send_message(USER_ID,
        f"🎯 Ціль: пробігти 10 км до 15 вересня 2025\n"
        f"📆 Залишилось: {days_left} днів"
    )

# === РОЗКЛАД ===
schedule.every().tuesday.at("18:30").do(running_reminder)
schedule.every().wednesday.at("18:30").do(running_reminder)
schedule.every().thursday.at("18:30").do(strength_training)
schedule.every().friday.at("18:30").do(running_reminder)
schedule.every().saturday.at("18:30").do(lambda: bot.send_message(USER_ID, "🚶‍♂️ Суботня прогулянка з сином — відпочинок і відновлення!"))
schedule.every().sunday.at("18:30").do(running_reminder)
schedule.every().monday.at("18:30").do(strength_training)
schedule.every().monday.at("07:30").do(weight_checkin)
schedule.every().day.at("20:30").do(mood_checkin)
schedule.every().sunday.at("21:00").do(send_weekly_report)

# === ФОН ===
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    logging.info("🤖 Бот стартує...")
    threading.Thread(target=run_schedule, daemon=True).start()
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
