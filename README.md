# hw05_final
## Финальный проект курса по Джанго ООП
### Возможности проекта:
1. Создание, регистрации, редактирование пользовалей
2. Просмотр блогов и записей, в целом на сайте или по интересным авторам(только для зарегистрированных пользователей)
3. Размещение постов и комментарии к ним.
4. Немного обо ине
### В проекте реализовано:
1. Стандартная модель пользователя Джанго
2. Модели Посты, Комментарии, Подписка
3. Тестирование Unittest
## Для разворачивания проекта на локальной машине:
1. Клонировать проект:
  https://github.com/SergSukh/HW05_finally_Django
2. Установить виртуальное окружение  в рабочей директории:
(Windows) $python -m venv venv
(Mac or Linux) $python3 -m venv venv
4. Активировать виртуальное окружение
5. Установить зависимости:
  pip install -r requirements.txt
6. Выполнить миграции:
  (Windows) $python manage.py migrate
  (Mac or Linux) $python3 manage.py migrate
7. ГОТОВО! можно запустить проект локально командой:
  (Windows) $python manage.py runserver
  (Mac or Linux) $python3 manage.py runserver
### А можно зайти на сайт:
  www.sukhanov.sytes.net

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
