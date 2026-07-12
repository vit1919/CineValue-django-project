import asyncio
import logging
from django.core.management.base import BaseCommand
from bot.loader import bot, dp
from bot.handlers import user_handlers 

class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        dp.include_router(user_handlers.router)
        self.stdout.write(self.style.SUCCESS("Бот запускается..."))

        try:
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Бот остановлен"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))

    async def start_bot(self):
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
