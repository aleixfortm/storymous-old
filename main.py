from flask import Flask, render_template, url_for, redirect, current_app
from flask_login import LoginManager
import os, time, requests, random
from blueprints.auth import login_manager
from blueprints.config import SECRET_KEY, API_ENDPOINT


def register_blueprints(app):
    from blueprints.auth import auth_bp, db
    app.register_blueprint(auth_bp)


# create app object and assign secret key
app = Flask(__name__)
app.secret_key = SECRET_KEY

# register blueprints from respective directory
register_blueprints(app)

# initialize login manager
login_manager.init_app(app)


##### API STORY RETRIEVING #####
stories_api = requests.get(API_ENDPOINT)
if stories_api.status_code == 200:
    test_stories = stories_api.json()
else:
    print("Error: API request failed with status code", stories_api.status_code)


##### ROUTING #####
@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():

    random.shuffle(test_stories)
    print(test_stories)
    return render_template("home.html", stories=test_stories, user_logged=True)


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404


##### RUN #####
if __name__ == "__main__":
    if method == 'device':
        app.run(port=3000)
    elif method == 'local':
        app.run(host="192.168.1.44", port=3000)
    elif method == 'public':
        app.run(host="0.0.0.0", port=8080)