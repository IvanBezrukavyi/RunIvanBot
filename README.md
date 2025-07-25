# RunIvanBot 🏃‍♂️

**RunIvanBot** — це Telegram-бот для особистої мотивації до бігу та фітнесу, створений на Python. Він надсилає нагадування, перевіряє настрій, веде лог тренувань і щонеділі генерує PDF-звіт.

---

## 🚀 Можливості

- Нагадування про пробіжки та інтервальні тренування
- Мотиваційні повідомлення
- Щотижневий звіт про виконані/пропущені тренування
- Підтримка розминки, техніки бігу і трекінгу
- Надсилання у Telegram через polling
- Пінгується через UptimeRobot для постійного онлайна

---

## 🛠 Технології

- Python 3.12
- Flask (порт 3000) — для пінгування UptimeRobot
- pyTelegramBotAPI
- schedule + threading
- PDF-звіти через `fpdf`
- Replit як хостинг

---

## ⚙️ Як запустити

### 1. Клонуй репозиторій
```bash
git clone https://github.com/your-username/RunIvanBot.git
cd RunIvanBot
```

### 2. Створи `.env` файл

```dotenv
BOT_TOKEN=токен_від_@BotFather
USER_ID=твій_telegram_id (через @userinfobot)
```

### 3. Встанови залежності
```bash
pip install -r requirements.txt
```

### 4. Запуск (локально)

```bash
python runbot.py
```

### 5. Деплой на Render.com

1. Створи новий Web Service на [Render.com](https://render.com/)
2. Вкажи репозиторій GitHub
3. Інсталюй Python 3.12 як середовище
4. Вкажи команду запуску: `python runbot.py`
5. Додай змінні середовища (наприклад, `BOT_TOKEN`, `USER_ID`)

> **Примітка:** Для підтримки онлайн-статусу можна використовувати UptimeRobot, який буде пінгувати Flask endpoint на порту 3000.

---


## 🖥 UptimeRobot інтеграція

1. Знайди публічний URL твого Render.com Web Service (Flask endpoint)
2. Встав у [UptimeRobot](https://uptimerobot.com/) як **HTTP monitor**
3. Перевірка що 5 хв, очікуваний статус: `200 OK`