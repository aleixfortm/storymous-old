from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField
from werkzeug.security import generate_password_hash
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
import re


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
        return db_users.find_one({'email': field.data})

    def check_username(self, field):
        # Check if not None for that username!
        return db_users.find_one({'username': field.data})
    
    def is_valid_username(self, field):
        # Check if username meets all requirements: accepted special chars: "_" and len<=20chars
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, field.data))

    def save_user_to_db(self):
        password_hash = generate_password_hash(self.password.data)
        db_users.insert_one({
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
        if db_users.find_one({"email": field.data}):
            raise ValidationError("That email has already been registered")
        
    def check_username(self, field):
        if db_users.find_one({"username": field.data}):
            raise ValidationError("That username already exists")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")


from main import db_users