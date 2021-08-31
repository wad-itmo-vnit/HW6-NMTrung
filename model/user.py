import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo

def gen_session_token(length=24):
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])
    return token

class User:
    def __init__(self, username, password, avatar="", token=None):
        self.username = username
        self.password = password
        self.token = token
        if avatar=="":
            self.avatar = "https://bombyxplm.com/wp-content/uploads/2021/01/421-4213053_default-avatar-icon-hd-png-download.png"
        else:
            self.avatar = avatar
        self.dump()
    
    @classmethod
    def new(cls, username, password):
        password = generate_password_hash(password)
        return cls(username, password)

    @classmethod
    def from_db(cls, user):
        username = mongo.db.users.find_one({"user": user})['user']
        password = mongo.db.users.find_one({"user": user})['password'] 
        token = mongo.db.users.find_one({"user": user})['token']
        avatar = mongo.db.users.find_one({"user": user})['avatar']
        if token == 'None':
            return cls(username, password, avatar)
        return cls(username, password, avatar, token) 

    def authenticate(self, password):
        return check_password_hash(self.password, password)
        
    def update_avatar(self, avatar):
        self.avatar = avatar
        self.dump()

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
        mongo.db.users.update_one({"user": self.username},{'$set':
        {"user": self.username, "password": self.password, "token":self.token, "avatar": self.avatar}},upsert=True)
