from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from werkzeug.exceptions import abort

userLoggedIn = False

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

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('index.html', posts=posts, userLoggedIn=userLoggedIn)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

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

def update_renter(email,title):
    task = (email,title)
    conn = get_db_connection()
    post = conn.execute('UPDATE books SET renter = ? WHERE title = ?',task)
    conn.commit()
    conn.close()
    return "Book Renter Updated"



