from flask import render_template, redirect, request, make_response, flash, send_from_directory
from functools import wraps
from werkzeug.utils import secure_filename
from app import app, db, mongo
from model.user import User

import os
import app_config

def check_cookie(request):
    return User.from_db(request.cookies.get('username')).authorize(request.cookies.get('token'))

def login_required(func):
    @wraps(func)
    def login_func(*arg, **kwargs):
        try:
            if check_cookie(request):
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
            if check_cookie(request):
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
    return render_template('index.html', avatar=db.users.find_one({"user":username})['avatar'], text=username)

@app.route('/login', methods=['GET', 'POST'])
@no_login
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if db.users.find_one({"user": username}) != None:
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
    acc = db.users.find_one({"user":username})

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

def allowed_extension(filename):
    EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    extensions = filename.split('.')[-1].lower()
    return extensions in EXTENSIONS
        
@app.route('/profile', methods=['GET','POST'])
@login_required
def change_avt():
    username = request.cookies.get("username")
    user = User.from_db(username)
    link = user.get_avatar()
    if request.method == 'GET':       
        return render_template("profile.html", avatar=link)
    else:
        avatar = request.files['file']
        filename = secure_filename(avatar.filename)
        if avatar == None:
            flash("File not found")
            return render_template("profile.html", avatar=link)

        if filename == '':
            flash("No file selected!!!")
            return render_template("profile.html", avatar=link)

        if not allowed_extension(filename):
            flash("Invalid file extension")
            return render_template("profile.html", avatar=link)
        
        try:
            user_avatar = user.get_avatar()
            # Xóa avatar cũ
            try:
                if user_avatar != 'default.png':
                    id = mongo.db.fs.files.find_one({"filename": user_avatar}).get('_id')
                    mongo.db.fs.chunks.remove({'files_id': id})
                    mongo.db.fs.files.remove({'_id': id})
            except:
                flash("Avatar is not in database!!!")

            mongo.save_file(filename, avatar)
            user.update_avatar(filename)
        except:
            flash("Error saving file!!!")
            return redirect('/profile')
        # avatar.save(os.path.join(app_config.UPLOAD_DIR, filename))
        # user.update_avatar(filename)

        flash("Avatar updated!!!")  
        return render_template("index.html", avatar = filename, text=username)

@app.route('/uploads/<filename>')
def upload_avatar(filename):
    if filename == 'default.png':
        return app.send_static_file(filename)
    #return send_from_directory(app_config.UPLOAD_DIR, filename)
    return mongo.send_file(filename)

if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug=True)