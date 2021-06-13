from pathlib import Path
import json

DB_PATH = "db.json"


def get_db() -> dict:
    """ Load database. """
    if not Path(DB_PATH).exists():
        create_new_db()

    with open(DB_PATH, "r", encoding="utf-8") as fhandle:
        return json.load(fhandle)


def create_new_db():
    """ Create a new empty database. """
    db = {"user": {}, "challenge": {}}
    save_db(db)
        

def save_db(db: dict):
    """ Store db. """
    with open(DB_PATH, "w", encoding="utf-8") as fhandle:
        json.dump(db, fhandle)


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
    return get_db()["user"].get(username, {})


def add_user(username: str, score: int):
    """ Add new user to database. """
    db = get_db()
    db["user"][username] = {}
    db["user"][username]["score"] = score
    
    save_db(db)
    

def add_score(username: str, score: int):
    """ Add score to user score. """
    db = get_db()
    db["user"][username]["score"] += score
    
    save_db(db)


def add_guess(image_date: str, username: str, country: str):
    """ Add user's first guess to today's challenge. """
    db = get_db()
    
    db["challenge"].setdefault(image_date, {})
    db["challenge"][image_date].setdefault(username, country)
    
    save_db(db)
