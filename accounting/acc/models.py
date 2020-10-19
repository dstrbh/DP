from django.db import models



class Customers(models.Model):
    ### Блок ФИО
    surname = models.CharField(max_length=100, verbose_name='Фамилия', blank=True, null=True)
    name = models.CharField(max_length=50, verbose_name='Имя', blank=True, null=True)
    second_name = models.CharField(max_length=50, verbose_name='Отчество', blank=True, null=True)

    ### Блок Адрес
    massive = models.IntegerField(verbose_name='Массив')
    line = models.IntegerField(verbose_name='Линия')
    sector = models.IntegerField(verbose_name='Участок')

    ### Блок Контактов
    phone_1 =models.CharField(max_length = 10, verbose_name = '№ телефона 1', blank = True, null = True)
    phone_2 =models.CharField(max_length = 10, verbose_name = '№ телефона 2', blank = True, null = True)
    email = models.EmailField(max_length = 50, verbose_name = 'e-mail', blank = True, null = True)

    ### Блок Вода
    water_service = models.BooleanField(default=True, verbose_name = 'Наличие договора на воду')
    water_counter_number = models.CharField(max_length=50, verbose_name = '№ счетчика воды', blank=True, null=True)
    water_counter_last_check = models.DateField(verbose_name='Дата последней поверки счетчика', blank = True, null = True)
    water_counter_next_check = models.DateField(verbose_name='Дата следующей поверки счетчика', blank = True, null = True)
    water_counter_photo = models.ImageField(upload_to='photos/base/water_counters/', verbose_name='Фото вводного узла воды', blank=True)

    ### Блок Электро
    el_service = models.BooleanField(default=True, verbose_name = 'Наличие договора на электричество')
    el_counter_number = models.CharField(max_length=50, verbose_name = '№ счетчика электричества', blank=True, null=True)
    el_counter_last_check = models.DateField(verbose_name='Дата последней поверки счетчика', blank = True, null = True)
    el_counter_next_check = models.DateField(verbose_name='Дата следующей поверки счетчика', blank = True, null = True)
    el_counter_photo = models.ImageField(upload_to='photos/base/el_counters', verbose_name='Фото вводного узла электрики', blank=True)

    ### Блок Заметки

    notation = models.TextField(blank=True, null=True, max_length=500, verbose_name='Примечания')


    def __str__(self):
        return f'Участок {self.massive}-{self.line}-{self.sector}: {self.surname} {self.name} {self.second_name}'

    class Meta:
        verbose_name = 'Участок'
        verbose_name_plural = "Участки"

class Water_values(models.Model):
    customer = models.ForeignKey('Customers', on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения показания')
    w_values = models.IntegerField(verbose_name='Текущие показания')
    photo_values = models.ImageField(upload_to='photos/water/%Y/%m/%d/', verbose_name='Фото текущих значений', blank=True)
    notation = models.TextField(blank=True, null=True, max_length=100, verbose_name='Примечания')
    provides_options = (('By_admin', 'Администрацией'), ('By_telegram', 'Телеграм-пользователем'))
    provides_by = models.CharField(max_length=50, choices=provides_options, default='By_admin', verbose_name='Добавлено')

    def __str__(self):
        return f'{self.customer}'
    class Meta:
        verbose_name = 'Показания счетчиков воды'
        verbose_name_plural = "Показания счетчиков воды"
        ordering = ['-add_date']

class Electro_values(models.Model):
    customer = models.ForeignKey('Customers', on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения показания')
    e_values_daytime = models.IntegerField(verbose_name="Текущие показания - дневной тариф")
    e_values_nighttime = models.IntegerField(verbose_name="Текущие показания - ночной тариф")
    photo_values = models.ImageField(upload_to='photos/electro/%Y/%m/%d/', verbose_name='Фото текущих значений', blank=True)
    notation = models.TextField(blank=True, null=True, max_length=100, verbose_name='Примечания')
    provides_options = (('By_admin', 'Администрацией'), ('By_telegram', 'Телеграм-пользователем'))
    provides_by = models.CharField(max_length=50, choices=provides_options, default='By_admin', verbose_name='Добавлено')

    def __str__(self):
        return f'{self.customer}'
    class Meta:
        verbose_name = 'Показания электросчетчиков'
        verbose_name_plural = "Показания электросчетчиков"
        ordering = ['-add_date']

#todo поменять в модели Integer field на Float field для возможности ввода дробных значений оплат
class Payment_Data(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, verbose_name='Потребитель')
    payment_date_check = models.DateField(verbose_name='Дата уточнения оплаты по показаниям')
    payment_w_values = models.FloatField(verbose_name='Оплаченые кубометры воды', blank=True, null=True, default=0)
    payment_e_values_daytime = models.FloatField(verbose_name='Оплаченые КВт электроэенергии (Дневной тариф)', blank=True, null=True, default=0)
    payment_e_values_nighttime = models.FloatField(verbose_name='Оплаченые КВт электроэенергии (Ночной тариф)', blank=True, null=True, default=0)
    def __str__(self):
        return f'{self.customer}'
    class Meta:
        verbose_name = 'Данные об оплате'
        verbose_name_plural = 'Данные об оплате'
        ordering=['payment_date_check']

# Модель экспорта xls

class Export_Data_xls(models.Model):
    export_date = models.DateTimeField(verbose_name='Дата экспорта', auto_now_add=True,)
    user = models.CharField(verbose_name='Пользователь', max_length=50, blank=True, null=True)
    export_file = models.FileField(upload_to='export_xls/', verbose_name='Файл экспорта', blank=True, null=True)
    def __str__(self):
        return  f'{self.export_date}'
    class Meta:
        verbose_name = 'Экспорт показаний Excel'
        verbose_name_plural = 'Экспорт показаний Excel'
        ordering = ['-export_date']

class Telegram_User(models.Model):
    tuser_id = models.IntegerField(verbose_name='ID телеграм-пользователя')
    phone_num = models.IntegerField(verbose_name='Номер телефона пользователя')
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, verbose_name='Потребитель')
    add_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата первой авторизации')

    def __str__(self):
        return f'{self.tuser_id}'
    class Meta:
        verbose_name = 'Пользователи Телеграм'

class TUser_Activity(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, verbose_name='Потребитель')
    activity_date = models.DateTimeField(auto_now_add=True, verbose_name='Время активности телеграм-пользователя')
    action = models.CharField(verbose_name='Название активности телеграм-пользователя', max_length=100)

    def __str__(self):
        return f'{self.tuser_id} - {self.action}'