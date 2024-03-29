from flask import Blueprint, url_for, render_template, redirect, session, request
from flask_login import login_required, current_user
from misc.forms import PostForm, CommentForm
from misc.models import Post, User, Comment
from flask_pymongo import ObjectId
from main import db_posts, db_users
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
@posts_bp.route("/post/<post_id>", methods=["POST", "GET"])
def post(post_id):
    
    if post_id is None:
        message = "Invalid post id"
        return redirect(url_for("home.home", message=message))

    # retrieve data from db
    post_data = db_posts.find_one({"_id": ObjectId(post_id)})
    formatted_post = Post.format_date_data(post_data)
    owner_data = db_users.find_one({"username": post_data["username"]})

    post_comments_id = post_data["user_comments"] 
    post_comments = Comment.find_docs_in_db(post_comments_id)

    # add user session tracking based on post to avoid same user spam clicking post to increase stats
    # increment post view count if user has not visited yet in the current session
    if not session.get(post_id, False):
        # increase view count +1
        db_posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"visits": 1}})
        session[post_id] = True

    # insert pic_path of each user to respective comment
    comments = Comment.add_pic_to_comments(post_comments)
    # map the posts to format the creation date
    comments = list(map(Post.format_date_data, comments))

    form = CommentForm()
    if request.method == "POST":
    
        if form.validate_on_submit():
            
            if current_user.is_anonymous:
                return redirect(url_for('auth.login', error_message="You must log in to post stories and comments"))
            
            user = current_user.username

            # build story object and save it to db
            comment_object = Comment(username=user, content=form.comment_content.data, 
                                    date=datetime.datetime.now().isoformat())
            # quicksave post to db
            comment_object.quicksave_to_db()

            # increase comment count +1 in post document
            db_posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"n_comments": 1}})
            # add comment _id to section "user_comments" at the Post's document
            Post.add_comment_id(post_id=post_id, comment_id=comment_object._id)
            # update user stats (number of written posts) directly to database (no need to retrieve user data)
            User.increase_written_comments_by_one(user)

            """
            redirect user to force GET request (Post, Redirect, Get pattern)
            --> User refreshing page might resend post request again. This is avoided by redirecting
                user to the same URL to force GET Request, and if the page is reloaded, it will just 
                send a GET Request instead of a POST if the redirect were not to happen.
            """

            return redirect(url_for("posts.post", post_id=post_id))

        else:
            error_message = "Invalid comment format"
            return redirect(url_for("posts.post", post_id=post_id, error_message=error_message))
    # retrieve posts using piepline --> Post data + profile picture from its owner
    #stories = list(db_posts.aggregate(POST_PIC_PIPELINE))
    # map the posts to format the creation date
    #stories = list(map(Post.format_date_data, stories))

    return render_template("post.html", form=form, story=formatted_post, owner=owner_data, comments=comments, user_logged=current_user.is_authenticated)
    
