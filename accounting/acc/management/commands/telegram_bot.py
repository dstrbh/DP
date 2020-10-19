from django.core.management.base import BaseCommand
import telebot
from .lib import bot_config, teleg_db_func
from .lib.logging import log
from telebot import types
from acc.models import Customers, Telegram_User, Water_values, Electro_values, Payment_Data, TUser_Activity
from django.db.models import Q

user_auth = {}

# наличие данного класа и функции handle - требование Django при оспользовании базовых команд.
class Command(BaseCommand):
    def handle(self, *args, **options):

        bot = telebot.TeleBot(bot_config.token)

        @bot.message_handler(func=lambda message: message.content_type == 'text')
        @log
        def start_bot(message):
            bot.send_message(message.from_user.id,
                             'Здравствуй! Я программа-бот СОГ Черноморец. При помощи меня ты сможешь передать показания счетчиков воды и электричества а так же узнать задолженность.')

            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text='Да. Готов пройти проверку', callback_data='yes')
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
            keyboard.add(key_yes, key_no)

            bot.send_message(message.from_user.id,
                             'Работа с ботом доступна только для членов СОГ Черноморец. Для начала нам нужно узнать что ты таковым являешься.',
                             reply_markup=keyboard)

        @bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
        @log
        def callback_worker(call):
            if call.data == "yes":
                check_phone1(call)
            elif call.data == "no":
                info_func(call)

        def check_phone1(message):
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            button_phone = types.KeyboardButton(text='Отправить свой номер телефона', request_contact=True)
            keyboard.add(button_phone)
            msg = bot.send_message(message.from_user.id,
                                   'Отправь свой номер телефона для продолжения. Кнопка подтверждения внизу окна.',
                                   reply_markup=keyboard)
            bot.register_next_step_handler(msg, check_phone2)

        @log
        def check_phone2(message):
            try:
                # Дополнительное условие, т.к. клиент телеграм РС передает номер в формате +38...
                if message.contact.phone_number.startswith('+'):
                    phone_number = message.contact.phone_number[3:]
                else:
                    phone_number = message.contact.phone_number[2:]

                keyboard = types.ReplyKeyboardRemove()
                phone_DB = Customers.objects.filter(
                    Q(phone_1__contains=phone_number) | Q(phone_2__contains=phone_number))
                # Проверяем, не пустой ли QuerySet c найденными пользователями
                if phone_DB:
                    bot.send_message(message.from_user.id,
                                     "Да, действительно такой номер телефона у нас зарегистрирован",
                                     reply_markup=keyboard)
                    # пишем в глобальную переменную номер телефона
                    user_auth['phone'] = phone_number
                    check_massive(message)
                else:
                    bot.send_message(message.from_user.id, '''Такой номер телефона не зарегистрирован в нашей базе.''')
                    wrong_auth(message)
            except Exception as e:
                check_phone1(message)

        # @log
        def check_massive(message):
            msg = bot.send_message(message.from_user.id, "Введи номер МАССИВА твоего участка")
            bot.register_next_step_handler(msg, check_line)

        # Проверка введненного Массива и запрос ввода Линии
        @log
        def check_line(message):
            # print(message)
            if message.text.isdigit():
                massive = message.text
                # Проверяем, не пустой ли QuerySet c найденными пользователями
                massive_DB = Customers.objects.filter(massive=massive)
                # Проверяем, не пустой ли QuerySet c найденными пользователями
                if massive_DB:
                    user_auth['massive'] = message.text
                    msg = bot.send_message(message.from_user.id, "Введи номер ЛИНИИ твоего участка")
                    bot.register_next_step_handler(msg, check_sector)
                else:
                    bot.send_message(message.from_user.id, "Такого массива у меня в базе нет..")
                    wrong_auth(message)
            else:
                bot.send_message(message.from_user.id, "Нужно ввести именно номер массива (цифра)")
                check_massive(message)

        # Проверка введненного номера Линии и запрос ввода номера участка
        @log
        def check_sector(message):
            if message.text.isdigit():
                line = message.text
                # Проверяем, не пустой ли QuerySet c найденными пользователями
                line_DB = Customers.objects.filter(line=line)
                if line_DB:
                    user_auth['line'] = message.text
                    msg = bot.send_message(message.from_user.id, "Введи НОМЕР твоего участка")
                    bot.register_next_step_handler(msg, success_auth)
                else:
                    bot.send_message(message.from_user.id, "Такой линии у меня в базе нет..")
                    wrong_auth(message)
            else:
                bot.send_message(message.from_user.id, "Нужно ввести именно номер линии (цифра)")
                check_line(message)

        # Проверка введненного номера участка и вывод сообщения
        @log
        def success_auth(message):
            if message.text.isdigit():
                sector = message.text
                user_auth['sector'] = message.text
                user_auth['tuser_id'] = message.from_user.id

                # Проверяем, не пустой ли объект c найденным пользователем (комбинация телефона и адреса)
                user_check_DB = Customers.objects.filter(Q(phone_1__contains=user_auth['phone'])
                                                         | Q(phone_2__contains=user_auth['phone']),
                                                         massive=user_auth['massive'],
                                                         line=user_auth['line'],
                                                         sector=sector)

                if user_check_DB:
                    bot.send_message(message.from_user.id, "Отлично! Ты действительно наш")
                    user_in_DB = Customers.objects.get(massive=user_auth['massive'],
                                                       line=user_auth['line'],
                                                       sector=user_auth['sector'])
                    # Делаем проверку, есть ли у нас в ДБ пользователь с таким telegram ID
                    if not Telegram_User.objects.filter(tuser_id=user_auth['tuser_id']):
                        # Сохраняем запись телеграм пользователя в ДБ
                        telegram_user = Telegram_User(tuser_id=user_auth['tuser_id'],
                                                      phone_num=user_auth['phone'])

                        telegram_user.customer = user_in_DB
                        telegram_user.save()

                    user_auth['customer_id'] = user_in_DB.id
                    select_action(message)

                    print(user_auth)
                else:
                    bot.send_message(message.from_user.id,
                                     "Такой комбинации адреса и номера телефона у меня в базе нет..")
                    wrong_auth(message)
            else:
                bot.send_message(message.from_user.id, "Нужно ввести именно НОМЕР (цифра)")
                check_line(message)

        def select_action(message):
            # Клавиатура выбора дальнейшего действия
            keyboard1 = types.InlineKeyboardMarkup()
            key_debth = types.InlineKeyboardButton(text='Просмотреть задолженность', callback_data='get_debth')
            key_values = types.InlineKeyboardButton(text='Передать показания счетчиков', callback_data='provide_values')
            keyboard1.add(key_debth)
            keyboard1.add(key_values)
            bot.send_message(message.from_user.id,
                             'Хочешь передать показания счетчиков или просмотреть свою задолженность?',
                             reply_markup=keyboard1)

        @bot.callback_query_handler(func=lambda call: call.data in ['get_debth', 'provide_values'])
        def callback_worker1(message):
            if message.data == "get_debth":
                get_debth(message)
            elif message.data == "provide_values":
                provide_values(message)

        @log
        def get_debth(message):
            bot.send_message(message.from_user.id, 'Задолженность по твоему участку:')
            msg = teleg_db_func.get_debth_db(user_auth)
            bot.send_message(message.from_user.id, msg)
            write_user_action(user_auth, f'Запросил задолженность')
            info_func(message)  # Выход из диалога переходом на инфо-функцию

        @log
        def provide_values(message):
            keyboard2 = types.InlineKeyboardMarkup()
            key_water = types.InlineKeyboardButton(text='Показания счетчика воды', callback_data='key_water')
            key_electro = types.InlineKeyboardButton(text='Показания счетчика электричества',
                                                     callback_data='key_electro')
            keyboard2.add(key_water)
            keyboard2.add(key_electro)
            bot.send_message(message.from_user.id, 'Передача показаний счетчиков:', reply_markup=keyboard2)

        @bot.callback_query_handler(func=lambda call: call.data in ['key_water', 'key_electro'])
        def callback_worker(message):
            if message.data == 'key_water':
                input_water_values1(message)
            elif message.data == 'key_electro':
                input_electro_values1(message)

        @log
        def input_water_values1(message):
            msg = bot.send_message(message.from_user.id,
                                   'Введи показания (только цифры) счетчика воды. Введенные показания не должны быть меньше предоставленных ранее')
            bot.register_next_step_handler(msg, input_water_values2)

        @log
        def input_water_values2(message):

            if message.text.isdigit():
                user_auth['water'] = message.text
                check_input_values(message, 'water', f"{user_auth['water']}m3")
            else:
                bot.send_message(message.from_user.id, 'Это не цифры! Показания только в цифрах!!!')
                input_water_values1(message)

            @bot.callback_query_handler(func=lambda call: call.data in ['water-right', 'water-wrong'])
            @log
            def worker(message):
                if message.data == 'water-right':
                    def write_bd_water_w(user_auth, message):
                        bot.send_message(message.from_user.id, f'Записываются показания воды - {user_auth["water"]}')
                        w_values = Water_values(w_values=user_auth['water'],
                                                provides_by='By_telegram')

                        w_values.customer = Customers.objects.get(id=user_auth['customer_id'])
                        w_values.save()
                        write_user_action(user_auth, f'Передал показания воды - {user_auth["water"]}')
                        return values_uploaded(message)

                    # Делаем проверку, на уже имеющиеся в БД показания.
                    latest_w_values = Water_values.objects.filter(customer=user_auth['customer_id'])
                    # Если в ДБ показани присутствуют:
                    if latest_w_values:
                        latest_w_values = latest_w_values.latest('add_date')
                        if int(user_auth['water']) >= latest_w_values.w_values:
                            write_bd_water_w(user_auth, message)
                        else:
                            bot.send_message(message.from_user.id, 'Введеные показания меньше уже имеющихся..')
                            select_action(message)
                    # Если в ДБ показани отсутствуют:
                    else:
                        write_bd_water_w(user_auth, message)

                elif message.data == 'water-wrong':
                    # back to input water values
                    input_water_values1(message)

        @log
        def input_electro_values1(message):
            msg = bot.send_message(message.from_user.id,
                                   'Введи показания (только цифры) счетчика электричества. Введенные показания не должны быть меньше предоставленных ранее.'
                                   '(Для двузоновых счетчиков - дневной тариф)')
            bot.register_next_step_handler(msg, input_electro_values2)

        @log
        def input_electro_values2(message):
            if message.text.isdigit():
                user_auth['el1'] = message.text
                msg = bot.send_message(message.from_user.id,
                                       'Введи показания (только цифры) счетчика Ночного тарифа. Введенные показания не должны быть меньше предоставленных ранее.'
                                       '(Если у тебя нет ночного тарифа - введи 0)')
                bot.register_next_step_handler(msg, input_electro_values3)
            else:
                bot.send_message(message.from_user.id, 'Это не цифры! Показания только в цифрах!!!')
                input_electro_values1(message)

        @log
        def input_electro_values3(message):
            if message.text.isdigit():
                user_auth['el2'] = message.text
                check_input = check_input_values(message, 'el', f'{user_auth["el1"]}кВт и {user_auth["el2"]}кВт')
            else:
                bot.send_message(message.from_user.id, 'Это не цифры! Показания только в цифрах!!!')
                input_electro_values2(message)

            @bot.callback_query_handler(func=lambda call: call.data in ['el-right', 'el-wrong'])
            @log
            def worker(message):
                if message.data == 'el-right':
                    last_el_value_db = Electro_values.objects.filter(customer=user_auth['customer_id'])
                    # проверка, не пустой ли queryset, т.е. есть ли вообще показания данного пользователя
                    def write_el(user_auth):
                        wr_db_el = Electro_values(e_values_daytime=user_auth['el1'],
                                                  e_values_nighttime=user_auth['el2'],
                                                  provides_by='By_telegram')
                        customer = Customers.objects.get(id=user_auth['customer_id'])
                        wr_db_el.customer = customer
                        wr_db_el.save()
                        write_user_action(user_auth, f'Передал показания электричества - {user_auth["el1"]}/{user_auth["el2"]}')
                        return values_uploaded(message)
                    if last_el_value_db:
                        try:
                            last_electro_value_day = last_el_value_db.latest('e_values_daytime').e_values_daytime
                        except Exception as e:
                            last_electro_value_day = 0
                        try:
                            last_electro_value_night = last_el_value_db.latest('e_values_nighttime').e_values_nighttime
                        except Exception as e:
                            last_electro_value_night = 0

                        if int(user_auth['el1']) >= last_electro_value_day and int(user_auth['el2']) >= last_electro_value_night:
                            write_el(user_auth)
                        else:
                            bot.send_message(message.from_user.id, f'Введеные показания меньше уже имеющихся..День - {last_electro_value_day},'
                                                                   f'Ночь - {last_electro_value_night}')
                            select_action(message)
                    else:
                        write_el(user_auth)
                elif message.data == 'el-wrong':
                    input_electro_values1(message)

        # Функция вызова диалога подтверждения введенных данных пользователем
        def check_input_values(message, var1, values):
            keyboard = types.InlineKeyboardMarkup()
            key_right = types.InlineKeyboardButton(text='Все верно', callback_data=f'{var1}-right')
            key_wrong = types.InlineKeyboardButton(text='Нет', callback_data=f'{var1}-wrong')
            keyboard.add(key_right, key_wrong)
            bot.send_message(message.from_user.id,
                             f'Введенные показания - {values}. Верно?', reply_markup=keyboard)

        def wrong_auth(message):
            bot.send_message(message.from_user.id,
                             'Свяжись с правлением СОГ Черноморец для уточнения данных по твоему участку')
            info_func(message)

        # Функция записи активности в БД (передача покказаний либо запрос долга)
        def write_user_action(auth_user, act_text):
            customer = Customers.objects.get(id=user_auth['customer_id'])
            act_text = f'{customer} - {act_text}'
            user_action = TUser_Activity(action=act_text)
            user_action.customer = customer
            user_action.save()

        def values_uploaded(message):
            bot.send_message(message.from_user.id, 'Отлично! Данные пареданы в правление')
            info_func(message)

        def info_func(message):
            bot.send_message(message.from_user.id,
                             'По всем вопросам обращайтесь по телефону: +38-777-777-7777. До встречи!')

        bot.polling(none_stop=True, interval=0)
