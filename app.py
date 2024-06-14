"""Модуль делает API запросы."""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import DEFAULT_PORT, NOT_FOUND, OK

load_dotenv()

KEY = os.environ.get('API_KEY')
NAME = 'name'
GET_REQUEST = 'GET'
ERROR_USER = 'Пользователь не найден'
ERROR_MOVIE = 'Фильм не найден'
ERROR = 'error'
MESSAGE = 'message'
ID_FILM1 = 8244
ID_FILM2 = 4489198
ID_FILM3 = 5275429
ID_FILM4 = 258687
ID_FILM5 = 677893
ID_FILM6 = 1355059
ID_FILM7 = 535341
ID_FILM8 = 361
ID_FILM9 = 4370148
ID_FILM10 = 255611
ID_FILM11 = 463724
LENGTH_USERNAME = 80
LENGTH_EMAIL_PASSWORD = 120
LENGTH_OTHER_DATA = 255
WATCHLIST = 'watchlist'
WATCHED = 'watched'


def get_connection() -> str:
    """
    Получает строку подключения к базе данных PostgreSQL из переменных окружения.

    Returns:
        str: Строка подключения к базе данных PostgreSQL'
    """
    consts = 'PG_USER', 'PG_PASSWORD', 'PG_HOST', 'PG_PORT', 'PG_DBNAME'
    user, password, host, port, dbname = [os.environ.get(const) for const in consts]

    return f'postgresql://{user}:{password}@{host}:{port}/{dbname}'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = get_connection()
db = SQLAlchemy(app)


class User(db.Model):
    """Модель пользователя в базе данных.

    Attributes:
        id (int): Идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Email пользователя.
        password (str): Пароль пользователя.
        watchlist (list[Movie]): Список фильмов в списке "хочу посмотреть" пользователя.
        watched (list[Movie]): Список фильмов в списке "уже посмотрел" пользователя.
    """

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        db.String(LENGTH_USERNAME),
        unique=True,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        db.String(LENGTH_EMAIL_PASSWORD), unique=True, nullable=True,
    )
    password: Mapped[str] = mapped_column(
        db.String(LENGTH_EMAIL_PASSWORD), nullable=True,
    )
    watchlist: Mapped[list['Movie']] = relationship(
        'Movie',
        secondary=WATCHLIST,
        back_populates='user_watchlists',
    )
    watched: Mapped[list['Movie']] = relationship(
        'Movie',
        secondary=WATCHED,
        back_populates='user_watcheds',
    )


class Movie(db.Model):
    """Модель пользователя в базе данных.

    Attributes:
        id (int): Идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Email пользователя.
        password (str): Пароль пользователя.
        watchlist (list[Movie]): Список фильмов в списке "хочу посмотреть" пользователя.
        watched (list[Movie]): Список фильмов в списке "уже посмотрел" пользователя.
    """

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(LENGTH_OTHER_DATA), nullable=True)
    year: Mapped[int] = mapped_column(db.Integer, nullable=True)
    description: Mapped[str] = mapped_column(db.Text, nullable=True)
    kinopoisk_rating: Mapped[float] = mapped_column(db.Float, nullable=True)
    genres: Mapped[str] = mapped_column(db.String(LENGTH_OTHER_DATA), nullable=True)
    poster_url: Mapped[str] = mapped_column(db.String(LENGTH_OTHER_DATA), nullable=True)
    actors: Mapped[str] = mapped_column(db.Text, nullable=True)
    director: Mapped[str] = mapped_column(db.String(LENGTH_OTHER_DATA), nullable=True)
    user_watchlists: Mapped[list['User']] = relationship(
        'User',
        secondary=WATCHLIST,
        back_populates=WATCHLIST,
    )
    user_watcheds: Mapped[list['User']] = relationship(
        'User',
        secondary=WATCHED,
        back_populates=WATCHED,
    )


watchlist = db.Table(
    WATCHLIST,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
)

watched = db.Table(
    WATCHED,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
)


class UserSchema(Schema):
    """
    Схема для валидации и сериализации данных пользователя.

    Атрибуты:
        id (fields.Integer): Уникальный идентификатор пользователя.
        username (fields.String): Имя пользователя.
        email (fields.String): Электронная почта пользователя.
        watchlist (fields.Nested): Список фильмов, которые пользователь хочет посмотреть.
        watched (fields.Nested): Список фильмов, которые пользователь уже посмотрел.
    """

    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    watchlist = fields.Nested('MovieSchema', many=True)
    watched = fields.Nested('MovieSchema', many=True)


class MovieSchema(Schema):
    """
    Схема для валидации и сериализации данных о фильмах.

    Атрибуты:
        id (fields.Integer): Уникальный идентификатор фильма.
        title (fields.String): Название фильма.
        year (fields.Integer): Год выпуска фильма.
        description (fields.String): Краткое описание фильма.
        kinopoisk_rating (fields.Float): Рейтинг фильма на Кинопоиске.
        genres (fields.String): Жанры, связанные с фильмом.
        poster_url (fields.String): URL-адрес постера фильма.
        actors (fields.String): Главные актеры фильма.
        director (fields.String): Режиссер фильма.
    """

    id = fields.Integer()
    title = fields.String()
    year = fields.Integer()
    description = fields.String()
    kinopoisk_rating = fields.Float()
    genres = fields.String()
    poster_url = fields.String()
    actors = fields.String()
    director = fields.String()


def get_movie_info(movie_id) -> dict:
    """Получает информацию о фильме по его идентификатору.

    Args:
        movie_id: Идентификатор фильма.

    Returns:
        dict: Информация о фильме.
    """
    base_url = 'https://api.kinopoisk.dev/v1.4'
    endpoint = f'/movie/{movie_id}'

    headers = {
        'X-API-KEY': KEY,
        'Accept': 'application/json',
    }

    response = requests.get(base_url + endpoint, headers=headers, timeout=1)
    response.raise_for_status()
    if response.status_code == OK:
        movie_data = response.json()

        return {
            'title': movie_data.get(NAME, None),
            'year': movie_data.get('year', None),
            'description': movie_data.get('description', None),
            'kinopoisk_rating': movie_data.get('rating', None).get('kp', None),
            'genres': [genre[NAME] for genre in movie_data.get('genres', [])],
            'poster_url': movie_data.get('poster', None).get('url', None),
            'actors': [
                person[NAME]
                for person in movie_data.get('persons', [])
                if person.get('profession', None) == 'актеры'
            ],
            'director': [
                person[NAME]
                for person in movie_data.get('persons', [])
                if person.get('profession', None) == 'режиссеры'
            ],
        }


@app.route('/movies', methods=[GET_REQUEST])
def get_movies() -> str:
    """Получает список всех фильмов.

    Returns:
        str: JSON с данными о фильмах.
    """
    movies = db.session.query(Movie).all()
    movie_schema = MovieSchema(many=True)
    return jsonify(movie_schema.dump(movies))


@app.route('/movies/<int:movie_id>', methods=[GET_REQUEST])
def get_movie(movie_id) -> str:
    """Получает информацию о конкретном фильме по его идентификатору.

    Args:
        movie_id: Идентификатор фильма.

    Returns:
        str: JSON с данными о фильме.
    """
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({ERROR: 'Не найдено'}), NOT_FOUND
    movie_schema = MovieSchema()
    return jsonify(movie_schema.dump(movie))


@app.route('/movies/search', methods=[GET_REQUEST])
def search_movies() -> str:
    """Поиск фильмов по названию.

    Returns:
        str: JSON с данными о найденных фильмах.
    """
    title = request.args.get('title')
    movies = (
        db.session.query(Movie).
        filter(
            Movie.title.ilike(f'%{title}%'),
        ).
        all()
    )
    movie_schema = MovieSchema(many=True)
    return jsonify(movie_schema.dump(movies))


@app.route('/users/<int:user_id>/watchlist/<int:movie_id>', methods=['POST'])
def add_to_watchlist(user_id, movie_id) -> str:
    """Добавляет фильм в список 'хочу посмотреть' для определенного пользователя.

    Args:
        user_id: Идентификатор пользователя.
        movie_id: Идентификатор фильма.

    Returns:
        str: JSON с сообщением об успешном добавлении фильма.
    """
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({ERROR: ERROR_USER}), NOT_FOUND
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({ERROR: ERROR_MOVIE}), NOT_FOUND

    user.watchlist.append(movie)
    db.session.commit()
    return jsonify({MESSAGE: "Фильм добавлен в список 'хочу посмотреть'"})


@app.route('/users/<int:user_id>/watched/<int:movie_id>', methods=['POST'])
def add_to_watched(user_id, movie_id) -> str:
    """Добавляет фильм в список 'уже посмотрел' для определенного пользователя.

    Args:
        user_id: Идентификатор пользователя.
        movie_id: Идентификатор фильма.

    Returns:
        str: JSON с сообщением об успешном добавлении фильма.
    """
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({ERROR: ERROR_USER}), NOT_FOUND
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({ERROR: ERROR_MOVIE}), NOT_FOUND

    user.watched.append(movie)
    db.session.commit()
    return jsonify({MESSAGE: "Фильм добавлен в список 'уже посмотрел'"})


@app.route('/users/<int:user_id>/watchlist/<int:movie_id>', methods=['DELETE'])
def remove_from_watchlist(user_id, movie_id) -> str:
    """Удаляет фильм из списка 'хочу посмотреть' для определенного пользователя.

    Args:
        user_id: Идентификатор пользователя.
        movie_id: Идентификатор фильма.

    Returns:
        str: JSON с сообщением об успешном удалении фильма.
    """
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({ERROR: ERROR_USER}), NOT_FOUND
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({ERROR: ERROR_MOVIE}), NOT_FOUND

    if movie in user.watchlist:
        user.watchlist.remove(movie)
        db.session.commit()
        return jsonify({MESSAGE: "Фильм удален из списка 'хочу посмотреть'"})
    return jsonify({ERROR: 'Фильма нет в списке'}), NOT_FOUND


@app.route('/users/<int:user_id>/watched/<int:movie_id>', methods=['DELETE'])
def remove_from_watched(user_id, movie_id) -> str:
    """Удаляет фильм из списка 'уже посмотрел' для определенного пользователя.

    Args:
        user_id: Идентификатор пользователя.
        movie_id: Идентификатор фильма.

    Returns:
        str: JSON с сообщением об успешном удалении фильма.
    """
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({ERROR: ERROR_USER}), NOT_FOUND
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({ERROR: ERROR_MOVIE}), NOT_FOUND

    if movie in user.watched:
        user.watched.remove(movie)
        db.session.commit()
        return jsonify({MESSAGE: "Фильм удален из списка 'уже посмотрел'"})
    return jsonify({ERROR: 'Фильма нет в списке'}), NOT_FOUND


@app.route('/users', methods=['POST'])
def create_user() -> str:
    """Создает нового пользователя.

    Returns:
        str: JSON с данными о новом пользователе.
    """
    data_info = request.get_json()
    user = User(
        username=data_info.get('username'),
        email=data_info.get('email'),
        password=data_info.get('password'),
    )
    db.session.add(user)
    db.session.commit()
    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))


@app.route('/users/<int:user_id>', methods=[GET_REQUEST])
def get_user(user_id) -> str:
    """Получает информацию о конкретном пользователе.

    Args:
        user_id: Идентификатор пользователя.

    Returns:
        str: JSON с данными о пользователе.
    """
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({ERROR: ERROR_USER}), NOT_FOUND

    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id) -> str:
    """Обновляет информацию о конкретном пользователе.

    Args:
        user_id: Идентификатор пользователя.

    Returns:
        str: JSON с обновленными данными пользователя.
    """
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({ERROR: ERROR_USER}), NOT_FOUND

    data_info = request.get_json()
    user.username = data_info.get('username', user.username)
    user.email = data_info.get('email', user.email)
    user.password = data_info.get('password', user.password)
    db.session.commit()

    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))


with app.app_context():
    db.create_all()

with app.app_context():
    if not Movie.query.all():
        movies = [
            get_movie_info(ID_FILM1),
            get_movie_info(ID_FILM2),
            get_movie_info(ID_FILM3),
            get_movie_info(ID_FILM4),
            get_movie_info(ID_FILM5),
            get_movie_info(ID_FILM6),
            get_movie_info(ID_FILM7),
            get_movie_info(ID_FILM8),
            get_movie_info(ID_FILM9),
            get_movie_info(ID_FILM10),
            get_movie_info(ID_FILM11),
        ]
        db.session.bulk_insert_mappings(Movie, movies)
        db.session.commit()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    FLASK_PORT = os.getenv('FLASK_PORT', default=DEFAULT_PORT)
    app.run(port=FLASK_PORT)
