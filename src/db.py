import json
from functools import wraps
from pathlib import Path

DB_PATH = "db.json"


def get_db() -> dict:
    """ Load database. """
    if not Path(DB_PATH).exists():
        create_new_db()

    with open(DB_PATH, "r", encoding="utf-8") as fhandle:
        return json.load(fhandle)


def save_db(func):
    """ Store db. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = func(*args, **kwargs)
        
        with open(DB_PATH, "w", encoding="utf-8") as fhandle:
            json.dump(db, fhandle)
    
    return wrapper


@save_db
def create_new_db():
    """ Create a new empty database. """
    db = {"user": {}, "challenge": {}}
    
    return db


def get_usernames() -> list[str]:
    """ Return a list of all registered user names. """
    db = get_db()
    return list(db["user"].keys())


def user_exists(username: str) -> bool:
    """ Check if user already exists. """
    db = get_db()
    return username in db["user"]


def get_user(username: str) -> dict:
    """ Get user data from database. """
    db = get_db()
    return db["user"].get(username, {})


@save_db
def add_user(username: str, score: int):
    """ Add new user to database. """
    db = get_db()
    db["user"][username] = {}
    db["user"][username]["score"] = score
    
    return db

    
@save_db
def add_score(username: str, score: int):
    """ Add score to user score. """
    db = get_db()
    db["user"][username]["score"] += score

    return db

@save_db
def add_guess(image_date: str, username: str, country: str):
    """ Add user's first guess to today's challenge. """
    db = get_db()
    db["challenge"].setdefault(image_date, {})
    db["challenge"][image_date].setdefault(username, country)

    return db
