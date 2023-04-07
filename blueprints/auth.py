from flask import Blueprint, url_for, render_template, flash, redirect
from flask_login import UserMixin, current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, email_validator, ValidationError
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from blueprints.config import MONGODB_URI, POLL


print(POLL + " this is auth")
# mongodb database setup
client = MongoClient(MONGODB_URI)
database = client.storymous
db = database.main #collection

# blueprint creation 
auth_bp = Blueprint("auth", __name__)

def register_blueprints(app):
    from blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)


class User(UserMixin):
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def find_by_email(email):
        return db.find_one({'email': email})

    @staticmethod
    def find_by_username(username):
        return db.find_one({'username': username})

    def save_to_db(self):
        db.insert_one({
            'email': self.email,
            'username': self.username,
            'password_hash': self.password_hash
        })


##### FORMS #####
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register!')

    def check_email(self, field):
        # Check if not None for that user email!
        if db.find_one({'email': field.data}):
            raise ValidationError('Your email has been registered already!')

    def check_username(self, field):
        # Check if not None for that username!
        if db.find_one({'username': field.data}):
            raise ValidationError('Sorry, that username is taken!')

    def save_user(self):
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


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    
    if form.validate_on_submit():
        print("validated")
        # Find the user in the database
        user = User.find_by_email(form.email.data)
        # Check if the user exists by that email and the password is correct
        if user and user.check_password(form.password.data):
            print("found")
            login_user(user)
            return redirect(url_for("home"))
        print("Rejected")
        flash("Invalid email or password")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        user.save_to_db()
        flash("Thanks for registering")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)