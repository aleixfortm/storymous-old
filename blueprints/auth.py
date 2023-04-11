from flask import Blueprint, url_for, render_template, redirect
from flask_login import current_user, login_user, LoginManager, login_required, logout_user, login_manager
from misc.models import User
from misc.forms import LoginForm, RegistrationForm


# blueprint creation 
auth_bp = Blueprint("auth", __name__)


@login_required
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    message = None
    if current_user.is_authenticated:
        print("\nAlready logged, sending back home\n")
        return redirect(url_for("home.home"))
    
    form = LoginForm()
    
    if form.validate_on_submit():

        user_data = User.find_by_email(form.user.data)
        if not user_data: # not found by email
            user_data = User.find_by_username(form.user.data)

            if not user_data:
                message = "Incorrect e-mail or username"
                return render_template("login.html", form=form, message=message)
        
        user_object = User(email=user_data["email"], 
                           username=user_data["username"], 
                           password_hash=user_data["password_hash"])

        if user_object.check_password(form.password.data):

            login_user(user_object)
            print("\nLogged in successfully\n")
            return redirect(url_for("home.home"))
        
        else:
            message = "Incorrect password"
    
    return render_template("login.html", form=form, message=message)


@login_required
@auth_bp.route("/logout")
def logout():

    if current_user.is_authenticated:

        logout_user() #log user out and clear cookies

    return redirect(url_for("home.home"))


@login_required
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    
    message = None
    # redirect home if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    
    form = RegistrationForm()

    if form.validate_on_submit():

        found_email = form.check_email(form.email)
        found_username = form.check_username(form.username)

        if found_email is not None: # email exists in database?
            message = "E-mail already taken"

        elif found_username is not None: # username exists in database?
            message = "Username already taken"

        elif not form.is_valid_username(form.username):
            message = "Invalid username, allowed (a-z, A-Z, _)"

        else: # proceeds if user or email do not exist
            form.save_user_to_db()

            print("\nRegistered successfully!\n")
            message = "Thanks for registering!"
            return redirect(url_for("auth.login"))
        
    return render_template("register.html", form=form, message=message)