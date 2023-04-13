from flask import Blueprint, render_template, url_for, redirect, session, request
from flask_login import login_required, current_user
from misc.api import test_stories
from main import db_posts, db_users
import random


#blueprint creation 
home_bp = Blueprint("home", __name__)

POSTS_PER_PAGE = 5

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
    
    message = request.args.get('message')
    error_message = None

    more_posts = False
    stories = None
    if feed == "templates":
        current_posts = session.get('current_posts', POSTS_PER_PAGE)
        current_pages = current_posts // 5
        n_pages = len(test_stories) // 5
        stories = test_stories[:current_posts]
        more_posts = True if current_pages < n_pages else False

    
    elif feed == "recent":
        session["current_posts"] = POSTS_PER_PAGE
        user_posts = list(db_posts.find({"username": "pollancre"}))
        stories = user_posts[::-1] #order from newest to oldest
    

    # returns logged in homepage
    if current_user.is_authenticated:
        print("\nUser: " + current_user.username + "\n")
        return render_template("home.html", user=current_user.username, error_message=error_message,
                                            user_logged=current_user.is_authenticated, message=message,
                                            stories=stories, feed=feed, more_posts=more_posts)
                                           
    
    # not logged in, returns logged out homepage
    return render_template("home.html", user=None, error_message=error_message,
                                        user_logged=current_user.is_authenticated, 
                                        stories=stories, feed=feed, message=message)
                                        

@home_bp.route('/load-more-templates')
def load_more_templates():

    current_posts = session.get('current_posts', POSTS_PER_PAGE)
    current_posts += POSTS_PER_PAGE
    session['current_posts'] = current_posts

    return redirect(url_for('home.home'))                   


@login_required
@home_bp.route("/about")
def about():
    return render_template("about.html", user_logged=current_user.is_authenticated)
    

@home_bp.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404