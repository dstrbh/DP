from django.contrib import admin
from .models import *

# Register your models here.

class CustomersAdmin(admin.ModelAdmin):
    # site = f'Участок - {massive}-{line}-{sector}'
    list_display =['__str__', 'surname', 'name', 'second_name', 'water_service', 'el_service']
    list_editable =['water_service', 'el_service']
    list_display_links = ['__str__', 'surname']


class Water_values_Admin(admin.ModelAdmin):
    list_display = ['customer','add_date', 'w_values']

class Electro_values_Admin(admin.ModelAdmin):
    list_display = ['customer','add_date', 'e_values_daytime', 'e_values_nighttime']


class Payment_Data_Admin(admin.ModelAdmin):
    list_display = ['customer', 'payment_date_check', 'payment_w_values', 'payment_e_values_daytime', 'payment_e_values_nighttime']

admin.site.register(Customers, CustomersAdmin)
admin.site.register(Water_values, Water_values_Admin)
admin.site.register(Electro_values, Electro_values_Admin)
admin.site.register(Payment_Data, Payment_Data_Admin)



