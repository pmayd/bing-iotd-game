import json
from functools import wraps
from pathlib import Path

from . import bing

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
def get_usernames(db = None) -> list[str]:
    """ Return a list of all registered user names. """
    return list(db["user"].keys())


@provide_db
def user_exists(username: str, db = None) -> bool:
    """ Check if user already exists. """
    return username in db["user"]


@provide_db
def get_user(username: str, db = None) -> dict:
    """ Get user data from database. """
    return db["user"].get(username, {})


@update_db
@provide_db
def add_user(username: str, score: int, db = None):
    """ Add new user to database. """
    db["user"][username] = {}
    db["user"][username]["score"] = score

    return db


@update_db
@provide_db
def add_score(username: str, score: int, db = None):
    """ Add score to user score. """
    db["user"][username]["score"] += score

    return db


@update_db
@provide_db
def add_guess(username: str, country: str, db = None):
    """ Add user's first guess to today's challenge. """
    image_date = bing.get_image_date()
    db["challenge"].setdefault(image_date, {})
    db["challenge"][image_date].setdefault(username, country)
    # TODO add distance for country so we do not have to calcualte it each time
        
    return db


@provide_db
def get_challenge(image_date: str = bing.get_image_date(), db = None) -> dict:
    """ Get the challenge for the given date. """
    return db["challenge"].get(image_date, {})