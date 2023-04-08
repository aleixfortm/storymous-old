from flask import Flask, render_template, url_for, redirect, current_app
from flask_login import LoginManager
from pymongo import MongoClient
import os, time, requests, random
from blueprints.config import SECRET_KEY, API_ENDPOINT, POLL


def register_blueprints(app):
    from blueprints.auth import auth_bp, db
    app.register_blueprint(auth_bp)


# TODO: Import LoginManager from flask_login to manage user login, logout, save user session, restrict access, etc.
# Import is needed and then check how to import in the other module
print(POLL + " this is main")


# create app object and assign secret key
app = Flask(__name__)
app.secret_key = SECRET_KEY
# register blueprints from respective directory
register_blueprints(app)

"""
# create login manager instance to keep track of user authentication
login_manager = LoginManager()
login_manager.init_app(app)
"""


##### API STORY RETRIEVING #####
test_api_response = requests.get(API_ENDPOINT)
if test_api_response.status_code == 200:
    data_dict = test_api_response.json()
else:
    print("Error: API request failed with status code", test_api_response.status_code)


##### ROUTING #####
@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    x = random.randint(0, 2)
    post_dict = data_dict[x]
    return render_template("home.html", title=post_dict["title"], content=post_dict["content"], user_logged=True)


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404


##### RUN #####
if __name__ == "__main__":
    app.run(debug=True)