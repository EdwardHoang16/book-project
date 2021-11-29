# This file handles the logic and routes of the application.

import flask
from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from flask.helpers import make_response
from werkzeug.exceptions import abort

#Gets a database connection to database.db.
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#Get a book record by ID.
def get_post(post_bookID):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM books WHERE bookID = ?',
                         (post_bookID,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

#Get a book record by title.
def get_book_record_by_title(title):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM books WHERE title LIKE ?',
                         ('%' + title + '%',)).fetchall()
    conn.close()
    if post is None:
        abort(404)
    return post

#Get all the book records a user is renting
def get_renters_books(email):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE renter  = ?',
                         (email,)).fetchall()
    conn.close()
    if post is None:
        abort(404)
    return posts

#Update a book record with a new renter
def update_renter(email, isbn):
    conn = get_db_connection()
    conn.execute(f"UPDATE books SET renter = '{email}' WHERE isbn = '{isbn}'")
    conn.commit()
    conn.close()
    return "Book Renter Updated"

#Checks if a book is rented
def is_book_rented(isbn):
    book = get_book_by_isbn(isbn)
    if len(book[0]['renter'])==0:
        return False
    return True

#Gets all the book records from our database
def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return posts

#Gets all the book records by author
def get_books_by_author(author):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE authors LIKE ?',('%' + author + '%',)).fetchall()
    conn.close()
    return posts

#Gets all the book records by language
def get_books_by_language(language):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE language_code = ?',(language,)).fetchall()
    conn.close()
    return posts

#Gets all the book records by isbn
def get_book_by_isbn(isbn):
    conn = get_db_connection()
    post = conn.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'").fetchall()
    conn.close()
    return post

#Gets the user email
def get_email():
    email = request.cookies.get('email')
    return email

#Checks if a book is able to be rented
def rentable(isbn):
    email = get_email()
    return not email is None and not is_book_rented(isbn)

#Checks if a user is currently renting a particular book
def owns_book(isbn):
    return get_email() == get_book_by_isbn(isbn)[0]['renter']

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

#Allows get_email, rentable, and owns_book functions to be used in Jinja.
@app.context_processor
def get_login():
    return dict(get_email=get_email, rentable=rentable, owns_book=owns_book)

#post all book records on our home page
@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

#post a book record by ID
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(str(post_id))
    return render_template('post.html', post=post)

#post all book records by title
@app.route('/<title>')
def book_by_title(title):
    posts = get_book_record_by_title(title)
    return render_template('index.html', posts=posts)

#post all books a user is renting
@app.route('/booksRenting')
def books_by_user():
    email = get_email()
    posts = get_renters_books(email)
    return render_template('index.html', posts=posts)

# Handles the renting of a book by a logged-in user
@app.route('/rent_book/<isbn>', methods=['GET', 'POST'])
def rent_a_book(isbn):
    email = get_email()
    if request.method == 'POST':
        if is_book_rented(isbn):
            flash('Book Is Rented!')
            return render_template('index.html', posts=get_all_posts())
        else:
            update_renter(email, isbn)
            posts = get_renters_books(email)
            return render_template('index.html', posts=posts)
    else:
        return render_template('index.html', posts=get_book_by_isbn(isbn))

# Handles the returning of a book by a logged-in user
@app.route('/return_book/<isbn>', methods=['POST'])
def return_book(isbn):
    update_renter('', isbn)
    email = get_email()
    posts = get_renters_books(email)
    return render_template('index.html', posts=posts)

#Search for a book in the search page
@app.route('/search', methods=['GET', 'POST'])
def search_a_book():
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

# Shows the user the page for searching
@app.route('/search')
def search():
    return render_template('search.html')

# Shows the logged-in user the books they are currently renting
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
