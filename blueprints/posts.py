from flask import Blueprint, url_for, render_template, redirect
from flask_login import login_required, current_user
from misc.forms import PostForm
from misc.models import Post


# blueprint creation
posts_bp = Blueprint("posts", __name__)


@login_required
@posts_bp.route("/newstory", methods=["POST", "GET"])
def newstory():

    if current_user.is_authenticated:
        
        form = PostForm()

        if form.validate_on_submit(): #if form submitted
            pass

        return render_template("newstory.html")
    
    
    return redirect(url_for("home.home"))
