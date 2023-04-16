from flask import Blueprint, url_for, render_template, redirect
from flask_login import current_user, login_required
from misc.models import User, Post
from main import db_posts


# blueprint creation 
users_bp = Blueprint("users", __name__)


@login_required
@users_bp.route("/user")
@users_bp.route("/user/<username>")
def user(username=None):

    visitor = current_user

    # return visitor back to homepage if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for("home.home", error_message="You must log in to visit user profiles"))

    # if reloaded successfully, user's username will not be None
    elif username is not None:

        # give admin rights if profile visitor visits own profile
        admin_rights = True if visitor.username == username else False

        # retrieve user data to display
        user_data = User.find_by_username(username)
        # date data formatting
        user_data = User.format_date_data(user_data)

        # retrieve user posts to display
        user_posts = list(db_posts.find({"username": username}))[::-1]
        user_posts = list(map(Post.format_date_data, user_posts))

        return render_template("profile.html", stories=user_posts, admin_rights=admin_rights, **user_data)
    
    # user will reload the page if authenticated, with its username as part of URL
    username = current_user.username
    return redirect(url_for("users.user", username=username))


@login_required
@users_bp.route("/settings")
@users_bp.route("/settings/<username>")
def settings(username=None):

    # return visitor back to homepage if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for("home.home", error_message="You must log in to access settings"))

    # if reloaded successfully, user's username will not be None
    elif username is not None:
        

        return render_template("settings.html")
    
    # user will reload the page if authenticated, with its username as part of URL
    username = current_user.username
    return redirect(url_for("users.settings", username=username))