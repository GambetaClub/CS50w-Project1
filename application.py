import os
import requests
from flask import jsonify
from flask import Flask, render_template, request
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pickle

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def get_value(book_isbn, information):
    res = requests.get("https://www.goodreads.com/book/review_counts.json?&key=ANacHyJRtneWNOKrj1uxg",
                        params={"isbns": book_isbn})
    if res.status_code != 200:
        if res.status_code == 404:
            return render.template("error.html", message="Page not found")
        if res.status_code == 402:
            return render.template("error.html", message="Bad request")
        raise Exception("ERROR: API request unsuccessful.")

    data = res.json()
    for item in data['books']:
        return(item[information])
        

@app.route("/")
def index():

    """Main Page"""

    return render_template("index.html")

@app.route("/login", methods= ["POST"])
def login():

    """Logging in..."""

    user_username = request.form.get("username")
    user_password = request.form.get("password")
    pickle.dump(username, open( "save.p", "wb" ))

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": user_username}).rowcount == 0:
        #INVALID USERNAME
        return render_template("error.html", message= "Invalid username")
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": user_username, "password": user_password}).rowcount == 1:
        #SUCCESS
        return render_template("login.html", username = user_username)
    #INVALID PASSWORD
    return render_template("error.html", message="Invalid password")

@app.route("/books", methods= ["POST"])
def search_books():

    """Search books"""

    isbn = request.form.get("book_isbn")
    title = request.form.get("book_title")
    author = request.form.get("book_author")

    if isbn:
        isbn = isbn + '%'
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": isbn}).fetchall()
        return render_template("list_of_books.html", books=books)
    if title:
        title = title + '%'
        books = db.execute("SELECT * FROM books WHERE title LIKE :title", {"title": title}).fetchall()
        return render_template("list_of_books.html", books=books)
    if author:
        author = author + '%'
        books = db.execute("SELECT * FROM books WHERE author LIKE :author", {"author": author}).fetchall()
        return render_template("list_of_books.html",books=books)
        
    user_username = pickle.load( open( "save.p", "rb" ))
    return render_template("login.html",username= user_username)


@app.route ("/books/<int:book_id>")
def book_info(book_id):

    """Displaying book info"""
  
    bookID = book_id
    pickle.dump(bookID, open( "save1.p", "wb" ))
    book_isbn = db.execute("SELECT isbn FROM books WHERE id = :id", {"id": book_id}).fetchone()
    avg_rating = get_value(book_isbn,'average_rating')
    reviews_count = get_value(book_isbn,'reviews_count')

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

    return render_template("book.html",book_isbn= book_isbn,book=book, reviews=reviews, avg_rating=avg_rating, reviews_count=reviews_count)


@app.route ("/books/review_posted", methods= ["POST"])
def post_review():

    """Inserting review to reviews table"""
    new_rating  = request.form.get("rating")
    new_review = request.form.get("new_review")
    username = pickle.load( open( "save.p", "rb" ))
    book_id = pickle.load( open("save1.p", "rb"))
    book_isbn = db.execute("SELECT isbn FROM books WHERE id = :id", {"id": book_id}).fetchone()
    avg_rating = get_value(book_isbn,'average_rating')
    reviews_count = get_value(book_isbn,'reviews_count')

    if db.execute("SELECT * FROM reviews WHERE username = :username AND book_id = :book_id", {"username": username, "book_id": book_id}).rowcount >= 1:
        return render_template("error.html", message= "You cannot review the same book more than once")
    
    #Checking if the user has reviewed the book before
    db.execute("INSERT INTO reviews (reviews, rating, book_id, username) VALUES (:new_review, :new_rating, :book_id, :username)",
             {"new_review": new_review,"new_rating": new_rating, "book_id": book_id, "username": username})
    db.commit()

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id})
    
    return render_template("review_posted.html", book=book, reviews=reviews, avg_rating=avg_rating, reviews_count=reviews_count)

@app.route("/api/books/<string:book_isbn>")
def book_api(book_isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid book_isbn"}), 422

    avg_rating = get_value(book_isbn,'average_rating')
    reviews_count = get_value(book_isbn,'reviews_count')
    
    book_title = book.title
    book_author = book.author 
    book_year = book.year  
    return jsonify({
            "title": book_title,
            "author": book_author,
            "year": book_year,
            "isbn": book_isbn,
            "review_count": reviews_count,
            "average_score": avg_rating
        })


@app.route("/signup")
def createacc():

    """Creating account"""

    return render_template("signup.html")

@app.route("/success", methods= ["POST"])
def signup():

    """Signing up"""
    
    new_username = request.form.get("username")
    new_password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": new_username}).rowcount == 1:
        return render_template("error.html", message= "Username has already taken, please try another one")
    
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": new_username, "password": new_password})
    db.commit()
    return render_template("success.html", username=new_username)

#@app.route("books/api/<str:isbn")
#def api():

 