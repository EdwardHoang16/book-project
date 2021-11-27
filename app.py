import flask
from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from flask.helpers import make_response
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_bookID):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM books WHERE bookID = ?',
                         (post_bookID,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_title(title):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM books WHERE title  = ?',
                         (title,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_renter(email):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM books WHERE renter  = ?',
                         (email,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return posts

def get_email():
    email = request.cookies.get('email')
    return email

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(str(post_id))
    return render_template('post.html', post=post)

@app.route('/title/<title>')
def books_by_title(title):
    post = get_title(title)
    return render_template('post.html', post=post)


@app.route('/user/<email>')
def books_by_user(email):
    post = get_renter(email)
    return render_template('post.html', post=post)

### Authentication ###
@app.route('/signup')
def signup():
    return render_template('signup.html')

# if user logged in, reroute to index otherwise reroute to login
@app.route('/login')
def login():
    if not get_email():
        return render_template('login.html')
    else:
        posts = get_all_posts()
        return render_template('index.html', posts=posts)

# delete cookie holding user's email info and return them to index
@app.route('/logout')
def logout():
    posts = get_all_posts()
    resp = make_response(render_template('index.html', posts=posts))
    flask.Response.delete_cookie(resp, key='email')
    return resp

# check if credentials match against db
# if credentials match, set cookie (with 1 hour timeout) on user's side which contains email
# redirect to index
@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM credentials WHERE email = '{email}' AND password = '{password}'").fetchall()
    if len(user) != 1:
        conn.close()
        abort(401)
    conn.close()

    posts = get_all_posts()
    resp = make_response(render_template('index.html', posts=posts))
    resp.set_cookie(key='email', value=f'{email}', max_age=3600) # max_age in seconds so 1 hour
    return resp

# save user in db if they are not already there
# redirect to login page
@app.route('/new_user', methods=['POST'])
def new_user():
    email = request.form['email']
    password = request.form['password']
    print(email, password)

    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM credentials WHERE email = '{email}'").fetchall()
    if len(user) > 0:
        conn.close()
        return make_response(render_template('login.html'))
    conn.execute(f"INSERT INTO credentials (email, password) VALUES ('{email}', '{password}')")
    conn.commit()
    conn.close() 

    return render_template('login.html')

# use this to test if our server can figure out the user's email after login
# also use to test if logout works
@app.route('/get_user')
def get_user():
    email = request.cookies.get('email')
    if not email:
        return '<h1>Please Log In!</h1>'
    return '<h1>Welcome ' + email + '</h1>'
