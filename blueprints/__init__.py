from flask import Flask
from blueprints.config import SECRET_KEY, MONGODB_URI
from flask_pymongo import PyMongo



# create app object and assign secret key
app = Flask(__name__)
app.secret_key = SECRET_KEY

# pymongo config
app.config["MONGO_URI"] = MONGODB_URI
mongo = PyMongo(app)
# create collection instances
db_users = mongo.db.users
db_posts = mongo.db.posts


def register_blueprints(app):
    from blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    from blueprints.posts import posts_bp
    app.register_blueprint(posts_bp)


# register blueprints from respective directory
register_blueprints(app)

# import instances from just initialized blueprints (importing after registering blueprints to avoid errors)
from blueprints.auth import login_manager

# initialize login manager
login_manager.init_app(app)