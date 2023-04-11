from flask import Blueprint, url_for, render_template, flash, redirect
from flask_login import login_required, current_user

# blueprint creation
posts_bp = Blueprint("posts", __name__)

