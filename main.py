from flask import Flask, render_template, url_for, redirect
from flask_login import login_required, current_user
from blueprints.config import SECRET_KEY, MONGODB_URI
from flask_pymongo import PyMongo
from blueprints.api import test_stories
import random


# create app object and assign secret key
app = Flask(__name__)
app.secret_key = SECRET_KEY

# pymongo config
app.config["MONGO_URI"] = MONGODB_URI
mongo = PyMongo(app)
# create collection instances
db_users = mongo.db.users
db_posts = mongo.db.posts


def register_blueprints(app):
    from blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    from blueprints.posts import posts_bp
    app.register_blueprint(posts_bp)


# register blueprints from respective directory
register_blueprints(app)

# import instances from just initialized blueprints (importing after registering blueprints to avoid errors)
from blueprints.auth import login_manager

# initialize login manager
login_manager.init_app(app)



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