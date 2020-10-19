from .forms import Water_Values_Form, Electro_Values_Form
from .models import Water_values, Electro_values, Customers
from django.db.models import Max
from django.shortcuts import render, redirect


def add_water_values(request, pk):
    ctx = {}
    ctx['page_type'] = 'water'
    form = Water_Values_Form(initial={'customer': pk})
    ctx['form'] = form
    max_previous_values = Water_values.objects.filter(customer=pk).aggregate(Max('w_values'))[
        'w_values__max']
    if max_previous_values is None:
        max_previous_values = 0
    ctx['max_previous_values'] = max_previous_values
    ctx['last_date'] = Water_values.objects.filter(customer=pk).aggregate(Max('add_date'))[
        'add_date__max']
    if request.method == 'POST':
        form = Water_Values_Form(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['w_values'] >= max_previous_values:
                form.save()
                return redirect(f'/w-values/{pk}/')
            else:
                ctx['value_error'] = True
                return render(request, 'values/add_values.html', ctx)
    return render(request, 'values/add_values.html', ctx)


def add_electro_values(request, pk):
    ctx = {}
    ctx['page_type'] = 'electro'
    form = Electro_Values_Form(initial={'customer': pk})
    max_previous_values_day = Electro_values.objects.filter(customer=pk).aggregate(Max('e_values_daytime'))[
        'e_values_daytime__max']
    if max_previous_values_day is None:
        max_previous_values_day = 0
    ctx['max_previous_values_day'] = max_previous_values_day
    max_previous_values_night = Electro_values.objects.filter(customer=pk).aggregate(Max('e_values_nighttime'))[
        'e_values_nighttime__max']
    if max_previous_values_night is None:
        max_previous_values_night = 0
    ctx['max_previous_values_night'] = max_previous_values_night
    ctx['last_date'] = Electro_values.objects.filter(customer=pk).aggregate(Max('add_date'))[
        'add_date__max']
    ctx['form'] = form
    if request.method == 'POST':
        form = Electro_Values_Form(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['e_values_daytime'] >= max_previous_values_day and \
                    form.cleaned_data['e_values_nighttime'] >= max_previous_values_night:
                form.save()
                return redirect(f'/e-values/{pk}/')
            else:
                ctx['value_error'] = True
                return render(request, 'values/add_values.html', ctx)

    return render(request, 'values/add_values.html', ctx)

