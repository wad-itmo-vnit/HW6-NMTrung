from flask import Flask
from flask_pymongo import PyMongo
import app_config

app = Flask(__name__)
app.config['SECRET_KEY'] = app_config.SECRET_KEY
app.config["MONGO_URI"] = "mongodb://localhost:27017/wad_hw"
mongo = PyMongo(app)
db = mongo.db