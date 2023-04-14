from flask import Blueprint, render_template, url_for, redirect, session, request
from flask_login import login_required, current_user
from misc.api import test_stories
from misc.models import User
from misc.pipelines import POST_PIC_PIPELINE
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

        # stories = list(db_posts.find().sort("date", -1).limit(10))

        # Perform a left outer join with the users collection using $lookup

        stories = list(db_posts.aggregate(POST_PIC_PIPELINE))
        print(stories)

    # returns logged in homepage
    if current_user.is_authenticated:
        user_data = User.find_by_username(current_user.username)

        return render_template("home.html", user=current_user.username, user_data=user_data, error_message=error_message,
                                            user_logged=current_user.is_authenticated, message=message,
                                            stories=stories, feed=feed, more_posts=more_posts)
                                           
    # not logged in, returns logged out homepage
    return render_template("home.html", user=None, error_message=error_message, more_posts=more_posts,
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


pic_pipeline = [
            {
                '$sort': {'date': -1}
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'username',
                    'foreignField': 'username',
                    'as': 'post_data'
                }
            },
            {
                '$unwind': '$user'
            },
            {
                '$addFields': {
                    'pic_path': {'$arrayElemAt': ['$user.picture', 0]}
                }
            },
            {
                '$project': {
                    'user': 0
                }
            }
            ]