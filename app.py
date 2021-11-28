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

def get_book_record_by_title(title):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM books WHERE title LIKE ?',
                         ('%' + title + '%',)).fetchall()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_renters_books(email):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE renter  = ?',
                         (email,)).fetchall()
    conn.close()
    if post is None:
        abort(404)
    return posts

def update_renter(email,title):
    task = (email,title)
    conn = get_db_connection()
    post = conn.execute('UPDATE books SET renter = ? WHERE title = ?',task)
    conn.commit()
    conn.close()
    return "Book Renter Updated"


def is_book_rented(title):
    post = get_book_record_by_title(title)
    if len(post['renter'])==0:
        return False
    return True

def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return posts

def get_books_by_author(author):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE authors LIKE ?',('%' + author + '%',)).fetchall()
    conn.close()
    return posts

def get_books_by_language(language):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE language_code = ?',(language,)).fetchall()
    conn.close()
    return posts

def get_email():
    email = request.cookies.get('email')
    return email

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

@app.context_processor
def get_login():
    return dict(get_email=get_email)

@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(str(post_id))
    return render_template('post.html', post=post)

@app.route('/<title>')
def book_by_title(title):
    posts = get_book_record_by_title(title)
    return render_template('index.html', posts=posts)

@app.route('/booksRenting')
def books_by_user():
    email = get_email()
    posts = get_renters_books(email)
    return render_template('index.html', posts=posts)

@app.route('/rentABook/<title>', methods=['GET', 'POST'])
def rent_a_book(title):
    email = get_email()
    if request.method == 'POST':
        if is_book_rented(title):
            flash('Book Is Rented!')
        else:
            update_renter(email,title)
            return redirect(url_for('index'))

    return book_by_title(title)

@app.route('/search', methods=['GET', 'POST'])
def search_a_book():
    email = get_email()
    if request.method == 'POST':
        if request.form.get('title'):
            title = request.form['title']
            posts = get_book_record_by_title(title)
            return render_template('index.html', posts=posts)
        if request.form.get('author'):
            author = request.form['author']
            posts = get_books_by_author(str(author))
            return render_template('index.html', posts=posts)
        if request.form.get('language'):
            language = request.form['language']
            posts = get_books_by_language(str(language))
            return render_template('index.html', posts=posts)
        flash('Enter one of the Fields')
    return render_template('search.html')

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
    resp = make_response(render_template('loggedout.html'))
    flask.Response.delete_cookie(resp, key='email')
    return resp

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/booksRenting')
def books_renting():
    email = get_email()
    posts = get_renters_books(email)
    return render_template('books_renting.html', posts=posts)

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
