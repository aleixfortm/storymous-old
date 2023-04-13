from flask import Flask
from flask_login import LoginManager
from misc.config import SECRET_KEY, MONGODB_URI
from flask_pymongo import PyMongo


# create app object and assign secret key
app = Flask(__name__, template_folder='./templates')
app.secret_key = SECRET_KEY

# pymongo config
app.config["MONGO_URI"] = MONGODB_URI
mongo = PyMongo(app)
# create collection instances
db_users = mongo.db.users
db_posts = mongo.db.posts
db_comments = mongo.db.comments
db_friends = mongo.db.friends

# create login manager instance to keep track of user authentication
login_manager = LoginManager()
login_manager.init_app(app)

from misc.models import User
@login_manager.user_loader
def load_user(username):
    
    user = User.check_user(username)
    return user


# register blueprints
from blueprints.home import home_bp
app.register_blueprint(home_bp)
from blueprints.auth import auth_bp
app.register_blueprint(auth_bp)
from blueprints.posts import posts_bp
app.register_blueprint(posts_bp)