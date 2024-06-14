"""Данный модуль тестирует API из файла app.py."""

import os

import pytest
from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient

from app import Movie, User, app, db
from config import NOT_FOUND, OK

TEST_YEAR = 2023
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')
TEST_FILM = 'Фильм 1'
PATH_USERS = '/users/'
MESSAGE = 'message'
USERNAME = 'username'

load_dotenv()


def get_connection() -> str:
    """
    Получает строку подключения к базе данных PostgreSQL из переменных окружения.

    Returns:
        str: Строка подключения к базе данных PostgreSQL'
    """
    consts = 'PG_USER', 'PG_PASSWORD', 'PG_HOST', 'PG_PORT', 'PG_DBNAME'
    user, password, host, port, dbname = [os.environ.get(const) for const in consts]

    return f'postgresql://{user}:{password}@{host}:{port}/{dbname}'


@pytest.fixture(scope='session')
def app_with_db():
    """Инициализирует приложение с базой данных для тестирования.

    Yields:
        tuple: Кортеж с объектом приложения и базой данных.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = get_connection()
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app, db

    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture
def client(app_with_db: tuple) -> FlaskClient:
    """Инициализирует клиента для тестирования приложения.

    Args:
        app_with_db (tuple): Кортеж с объектом приложения и базой данных.

    Returns:
        FlaskClient: Клиент Flask для тестирования.
    """
    app, _ = app_with_db
    return app.test_client()


def test_get_movies(client: Flask) -> None:
    """Тест для получения списка фильмов.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    response = client.get('/movies')
    assert response.status_code == OK
    assert response.json == [
        {
            "actors": "{\"Ричард Кайнд\",\"Дэна Хилл\",\"Энди МакЭфи\",\"Тони Джей\",\"Рип Тейлор\",\"Генри Гибсон\",\"Майкл Белл\",\"Эд Гилберт\",\"Дэвид Л. Лэндер\",\"Ховард Моррис\"}",
            "description": "Неугомонная парочка отважных друзей в полнометражном мультфильме «Том и Джерри». Здесь они не гоняются друг за другом, а помогают маленькой девочке найти пропавшего отца.\n\nНо не думайте, что вам будет скучно. Ведь это Том и Джерри! Погони, море опасностей, злые козни старой тетки. Неповторимый юмор и радость от общения с любимыми героями!",
            "director": "{\"Фил Роман\"}",
            "genres": "{мультфильм,мюзикл,комедия,приключения,семейный}",
            "id": 1,
            "kinopoisk_rating": 7.354,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/1704946/8edcfdd3-1197-4fcc-95d3-1923849cd4f0/orig",
            "title": "Том и Джерри: Фильм",
            "year": 1992,
        },
        {
            "actors": "{\"Олег Куликович\",\"Валерий Соловьев\",\"Дмитрий Быковский-Ромашов\",\"Сергей Маковецкий\",\"Дмитрий Высоцкий\",\"Анатолий Петров\",\"Михаил Черняк\",\"Алиса Боярская\",\"Лия Медведева\",\"Юлия Зоркина\"}",
            "description": "По сказкам мы знаем, что было давным-давно, но что было еще давным-давнее? Трем богатырям предстоит узнать ответ на этот вопрос, хоть они его и не задавали. Тут такое началось, что игогошеньки! Горыныч вдруг находит динозаврика, а Алеша Попович с Князем и конем Юлием буквально проваливаются сквозь землю. Теперь надо срочно понять, как вернуть их назад в будущее. А главное, узнать, кто или что такое загадочный Пуп Земли.",
            "director": "{\"Константин Феоктистов\"}",
            "genres": "{мультфильм,приключения,семейный}",
            "id": 2,
            "kinopoisk_rating": 6.851,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/10809116/eaae6412-29ca-422c-93cf-d2774d054dcd/orig",
            "title": "Три богатыря и Пуп Земли",
            "year": 2023,
        },
        {
            "actors": "{\"Александр Петров\",\"Мария Аронова\",\"Анна Савранская\",\"Степан Белозеров\",\"Сергей Лавыгин\",\"Сергей Беляев\",\"Василий Копейкин\",\"Елена Николаева\",\"Виталия Корниенко\",\"Вероника Жилина\"}",
            "description": "Надя выросла и стала фигуристкой. Она мечтает о «Кубке льда», как когда-то мечтала ее мама. Горин возражает против спортивной карьеры дочери — он оберегает ее от любых трудностей. На тайной тренировке Надя знакомится с молодым и дерзким хоккеистом из Москвы, и между ними вспыхивает первая любовь. Отец не верит в искренность чувств юноши и разлучает пару.",
            "director": "{\"Юрий Хмельницкий\"}",
            "genres": "{мелодрама,спорт,мюзикл}",
            "id": 3,
            "kinopoisk_rating": 8.222,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/10671298/5d4e5068-4902-4dd3-a318-c13272de7134/orig",
            "title": "Лёд 3",
            "year": 2024,
        },
        {
            "actors": "{\"Мэттью Макконахи\",\"Энн Хэтэуэй\",\"Джессика Честейн\",\"Маккензи Фой\",\"Майкл Кейн\",\"Дэвид Джеси\",\"Уэс Бентли\",\"Кейси Аффлек\",\"Джон Литгоу\",\"Мэтт Дэймон\"}",
            "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области пространства-времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями.",
            "director": "{\"Кристофер Нолан\"}",
            "genres": "{фантастика,драма,приключения}",
            "id": 4,
            "kinopoisk_rating": 8.639,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/1600647/430042eb-ee69-4818-aed0-a312400a26bf/orig",
            "title": "Интерстеллар",
            "year": 2014,
        },
        {
            "actors": "{\"Роберт Де Ниро\",\"Энн Хэтэуэй\",\"Рене Руссо\",\"Андерс Холм\",\"ДжоДжо Кушнер\",\"Эндрю Рэннеллс\",\"Адам Дивайн\",\"Зак Перлман\",\"Джейсон Орли\",\"Кристина Шерер\"}",
            "description": "70-летний вдовец Бен Уитакер обнаруживает, что выход на пенсию — еще не конец. Пользуясь случаем, он становится старшим стажером в интернет-магазине модной одежды под руководством Джулс Остин.",
            "director": "{\"Нэнси Майерс\"}",
            "genres": "{мелодрама,комедия}",
            "id": 5,
            "kinopoisk_rating": 7.628,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/6201401/d71cea2b-944b-4c37-adf4-aaccfb146924/orig",
            "title": "Стажёр",
            "year": 2015,
        },
        {
            "actors": "{\"Павел Деревянко\",\"Оксана Акиньшина\",\"Павел Табаков\",\"Аглая Тарасова\",\"Максим Виторган\",\"Ингеборга Дапкунайте\",\"Николай Фоменко\",\"Кристина Бабушкина\",\"Юрий Колокольников\",\"Надежда Михалкова\"}",
            "description": "Добро пожаловать на Патриаршие. Смешные и волнующие подробности личной жизни богатых москвичей, которые, как и все, попадают в неловкие ситуации. Правда, ситуации у них не самые обычные... Жена чувствует себя виноватой, познакомившись с любовницей мужа. Муж прикрывается выдуманной дочерью друга. А друг толкает помощника на измену, потому что так хочет жена. И это только начало. Одним словом, неприличные истории о приличных, казалось бы, людях. ",
            "director": "{\"Роман Прыгунов\"}",
            "genres": "{комедия}",
            "id": 6,
            "kinopoisk_rating": 7.727,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/10592371/e2db42c4-4176-4a0f-b933-488412cd06a5/orig",
            "title": "Беспринципные",
            "year": 2020,
        },
        {
            "actors": "{\"Франсуа Клюзе\",\"Омар Си\",\"Анн Ле Ни\",\"Одри Флёро\",\"Жозефин де Мо\",\"Клотильд Молле\",\"Альба Гайя Крагеде Беллуджи\",\"Сирил Менди\",\"Салимата Камате\",\"Абса Дьяту Тур\"}",
            "description": "Пострадав в результате несчастного случая, богатый аристократ Филипп нанимает в помощники человека, который менее всего подходит для этой работы, – молодого жителя предместья Дрисса, только что освободившегося из тюрьмы. Несмотря на то, что Филипп прикован к инвалидному креслу, Дриссу удается привнести в размеренную жизнь аристократа дух приключений.",
            "director": "{\"Оливье Накаш\",\"Эрик Толедано\"}",
            "genres": "{драма,комедия}",
            "id": 7,
            "kinopoisk_rating": 8.826,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/1946459/bf93b465-1189-4155-9dd1-cb9fb5cb1bb5/orig",
            "title": "1+1",
            "year": 2011,
        },
        {
            "actors": "{\"Эдвард Нортон\",\"Брэд Питт\",\"Хелена Бонем Картер\",\"Мит Лоаф\",\"Зэк Гренье\",\"Холт Маккэллани\",\"Джаред Лето\",\"Эйон Бэйли\",\"Ричмонд Аркетт\",\"Дэвид Эндрюс\"}",
            "description": "Сотрудник страховой компании страдает хронической бессонницей и отчаянно пытается вырваться из мучительно скучной жизни. Однажды в очередной командировке он встречает некоего Тайлера Дёрдена — харизматического торговца мылом с извращенной философией. Тайлер уверен, что самосовершенствование — удел слабых, а единственное, ради чего стоит жить, — саморазрушение.\n\nПроходит немного времени, и вот уже новые друзья лупят друг друга почем зря на стоянке перед баром, и очищающий мордобой доставляет им высшее блаженство. Приобщая других мужчин к простым радостям физической жестокости, они основывают тайный Бойцовский клуб, который начинает пользоваться невероятной популярностью.",
            "director": "{\"Дэвид Финчер\"}",
            "genres": "{триллер,драма,криминал}",
            "id": 8,
            "kinopoisk_rating": 8.671,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/1898899/8ef070c9-2570-4540-9b83-d7ce759c0781/orig",
            "title": "Бойцовский клуб",
            "year": 1999,
        },
        {
            "actors": "{\"Сергей Гармаш\",\"Ольга Кузьмина\",\"Полина Максимова\",\"Фёдор Добронравов\",\"Сергей Лавыгин\",\"Елена Яковлева\",\"Дмитрий Лысенков\",\"Софья Зайка\",\"Илья Кондратенко\",\"Ева Смирнова\"}",
            "description": "На небольшой приморский городок обрушивается дождь из апельсинов, а вместе с фруктами с неба падает неизвестный науке мохнатый непоседливый зверёк. Одержимое апельсинами животное оказывается в домике нелюдимого старика-садовника Геннадия, который из вредности решает оставить его жить у себя, так как местная богачка жаждет заполучить необычного зверя для своей избалованной внучки. Также эта коварная женщина, владелица кондитерской фабрики, пытается выведать секрет шоколада у хозяйки маленького магазинчика — дочери Геннадия, много лет обиженной на отца.",
            "director": "{\"Дмитрий Дьяченко\"}",
            "genres": "{семейный,комедия,фэнтези}",
            "id": 9,
            "kinopoisk_rating": 7.373,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/10671298/be64a414-cc47-4050-9f87-7aa635458950/orig",
            "title": "Чебурашка",
            "year": 2022,
        },
        {
            "actors": "{\"Кира Найтли\",\"Джеймс Макэвой\",\"Сирша Ронан\",\"Харриет Уолтер\",\"Ромола Гарай\",\"Бренда Блетин\",\"Патрик Кеннеди\",\"Бенедикт Камбербэтч\",\"Джуно Темпл\",\"Дэниэл Мейс\"}",
            "description": "Действие фильма начинается в 1935 году и разворачивается на фоне Второй мировой войны. Талантливая тринадцатилетняя писательница Бриони Таллис бесповоротно меняет ход нескольких жизней, когда обвиняет любовника старшей сестры в преступлении, которого он не совершал.",
            "director": "{\"Джо Райт\"}",
            "genres": "{драма,мелодрама,детектив,военный}",
            "id": 10,
            "kinopoisk_rating": 8.037,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/4774061/93d7c297-15d6-48e4-907a-88ef9ce359c0/orig",
            "title": "Искупление",
            "year": 2007,
        },
        {
            "actors": "{\"Леонардо ДиКаприо\",\"Тоби Магуайр\",\"Кэри Маллиган\",\"Джоэл Эдгертон\",\"Айла Фишер\",\"Джейсон Кларк\",\"Элизабет Дебики\",\"Каллэн МакОлифф\",\"Джек Томпсон\",\"Амитабх Баччан\"}",
            "description": "Весной 1922 года, в эпоху разлагающейся морали, блистательного джаза и «королей контрабандного алкоголя», Ник Каррауэй приезжает из Среднего Запада в Нью-Йорк. Преследуя собственную американскую мечту, он селится по соседству с таинственным, известным своими вечеринками миллионером Джеем Гэтсби, а на противоположном берегу бухты проживают его кузина Дэйзи и её муж, повеса и аристократ, Том Бьюкенен. Так Ник оказывается вовлечённым в захватывающий мир богатых — их иллюзий, любви и обманов. Он становится свидетелем происходящего в этом мире и пишет историю невозможной любви, вечных мечтаний и человеческой трагедии, которые являются отражением современных времен и нравов.",
            "director": "{\"Баз Лурман\"}",
            "genres": "{драма,мелодрама}",
            "id": 11,
            "kinopoisk_rating": 7.945,
            "poster_url": "https://image.openmoviedb.com/kinopoisk-images/1946459/390dc48d-2025-4323-b225-cb0883ab8374/orig",
            "title": "Великий Гэтсби",
            "year": 2013,
        },
    ]


def test_get_movie(client: Flask) -> None:
    """Тест для получения информации о конкретном фильме.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    movie = Movie(title=TEST_FILM, year=TEST_YEAR)
    db.session.add(movie)
    db.session.commit()

    response = client.get(f'/movies/{movie.id}')
    assert response.status_code == OK
    assert response.json['title'] == TEST_FILM


def test_get_movie_not_found(client: Flask) -> None:
    """Тест для проверки обработки случая, когда фильм не найден.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    response = client.get('/movies/999')
    assert response.status_code == NOT_FOUND


def test_search_movies(client: Flask) -> None:
    """Тест для поиска фильмов по названию.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    movie = Movie(title='Фильм 2', year=TEST_YEAR)
    db.session.add(movie)
    db.session.commit()

    response = client.get('/movies/search?title=Фильм')
    assert response.status_code == OK
    assert len(response.json) == 3

    response = client.get('/movies/search?title=1')
    assert response.status_code == OK
    assert len(response.json) == 2


def test_add_to_watchlist(client: Flask) -> None:
    """Тест для добавления фильма в список "хочу посмотреть".

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    user = User(username='user1', email='user1@example.com', password=TEST_PASSWORD)
    movie = Movie(title=TEST_FILM, year=TEST_YEAR)
    db.session.add_all([user, movie])
    db.session.commit()

    response = client.post(f'{PATH_USERS}{user.id}/watchlist/{movie.id}')
    assert response.status_code == OK
    assert response.json[MESSAGE] == "Фильм добавлен в список 'хочу посмотреть'"

    user = db.session.get(User, user.id)
    assert movie in user.watchlist


def test_add_to_watched(client: Flask) -> None:
    """Тест для добавления фильма в список "уже посмотрел".

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    user = User(username='user2', email='user2@example.com', password=TEST_PASSWORD)
    movie = Movie(title=TEST_FILM, year=TEST_YEAR)
    db.session.add_all([user, movie])
    db.session.commit()

    response = client.post(f'{PATH_USERS}{user.id}/watched/{movie.id}')
    assert response.status_code == OK
    assert response.json[MESSAGE] == "Фильм добавлен в список 'уже посмотрел'"

    user = db.session.get(User, user.id)
    assert movie in user.watched


def test_remove_from_watchlist(client: Flask) -> None:
    """Тест для удаления фильма из списка "хочу посмотреть".

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    user = User(username='user3', email='user3@example.com', password=TEST_PASSWORD)
    movie = Movie(title=TEST_FILM, year=TEST_YEAR)
    user.watchlist.append(movie)
    db.session.add_all([user, movie])
    db.session.commit()

    response = client.delete(f'{PATH_USERS}{user.id}/watchlist/{movie.id}')
    assert response.status_code == OK
    assert response.json[MESSAGE] == "Фильм удален из списка 'хочу посмотреть'"

    user = db.session.get(User, user.id)
    assert movie not in user.watchlist


def test_remove_from_watched(client: Flask) -> None:
    """Тест для удаления фильма из списка "уже посмотрел".

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    user = User(username='user4', email='user4@example.com', password=TEST_PASSWORD)
    movie = Movie(title=TEST_FILM, year=TEST_YEAR)
    user.watched.append(movie)
    db.session.add_all([user, movie])
    db.session.commit()

    response = client.delete(f'{PATH_USERS}{user.id}/watched/{movie.id}')
    assert response.status_code == OK
    assert response.json[MESSAGE] == "Фильм удален из списка 'уже посмотрел'"

    user = db.session.get(User, user.id)
    assert movie not in user.watched


def test_create_user(client: Flask) -> None:
    """Тест для создания пользователя.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    response = client.post(
        '/users',
        json={
            USERNAME: 'user5',
            'email': 'user5@example.com',
            'password': TEST_PASSWORD,
        },
    )
    assert response.status_code == OK
    assert response.json[USERNAME] == 'user5'


def test_get_user(client: Flask) -> None:
    """Тест для получения информации о пользователе.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    user = User(username='user6', email='user6@example.com', password=TEST_PASSWORD)
    db.session.add(user)
    db.session.commit()

    response = client.get(f'{PATH_USERS}{user.id}')
    assert response.status_code == OK
    assert response.json[USERNAME] == 'user6'


def test_get_user_not_found(client: Flask) -> None:
    """Тест для проверки случая, когда пользователь не найден.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    response = client.get(f'{PATH_USERS}999')
    assert response.status_code == NOT_FOUND


def test_update_user(client: Flask) -> None:
    """Тест для обновления информации о пользователе.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    user = User(username='user7', email='user7@example.com', password=TEST_PASSWORD)
    db.session.add(user)
    db.session.commit()

    updated_data = {USERNAME: 'user7_updated', 'email': 'user7_updated@example.com'}
    response = client.put(f'{PATH_USERS}{user.id}', json=updated_data)
    assert response.status_code == OK
    assert response.json[USERNAME] == 'user7_updated'


def test_update_user_not_found(client: Flask) -> None:
    """Тест для проверки обновления информации о несуществующем пользователе.

    Args:
        client (Flask): Клиент Flask для взаимодействия с приложением.
    """
    response = client.put(
        f'{PATH_USERS}999',
        json={USERNAME: 'user7_updated', 'email': 'user7_updated@example.com'},
    )
    assert response.status_code == NOT_FOUND
