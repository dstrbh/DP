from django.shortcuts import render, redirect, HttpResponse
from .models import Customers, Water_values, Electro_values, Payment_Data
from django.contrib.auth.decorators import login_required
from .forms import *
from django.db.models import Q, Max, Sum
from .outer_function import *
import datetime

# todo Очистить импорт
from reportlab.pdfgen import canvas
from django.http import HttpResponse



# todo Очистить тестовую функцию
def test_fn(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='rrr')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response


def start(request):
    ctx = {}
    return render(request, 'acc/main_page.html', ctx)


@login_required
def customers_page(request):
    ctx = {}
    ctx['page'] = 'customers_p'
    ctx['customers'] = Customers.objects.all()
    ctx['c_water_customers'] = Customers.objects.filter(water_service=True).count()
    ctx['c_el_customers'] = Customers.objects.filter(el_service=True).count()
    # сортировка по полю фамилия
    if request.path == '/cstmrs/d-fio/':
        ctx['page'] = 'customers_p_d_fio'
        ctx['customers'] = Customers.objects.all().order_by('surname')
    # сортировка по полю фамилия в обратном порядке
    elif request.path == '/cstmrs/r-fio/':
        ctx['page'] = 'customers_p_r_fio'
        ctx['customers'] = Customers.objects.all().order_by('-surname')
    # сортировка по полю адреса в прямом порядке
    if request.path == '/cstmrs/d-adress/':
        ctx['page'] = 'customers_p_d_adress'
        ctx['customers'] = Customers.objects.all().order_by('massive', 'line', 'sector')
    # сортировка по полю адреса в обратном порядке
    elif request.path == '/cstmrs/r-adress/':
        ctx['page'] = 'customers_p_r_adress'
        ctx['customers'] = Customers.objects.all().order_by('-massive', '-line', '-sector')

    # Форма поиска на той же странице
    if request.path == '/search-customer/':
        ctx['search'] = True
    if request.method == 'POST':
        fio = request.POST['fio'] or 'Null text'
        massive_ = request.POST['massive_'] or 0
        line_ = request.POST['line_'] or 0
        sector_ = request.POST['sector_'] or 0

        found_customers = Customers.objects.filter(Q(name__contains=fio) | Q(surname__contains=fio) |
                                                   Q(second_name__contains=fio) | Q(massive=massive_) |
                                                   Q(line=line_) | Q(sector=sector_))
        ctx['customers'] = found_customers

    return render(request, 'acc/customers.html', ctx)


@login_required
def customer_detail(request, customer_id):
    ctx = {}
    get_customer = Customers.objects.get(pk=customer_id)
    ctx['customer'] = get_customer
    get_water_values = Water_values.objects.filter(customer=customer_id)
    ctx['water_values'] = get_water_values.order_by('add_date').reverse()[:3]
    get_el_values = Electro_values.objects.filter(customer=customer_id)
    ctx['el_values'] = get_el_values.order_by('add_date').reverse()[:3]
    try:
        water_payment = Payment_Data.objects.filter(customer=customer_id, payment_w_values__gt=0)
        ctx['water_payment'] = water_payment.latest('payment_date_check')
        sum_water_payment = water_payment.aggregate(Sum('payment_w_values'))['payment_w_values__sum']
        ctx['sum_water_payment'] = sum_water_payment
        ctx['water_debt'] = get_water_values.latest('add_date').w_values - sum_water_payment
    except Exception as e:
        ctx['err_w_p'] = e
    try:
        # Определяем оплаты для электричества для Пользователя, отдельно для ненулевых значений.
        '''нужно вывести:  latest_payment_date - Дата последней оплаты
                        sum_e_payments_day - Суммарно оплачено днем
                        sum_e_payments_night - Суммарно оплачено ночь
                        el_debt_day - Долг по оплате на тек.датую День.
                        el_debt_night - Долг по оплате на текущую дату. Ночь.
        '''
        ctx['latest_payment_date'] = Payment_Data.objects.filter(
            Q(payment_e_values_daytime__gt=0) | Q(payment_e_values_nighttime__gt=0), customer=customer_id). \
            latest('payment_date_check').payment_date_check
        sum_e_payments_day = Payment_Data.objects.filter(customer=customer_id).aggregate \
            (Sum('payment_e_values_daytime'))['payment_e_values_daytime__sum']
        ctx['sum_e_payments_day'] = sum_e_payments_day
        sum_e_payments_night = Payment_Data.objects.filter(customer=customer_id).aggregate \
            (Sum('payment_e_values_nighttime'))['payment_e_values_nighttime__sum']
        ctx['sum_e_payments_night']  =sum_e_payments_night
        ctx['el_debt_day'] = get_el_values.latest('add_date').e_values_daytime - sum_e_payments_day
        ctx['el_debt_night'] = get_el_values.latest('add_date').e_values_nighttime - sum_e_payments_night


        # electro_payment_day = Payment_Data.objects.filter(customer=customer_id, payment_e_values_daytime__gte=0)
        # electro_payment_night = Payment_Data.objects.filter(customer=customer_id,
        #                                                     payment_e_values_nighttime__gte=0)
        # ctx['electro_payment_daytime'] = electro_payment_day.latest('payment_date_check')
        # ctx['electro_payment_nighttime'] = electro_payment_night.latest('payment_date_check')
        # sum_e_payments_day = electro_payment_day.aggregate(Sum('payment_e_values_daytime'))[
        #     'payment_e_values_daytime__sum']
        # ctx['sum_e_payments_day'] = sum_e_payments_day
        # sum_e_payments_night = electro_payment_night.aggregate(Sum('payment_e_values_nighttime'))[
        #     'payment_e_values_nighttime__sum']
        #
        # ctx['sum_e_payments_night'] = sum_e_payments_night
        # ctx['el_debt_day'] = get_el_values.latest('add_date').e_values_daytime - sum_e_payments_day
        # ctx['el_debt_night'] = get_el_values.latest('add_date').e_values_nighttime - sum_e_payments_night
        # print('this way')
        # ctx['latest_payment_date'] = max(electro_payment_day.latest('payment_date_check').payment_date_check,
        #                                  electro_payment_night.latest('payment_date_check').payment_date_check)

    except Exception as el:
        ctx['err_e_p'] = el
        print(el)

    return render(request, 'acc/customer_detail.html', ctx)


@login_required
def add_customer(request):
    ctx = {}
    if request.method == 'POST':
        form = Customer_Form(request.POST, request.FILES)
        # adress_list = [form.massive, form.line, form.sector]
        if form.is_valid():
            if not Customers.objects.filter(massive=form.cleaned_data['massive'], line=form.cleaned_data['line'],
                                            sector=form.cleaned_data['sector']):
                cstmrs = form.save()
                return redirect('/cstmrs/')
            else:
                ctx['form'] = form
                ctx['adress_err'] = 'Такой адрес уже существует'
                return render(request, 'acc/add_customer.html', ctx)
    else:
        form = Customer_Form()
    ctx['form'] = form
    return render(request, 'acc/add_customer.html', ctx)


@login_required
def edit_customer(request, pk):
    ctx = {}
    customer = Customers.objects.get(pk=pk)
    form = Customer_Edit_Form(instance=customer)
    ctx['form'] = form
    if request.method == 'POST':
        form = Customer_Edit_Form(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            customer = form.save()
            customer.save()
            return redirect('/cstmrs/')

    return render(request, 'acc/edit_customer.html', ctx)


@login_required
def water_values(request, pk):
    ctx = {}
    ctx['customer'] = pk
    ctx['values'] = Water_values.objects.filter(customer=pk)
    # сортировка вывода показаний воды по дате в прямом порядке
    if request.path == f'/w-values/{pk}/d-date/':
        ctx['page'] = 'water_values_d_date'
        ctx['values'] = Water_values.objects.filter(customer=pk).order_by('add_date')
    # сортировка вывода показаний воды по дате в обратном порядке
    elif request.path == f'/w-values/{pk}/r-date/':
        ctx['page'] = 'water_values_r_date'
        ctx['values'] = Water_values.objects.filter(customer=pk).order_by('-add_date')
    # сортировка вывода показаний воды по показаниям в прямом порядке
    elif request.path == f'/w-values/{pk}/d-value/':
        ctx['page'] = 'water_values_d_value'
        ctx['values'] = Water_values.objects.filter(customer=pk).order_by('w_values')
    # сортировка вывода показаний воды по показаниям в обратном порядке
    elif request.path == f'/w-values/{pk}/r-value/':
        ctx['page'] = 'water_values_r_value'
        ctx['values'] = Water_values.objects.filter(customer=pk).order_by('-w_values')
    return render(request, 'values/water_values.html', ctx)


@login_required
def electro_values(request, pk):
    ctx = {}
    ctx['customer'] = pk
    ctx['values'] = Electro_values.objects.filter(customer=pk)
    # сортировка вывода показаний электричества по дате в прямом порядке
    if request.path == f'/e-values/{pk}/d-date/':
        ctx['page'] = 'electro_values_d_date'
        ctx['values'] = Electro_values.objects.filter(customer=pk).order_by('add_date')
    # сортировка вывода показаний электричества по дате в обратном порядке
    elif request.path == f'/e-values/{pk}/r-date/':
        ctx['page'] = 'electro_values_r_date'
        ctx['values'] = Electro_values.objects.filter(customer=pk).order_by('-add_date')
    # сортировка вывода показаний электричества по дневным показаниям в прямом порядке
    elif request.path == f'/e-values/{pk}/d-value_day/':
        ctx['page'] = 'electro_values_d_value_day'
        ctx['values'] = Electro_values.objects.filter(customer=pk).order_by('e_values_daytime')
    # сортировка вывода показаний электричества по дневным показаниям в обратном порядке
    elif request.path == f'/e-values/{pk}/r-value_day/':
        ctx['page'] = 'electro_values_r_value_day'
        ctx['values'] = Electro_values.objects.filter(customer=pk).order_by('-e_values_daytime')
    # сортировка вывода показаний электричества по ночным показаниям в прямом порядке
    elif request.path == f'/e-values/{pk}/d-value_night/':
        ctx['page'] = 'electro_values_d_value_night'
        ctx['values'] = Electro_values.objects.filter(customer=pk).order_by('e_values_nighttime')
    # сортировка вывода показаний электричества по ночным показаниям в обратном порядке
    elif request.path == f'/e-values/{pk}/r-value_night/':
        ctx['page'] = 'electro_values_r_value_night'
        ctx['values'] = Electro_values.objects.filter(customer=pk).order_by('-e_values_nighttime')
    return render(request, 'values/electro_values.html', ctx)


@login_required
def add_values(request, pk):
    if request.path == f'/w-values/add/{pk}/':
        return add_water_values(request, pk)
    elif request.path == f'/e-values/add/{pk}/':
        return add_electro_values(request, pk)


@login_required
def edit_value(request, pk):
    ctx = {}
    if request.path == f'/e-values/edit/{pk}/':
        ctx['page_type'] = 'edit_e'
        value = Electro_values.objects.get(pk=pk)
        form = Electro_Values_Form(instance=value)
        if request.method == "POST":
            form = Electro_Values_Form(request.POST, request.FILES, instance=value)
            if form.is_valid():
                form.save()
                return redirect('acc_app:electro_values', pk=value.customer_id)
    elif request.path == f'/w-values/edit/{pk}/':
        ctx['page_type'] = 'edit_w'
        value = Water_values.objects.get(pk=pk)
        form = Water_Values_Form(instance=value)
        if request.method == "POST":
            form = Water_Values_Form(request.POST, request.FILES, instance=value)
            if form.is_valid():
                form.save()
                return redirect('acc_app:water_values', pk=value.customer_id)
    ctx['form'] = form
    ctx['value_pk'] = pk
    print(pk)

    return render(request, 'values/add_values.html', ctx)


@login_required
def del_obj(request, pk):
    ctx = {}
    if request.path == f'/del-confirm_cust/{pk}/':
        ctx['page_type'] = 'del_cust'
        ctx['customer'] = Customers.objects.get(pk=pk)
        if request.method == 'POST':
            customer_to_delete = Customers.objects.get(pk=pk)
            customer_to_delete.delete()
            return redirect('acc_app:customers_p')
    elif request.path == f'/del-confirm-w_value/{pk}/':
        ctx['page_type'] = 'del_w_value'
        ctx['value'] = Water_values.objects.get(pk=pk)
        if request.method == 'POST':
            value_to_delete = Water_values.objects.get(pk=pk)
            customer = value_to_delete.customer_id
            value_to_delete.delete()
            return redirect('acc_app:water_values', pk=customer)
    elif request.path == f'/del-confirm-e_value/{pk}/':
        ctx['page_type'] = 'del_e_value'
        ctx['value'] = Electro_values.objects.get(pk=pk)
        if request.method == 'POST':
            value_to_delete = Electro_values.objects.get(pk=pk)
            customer = value_to_delete.customer_id
            value_to_delete.delete()
            return redirect('acc_app:electro_values', pk=customer)
    elif request.path == f'/del-confirm-payment/{pk}/':
        ctx['page_type'] = 'del_payment'
        ctx['payment'] = Payment_Data.objects.get(pk=pk)
        if request.method == 'POST':
            payment_to_delete = Payment_Data.objects.get(pk=pk)
            customer = payment_to_delete.customer_id
            payment_to_delete.delete()
            return redirect('acc_app:customer_detail', customer_id=customer)
    return render(request, 'service/del_conf.html', ctx)


@login_required
def payments(request, pk):
    ctx = {}
    ctx['customer'] = pk
    if request.path == f'/payments/water/{pk}/':
        ctx['type_payments'] = 'water'
        try:
            ctx['payments'] = Payment_Data.objects.filter(customer=pk, payment_w_values__gt=0)
            sum_w_payments = Payment_Data.objects.filter(customer=pk, payment_w_values__gt=0).aggregate(
                Sum('payment_w_values'))
            ctx['sum_w_payments'] = sum_w_payments['payment_w_values__sum']
            ctx['latest_date'] = Payment_Data.objects.filter(customer=pk, payment_w_values__gt=0).latest(
                'payment_date_check')
        except Exception as e:
            print(e)
            ctx['err_mess'] = 'Отсутсвуют данные об оплате..'
    elif request.path == f'/payments/electro/{pk}/':
        ctx['type_payments'] = 'electro'
        try:
            payments_ = Payment_Data.objects.filter(
                Q(payment_e_values_daytime__gt=0) | Q(payment_e_values_nighttime__gt=0), customer=pk)
            ctx['payments'] = payments_
            sum_e_payments_day = Payment_Data.objects.filter(customer=pk,
                                                             payment_e_values_daytime__gte=0).aggregate(
                Sum('payment_e_values_daytime'))
            sum_e_payments_night = Payment_Data.objects.filter(customer=pk,
                                                               payment_e_values_nighttime__gte=0).aggregate(
                Sum('payment_e_values_nighttime'))
            ctx['sum_e_payments_day'] = sum_e_payments_day['payment_e_values_daytime__sum']
            ctx['sum_e_payments_night'] = sum_e_payments_night['payment_e_values_nighttime__sum']
            ctx['latest_date'] = payments_.latest('payment_date_check')
        except Exception as e:
            print(e)
            ctx['err_mess'] = 'Отсутсвуют данные об оплате..'

    return render(request, 'payment/payments.html', ctx)


@login_required
def add_payments(request, pk):
    ctx = {}
    current_date = datetime.date.today()
    form = Payments_Form(initial={'customer': pk, 'payment_date_check': current_date})
    ctx['form'] = form
    if request.method == 'POST':
        form = Payments_Form(request.POST)
        if form.is_valid():

            form.save()
            return redirect('acc_app:customer_detail', customer_id=pk)
        else:
            ctx['validation_err'] = 'Данные введены некорректно'
    return render(request, 'payment/add_payments.html', ctx)


@login_required
def payment_detail(request, pk):
    ctx = {}
    ctx['payment_id'] = pk
    payment = Payment_Data.objects.get(pk=pk)
    form = Payments_Form(instance=payment)
    ctx['form'] = form
    if request.method == 'POST':
        form = Payments_Form(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('acc_app:customer_detail', customer_id=payment.customer_id)
        else:
            ctx['validation_err'] = 'Данные введены некорректно'
    return render(request, 'payment/payment_detail.html', ctx)

def comunity(request):

    return render(request, 'acc/comunity.html')


