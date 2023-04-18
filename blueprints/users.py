from flask import Blueprint, url_for, render_template, redirect, request
from flask_login import current_user, login_required
from misc.models import User, Post, Settings
from misc.forms import ColorChoiceForm
from main import db_posts, db_settings


# blueprint creation 
users_bp = Blueprint("users", __name__)


@login_required
@users_bp.route("/user")
@users_bp.route("/user/<username>")
def user(username=None):

    visitor = current_user

    follow_status_update = request.args.get("follow_status")
    if follow_status_update == "follow":
        pass
        ### update visitor following list

    elif follow_status_update == "unfollow":
        pass
        ### update visitor following list
        ### update username

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
@users_bp.route("/settings/<username>", methods=["GET", "POST"])
def settings(username=None):

    # return visitor back to homepage if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for("home.home", error_message="You must log in to access settings"))

    # if reloaded successfully, user's username will not be None
    elif username is not None:

        # return current user settings
        current_settings = Settings.check_user_settings(username)
        if not current_settings:
            settings_object = Settings(username=username, color="red")
            settings_object.create_or_update_settings_to_db()
            
        # create form object
        form = ColorChoiceForm()
        form.color_dropdown.default = current_settings["color"]

        if request.method == "POST":

            if form.validate_on_submit():

                # create user settings object with form values
                user_settings_object = Settings(username=username, color=form.color_dropdown.data)
                # send data to settings collection with username
                user_settings_object.create_or_update_settings_to_db()
                user_settings_object.update_pic_to_users_db()
                    
                return redirect(url_for("users.user", message="Successfully updated user settings"))
        
        form.process()
        return render_template("settings.html", form=form, **current_settings)


    # user will reload the page if authenticated, with its username as part of URL
    return redirect(url_for("users.settings", username=current_user.username))