from flask import Blueprint, url_for, render_template, redirect, request
from flask_login import current_user, login_required
from misc.models import User, Post, Settings
from misc.forms import ColorChoiceForm
from main import db_posts, db_settings


# blueprint creation 
users_bp = Blueprint("users", __name__)


@login_required
@users_bp.route("/user")
@users_bp.route("/user/<username>", methods=["POST", "GET"])
def user(username=None):

    # visitor is the object of the visiting user
    visitor = current_user

    user_following = None
    # if visitor clicks follow/unfollow button
    if request.method == "POST":
        # checks if visitor sent request to follow or unfollow the owner user
        follow_status_update = request.form.get("follow_status")
        follow_message = request.form.get("follow_message")
        # update following status of both users (followed)
        if follow_status_update == "follow":
            User.add_follower(user_being_followed=username, user_follows=visitor.username)

        # update following status of both users (unfollowed)
        elif follow_status_update == "unfollow":
            User.remove_follower(user_being_unfollowed=username, user_stops_following=visitor.username)

        return redirect(url_for("users.user", username=username, follow_message=follow_message))


    # if visitor is not the owner
    if visitor.username != username:
        # check if visitor follows the user and act accordingly
        visitor_data = User.find_by_username(visitor.username)
        following_array = visitor_data.get("following", [])
        if username in following_array:
            user_following = True
        else:
            user_following = False
            

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

        #retrieve message, if any, most likely sent as a change of following status or from successfully saved settings
        follow_message = request.args.get("follow_message")
        settings_message = request.args.get("settings_message")

        return render_template("profile.html", stories=user_posts, admin_rights=admin_rights, **user_data, 
                               user_following=user_following, follow_message=follow_message, settings_message=settings_message)
    
    # user will reload the page if authenticated, with its username as part of the URL
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
                # create settings message to inform about successful changes
                settings_message = "Successfully updated user settings"

                # redirect back to user page with success message
                return redirect(url_for("users.user", username=username , settings_message=settings_message))

        # process form if loading settings html page
        form.process()

        return render_template("settings.html", form=form, **current_settings)


    # user will reload the page if authenticated, with its username as part of URL
    return redirect(url_for("users.settings", username=current_user.username))