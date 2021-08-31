from flask import render_template, redirect, request, make_response, flash, send_from_directory
from functools import wraps
from werkzeug.utils import secure_filename
from app import mongo, app
from model.user import User

import os
import app_config

def login_required(func):
    @wraps(func)
    def login_func(*arg, **kwargs):
        try:
            user = User.from_db(request.cookies.get('username'))
            if user.authorize(request.cookies.get('token')):
                return func(*arg, **kwargs)
        except:
            pass
        flash ("Login required!!!")
        return redirect('/login')

    return login_func

def no_login(func):
    @wraps(func)
    def no_login_func(*arg, **kwargs):
        try:
            username = User.from_db(request.cookies.get('username'))
            if username.authorize(request.cookies.get('token')):
                flash("You're already in!!!")
                return redirect('/index')
        except:
            pass
        return func(*arg, **kwargs)

    return no_login_func

@app.route('/')
def home():
    return redirect('/login')

@app.route('/index')
@login_required
def index():
    username = request.cookies.get('username')
    return render_template('index.html', avatar=mongo.db.users.find_one({"user":username})['avatar'], text=username)

@app.route('/login', methods=['GET', 'POST'])
@no_login
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if mongo.db.users.find_one({"user": username}) != None:
        acc = User.from_db(username)
        if username == "drum":
            if acc.authenticate(password):
                token = acc.init_session()
                resp = make_response(redirect('/drum'))
                resp.set_cookie('username', username)
                resp.set_cookie('token', token)
                return resp
        else:
            if acc.authenticate(password):
                token = acc.init_session()
                resp = make_response(redirect('/index'))
                resp.set_cookie('username', username)
                resp.set_cookie('token', token)
                return resp
            else:
                flash("Username or password is incorrect!!!")
    else:
        flash("User does not exists")

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    username = request.cookies.get('username')
    acc = User.from_db(username)
    acc.terminate_session()
    resp = make_response(redirect('/login'))
    resp.delete_cookie('username')
    resp.delete_cookie('token')
    flash("You've logged out!!!")
    return resp

@app.route('/register', methods=['POST', 'GET'])
@no_login
def register():
    if request.method == "GET":
        return render_template('register.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    acc = mongo.db.users.find_one({"user":username})

    if acc == None:
        if password == password_confirm:
            acc = User.new(username, password)
            token = acc.init_session()
            resp = make_response(redirect('/index'))
            resp.set_cookie('username', username)
            resp.set_cookie('token', token)
            return resp
        else:
            flash("Passwords do not match!!!")
    else:
        flash("User already exists!!!")

    return render_template('register.html')

@app.route('/changepwd', methods=['GET', 'POST'])
@login_required
def change_pwd():
    if request.method == 'GET':
        return render_template('changepwd.html')
    else:
        username = request.cookies.get('username')
        password = request.form.get('cur_password')
        new_password = request.form.get('new_password')
        password_confirm = request.form.get('password_confirm')
        acc = User.from_db(username)

        if acc.authenticate(password):
            if new_password == password_confirm:
                acc = User.new(username,new_password)
                acc.dump()
                resp = make_response(redirect('/login'))
                flash("You have to login again!!!")
                return resp
            else:
                flash("Password do not match!!!")
        else:
            flash("Password is incorrect!!!")

    return render_template('changepwd.html')

@app.route('/drum', methods=['GET', 'POST'])
@login_required
def drum():
    return render_template('drum.html')
        
@app.route('/profile', methods=['GET','POST'])
@login_required
def change_avt():
    username = request.cookies.get("username")
    if request.method == 'GET':
        link = mongo.db.users.find_one({"user": username})['avatar']
        return render_template("profile.html", avatar=link)
    else:
        avatar = request.files['file']
        user = User.from_db(username)
        filename = secure_filename(avatar.filename)
        
        if filename != '':
            avatar.save(os.path.join(app_config.UPLOAD_DIR, filename))
            url = "./uploads/" + str(filename)
            user.update_avatar(url)
            flash("Avatar updated!!!")
            return redirect("/")
        else:
            flash("Image not found")
    return render_template("profile.html")

@app.route('/uploads/<filename>')
def upload_avatar(filename):
    return send_from_directory('./uploads/', filename)

if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug=True)