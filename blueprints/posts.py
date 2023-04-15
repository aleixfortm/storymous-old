from flask import Blueprint, url_for, render_template, redirect
from flask_login import login_required, current_user
from misc.forms import PostForm, CommentForm
from misc.models import Post, User, Comment
from flask_pymongo import ObjectId
from main import db_posts, db_users, db_comments
from misc.pipelines import COMMENT_PIC_PIPELINE
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
@posts_bp.route("/post/<post_id>", methods=["POST", "GET"])
def post(post_id):

    if current_user.is_authenticated:
        pass
    
    if post_id is None:
        message = "Invalid post id"
        return redirect(url_for("home.home", message=message))

    # retrieve data from db
    post_data = db_posts.find_one({"_id": ObjectId(post_id)})
    formatted_post = Post.format_date_data(post_data)
    owner_data = db_users.find_one({"username": post_data["username"]})

    post_comments_id = post_data["user_comments"] 
    post_comments = Comment.find_docs_in_db(post_comments_id)

    # increase view count +1 (consider saving flag data to session to avoid spam-reload increment)
    db_posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"visits": 1}})



    # map the posts to format the creation date
    comments = list(map(Post.format_date_data, comments))


    form = CommentForm()
    if form.validate_on_submit():
        
        user = current_user.username

        # build story object and save it to db
        comment_object = Comment(username=user, content=form.comment_content.data, 
                                 date=datetime.datetime.now().isoformat())
        # quicksave of post to db
        comment_object.quicksave_to_db()

        # increase comment count +1 in post document
        db_posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"n_comments": 1}})
        # add comment _id to section "user_comments" at the Post's document
        Post.add_comment_id(post_id=post_id, comment_id=comment_object._id)
        # update user stats (number of written posts) directly to database (no need to retrieve user data)
        User.increase_written_posts_by_one(user)

        """
        redirect user to force GET request (Post, Redirect, Get pattern)
        --> User refreshing page might resend post request again. This is avoided by redirecting
            user to the same URL to force GET Request, and if the page is reloaded, it will just 
            send a GET Request instead of a POST if the redirect were not to happen.
        """

        return redirect(url_for("posts.post", post_id=post_id))

    # retrieve posts using piepline --> Post data + profile picture from its owner
    #stories = list(db_posts.aggregate(POST_PIC_PIPELINE))
    # map the posts to format the creation date
    #stories = list(map(Post.format_date_data, stories))

    return render_template("post.html", form=form, story=formatted_post, owner=owner_data, comments=post_comments)
    
