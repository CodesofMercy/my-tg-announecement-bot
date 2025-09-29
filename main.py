import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from events import start, events_command, show_events_handler, show_event_details_handler, start_handler
from registration import conv_handler
from user_registration import handle_contact

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Твой токен
TOKEN = 'USE YOUR TOKEN'

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(start)
    application.add_handler(events_command)
    application.add_handler(show_events_handler)
    application.add_handler(show_event_details_handler)
    application.add_handler(start_handler)
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()