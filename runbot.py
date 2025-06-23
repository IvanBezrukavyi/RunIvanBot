import os
import time
import threading
from datetime import datetime, date
import schedule
from dotenv import load_dotenv
import telebot
import pytz
from flask import Flask
import tracker

# === FLASK SERVER ДЛЯ ПІНГЕРА ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# === БАЗОВЕ НАЛАШТУВАННЯ ===
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
running_days_count = 0
goal_date = date(2025, 9, 15)

# === РОЗМИНКА ===
warmup_links = [
    "https://www.youtube.com/watch?v=Gf7nqxkY0yU",
    "https://www.youtube.com/watch?v=nph81YymVqg",
    "https://www.youtube.com/watch?v=K-CrEi0ymMg",
]

# === МОТИВАЦІЯ ===
motivations = [
    "💪 Пам'ятай, ти робиш це для себе і свого здоров'я!",
    "🏃‍♂️ Кожен крок наближає тебе до цілі — 10 км!",
    "🔥 Рух — життя. Ти вже на правильному шляху!",
    "✅ Кожне тренування — цеглинка у твоєму новому тілі!",
]

# === ТЕХНІКА БІГУ ===
running_tips = [
    "👣 Твоя стопа має торкатися землі під центром ваги. Уникай приземлення на п’яту.",
    "🦵 Збільш каденс: ціль — 170–180 кроків/хв для кращої ефективності.",
    "👐 Тримай руки зігнутими під 90°, не затискай кулаки — це допомагає розслабитись.",
    "📏 Погляд уперед, корпус трохи нахилений — це допомагає бігти економніше.",
    "💨 Дихай глибоко, через ніс або рот, ритмічно: 2 вдихи — 2 видихи."
]

# === ЧАС КИЄВА ===
def local_time():
    tz = pytz.timezone("Europe/Kyiv")
    return datetime.now(tz)

# === ІНТЕРВАЛИ ===
def get_interval_plan():
    today = date.today()
    days_left = (goal_date - today).days

    if days_left > 70:
        return "1 хв біг / 1 хв хода × 6 раундів (~1.5 км)"
    elif days_left > 50:
        return "2 хв біг / 1 хв хода × 6 раундів (~2.5 км)"
    elif days_left > 35:
        return "5 хв біг / 1 хв хода × 4 раунди (~3.5 км)"
    elif days_left > 21:
        return "10 хв біг / 1 хв хода × 3 раунди (~5.5 км)"
    elif days_left > 10:
        return "Біжи без зупинки у комфортному темпі (~7 км)"
    elif days_left > 1:
        return "Пробіжка на ~8-9 км у темпі змагання, фінальне навантаження"
    elif days_left == 1:
        return "🎯 Завтра змагання! Легка пробіжка або повний відпочинок. Підготуй форму, воду і план темпу."
    else:
        return "🏁 Сьогодні змагання! Довіряй підготовці, ти готовий пробігти 10 км! 💥"

# === КОМАНДИ ===
@bot.message_handler(commands=['start', 'test'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Бот активний! Готовий допомагати тобі в тренуваннях.")

# === НАГАДУВАННЯ ===
def running_reminder():
    global pushups_count, running_days_count
    warmup = warmup_links[local_time().day % len(warmup_links)]
    motivation = motivations[local_time().day % len(motivations)]
    tip = running_tips[local_time().day % len(running_tips)]
    intervals = get_interval_plan()
    days_left = (goal_date - date.today()).days

    bot.send_message(USER_ID,
        f"🏃‍♂️ Час на пробіжку!\n"
        f"🔸 Залишилось {days_left} днів до 10 км\n"
        f"🔸 Зроби розминку: {warmup}\n"
        f"🔸 Відтиснись {pushups_count} раз(ів)\n"
        f"🔸 Біг сьогодні: {intervals}\n"
        f"🔸 Оптимальний темп: 7:45–8:30 хв/км (зона жироспалення)\n"
        f"🔸 Порада дня: {tip}\n\n"
        f"{motivation}")

    pushups_count += 1
    running_days_count += 1
    tracker.log_training_day()

# === ІНШІ НАГАДУВАННЯ ===
def weight_checkin():
    bot.send_message(USER_ID, "⚖️ Час зважування! Вкажи свою вагу у кг.")

def mood_checkin():
    bot.send_message(USER_ID, "🧠 Як настрій сьогодні? (від 1 до 10 або короткий опис)")

def sleep_checkin():
    bot.send_message(USER_ID, "🛌 Скільки ти спав у середньому цього тижня?")

def goal_motivation():
    today = local_time()
    days_left = (goal_date - today.date()).days
    bot.send_message(USER_ID, f"📅 До забігу залишилось {days_left} днів! Пам'ятай, твоя мета — пробігти 10 км. \n💥 Ти вже близько до фінішу!")

def sunday_check():
    missed = tracker.check_missed_days()
    if missed:
        bot.send_message(USER_ID,
            f"📋 Ти пропустив тренування у: {', '.join(sorted(missed))}\n"
            f"💡 Спробуй надолужити або розплануй наступний тиждень!")
    else:
        bot.send_message(USER_ID, "✅ Усі тренування цього тижня виконано! Чудова робота!")

    report_path = tracker.generate_weekly_report_pdf()
    with open(report_path, "rb") as pdf_file:
        bot.send_document(USER_ID, pdf_file)

    tracker.reset_week_log()

# === РОЗКЛАД ===
schedule.every().tuesday.at("18:30").do(running_reminder)
schedule.every().wednesday.at("18:30").do(running_reminder)
schedule.every().friday.at("18:30").do(running_reminder)
schedule.every().sunday.at("18:30").do(running_reminder)
schedule.every().monday.at("08:30").do(weight_checkin)
schedule.every().day.at("20:30").do(mood_checkin)
schedule.every().sunday.at("21:00").do(sunday_check)
schedule.every().monday.at("18:30").do(lambda: tracker.send_strength_reminder(bot, USER_ID))
schedule.every().thursday.at("18:30").do(lambda: tracker.send_strength_reminder(bot, USER_ID))
schedule.every().day.at("08:00").do(goal_motivation)
schedule.every().saturday.at("20:00").do(sleep_checkin)

# === НОВІ НАГАДУВАННЯ ===
def run_interval_reminder():
    bot.send_message(USER_ID,
        "🔁 **Сьогодні — інтервальне тренування**\n"
        "⭐️ 5×3 хв біг у темпі *6:00/км*\n"
        "⭐️ Відпочинок — 2 хв ходьби між інтервалами\n"
        "⭐️ Розминка: 10 хв (швидка ходьба + легкий біг)\n"
        "⭐️ Заминка: 5–10 хв (ходьба + розтяжка)\n\n"
        "🌟 Тримай каденс *165–170 кроків/хв*\n"
        "🧠 Фокус: короткі кроки, дихай ритмічно (2:2)\n"
        "📹 Відео по техніці: https://youtu.be/GDj34zHAe4k")

def run_tempo_reminder():
    bot.send_message(USER_ID,
        "🚀 **Сьогодні — темповий біг**\n"
        "⭐️ 3×8 хв у темпі *6:15–6:30/км*\n"
        "⭐️ Відновлення: 3 хв між сегментами (повільний біг або ходьба)\n"
        "⭐️ Розминка: 10 хв біг/ходьба\n"
        "⭐️ Заминка: 10 хв стретчинг\n\n"
        "📈 Пульс: 155–165 уд/хв (порогова зона)\n"
        "🧠 Фокус: рівний темп, стабільне дихання\n"
        "📹 Техніка бігу: https://youtu.be/PC1N1AfS5n8")

# === РОЗКЛАД ДОПОВНЕННЯ ===
schedule.every().tuesday.at("18:15").do(run_interval_reminder)
schedule.every().wednesday.at("18:15").do(run_tempo_reminder)

# === ЗАПУСК ===
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

keep_alive()
threading.Thread(target=run_schedule, daemon=True).start()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot polling error: {e}")