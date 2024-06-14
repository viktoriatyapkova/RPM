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
    assert response.json == []


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
    assert len(response.json) == 2

    response = client.get('/movies/search?title=1')
    assert response.status_code == OK
    assert len(response.json) == 1


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
        json={USERNAME: 'user5', 'email': 'user5@example.com', 'password': TEST_PASSWORD},
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
