import datetime

# Декоратор логирования
def log(fn):
    def wrapper(ms):
        with open('LOG/telegram.log', 'a') as LOG:
            fn(ms)
            log_chain = 'something going wrong..'
            try:
                if ms.content_type == 'text':
                    log_chain = f'date: {datetime.datetime.fromtimestamp(ms.date)};  mess_ID:{ms.message_id};  user_ID:{ms.from_user.id};  ' \
                                f'cont_type:{ms.content_type};  text:{ms.text}'
                elif ms.content_type == 'contact':
                    log_chain = f'date: {datetime.datetime.fromtimestamp(ms.date)};  mess_ID:{ms.message_id};  user_ID:{ms.from_user.id};  ' \
                                f'cont_type:{ms.content_type};  Phone_Number:{ms.contact.phone_number}'
            except Exception as e:
                print(e)
            try:
                if ms.data:
                    log_chain = f'date: {datetime.datetime.fromtimestamp(ms.message.date)};  mess_ID:{ms.message.message_id};  user_ID:{ms.from_user.id};  ' \
                                f'cont_type:callback_data;  Inline_message_data:{ms.data}'
            except Exception as e:
                print(e)
                LOG.write(log_chain + '\n')

    return wrapper