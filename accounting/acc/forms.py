from django import forms
from .models import Customers, Water_values, Electro_values, Payment_Data

class Customer_Form(forms.ModelForm):
    class Meta:
        model = Customers
        fields = ['surname', 'name', 'second_name', 'massive',
                  'line', 'sector', 'phone_1', 'phone_2', 'email', 'water_service',
                  'water_counter_number', 'water_counter_last_check', 'water_counter_next_check',
                   'water_counter_photo','el_service', 'el_counter_number',
                  'el_counter_last_check', 'el_counter_next_check', 'el_counter_photo',
                  'notation']
        widgets = {

            'water_counter_last_check':forms.SelectDateWidget(years=range(2010,2023), attrs={'class': 'form-control-sm'}),
            'water_counter_next_check':forms.SelectDateWidget(years=range(2020,2032), attrs={'class': 'form-control-sm'}),
            'el_counter_last_check':forms.SelectDateWidget(years=range(2010,2023), attrs={'class': 'form-control-sm'}),
            'el_counter_next_check':forms.SelectDateWidget(years=range(2020,2032), attrs={'class': 'form-control-sm'}),
        }

class Water_Values_Form(forms.ModelForm):
    class Meta:
        model = Water_values
        fields = "__all__"
        exclude = ['provides_by']

class Electro_Values_Form(forms.ModelForm):
    class Meta:
        model = Electro_values
        fields = "__all__"
        exclude = ['provides_by']

class Payments_Form(forms.ModelForm):
    class Meta:
        model = Payment_Data
        fields = '__all__'
        widgets = {
        'payment_date_check':forms.SelectDateWidget(years=range(2020, 2040), attrs={'class': 'form-control-sm'}),
        }

class Customer_Edit_Form(Customer_Form):
    class Meta:
        model = Customers
        fields = ['surname', 'name', 'second_name', 'massive',
                  'line', 'sector', 'phone_1', 'phone_2', 'email', 'water_service',
                  'water_counter_number', 'water_counter_last_check', 'water_counter_next_check',
                   'water_counter_photo','el_service', 'el_counter_number',
                  'el_counter_last_check', 'el_counter_next_check', 'el_counter_photo',
                  'notation']
        widgets = {

            'water_counter_last_check':forms.SelectDateWidget(years=range(2010,2023), attrs={'class': 'form-control-sm'}),
            'water_counter_next_check':forms.SelectDateWidget(years=range(2020,2032), attrs={'class': 'form-control-sm'}),
            'el_counter_last_check':forms.SelectDateWidget(years=range(2010,2023), attrs={'class': 'form-control-sm'}),
            'el_counter_next_check':forms.SelectDateWidget(years=range(2020,2032), attrs={'class': 'form-control-sm'}),

        }
