from flask import Flask, render_template, url_for, redirect, current_app
from flask_login import LoginManager, login_required, current_user
import os, time, requests, random
from blueprints.auth import login_manager
from blueprints.config import SECRET_KEY, API_ENDPOINT, METHOD, DEBUG_MODE



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


@login_required
@app.route("/home")
def home():
        
    random.shuffle(test_stories)
    stories = test_stories[:5]

    return render_template("home.html", stories=stories, user_logged=current_user.is_authenticated)


@login_required
@app.route("/about")
def about():

    if current_user.is_authenticated:
        return render_template("about.html")
    
    return redirect(url_for("home"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404


##### RUN #####
if __name__ == "__main__":
    if METHOD == 'device':
        app.run(port=3000, debug=DEBUG_MODE)
    elif METHOD == 'local':
        app.run(host="192.168.1.44", port=3000, debug=DEBUG_MODE)
    elif METHOD == 'public':
        app.run(host="0.0.0.0", port=8080, debug=DEBUG_MODE)