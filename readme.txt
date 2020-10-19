1. Клонируем репо с Git-a: git clone https://github.com/dstrbh/DP.git

2. Создаем виртуальное окружение
3. Устанавливаем пакеты из requirements.txt: pip3 install -r requirements.txt
4. Создаем миграции: python3 manage.py makemigrations
5. Создаем БД: python3 manage.py migrate
6. Создаем суперпользователя для админки: python3 manage.py createsuperuser

7. Запускаем сервер: python3 manage.py runserver 127.0.0.1:9000

8. Запускаем телеграм-бота: python manage.py telegram_bot
    Предварительно вставляем валидный токен в файл: "acc/management/commands/lib/bot_config.py"