import os

from flask import Flask, render_template, request
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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


@app.route("/")
def index():
    """Main Page"""
    return render_template("index.html")

@app.route("/login", methods= ["POST"])
def login():
    """Logging in..."""
    user_username = request.form.get("username")
    user_password = request.form.get("password")
    
    if db.execute("SELECT * FROM users WHERE password = :password", {"password": user_password}).rowcount == 0:
        return render_template("error.html", message= "Invalid username or password")

    return render_template("login.html", username= user_username)

@app.route("/books", methods= ["POST"])
def search_books():
    """List of books"""
    isbn = request.form.get("book_isbn")
    title = request.form.get("book_title")
    author = request.form.get("book_author")


    

    if isbn is not None:
        books = db.execute("SELECT * FROM books WHERE isbn = isbn", {"isbn": isbn})
        return render_template("list_of_books.html", books=books)
    if title is not None:
        books = db.execute("SELECT * FROM books WHERE title = :title", {"title": title})
        return render_template("list_of_books.html", books=books)
    if author is not None:
        books = db.execute("SELECT * FROM books WHERE author = :author", {"author": author})
        return render_template("list_of_books.html", books=books)
    return render_template("login.html") 

@app.route ("/books/book_info")
def book_info(book_id):

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    return render_template("book.html", book= book)



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