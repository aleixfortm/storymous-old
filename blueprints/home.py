from flask import Blueprint, render_template, url_for, redirect, session, request
from flask_login import login_required, current_user
from misc.api import test_stories
from misc.models import User, Post
from misc.pipelines import POST_PIC_PIPELINE, pic_to_following_pipeline
from main import db_posts


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
def home(feed="recent"):
    
    message = request.args.get('message')
    error_message = request.args.get("error_message")

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

        # retrieve posts using piepline --> Post data + profile picture from its owner
        unformatted_stories = list(db_posts.aggregate(POST_PIC_PIPELINE))
        # map the posts to format the creation date
        stories = list(map(Post.format_date_data, unformatted_stories))

    elif feed == "following":
        if current_user.is_authenticated:
            user_stats = User.find_by_username(current_user.username)
            user_following_list = user_stats.get("following")
            unformatted_stories = list(db_posts.aggregate(pic_to_following_pipeline(user_following_list)))
            stories = list(map(Post.format_date_data, unformatted_stories))

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
    feed = "templates"

    return redirect(url_for('home.home', feed="templates"))                   


@login_required
@home_bp.route("/about")
def about():
    return render_template("about.html", user_logged=current_user.is_authenticated)