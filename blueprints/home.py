from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from misc.api import test_stories
from main import db_posts, db_users
import random


#blueprint creation 
home_bp = Blueprint("home", __name__)


tags = ["poll", "drama", "mysterious", "space", "jungle", 
    "horror", "night", "cursed", "secret", "treasure", 
    "haunted", "island", "mummy", "mansion", "ghost", "monster"]


@home_bp.route("/")
def index():
    return redirect(url_for("home.home"))


@login_required
@home_bp.route("/home")
@home_bp.route("/home/<feed>")
def home(feed="templates"):
    

    stories = None
    if feed == "templates":
        random.shuffle(test_stories)
        stories = test_stories[:5]
    
    elif feed == "recent":
        user_posts = list(db_posts.find({"username": "pollancre"}))
        stories = user_posts[::-1] #order from newest to oldest
    

    # returns logged in homepage
    if current_user.is_authenticated:
        print("\nUser: " + current_user.username + "\n")
        return render_template("home.html", user=current_user.username, 
                                            user_logged=current_user.is_authenticated, 
                                            stories=stories, feed=feed)
                                           
    
    # not logged in, returns logged out homepage
    return render_template("home.html", user=None, 
                                        user_logged=current_user.is_authenticated, 
                                        stories=stories, feed=feed)
                                        
                                        


@login_required
@home_bp.route("/about")
def about():
    return render_template("about.html", user_logged=current_user.is_authenticated)
    

@home_bp.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404