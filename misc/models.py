from flask_login import UserMixin
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
import datetime, random

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
    def __init__(self, email, username, password_hash, pic_path=None, creation_date=datetime.datetime.now().isoformat(), _id=None, n_comments=0, friends=[], n_writ_posts=0, n_contr_posts=0, n_friends=0):
        self._id = ObjectId(_id)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.n_writ_posts = n_writ_posts
        self.n_contr_posts = n_contr_posts
        self.n_friends = n_friends
        self.friends = friends
        self.n_comments = n_comments
        self.creation_date = creation_date
        self.pic_path = pic_path
        if pic_path is None:
            self.assign_pic_path()

    def get_id(self):
        return self.username
    
    def assign_pic_path(self):
        pic_dict = {0: "green", 1: "blue", 2: "grey", 3: "purple", 4: "red", 5: "yellow"}
        color = pic_dict[random.randint(0, 5)]
        filepath = f'/static/img/default_{color}.png'
        self.pic_path = filepath

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def quicksave_to_db(self):
        db_users.insert_one(self.__dict__)
    
    # check if account is old or new format
    def is_new_format(self):
        return "pic_path" in db_users.find_one({"username": self.username}) 

    def replace_user(self):
        db_users.replace_one({"username": self.username}, self.__dict__)
    
    @staticmethod
    def pic_color_static(pic_num):
        pic_dict = {0: "green", 1: "blue", 2: "grey", 3: "purple", 4: "red", 5: "yellow"}
        return pic_dict[pic_num]

    # retrieve user data as dict
    @staticmethod
    def find_by_email(email):
        return db_users.find_one({'email': email})
    
    # retrieve user data as dict
    @staticmethod
    def find_by_username(username):
        return db_users.find_one({'username': username})
    
    @staticmethod
    def format_date_data(user_data):
        dt = datetime.datetime.fromisoformat(user_data["creation_date"])
        formatted_date = dt.strftime('%b %d, %Y')
        user_data["creation_date"] = formatted_date
        return user_data

    # return user object from retrieved dict
    @staticmethod
    def check_user(username):
        user_data = db_users.find_one({'username': username})
        return User(**user_data) if user_data != None else None
    

class Post:
    def __init__(self, username, title, content, date=datetime.datetime.now().isoformat(), preview=None, post_comment=None):
        self._id = ObjectId()
        self.username = username
        self.date = date
        self.title = title
        self.content = content
        self.preview = preview
        self.post_comment = post_comment
        self.visits = 1
        self.n_comments = 0
        self.user_comments = []
    
    def quicksave_to_db(self):
        db_posts.insert_one(self.__dict__)
    
    def replace_db_doc(self):
        post_dict = self.__dict__
        db_posts.update_one({'_id': self._id}, {'$set': post_dict}, upsert=True)

    def increase_visits(self):
        self.visits += 1

    def add_user_comment(self, comment):
        self.n_comments += 1
        self.user_comments.append(comment)

    @staticmethod
    def format_date_data(post_data):
        dt = datetime.datetime.fromisoformat(post_data["date"])
        formatted_date = dt.strftime('%b %d')
        post_data["date"] = formatted_date
        return post_data


class Comment:
    def __init__(self, username, content, date):
        self.username = username
        self.content = content
        self.date = date


from main import db_users, db_posts