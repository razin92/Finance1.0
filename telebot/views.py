import telepot
import time
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
from lib.models import Pouch, Staff
from calc.models import Transaction
from django.utils import timezone
from .models import AuthorizedUser, Schedule

TOKEN = '433011800:AAFWG5KsdK2mMyX-xx9MLeZbksaM82N2ZSU'
bot = telepot.Bot(TOKEN)

#Словарь из входящего Json
def json_extractor(msg):
    return dict(msg)

#Часто используемые данные
def base_data(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    data = {'content_type': content_type, 'chat_type': chat_type, 'chat_id': chat_id}
    return data

class Keyboard():
    def registration_key(self):
        key1 = [KeyboardButton(text='🤝 Регистрация', request_contact=True)]
        keyboard = ReplyKeyboardMarkup(
                keyboard=[key1, ],
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
            )
        return keyboard

    def main_menu(self):
        key1 = [KeyboardButton(text='💳 Баланс счетов')]
        key2 = [KeyboardButton(text='🗞 Транзакции')]
        key3 = [KeyboardButton(text='Заявки')]
        keyboard =  ReplyKeyboardMarkup(
                    keyboard=[key1, key2, key3],
                    resize_keyboard=True
                )
        return keyboard



#Проверка на наличие полей входящего контакта
def user_data_check(msg, user_data):
    if user_data in json_extractor(msg)['contact']:
        return json_extractor(msg)['contact'][user_data]

def user_creator(msg):
    try:
        if 'username' in json_extractor(msg)['from']:
            username = json_extractor(msg)['from']['username']
        else:
            username = None
        user_id = user_data_check(msg, 'user_id')
        telephone = user_data_check(msg, 'phone_number')
        firstname = user_data_check(msg, 'first_name')
        secondname = user_data_check(msg, 'last_name')
        user = AuthorizedUser.objects.create(
            firstname=firstname,
            secondname=secondname,
            user_name=username,
            user_id=user_id,
            telephone=telephone
        )
        message = '🤝 Регистрация успешно завершена'
        return (message, user)
    except:
        message = '🤝 Вы уже зарегистрированы'
        return (message, None)

#Проверка на правльность принятного контакта для регистрации
def registration_control(msg):
    contact = json_extractor(msg)['contact']['user_id']
    sender = json_extractor(msg)['from']['id']
    return contact == sender

def registration(msg):
    content_type = base_data(msg)['content_type']
    chat_id = base_data(msg)['chat_id']
    if content_type == 'contact':
        if registration_control(msg):
            keys = Keyboard.main_menu(msg)
            message, user = user_creator(msg)
            bot.sendMessage(chat_id, message, reply_markup=keys)
            return (True, user)
        else:
            user = AuthorizedUser.objects.filter(user_id=chat_id)
            if user:
                message = '🤝 Вы уже зарегистрированы'
                bot.sendMessage(chat_id, message)
                return (None, None)
            else:
                message = 'Нельзя использовать чужие контакты для регистрации! Поделитесь своим контактом. Попробуем еще раз...'
                bot.sendMessage(chat_id, message)
                return (None, None)

def authorization(msg):
    chat_id = base_data(msg)['chat_id']
    user_id = json_extractor(msg)['from']['id']
    registration(msg)
    user = [x for x in AuthorizedUser.objects.filter(user_id=user_id).all()]

    if user:
        return (True, user[0])

    else:
        keys = Keyboard.registration_key(msg)
        message = 'Привет, незнакомец. Чтобы начать использовать бота, необходимо пройти регистрацию'
        bot.sendMessage(chat_id, message, reply_markup=keys)
        return (False, None)

def authentication(msg):
    chat_id = base_data(msg)['chat_id']

    if authorization(msg)[0]:
        user = authorization(msg)[1]
        phone = user.telephone
        staff = [x for x in Staff.objects.filter(telephone=phone).all()]

        if staff:
            return (True, staff[0])

        else:
            message = "У Вас недостаточно прав чтобы продолжить работу с ботом. Обратитесь к администратору"
            bot.sendMessage(chat_id, message)
            return (False, None)

def get_user_pouches(user):
    staff = user.pouches.all()
    staff_pouches = [x.id for x in staff]
    return staff_pouches

def get_schedule_list(user):
    list_schedule = Schedule.objects.filter(accepted=False)
    return list_schedule

def bot_body(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print(dict(msg))
    if authorization(msg)[0]:
        if content_type == 'text' and msg['text'] == '/start':
            keys = Keyboard.main_menu(msg)
            bot.sendMessage(chat_id, 'Вы в системе', reply_markup=keys)
            if authentication(msg)[0]:
                keys = Keyboard.main_menu(msg)
                bot.sendMessage(chat_id,'Кнопки ниже помогут Вам', reply_markup=keys)

        elif content_type == 'text' and msg['text'] == '💳 Баланс счетов':
            result, user = authentication(msg)
            if result:
                #Определяем разрешенные кошельки для отображения
                staff_pouches = get_user_pouches(user)
                pouch = Pouch.objects.filter(id__in=staff_pouches)
                for x in pouch:
                    message = '%s = %s' % (x.name, x.balance)
                    bot.sendMessage(chat_id, message)
        elif content_type == 'text' and msg['text'] == '🗞 Транзакции':
            result, user = authentication(msg)
            if result:
                staff_pouches = get_user_pouches(user)
                transaction = Transaction.objects.filter(money__in=staff_pouches).order_by('-date')[:5]
                message = 'Список последних 5 транзакций: Дата: сумма счет/тип - категория'
                bot.sendMessage(chat_id, message)
                for x in transaction:
                    if x.typeof:
                        type = 'Приход'
                    else:
                        type = 'Расход'
                    message = '%s : %d %s/%s - %s' % (
                        x.date.strftime("%d-%m"),
                        x.sum_val,
                        x.money,
                        type,
                        x.category,
                    )
                    bot.sendMessage(chat_id, message)

        elif content_type == 'text' and msg['text'] == 'Заявки':
            list_schedule = get_schedule_list(1)
            message = 'Список заявок'
            bot.sendMessage(chat_id, message)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Принять', callback_data='accept')],
                ])
            for x in list_schedule:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Принять', callback_data=str(x.id))],
                ])
                message = '%s - Дата подачи %s' % (
                    x.name,
                    x.date_start,
                )

                bot.sendMessage(chat_id, message, reply_markup=keyboard)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    title = Schedule.objects.get(id=int(query_data))
    user = AuthorizedUser.objects.get(user_id=int(from_id))
    staff = Staff.objects.get(telephone=user.telephone)
    title.master = staff
    title.date_accept = timezone.now()
    title.accepted = True
    title.save()

    bot.answerCallbackQuery(query_id, text='ПРИНЯТА')


def personal_bot(msg):
    chat_type = base_data(msg)['chat_type']
    chat_id = base_data(msg)['chat_id']
    if chat_type == 'private':
        bot_body(msg)
    else:
        message = 'Я не буду с Вами разговаривать при всех, только с глазу на глаз.'
        bot.sendMessage(chat_id, message)

def run_bot(request):
    MessageLoop(bot, {'chat': personal_bot, 'callback_query': on_callback_query} ).run_as_thread()
    print('Слушаю...')

    while 1:
        time.sleep(10)