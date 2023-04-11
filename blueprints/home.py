from flask import render_template, url_for, redirect
from flask_login import login_required, current_user
from blueprints import app
from blueprints.api import test_stories
import random

@app.route("/")
def index():
    return redirect(url_for("home"))


@login_required
@app.route("/home")
@app.route("/home/<feed>")
def home(feed="recommended"):

    stories = None

    if feed == "templates":
        random.shuffle(test_stories)
        stories = test_stories[:5]
    
    elif feed == "recommended":
        pass
    else:
        pass


    if current_user.is_authenticated:
        return render_template("home.html", user=current_user.username, user_logged=current_user.is_authenticated, stories=stories, feed=feed)

    return render_template("home.html", user=None, user_logged=current_user.is_authenticated, stories=stories, feed=feed)


@login_required
@app.route("/about")
def about():
    return render_template("about.html", user_logged=current_user.is_authenticated)
    

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404