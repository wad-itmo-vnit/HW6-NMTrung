import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

def gen_session_token(length=24):
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])
    return token

class User:
    def __init__(self, username, password, avatar="", token=None):
        self.username = username
        self.password = password
        self.token = token     
        if avatar=="":
            self.avatar = "default.png"
        else:
            self.avatar = avatar
        self.dump()

    @classmethod
    def new(cls, username, password):
        password = generate_password_hash(password)
        return cls(username, password)

    @classmethod
    def from_db(cls, user):
        username = db.users.find_one({"user": user})['user']
        password = db.users.find_one({"user": user})['password'] 
        token = db.users.find_one({"user": user})['token']
        avatar = db.users.find_one({"user": user})['avatar']
        if token == 'None':
            return cls(username, password, avatar)
        return cls(username, password, avatar, token) 

    def authenticate(self, password):
        return check_password_hash(self.password, password)

    def get_avatar(self):
        return self.avatar

    def update_avatar(self, avatar):
        self.avatar = avatar
        db.users.update_one({"user": self.username}, {"$set": {"avatar": self.avatar}})

    def init_session(self):
        self.token = gen_session_token()
        self.dump()
        return self.token

    def authorize(self, token):
        return token == self.token

    def terminate_session(self):
        self.token = None
        self.dump()

    def dump(self):
        db.users.update_one({"user": self.username},{'$set':
        {"user": self.username, "password": self.password, "token":self.token, "avatar": self.avatar}},upsert=True)
