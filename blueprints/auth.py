from flask import Blueprint, url_for, render_template, flash, redirect
from flask_login import UserMixin, current_user, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, email_validator, ValidationError
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
import re


# blueprint creation 
auth_bp = Blueprint("auth", __name__)

# create login manager instance to keep track of user authentication
login_manager = LoginManager()
login_manager.init_app(auth_bp)


@login_manager.user_loader
def load_user(username):
    # Your code to load user from database
    print("\nCalled user_loader from login_manager\n")
    user = User.check_user(username)
    return user


"""
By inheriting from UserMixin, the User class gains the following functionalities:

is_authenticated: A boolean property indicating whether the user is authenticated or not.
is_active: A boolean property indicating whether the user is active or not.
is_anonymous: A boolean property indicating whether the user is anonymous or not.
get_id(): A method that returns a unique identifier for the user, as a string.

Note: I have added an "id" attribute, since get_id() method looks for such attribute in the object.
However, I am setting the username to be the id of the user, and the username will also be unique across
users in the database.
"""
class User(UserMixin):
    def __init__(self, email, username, password_hash):
        self.id = username
        self.email = email
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # retrieve user data as dict
    @staticmethod
    def find_by_email(email):
        return db.find_one({'email': email})
    
    # retrieve user data as dict
    @staticmethod
    def find_by_username(username):
        return db.find_one({'username': username})

    # return user object from retrieved dict
    @staticmethod
    def check_user(username):
        user_data = db.find_one({'username': username})
        if user_data:
            return User(email=user_data['email'], username=user_data['username'], password_hash=user_data['password_hash'])
        return None


##### FORMS #####
class LoginForm(FlaskForm):
    user = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def check_email(self, field):
        # Check if not None for that user email!
        return db.find_one({'email': field.data})

    def check_username(self, field):
        # Check if not None for that username!
        return db.find_one({'username': field.data})
    
    def is_valid_username(self, field):
        # Check if username meets all requirements: accepted special chars: "_" and len<=20chars
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, field.data))

    def save_user_to_db(self):
        password_hash = generate_password_hash(self.password.data)
        db.insert_one({
            'email': self.email.data,
            'username': self.username.data,
            'password_hash': password_hash
        })


class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed([".png", ".jpg"])])
    submit = SubmitField("Update")

    def check_email(self, field):
        if db.find_one({"email": field.data}):
            raise ValidationError("That email has already been registered")
        
    def check_username(self, field):
        if db.find_one({"username": field.data}):
            raise ValidationError("That username already exists")


@login_required
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    message = None
    if current_user.is_authenticated:
        print("\nAlready logged, sending back home\n")
        return redirect(url_for("home"))

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
            return redirect(url_for("home"))
        
        else:
            message = "Incorrect password"
    
    return render_template("login.html", form=form, message=message)


@login_required
@auth_bp.route("/logout")
def logout():

    if current_user.is_authenticated:

        logout_user() #log user out and clear cookies

    return redirect(url_for("home"))


@login_required
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    
    message = None
    # redirect home if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
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


@login_required
@auth_bp.route("/user")
def user():
    if not current_user.is_authenticated:
        return redirect(url_for("home"))

    return render_template("profile.html")


# import from main file at the end to avoid circular imports
from main import db