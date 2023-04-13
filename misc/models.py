from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

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
        return db_users.find_one({'email': email})
    
    # retrieve user data as dict
    @staticmethod
    def find_by_username(username):
        return db_users.find_one({'username': username})

    # return user object from retrieved dict
    @staticmethod
    def check_user(username):
        user_data = db_users.find_one({'username': username})
        if user_data:
            return User(email=user_data['email'], username=user_data['username'], password_hash=user_data['password_hash'])
        return None
    

class Post:
    def __init__(self, username, date, title, content, preview=None, post_comment=None):
        self._id = ObjectId()
        self.username = username
        self.date = date
        self.title = title
        self.content = content
        self.preview = preview
        self.post_comment = post_comment
        self.vists = 1
        self.n_comments = 0
        self.user_comments = []

    def save_post_to_db(self):
        db_posts.insert_one({
            'username': self.username,
            'title': self.title,
            'content': self.content
            })
    
    def quicksave_to_db(self):
        db_posts.insert_one(self.__dict__)
    
    def replace_or_create_to_db(self):
        post_dict = self.__dict__
        db_posts.update_one({'_id': self._id}, {'$set': post_dict}, upsert=True)

    def increase_visits(self):
        self.visits += 1

    def add_user_comment(self, comment):
        self.n_comments += 1
        self.user_comments.append(comment)


class Comment:
    def __init__(self, username, content, date):
        self.username = username
        self.content = content
        self.date = date


from main import db_users, db_posts