from flask import Flask, render_template, url_for, redirect, current_app
from blueprints.auth import register_blueprints
from pymongo import MongoClient
import os, time, requests, random
from blueprints.config import SECRET_KEY, API_ENDPOINT, POLL


print(POLL + " this is main")

# create app object
app = Flask(__name__)
# configure secret key
app.secret_key = SECRET_KEY
# register blueprints from respective directory
register_blueprints(app)


##### API RETRIEVING #####
test_api_endpoint = API_ENDPOINT
test_api_response = requests.get(test_api_endpoint)
# check the response status code to ensure the request was successful
if test_api_response.status_code == 200:
    # if the request was successful, get the response data as a dictionary
    data_dict = test_api_response.json()
else:
    # if the request was unsuccessful, print an error message
    print("Error: API request failed with status code", test_api_response.status_code)


##### ROUTING #####
@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    x = random.randint(0, 2)
    post_dict = data_dict[x]
    return render_template("home.html", title=post_dict["title"], content=post_dict["content"])


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404


##### RUN #####
if __name__ == "__main__":
    app.run(debug=True)