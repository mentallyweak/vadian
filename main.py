import os
import time
import sqlite3
import flask_login
import datetime
import flask
from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)
app.secret_key = 'KSAHFIU@T#&*@#YQWIUFHBAUISATF&*ASCBAUIXHCGIYUASGD&*XzjhcvbXZJHGCV^WQREQ&E!Q@#@!#'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
class User(flask_login.UserMixin):
    pass
@login_manager.user_loader
def user_loader(username):
    db_connection = sqlite3.connect('website.db')
    cursor = db_connection.cursor()
    db_connection.execute("CREATE TABLE IF NOT EXISTS {}(username, user_password)".format('users'))
    db_connection.commit()
    password =  cursor.execute('SELECT user_password FROM users WHERE username == ?', (f'{username}',)).fetchone()
    if password == None:
        return
    user = User()
    user.id = username
    return user
@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    db_connection = sqlite3.connect('website.db')
    cursor = db_connection.cursor()
    db_connection.execute("CREATE TABLE IF NOT EXISTS {}(username, user_password)".format('users'))
    db_connection.commit()
    
    password =  cursor.execute('SELECT user_password FROM users WHERE username == ?', (f'{username}',)).fetchone()
    if password == None:
        return
    user = User()
    user.id = username
    return user
app.errorhandler(404)
def error(e):
    return render_template('error.html', error_text = 'Ошибка 404: страница не найдена!')
@app.errorhandler(401)
def error(e):
    return render_template('error.html', error_text = 'Ошибка 401: Вы не авторизованы!')
@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('/')
@app.route('/')
def index_page():
    return render_template('index.html')
@app.route('/reg', methods = ['GET', 'POST'])
def registration_page():
    db_connection = sqlite3.connect('website.db')
    cursor = db_connection.cursor()
    db_connection.execute("CREATE TABLE IF NOT EXISTS {}(username, user_password)".format('users'))
    db_connection.commit()
    if request.method == 'GET':
        return render_template('reg.html')
    elif request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        user_exists = cursor.execute('SELECT user_password FROM users WHERE username == ?', (f'{username}',)).fetchone()
        if user_exists == None:
            try:
              cursor.execute('INSERT INTO users VALUES(?, ?)', (f'{username}', f'{password}'))
              db_connection.commit()
              return "Аккаунт успешно зарегестрирован!"
            except:
                return render_template('registration.html')
        else:
            return render_template('registration.html')
        
@app.route('/login', methods = ['GET', 'POST'])
def login_page():
    db_connection = sqlite3.connect('website.db')
    cursor = db_connection.cursor()
    db_connection.execute("CREATE TABLE IF NOT EXISTS {}(username, user_password)".format('users'))
    db_connection.commit()
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            password_db = cursor.execute('SELECT user_password FROM users WHERE username == ?', (f'{username}',)).fetchone()
            if password_db == None:
                return render_template('error.html', error_text = 'Имя пользователя не найдено в базе!')
            
            if password.replace(' ', '') == password_db[0].replace(' ', ''):
                user = User()
                user.id = username
                flask_login.login_user(user)
                return redirect('/')
            else:
                return render_template('error.html', error_text = 'Не правильный пароль!')
    else:
        return render_template('login.html')
@app.route('/posts', methods=['GET', 'POST'])
@flask_login.login_required
def posts():
    db_connection = sqlite3.connect('website.db')
    cursor = db_connection.cursor()
    db_connection.execute("CREATE TABLE IF NOT EXISTS {}(id, post_name, post_text, author, datetime)".format('posts'))
    db_connection.commit()
    
    if request.method == 'GET':
        all_posts = cursor.execute('SELECT * FROM posts').fetchall()
        return render_template('posts.html', __author = flask_login.current_user.id, __logined = flask_login.current_user.id, __posts = all_posts, __posts_counter = len(all_posts))
    else:
        all_posts = cursor.execute('SELECT * FROM posts').fetchall()
        
        id = 0
        for i in range(len(all_posts)):
            if request.form.get(str(i + 1), False) != False:
                id = i + 1
                break
        
        if id != 0:
            cursor.execute('DELETE FROM posts WHERE id == ?', (f'{id}',))
            db_connection.commit()
            return redirect('/posts')
        posts = []
        search = request.form['post_search']
        all_posts = cursor.execute('SELECT * FROM posts').fetchall()
        for i in all_posts:
            if search.lower() in i[1].lower():
                posts.append(i)
        if len(posts) == 0:
            return render_template('posts.html', __logined = flask_login.current_user.id,  __posts_counter = len(all_posts), __error = 'По вашему запросу ничего не найдено')
        return render_template('posts.html', __logined = flask_login.current_user.id, __posts = posts, __posts_counter = len(all_posts))
@app.route('/add_post', methods=['GET', 'POST'])
@flask_login.login_required
def add_post():
    db_connection = sqlite3.connect('website.db')
    cursor = db_connection.cursor()
    db_connection.execute("CREATE TABLE IF NOT EXISTS {}(post_name, post_text, author, datetime)".format('posts'))
    db_connection.commit()
    if request.method == 'POST':
        post_name = request.form['post_name']
        post_content = request.form['post_text']
        time = str(datetime.datetime.now())
        user = str(flask_login.current_user.id)
        all_posts = cursor.execute('SELECT * FROM posts').fetchall()
        cursor.execute('INSERT INTO posts VALUES(?, ?, ?, ?, ?)', (f'{len(all_posts) + 1}', f'{post_name}', f'{post_content}', f'{user}', f'{time}'))
        db_connection.commit()
        return redirect('/posts')
    else:
        return render_template('add_post.html', __logined = flask_login.current_user.id)
app.run(debug=True)
