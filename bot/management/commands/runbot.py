import threading as th

from django.core.management.base import BaseCommand

from bot.bot import Bot
from bot.commands import Commands
from bot.messages import Messages
from bot.daily_runner import DailyRunner


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot = Bot()
        daily_runner = DailyRunner()


        @bot.instance.message_handler(commands=[Commands.START])
        def handle_start(message):
            bot.start(message)


        @bot.instance.message_handler(regexp=Messages.ADD_ENTITY)
        def handle_add_entity(message):
            bot.process_adding_entity(message)


        @bot.instance.message_handler(regexp=Messages.REMOVE_ENTITY)
        def handle_remove_entity(message):
            bot.process_removing_entity(message)


        @bot.instance.message_handler(regexp=Messages.SHOW_LIST)
        def handle_list(message):
            bot.list(message)


        @bot.instance.message_handler()
        def handle_trash(message):
            bot.trash(message)

        mailing_thread = th.Thread(target=DailyRunner.run, args=[bot.mailing, []])
        polling_thread = th.Thread(target=bot.infinite_polling)
        
        polling_thread.start()
        mailing_thread.start()
