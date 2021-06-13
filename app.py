import os
from datetime import date

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)

from src import bing, db

BING_URL = "https://www.bing.com"
BING_DAILY_IMAGE = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-de"

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=os.urandom(16))

@app.route("/")
def index():
    return render_template("index.html", username=session.get("user"))


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        score = int(request.form['score'])

        error = None

        if not username:
            error = 'Username is required.'
        elif db.user_exists(username):
            error = f"User {username} is already registered."

        if error is None:
            db.add_user(username, score)
            return redirect(url_for('index'))
        else:
            flash(error)

    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        error = None

        if not db.user_exists(username):
            error = 'Incorrect username.'

        if error is None:
            session.clear()
            session['user'] = username
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')


@app.route("/challenge", methods=('GET', 'POST'))
def challenge():
    if session.get("user") is None:
        flash("You are not logged in as a user. Please login first!") 
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        country = request.form["country"]
        error = None
    
        if not country:
            error ="Country is required."
            
        if error is None:
            db.add_guess(session["user"], country)
        else:
            flash(error)
        
    return render_template("challenge.html", image_url=bing.get_image_url(), image_date=bing.get_image_startdate(), image_author=bing.get_image_author())
