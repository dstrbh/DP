from acc.models import Customers, Telegram_User, Water_values, Electro_values, Payment_Data
from django.db.models import Q, Sum

def get_debth_db(user_auth):
    customer = user_auth['customer_id']

    # Блок долга по Воде
    try:
        get_water_values = Water_values.objects.filter(customer=customer)
        latest_water_values = get_water_values.latest('add_date').w_values
    except Exception as e:
        print(e)
        latest_water_values = 0
    try:
        water_payment = Payment_Data.objects.filter(customer=customer, payment_w_values__gt=0)
        sum_water_payment = water_payment.aggregate(Sum('payment_w_values'))['payment_w_values__sum']
    except Exception as e:
        print(e)
        sum_water_payment = 0

    if sum_water_payment is None:
        sum_water_payment = 0
    if latest_water_values is None:
        latest_water_values = 0

    water_debt = latest_water_values - sum_water_payment

    # Блок долга по Электричеству
    try:
        get_el_values = Electro_values.objects.filter(customer=customer)
        latest_electro_values_day = get_el_values.latest('add_date').e_values_daytime
        latest_electro_values_night = get_el_values.latest('add_date').e_values_nighttime
    except Exception as e:
        print(e)
        latest_electro_values_day = 0
        latest_electro_values_night = 0

    try:
        sum_e_payments_day = Payment_Data.objects.filter(customer=customer).aggregate \
            (Sum('payment_e_values_daytime'))['payment_e_values_daytime__sum']
    except Exception as e:
        print(e)
        sum_e_payments_day = 0

    try:
        sum_e_payments_night = Payment_Data.objects.filter(customer=customer).aggregate \
            (Sum('payment_e_values_nighttime'))['payment_e_values_nighttime__sum']
    except Exception as e:
        print(e)
        sum_e_payments_night = 0

    # Дурацкие проверки, т.к. нет времени искать, как ORM должен возвращать 0 вместо None
    if latest_electro_values_day is None:
        latest_electro_values_day = 0
    if sum_e_payments_day is None:
        sum_e_payments_day = 0
    if latest_electro_values_night is None:
        latest_electro_values_night = 0
    if sum_e_payments_night is None:
        sum_e_payments_night = 0

    el_debt_day = latest_electro_values_day - sum_e_payments_day
    el_debt_night = latest_electro_values_night - sum_e_payments_night

    if water_debt < 0:
        water_debt = f'Плюсовой баланс - {water_debt} м3'
    else:
        water_debt = f'Задолженность составляет - {water_debt} м3'

    if el_debt_day < 0:
        el_debt_day = f'Плюсовой баланс - {el_debt_day} кВт'
    else:
        el_debt_day = f'Задолженность составляет - {el_debt_day} кВт'

    if el_debt_night < 0:
        el_debt_night = f'Плюсовой баланс - {el_debt_night} кВт'
    else:
        el_debt_night = f'Задолженность составляет - {el_debt_night} кВт'

    return f'Вода - {water_debt} ' \
           f'Электричество, дневной тариф - {el_debt_day} ' \
           f'ночной тариф - {el_debt_night}'


