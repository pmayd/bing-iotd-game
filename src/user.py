from flask import g

from . import db


def load_user(username: str):
    """ Load user from database and make it available thorugh Flask g object. """
    if username:
        user = db.get_user(username)
        g.username = username
        g.user = user
