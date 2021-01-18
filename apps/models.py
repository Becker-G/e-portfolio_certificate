# coding=utf-8
from flask_login import UserMixin
from apps.ext import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(128), nullable=False, unique=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    group = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime())
    active = db.Column(db.Boolean())

    def __init__(self, student_id, username, email, group, password, confirmed_at, active):
        self.student_id = student_id
        self.username = username
        self.email = email
        self.group = group
        self.password = password
        self.confirmed_at = confirmed_at
        self.active = active