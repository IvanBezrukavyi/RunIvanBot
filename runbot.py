
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fitness_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
UKRAINE_TZ = pytz.timezone("Europe/Kyiv")

class FitnessBot:
    """Main fitness bot using tracker module."""
    
    def __init__(self):
        self._load_environment()
        self.bot = telebot.TeleBot(self.bot_token)
        self.tracker = tracker.TrainingTracker()
        self._setup_handlers()
        self._setup_schedule()
        
        # Configuration
        self.goal_date = date(2025, 9, 15)
        
        # Content arrays
        self.warmup_links = [
            "https://www.youtube.com/watch?v=Gf7nqxkY0yU",
            "https://www.youtube.com/watch?v=nph81YymVqg", 
            "https://www.youtube.com/watch?v=K-CrEi0ymMg",
        ]
        
        self.motivations = [
            "💪 Пам'ятай, ти робиш це для себе і свого здоров'я!",
            "🏃‍♂️ Кожен крок наближає тебе до цілі — 10 км!",
            "🔥 Рух — життя. Ти вже на правильному шляху!",
            "✅ Кожне тренування — цеглинка у твоєму новому тілі!",
            "🎯 Неділя — день без перерв! Сьогодні біжиш до кінця!",
        ]
    
    def _load_environment(self):
        """Load environment variables."""
        load_dotenv()
        
        self.bot_token = os.getenv("BOT_TOKEN")
        user_id_str = os.getenv("USER_ID")
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable not set")
        if not user_id_str:
            raise ValueError("USER_ID environment variable not set")
        
        try:
            self.user_id = int(user_id_str)
        except ValueError as exc:
            raise ValueError("USER_ID must be a valid integer") from exc
    
    def _setup_handlers(self):
        """Setup bot message handlers."""
        
        @self.bot.message_handler(commands=['start', 'test'])
        def send_welcome(message):
            response = (
                "🤖 Fitness Bot активний!\n\n"
                "📅 Розклад тренувань:\n"
                "🏃‍♂️ Біг: Вівторок, Середа, П'ятниця, Неділя\n"
                "💪 Силові: Понеділок, Четвер\n"
                "⚖️ Зважування: Понеділок вранці\n"
                "🧠 Настрій: Щодня ввечері\n\n"
                "Команди: /status, /done"
            )
            self.bot.reply_to(message, response)
        
        @self.bot.message_handler(commands=['done'])
        def mark_done(message):
            self._handle_training_completion(message)
        
        @self.bot.message_handler(commands=['status'])
        def send_status(message):
            self._send_status()
    
    def _setup_schedule(self):
        """Setup training schedule."""
        # Running reminders
        schedule.every().tuesday.at("18:30").do(self._send_running_reminder)
        schedule.every().wednesday.at("18:30").do(self._send_running_reminder)
        schedule.every().friday.at("18:30").do(self._send_running_reminder)
        schedule.every().sunday.at("18:30").do(self._send_sunday_running_reminder)
        
        # Strength training
        schedule.every().monday.at("18:30").do(self._send_strength_reminder)
        schedule.every().thursday.at("18:30").do(self._send_strength_reminder)
        
        # Check-ins
        schedule.every().monday.at("07:30").do(self._send_weight_checkin)
        schedule.every().day.at("20:30").do(self._send_mood_checkin)
        schedule.every().sunday.at("21:00").do(self._send_weekly_report)
    
    def get_interval_plan(self) -> str:
        """Get running interval plan based on days left."""
        days_left = (self.goal_date - date.today()).days
        
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
            return "Пробіжка на ~8-9 км у темпі змагання"
        elif days_left == 1:
            return "🎯 Завтра змагання! Легка пробіжка або відпочинок."
        else:
            return "🏁 Сьогодні змагання! Довіряй підготовці! 💥"
    
    def _send_running_reminder(self):
        """Send regular running reminder."""
        try:
            now = datetime.now(UKRAINE_TZ)
            warmup = self.warmup_links[now.day % len(self.warmup_links)]
            motivation = self.motivations[now.day % len(self.motivations)]
            intervals = self.get_interval_plan()
            days_left = (self.goal_date - date.today()).days
            pushups_count = self.tracker.get_current_pushups_count()
            
            message = (
                f"🏃‍♂️ Час на пробіжку!\n\n"
                f"🔸 Залишилось {days_left} днів до 10 км\n"
                f"🔸 Розминка: {warmup}\n"
                f"🔸 Відтиснись {pushups_count} раз(ів)\n"
                f"🔸 Біг сьогодні: {intervals}\n"
                f"🔸 Темп: 7:45–8:30 хв/км\n\n"
                f"{motivation}\n\n"
                f"Після тренування: /done"
            )
            
            self.bot.send_message(self.user_id, message)
            logger.info("Running reminder sent")
            
        except Exception as e:
            logger.error(f"Error sending running reminder: {e}")
    
    def _send_sunday_running_reminder(self):
        """Send special Sunday running reminder - no breaks!"""
        try:
            now = datetime.now(UKRAINE_TZ)
            warmup = self.warmup_links[now.day % len(self.warmup_links)]
            intervals = self.get_interval_plan()
            days_left = (self.goal_date - date.today()).days
            pushups_count = self.tracker.get_current_pushups_count()
            
            message = (
                f"🏃‍♂️🔥 НЕДІЛЯ - ДЕНЬ БЕЗ ПЕРЕРВ! 🔥\n\n"
                f"🎯 Сьогодні ти біжиш до кінця без зупинок!\n"
                f"🔸 Залишилось {days_left} днів до 10 км\n"
                f"🔸 Розминка: {warmup}\n"
                f"🔸 Відтиснись {pushups_count} раз(ів)\n"
                f"🔸 Біг: {intervals}\n"
                f"🔸 ⚠️ ВАЖЛИВО: БЕЗ перерв на ходьбу!\n\n"
                f"💪 Неділя — твій день сили!\n"
                f"🏆 Покажи собі, на що ти здатен!\n\n"
                f"Після тренування: /done"
            )
            
            self.bot.send_message(self.user_id, message)
            logger.info("Sunday running reminder sent")
            
        except Exception as e:
            logger.error(f"Error sending Sunday reminder: {e}")
    
    def _send_strength_reminder(self):
        """Send strength training reminder using tracker."""
        try:
            # ✅ Use tracker's method
            self.tracker.send_strength_reminder(self.bot, self.user_id)
            logger.info("Strength reminder sent")
        except Exception as e:
            logger.error(f"Error sending strength reminder: {e}")
    
    def _send_weight_checkin(self):
        """Send weight check-in reminder."""
        try:
            message = "⚖️ Час тижневого зважування! Вкажи свою вагу у кг."
            self.bot.send_message(self.user_id, message)
        except Exception as e:
            logger.error(f"Error sending weight check-in: {e}")
    
    def _send_mood_checkin(self):
        """Send mood check-in."""
        try:
            message = "🧠 Як настрій сьогодні? (від 1 до 10 або опис)"
            self.bot.send_message(self.user_id, message)
        except Exception as e:
            logger.error(f"Error sending mood check-in: {e}")
    
    def _send_weekly_report(self):
        """Send weekly report using tracker."""
        try:
            # ✅ Use tracker's methods
            missed = self.tracker.check_missed_days()
            
            if missed:
                message = (
                    f"📋 Тижневий звіт\n\n"
                    f"❌ Пропущені: {', '.join(sorted(missed))}\n"
                    f"💡 Надолуж або розплануй краще!"
                )
            else:
                message = (
                    "📋 Тижневий звіт\n\n"
                    "✅ Усі тренування виконано!\n"
                    "🏆 Чудова робота!"
                )
            
            self.bot.send_message(self.user_id, message)
            
            # Generate PDF using tracker
            try:
                report_path = self.tracker.generate_weekly_report_pdf()
                with open(report_path, "rb") as pdf_file:
                    self.bot.send_document(self.user_id, pdf_file)
                os.remove(report_path)
            except Exception as e:
                logger.error(f"Error with PDF: {e}")
            
            # Reset using tracker
            self.tracker.reset_week_log()
            
        except Exception as e:
            logger.error(f"Error sending weekly report: {e}")
    
    def _handle_training_completion(self, message):
        """Handle training completion."""
        try:
            today = datetime.now(UKRAINE_TZ).strftime("%A")
            
            if today in self.tracker.scheduled_running_days:
                pushups = self.tracker.get_current_pushups_count()
                # ✅ Use tracker's method
                self.tracker.log_training_day("running", pushups)
                
                if today == "Sunday":
                    response = (
                        "🏆 Неділя БЕЗ ПЕРЕРВ виконана!\n"
                        f"💪 Відтискання: {pushups}\n"
                        "🔥 Справжня сила волі!"
                    )
                else:
                    response = (
                        f"✅ Пробіжка завершена!\n"
                        f"💪 Відтискання: {pushups}\n"
                        "👏 Чудова робота!"
                    )
                    
            elif today in self.tracker.scheduled_strength_days:
                self.tracker.log_training_day("strength")
                response = "✅ Силове тренування завершено! 💪"
            else:
                response = "🤔 Сьогодні не заплановано тренувань."
            
            self.bot.reply_to(message, response)
            
        except Exception as e:
            logger.error(f"Error handling completion: {e}")
    
    def _send_status(self):
        """Send current status."""
        try:
            today = datetime.now(UKRAINE_TZ)
            day_name = today.strftime("%A")
            days_to_goal = (self.goal_date - date.today()).days
            
            message = (
                f"📊 Статус\n\n"
                f"📅 Сьогодні: {day_name}\n"
                f"🎯 Днів до мети: {days_to_goal}\n"
                f"💪 Віджимання: {self.tracker.get_current_pushups_count()}\n"
                f"🏃‍♂️ Днів бігу: {self.tracker.get_running_days_count()}\n"
            )
            
            if day_name == "Sunday":
                message += "\n🔥 Сьогодні НЕДІЛЯ - біг БЕЗ ПЕРЕРВ!"
            elif day_name in self.tracker.scheduled_running_days:
                message += "\n🏃‍♂️ Сьогодні день бігу"
            elif day_name in self.tracker.scheduled_strength_days:
                message += "\n💪 Сьогодні силове тренування"
            
            self.bot.send_message(self.user_id, message)
            
        except Exception as e:
            logger.error(f"Error sending status: {e}")
    
    def run_scheduler(self):
        """Run scheduler in background thread."""
        def scheduler_loop():
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(60)
        
        threading.Thread(target=scheduler_loop, daemon=True).start()
        logger.info("Scheduler started")
    
    def run(self):
        """Run the bot."""
        self.run_scheduler()
        logger.info("Bot started")
        
        while True:
            try:
                self.bot.polling(none_stop=True, timeout=60)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(10)

def main():
    """Main entry point."""
    try:
        bot = FitnessBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()