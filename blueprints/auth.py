from flask import Blueprint, url_for
from flask_login
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, email_validator
from flask_wtf.file import FileField, FileAllowed

# Image conversion
import os
from PIL import Image


# blueprint creation 
auth_bp = Blueprint("users", __name__)


# Image conversion funttion ### WIP
def add_profile_pic(pic_upload, username):

    filename = pic_upload.filename  # e.g. "picture.png"
    ext_type = filename.split(".")[-1]  # "png"
    storage_filename = str(username) + "." + ext_type  # save pic as "username.png"


##### FORMS #####
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

# TODO: CHECK IF EMAIL AND USERNAME ALREADY EXIST (WHEN DATABASE ADDED)
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo("password_confirm", message="Passwords do not match")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Register")

# TODO: CHECK IF EMAIL AND USERNAME ALREADY EXIST (WHEN DATABASE ADDED)
class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed([".png", ".jpg"])])
    submit = SubmitField("Update")
