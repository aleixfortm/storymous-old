from flask import Blueprint, url_for, render_template, redirect
from flask_login import login_required, current_user
from misc.forms import PostForm
from misc.models import Post, User
from flask_pymongo import ObjectId
from main import db_posts, db_users
from misc.pipelines import POST_PIC_PIPELINE
import datetime


# blueprint creation
posts_bp = Blueprint("posts", __name__)


@login_required
@posts_bp.route("/newstory", methods=["POST", "GET"])
def newstory():

    message = None

    if current_user.is_authenticated:
        
        form = PostForm()
        if form.validate_on_submit(): #if form submitted

            user = current_user.username

            # build story object and save it to db
            story_object = Post(username=user, title=form.newstory_title.data,
                                content=form.newstory_content.data, preview=form.newstory_preview.data,
                                post_comment=form.newstory_comment.data, date=datetime.datetime.now().isoformat())
            # quicksave of post to db
            story_object.quicksave_to_db()

            # update user stats (number of written posts) directly to database (no need to retrieve user data)
            db_users.update_one({"username": user}, {"$inc": {"n_writ_posts": 1}})

            message = "Story successfully uploaded!"
            print("\nPost saved successfully\n")
            return redirect(url_for("home.home", message=message))

        #message = "Invalid input"
        return render_template("newstory.html", form=form, message=message)
    
    
    return redirect(url_for("home.home"))


@login_required
@posts_bp.route("/user")
@posts_bp.route("/user/<username>")
def user(username=None):

    visitor = current_user

    # return visitor back to homepage if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for("home.home"))

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
    return redirect(url_for("posts.user", username=username))


@login_required
@posts_bp.route("/post/<post_id>")
def post(post_id):

    if current_user.is_authenticated:
        pass

    if post_id is None:
        message = "Invalid post id"
        return redirect(url_for("home.home", message=message))


    post = db_posts.find_one({"_id": ObjectId(post_id)})
    formatted_post = Post.format_date_data(post)
    owner = db_users.find_one({"username": post["username"]})
    comments = [{"username": "pollancre", "comment": "Let's gooo!!!", "pic_path": "/static/img/default_blue.png", "date": "Apr 25"}]

    # retrieve posts using piepline --> Post data + profile picture from its owner
    #stories = list(db_posts.aggregate(POST_PIC_PIPELINE))
    # map the posts to format the creation date
    #stories = list(map(Post.format_date_data, stories))

    return render_template("post.html", story=formatted_post, owner=owner, comments=comments)
    
