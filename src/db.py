import json
from functools import wraps
from pathlib import Path

DB_PATH = "db.json"


def get_db() -> dict:
    if not Path(DB_PATH).exists():
        create_new_db()

    with open(DB_PATH, "r", encoding="utf-8") as fhandle:
        return json.load(fhandle)


def provide_db(func):
    """ Load database. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = get_db()

        return func(*args, db=db, **kwargs)
        
    return wrapper


def update_db(func):
    """ Store db. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = func(*args, **kwargs)
        
        with open(DB_PATH, "w", encoding="utf-8") as fhandle:
            json.dump(db, fhandle)
    
    return wrapper


@update_db
def create_new_db():
    """ Create a new empty database. """
    db = {"user": {}, "challenge": {}}
    
    return db


@provide_db
def get_usernames(db) -> list[str]:
    """ Return a list of all registered user names. """
    return list(db["user"].keys())


@provide_db
def user_exists(username: str, db) -> bool:
    """ Check if user already exists. """
    return username in db["user"]


@provide_db
def get_user(username: str, db) -> dict:
    """ Get user data from database. """
    return db["user"].get(username, {})


@update_db
@provide_db
def add_user(username: str, score: int, db):
    """ Add new user to database. """
    db["user"][username] = {}
    db["user"][username]["score"] = score

    return db


@update_db
@provide_db
def add_score(username: str, score: int, db):
    """ Add score to user score. """
    db["user"][username]["score"] += score

    return db


@update_db
@provide_db
def add_guess(image_date: str, username: str, country: str, db):
    """ Add user's first guess to today's challenge. """
    db["challenge"].setdefault(image_date, {})
    db["challenge"][image_date].setdefault(username, country)

    return db
