[![Typing SVG align="center"](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=FOODGRAM)](https://git.io/typing-svg)
## О проекте
проект Foodgram это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Использованные технологии:
- Docker
- PostgreSQL
- Python
- Django


## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/VladRusinov/foodgram-project-react.git
```
Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Запустить проект:

```
docker compose up
```

## как заполнить .env:
```
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY=ваш SECRET_KEY
```

## Автор:

Автор - Русинов Влад
