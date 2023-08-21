import logging

logging.basicConfig(
    filename="errors.log",
    filemode='w',
    format='%(asctime)s: %(name)s - %(levelname)s - %(message)s'
)

class Errors:
    ERROR = "🛠 Технические трудности, которые мы уже исправляем. Пожалуйста, попробуйте позже."


class ErrorHandler:
    def handle(bot, tg_id, error):
        bot.send_message(
                tg_id,
                Errors.ERROR
            )
        logging.error(error)
    
    def handle_ofye(error):
        logging.fatal(error)