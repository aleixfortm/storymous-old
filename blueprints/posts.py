from flask import Blueprint, url_for, render_template, redirect
from flask_login import login_required, current_user
from misc.forms import PostForm
from misc.models import Post
from main import db_posts

# blueprint creation
posts_bp = Blueprint("posts", __name__)


@login_required
@posts_bp.route("/newstory", methods=["POST", "GET"])
def newstory():

    message = None

    if current_user.is_authenticated:
        
        form = PostForm()
        if form.validate_on_submit(): #if form submitted

            story_object = Post(username=current_user.username,
                                title=form.newstory_title.data,
                                content=form.newstory_content.data
                                )

            story_object.save_post_to_db()
            print("\nPost saved successfully\n")
            return redirect(url_for("home.home"))

        #message = "Invalid input"
        return render_template("newstory.html", form=form, message=message)
    
    
    return redirect(url_for("home.home"))


@login_required
@posts_bp.route("/user")
@posts_bp.route("/user/<username>")
def user(username=None):

    # return user back to homepage if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for("home.home"))

    # if reloaded successfully, user's username will not be None
    elif username is not None:

        user_posts = db_posts.find({"username": username})
        print(user_posts[0]["title"])

        return render_template("profile.html", username=current_user.username, stories=user_posts)
    
    # user will reload the page if authenticated, with its username as part of URL
    username = current_user.username
    return redirect(url_for("posts.user", username=username))


    
