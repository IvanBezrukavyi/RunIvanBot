from datetime import datetime
import pytz
from fpdf import FPDF

ukraine_tz = pytz.timezone("Europe/Kyiv")

# Дні тижня, в які планується біг
scheduled_days = {"Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"}

# Список успішних днів (лог)
running_log = set()


def log_training_day():
    today = datetime.now(ukraine_tz).strftime("%A")
    running_log.add(today)


def check_missed_days():
    missed = scheduled_days - running_log
    return missed


def reset_week_log():
    running_log.clear()


# Створити PDF-звіт тижня
def generate_weekly_report_pdf():
    now = datetime.now(ukraine_tz)
    report_name = f"weekly_report_{now.strftime('%Y-%m-%d')}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Тижневий звіт про тренування", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Дата звіту: {now.strftime('%d.%m.%Y')}", ln=1)
    pdf.ln(5)

    pdf.cell(200, 10, txt="✅ Виконані дні:", ln=1)
    if running_log:
        for day in sorted(running_log):
            pdf.cell(200, 10, txt=f"- {day}", ln=1)
    else:
        pdf.cell(200, 10, txt="- Немає записів цього тижня", ln=1)

    pdf.ln(5)
    missed = check_missed_days()
    pdf.cell(200, 10, txt="❌ Пропущені дні:", ln=1)
    if missed:
        for day in sorted(missed):
            pdf.cell(200, 10, txt=f"- {day}", ln=1)
    else:
        pdf.cell(200, 10, txt="- Усі тренування виконано!", ln=1)

    pdf.output(report_name)
    return report_name


# Силові тренування (гантелі) для рук
def strength_reminder():
    return (
        "💪 Сьогодні силове тренування на руки з гантелями!\n\n"
        "🔸 3 підходи по 10–12 повторів:\n"
        "- Підйом гантелей на біцепс\n"
        "- Французький жим\n"
        "- Плечовий жим стоячи\n"
        "- Тяга до підборіддя\n\n"
        "🎥 Відео для прикладу (12 хв): https://youtu.be/baii-KM6kS0"
    )


# Відправка силового нагадування до Telegram
def send_strength_reminder(bot, user_id):
    message = strength_reminder()
    bot.send_message(user_id, message)
