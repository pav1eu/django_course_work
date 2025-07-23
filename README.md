# Django CRM Рассылок

Веб-приложение на Django для управления клиентскими рассылками. Пользователи могут создавать,
просматривать, редактировать и удалять рассылки сообщений, а также инициировать их отправку вручную.

---

##  Функциональность

-  Регистрация и авторизация пользователей
-  Управление клиентами 
-  Управление рассылками (создание, редактирование, удаление)
-  Управление шаблонами сообщений
-  Ручная отправка сообщений клиентам
-  Аутентификация и авторизация на основе групп




---
##  Установка

1. Клонируй репозиторий:

```
git clone https://github.com/pav1eu/django_course_work.git
```

2. Установи зависимости:

```
python -m venv venv
```
Windows: 
```
venv\Scripts\activate
```
```
pip install -r requirements.txt
```

3. Выполни миграции

```
python manage.py migrate
```
4. Создай суперпользователя
```
python manage.py createsuperuser
```
5. Запусти сервер
```
python manage.py runserver
```

## Настройка SMTP
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@yandex.ru'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```