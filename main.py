from flask import Flask, render_template, url_for, redirect, current_app
from flask_login import LoginManager, login_required, current_user
import os, time, requests, random
from blueprints.auth import login_manager
from blueprints.config import SECRET_KEY, API_ENDPOINT, METHOD, DEBUG_MODE, PORT_LOCAL, PORT_PUBLIC, LOCAL_IP, PUBLIC_IP



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
    print(current_user.username)
    return redirect(url_for("home"))


@login_required
@app.route("/home")
def home():
        
    random.shuffle(test_stories)
    stories = test_stories[:5]

    if current_user.is_authenticated:

        return render_template("home.html", user=current_user.username, user_logged=current_user.is_authenticated, stories=stories)

    return render_template("home.html", user=None, user_logged=current_user.is_authenticated, stories=stories)


@login_required
@app.route("/about")
def about():

    return render_template("about.html", user_logged=current_user.is_authenticated)
    

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404


##### RUN APP #####
if __name__ == "__main__":
    if METHOD == 'device':
        app.run(port=PORT_LOCAL, debug=DEBUG_MODE)
    elif METHOD == 'local':
        app.run(host=LOCAL_IP, port=PORT_LOCAL, debug=DEBUG_MODE)
    elif METHOD == 'public':
        app.run(host=PUBLIC_IP, port=PORT_PUBLIC, debug=DEBUG_MODE)