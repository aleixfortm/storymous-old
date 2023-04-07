from flask import Flask
from pymongo import MongoClient

# mongodb database setup
client = MongoClient("---")
db = client.storymous

def register_blueprints(app):
    from .auth import auth_bp
    app.register_blueprint(auth_bp)


