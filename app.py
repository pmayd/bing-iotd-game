import os
from datetime import datetime

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from src import bing, db

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=os.urandom(16))


@app.route("/")
def index():
    return render_template("index.html", username=session.get("user"))


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        score = int(request.form["score"])

        error = None

        if not username:
            error = "Username is required."
        elif db.user_exists(username):
            error = f"User {username} is already registered."

        if error is None:
            db.add_user(username, score)
            return redirect(url_for("index"))
        else:
            flash(error)

    return render_template("register.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        error = None

        if not db.user_exists(username):
            error = "Incorrect username."

        if error is None:
            session.clear()
            session["user"] = username
            return redirect(url_for("index"))

        flash(error)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("index"))


@app.route("/challenge", methods=("GET", "POST"))
def challenge():
    if session.get("user") is None:
        flash("You are not logged in as a user. Please login first!")
        return redirect(url_for("login"))

    if request.method == "POST":
        user_input = request.form["country"]
        error = None

        if not user_input:
            error = "Country is required."

        if error is None:
            db.add_guess(session["user"], user_input)
        else:
            flash(error)

    image_metadata = bing.get_random_streetview_pic()
    image_src = bing.get_image_path(image_metadata["pano_id"])

    return render_template(
        "challenge.html",
        challenge=db.get_challenge(),
        image_metadata=image_metadata,
        image_src=image_src,
        image_date=datetime.today().strftime("%Y-%m-%d"),
    )


@app.route("/score", methods=("GET", "POST"))
def score():
    if session.get("user") is None:
        flash("You are not logged in as a user. Please login first!")
        return redirect(url_for("login"))

    if request.method == "POST":
        db.score_guesses()
        db.update_player_score()

    return render_template("score.html", challenge=db.get_challenge())


@app.route("/highscore")
def highscore():
    user = db.get_user()
    user = dict(sorted(user.items(), key=lambda x: x[1]["score"], reverse=True))
    return render_template("highscore.html", player=user)


# needed when running the flask app via python app.py and not via flask run
if __name__ == "__main__":
    app.debug = True
    app.run()
