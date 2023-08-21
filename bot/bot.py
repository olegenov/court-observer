import asyncio
import telebot as tb
import pandas as pd
import os

from django.conf import settings

from bot.error_handler import ErrorHandler
from bot.models import Observation, Entity, Case
from bot.messages import Messages
from bot.court_parser import get_court_data, sort_data
from bot.filedriver import FileDriver

'''
Класс бота.
'''
class Bot:
    instance = tb.TeleBot(settings.TOKEN)
    
    def start_webhook(self):
        self.instance.remove_webhook()
        self.instance.set_webhook(url=settings.WEBHOOK_URL)


    '''
    Начало работы.
    '''
    def start(self, message:tb.types.Message):
        self.send_message(
            message.from_user.id,
            Messages.START_TEXT, 
            reply_markup=self.add_CRUD_buttons(message)
        )

    '''
    Добавление отслеживания.
    '''
    def process_adding_entity(self, message:tb.types.Message):
        mes = self.send_message(
            message.from_user.id,
            Messages.CHOOSE_TEXT, 
            reply_markup=self.add_markup_buttons([Messages.CANCEL])
        )

        self.instance.register_next_step_handler(mes, self.add_entity)

    def add_entity(self, message:tb.types.Message):
        if message.text == Messages.CANCEL:
            return self.start(message)

        user_tg = message.from_user.id
        entity_name = message.text 
        
        if Observation.objects.filter(tg=user_tg, entity__name=entity_name).exists():
            self.send_message(user_tg, Messages.NOT_UNIQUE, self.add_CRUD_buttons(message))
            return

        if Entity.objects.filter(name=entity_name).exists():
            entity = Entity.objects.get(name=entity_name)
            observation = Observation.objects.create(tg=user_tg, entity=entity)

            self.send_message(user_tg, Messages.ADD_SUCCESS + f' "{message.text}"\n', self.add_CRUD_buttons(message))

            file = self.get_file(entity)
            message_text = f'❗️ У отслеживаемого лица "{entity.name}" есть дела'

            if file.empty():
                return
    
            with file.open() as document:
                self.send_document(user_tg, message_text, document) 

            file.delete()

            return

        entity = Entity.objects.get_or_create(name=entity_name)[0]
        observation = Observation.objects.create(tg=user_tg, entity=entity)
        
        self.send_message(user_tg, Messages.ADD_SUCCESS + f' "{message.text}"\n' + Messages.WAIT, self.add_CRUD_buttons(message))

        cases = self.parse_court(entity)

        if cases == None:
            return

        for case in cases:
            Case.objects.get_or_create(number=case[0], entity=entity, link=case[1])

        message_text = f'❗️ У отслеживаемого лица "{entity.name}" есть дела'
        file = self.get_file(entity)

        with file.open() as document:
            self.send_document(user_tg, message_text, document)   

        file.delete()
    
    def parse_court(self, entity: Entity):
        parse_result = get_court_data(entity.name)

        if not isinstance(parse_result, pd.DataFrame) or parse_result.empty:
            return None
        
        data = sort_data(parse_result)
        
        cases = []
        
        for (_, row) in data.iterrows():
            case = (row["Номер дела"], row["Ссылка"])
            cases.append(case)

        return cases

    def get_file(self, entity: Entity, cases: [Case]=None):
        if cases == None:
            cases = entity.cases.all()

        df = pd.DataFrame([case.as_dict() for case in cases])
        file_driver = FileDriver(entity.name)
        file_driver.make_excel(df)

        '''
        file_driver = FileDriver(entity.name)
        text = ""

        for case in cases:
            number = case.number
            link = case.link
            row_string = f"{number}: {link}\n\n"
            text += row_string

        file = file_driver.write_file(text)
        '''

        return file_driver

    '''
    Удаление отслеживания.
    '''
    def process_removing_entity(self, message:tb.types.Message):
        user_tg = message.from_user.id
    
        observations = Observation.objects.filter(tg=user_tg)
        entities = [observation.entity.name for observation in observations.all()]
        entities.append(Messages.CANCEL)

        mes = self.send_message(user_tg, Messages.CHOOSE_TEXT, self.add_markup_buttons(entities))

        self.instance.register_next_step_handler(mes, self.remove_entity)

    def remove_entity(self, message:tb.types.Message):
        if message.text == Messages.CANCEL:
            return self.start(message)

        user_tg = message.from_user.id
        entity_name = message.text 

        if not Observation.objects.filter(tg=user_tg, entity__name=entity_name).exists():
            self.send_message(user_tg, Messages.NOT_EXISTS, self.add_CRUD_buttons(message))
            return
        
        observation = Observation.objects.get(tg=user_tg, entity__name=entity_name)
        entity = Entity.objects.get(name=entity_name)
        observation.delete()

        self.send_message(user_tg, Messages.REMOVE_SUCCESS + f' "{entity_name}"', self.add_CRUD_buttons(message))
        
        if entity.observations.count() == 0:
            entity.delete()
    
    '''
    Ответка на мусор.
    '''
    def trash(self, message:tb.types.Message):
        self.send_message(
            message.from_user.id,
            Messages.TRASH_TEXT, 
            reply_markup=self.add_CRUD_buttons(message)
        )

    '''
    Рассылка
    '''
    def mailing(self):
        entities = Entity.objects.all()

        if not entities:
            return
        
        for entity in entities:
            observations = entity.observations.all()

            cases = self.parse_court(entity)
            case_objects = []

            if cases == None:
                continue

            for case in cases:
                if not Case.objects.filter(number=case[0], entity=entity).exists():
                    case_object = Case.objects.get_or_create(number=case[0], entity=entity, link=case[1])[0]
                    case_objects.append(case_object)

            message_text = f'❗️ У отслеживаемого лица "{entity.name}" новые дела'
            file = self.get_file(entity, case_objects)

            with file.open() as document:
                for observation in observations:
                    self.send_document(observation.tg, message_text, document)

            file.delete()

    def list(self, message:tb.types.Message):
        observations = Observation.objects.filter(tg=message.from_user.id)
        entities = [observation.entity.name for observation in observations]
        text = Messages.STALKING + '\n\n📌 ' + '\n📌 '.join(entities)

        self.send_message(
            message.from_user.id,
            text,
            reply_markup=self.add_CRUD_buttons(message)
        )

    '''
    Работа с меню.
    '''
    def add_CRUD_buttons(self, message:tb.types.Message):
        buttons = [Messages.ADD_ENTITY]

        if Observation.objects.filter(tg=message.from_user.id).count() != 0:
            buttons.extend([Messages.REMOVE_ENTITY, Messages.SHOW_LIST])

        return self.add_markup_buttons(buttons)
    
    def add_markup_buttons(self, buttons: list):
        markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)

        for button in buttons:
            markup.add(
                tb.types.KeyboardButton(button)
            )

        return markup
    
    def send_message(self, to:int, text:str, reply_markup:tb.types.ReplyKeyboardMarkup=None):
        try:
            message = self.instance.send_message(
                to,
                text, 
                reply_markup=reply_markup
            )

            if message is None or not isinstance(message, tb.types.Message):
                ErrorHandler.handle_ofye(f"Не удалось доставить сообщение {to}")
            
            return message
        except:
                ErrorHandler.handle_ofye(f"Не удалось завершить функцию отправки сообщения {to}")

    def send_document(self, to:int, caption:str, document):
        try:
            message = self.instance.send_document(
                to,
                caption=caption, 
                document=document
            )

            document.close()

            if message is None or not isinstance(message, tb.types.Message):
                ErrorHandler.handle_ofye(f"Не удалось доставить сообщение {to}")
            
            return message
        except:
                ErrorHandler.handle_ofye(f"Не удалось отправить сообщение {to}")
