from flask import Blueprint, url_for, render_template, redirect, request
from flask_login import current_user, login_user, LoginManager, login_required, logout_user, login_manager
from misc.models import User
from misc.forms import LoginForm, RegistrationForm


# blueprint creation 
auth_bp = Blueprint("auth", __name__)

"""
pass dict as kwargs without including ObjectId --> 
**{k: v for k, v in my_dict.items() if k != '_id'}
"""

@login_required
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    message = request.args.get('message')
    error_message = request.args.get("error_message")

    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    
    form = LoginForm()
    
    if form.validate_on_submit():

        user_data = User.find_by_email(form.user.data)
        if not user_data: # not found by email
            user_data = User.find_by_username(form.user.data)

            if not user_data: # not found by username either
                error_message = "Incorrect e-mail or username"
                return render_template("login.html", form=form, error_message=error_message)
        
        user_object = User(_id=user_data["_id"], 
                           email=user_data["email"], 
                           username=user_data["username"], 
                           password_hash=user_data["password_hash"])

        if user_object.check_password(form.password.data):

            if not user_object.is_new_format():
                user_object.replace_user()
                print("\nOutdated user account, updating...\nSuccess!\n")

            login_user(user_object)
            return redirect(url_for("home.home"))
        
        else:
            error_message = "Incorrect password for that user"

    return render_template("login.html", form=form, message=message, error_message=error_message)


@login_required
@auth_bp.route("/logout")
def logout():

    if current_user.is_authenticated:

        logout_user() #log user out and clear cookies

    return redirect(url_for("home.home"))


@login_required
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    
    error_message = ""

    # redirect home if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    
    
    form = RegistrationForm()
    if request.method == "POST":

        if form.validate_on_submit():

            found_email = form.check_email(form.email)
            found_username = form.check_username(form.username)

            if found_email is not None: # email exists in database?
                error_message = "E-mail already taken"

            elif found_username is not None: # username exists in database?
                error_message = "Username already taken"

            elif not form.is_valid_username_chars(form.username):
                error_message = "Invalid username, allowed (a-z, A-Z, _)"

            elif not form.is_valid_username_len(form.username):
                error_message = "Username length must be between 2 and 20 characters"

            else: # proceeds if user or email do not exist
                password_hash = form.hash_password()
                user_object = User(username=form.username.data, email=form.email.data, password_hash=password_hash)
                user_object.quicksave_to_db()

                message = "Registered successfully! Log in to continue"
                return redirect(url_for("auth.login", message=message))
        
        else:
            error_message = "Incorrect e-mail format"
            
    return render_template("register.html", form=form, error_message=error_message)