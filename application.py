import os

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from src import bing, db

application = Flask(__name__)
application.config.from_mapping(SECRET_KEY=os.urandom(16))


@application.route("/")
def index():
    return render_template("index.html", username=session.get("user"))


@application.route('/register', methods=('GET', 'POST'))
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


@application.route('/login', methods=('GET', 'POST'))
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


@application.route('/logout')
def logout():
    session.clear()
           
    return redirect(url_for('index'))


@application.route("/challenge", methods=('GET', 'POST'))
def challenge():
    if session.get("user") is None:
        flash("You are not logged in as a user. Please login first!")
        return redirect(url_for("login"))

    if request.method == 'POST':
        country = request.form["country"]
        error = None

        if not country:
            error = "Country is required."

        if error is None:
            db.add_guess(session["user"], country)
        else:
            flash(error)

    return render_template("challenge.html",
                           challenge=db.get_challenge(),
                           image_url=bing.get_image_url(),
                           image_date=bing.get_image_date(),
                           image_author=bing.get_image_author())


@application.route("/score", methods=('GET', 'POST'))
def score():
    if session.get("user") is None:
        flash("You are not logged in as a user. Please login first!")
        return redirect(url_for("login"))

    if request.method == 'POST':
        db.score_guesses()
        db.update_player_score()       
        

    return render_template("score.html", challenge=db.get_challenge())


@application.route("/highscore")
def highscore():
    user = db.get_user()
    user = dict(sorted(user.items(), key=lambda x: x[1]["score"], reverse=True))
    return render_template("highscore.html", player=user)


# needed when running the flask app via python app.py and not via flask run
if __name__ == "__main__":
    application.debug = True
    application.run()