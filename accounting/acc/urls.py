from django.urls import path, include
from .views import start, customers_page, customer_detail, \
    add_customer, edit_customer, water_values, electro_values, add_values, del_obj, \
    edit_value, payments, add_payments, payment_detail, comunity
from .auth_views import *
from .export_views import *

app_name = 'acc_app'
urlpatterns = [
    path('', start, name='index'),
    path('search-customer/', customers_page, name='search_customer'),
    path('cstmrs/<int:customer_id>/', customer_detail, name='customer_detail'),
    path('cstmrs/add-cstmr/', add_customer, name = 'add_customer'),
    path('cstmrs/edit-cstmr/<int:pk>/', edit_customer, name = 'edit_customer'),

    path('w-values/<int:pk>/', water_values, name = 'water_values'),
    path('e-values/<int:pk>/', electro_values, name = 'electro_values'),
    path('w-values/add/<int:pk>/', add_values, name = 'add_water_values'),
    path('e-values/add/<int:pk>/', add_values, name = 'add_electro_values'),
    path('e-values/edit/<int:pk>/', edit_value, name = 'edit_electro_values'),
    path('w-values/edit/<int:pk>/', edit_value, name = 'edit_water_values'),
    path('payments/water/<int:pk>/', payments, name = 'w_payments'),
    path('payments/electro/<int:pk>/', payments, name = 'e_payments'),
    path('payments/add/<int:pk>/', add_payments, name = 'add_payments'),
    path('payments/detail/<int:pk>/', payment_detail, name = 'payment_detail'),

    path('comunity/', comunity, name='comunity'),



    ]

values_sort = [
    path('w-values/<int:pk>/d-date/', water_values, name = 'water_values_d_date'),
    path('w-values/<int:pk>/r-date/', water_values, name = 'water_values_r_date'),
    path('w-values/<int:pk>/d-value/', water_values, name = 'water_values_d_value'),
    path('w-values/<int:pk>/r-value/', water_values, name = 'water_values_r_value'),

    path('e-values/<int:pk>/d-date/', electro_values, name='electro_values_d_date'),
    path('e-values/<int:pk>/r-date/', electro_values, name='electro_values_r_date'),
    path('e-values/<int:pk>/d-value_day/', electro_values, name='electro_values_d_value_day'),
    path('e-values/<int:pk>/r-value_day/', electro_values, name='electro_values_r_value_day'),
    path('e-values/<int:pk>/d-value_night/', electro_values, name='electro_values_d_value_night'),
    path('e-values/<int:pk>/r-value_night/', electro_values, name='electro_values_r_value_night'),
    ]

customers = [
            path('cstmrs/', customers_page, name='customers_p'),
            path('cstmrs/d-fio/', customers_page, name='customers_p_d_fio'),
            path('cstmrs/r-fio/', customers_page, name='customers_p_r_fio'),
            path('cstmrs/d-adress/', customers_page, name='customers_p_d_adress'),
            path('cstmrs/r-adress/', customers_page, name='customers_p_r_adress'),
            ]

service = [path('del-confirm_cust/<int:pk>/', del_obj, name='del_customer'),
            path('del-confirm-w_value/<int:pk>/', del_obj, name='del_w_value'),
            path('del-confirm-e_value/<int:pk>/', del_obj, name='del_e_value'),
            path('del-confirm-payment/<int:pk>/', del_obj, name='del_payment'),
           ]

auth = [
    path('login_page/', login_, name='login_page'),
    path('logout/', logout_, name='logout'),
    ]

export = [path('export/', make_export, name='make_export'),

    ]




urlpatterns += export
urlpatterns += service
urlpatterns += auth
urlpatterns += customers
urlpatterns += values_sort