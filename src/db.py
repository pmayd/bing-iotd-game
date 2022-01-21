from datetime import datetime
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
def get_usernames(db=None) -> list[str]:
    """ Return a list of all registered user names. """
    return list(db["user"].keys())


@provide_db
def user_exists(username: str, db=None) -> bool:
    """ Check if user already exists. """
    return username in db["user"]


@provide_db
def get_user(username: str=None, db=None) -> dict:
    """ Get user data from database. """
    if username:
        return db["user"].get(username, {})
    else:
        return db["user"]


@update_db
@provide_db
def add_user(username: str, score: int, db=None):
    """ Add new user to database. """
    db["user"][username] = {}
    db["user"][username]["score"] = score

    return db


@update_db
@provide_db
def update_player_score(db=None):
    """ Update all player scores with today's challenge score. """
    image_date = datetime.today().strftime("%Y-%m-%d")
    if db["challenge"][image_date].get("status", "") == "finished":   
        player = db["challenge"][image_date]["player"]
        
        for username, stats in player.items():
            db["user"][username]["score"] += stats["score"]
            
    return db


@update_db
@provide_db
def add_guess(username: str, user_country: str, db=None):
    """ Add user's first guess to today's challenge. """
    image_date = datetime.today().strftime("%Y-%m-%d")
    image_metadata = bing.get_random_streetview_pic()

    db["challenge"].setdefault(image_date, {})
    db["challenge"][image_date].setdefault("location", bing.get_image_location_name())
    db["challenge"][image_date].setdefault("status", "open")
    db["challenge"][image_date].setdefault("player", {})
    db["challenge"][image_date]["player"].setdefault(
        username, {
            "guess": user_country,
            "distance": bing.score_guess(user_country)
        })

    return db

@provide_db
@update_db
def score_guesses(db=None):
    """ Score all player's guesses
    
    First, all players are ranked by their guess distance
    Second, the best three playes get scores 3,2,1
    Third, challenge's status is set to 'finished
    """
    image_date = datetime.today().strftime("%Y-%m-%d")
    players_and_scores = sorted(db["challenge"][image_date]["player"].items(), key=lambda x: x[1]["distance"])
    
    score = 3
    old_guess = players_and_scores[0][1]["guess"]
    for username, entry in players_and_scores:        
        # in case two players have the same guess -> keep score
        if entry["guess"] != old_guess:
            old_guess = entry["guess"]
            score = max(score - 1, 0)
        
        db["challenge"][image_date]["player"][username].setdefault("score", score)
    
    db["challenge"][image_date]["status"] = "finished"
    
    return db
        
    
@provide_db
def get_challenge(image_date: str = datetime.today().strftime("%Y-%m-%d"), db=None) -> dict:
    """ Get the challenge for the given date. """
    return db["challenge"].get(image_date, {})
