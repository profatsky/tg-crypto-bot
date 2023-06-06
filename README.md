# tg-exchange-rate

Telegram бот для просмотра изменения цен криптовалюты за указанный период

## Функционал:
Доступны 3 команды:
* /d (/day) - изменение цены за день
* /w (/week) - изменение цены за неделю
* /m (/month) - изменение цены за месяц

![demo](app/assets/gifs/rate.gif)

## Инструкция по настройке и установке
### Настройка виртуального окружения и установка зависимостей
```
$ python -m venv venv

$ venv\Scripts\activate.bat - для Windows

$ source venv/bin/activate - для Linux и MacOS

$ python -m pip install -r requirements.txt
```

### Конфиг
Переименуйте файл .env.example в .env и укажите в нем токен бота и ваш ID в Telegram
```
TOKEN = токен бота

ADMIN_ID = ID администратора
```

### Запуск
```
$ cd app

$ python bot.py
```