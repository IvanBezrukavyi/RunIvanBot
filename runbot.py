import os
import time
import threading
import schedule
from datetime import datetime
from dotenv import load_dotenv
import telebot
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

# === СТАНИ ===
pushups_count = 13

# === РОЗМИНКА (відео YouTube до 2 хв) ===
warmup_links = [
    "https://youtu.be/HY7Zuo0bybw",  # 2 хв
    "https://youtu.be/c9M0l3uTJ78",  # 1:30 хв
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
    tracker.log_training_day()

# === ЩОТИЖНЕВИЙ ТРЕКЕР ВАГИ ===
def weight_checkin():
    bot.send_message(USER_ID, "⚖️ Час зважування! Вкажи свою вагу у кг.")

# === НАСТРІЙ ===
def mood_checkin():
    bot.send_message(USER_ID, "🧠 Як настрій сьогодні? (від 1 до 10 або короткий опис)")

# === ЩОТИЖНЕВА ПЕРЕВІРКА + PDF ===
def sunday_check():
    missed = tracker.check_missed_days()
    if missed:
        bot.send_message(USER_ID,
            f"📋 Ти пропустив тренування у: {', '.join(sorted(missed))}\n"
            f"💡 Спробуй надолужити або розплануй наступний тиждень!")
    else:
        bot.send_message(USER_ID, "✅ Усі тренування цього тижня виконано! Чудова робота!")

    # Звіт PDF
    report_path = tracker.generate_weekly_report_pdf()
    with open(report_path, "rb") as pdf_file:
        bot.send_document(USER_ID, pdf_file)

    tracker.reset_week_log()

# === ГРАФІК ===
schedule.every().tuesday.at("18:30").do(running_reminder)
schedule.every().wednesday.at("18:30").do(running_reminder)
schedule.every().friday.at("18:30").do(running_reminder)
schedule.every().sunday.at("18:30").do(running_reminder)

schedule.every().monday.at("07:30").do(weight_checkin)
schedule.every().day.at("20:30").do(mood_checkin)
schedule.every().sunday.at("21:00").do(sunday_check)

# === СИЛОВІ НАГАДУВАННЯ ===
schedule.every().monday.at("18:30").do(lambda: tracker.send_strength_reminder(bot, USER_ID))
schedule.every().thursday.at("18:30").do(lambda: tracker.send_strength_reminder(bot, USER_ID))

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
