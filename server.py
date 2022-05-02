import json
import os.path
import re
import sqlite3
from datetime import timedelta

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'Flask%Crud#Application'

app.permanent_session_lifetime = timedelta(minutes=5)

# Added ###################################################################
with open("./static/movies.json") as f:
    data = json.load(f)
    data.reverse()

genresList = []
for i in data:
    for j in i['genres']:
        genresList.append(j)

genresList = list( dict.fromkeys(genresList) )
genresList.sort()

print(genresList)

# Enter your database connection details below
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.sqlite")

#SqLite database connection
conn = sqlite3.connect(db_path, check_same_thread=False)

# Added ###################################################################
cursor_setup = conn.cursor()
cursor_setup.execute('CREATE TABLE IF NOT EXISTS users(firstname text, lastname text, email text, username text, password text)')
conn.commit()
cursor_setup.execute('DROP TABLE IF EXISTS movies')
conn.commit()
cursor_setup.execute('CREATE TABLE movies(title text, year integer, cast text, genres text)')
conn.commit()
cursor_setup.execute('DROP TABLE IF EXISTS movieCast')
conn.commit()
cursor_setup.execute('CREATE TABLE movieCast(title text, cast text)')
conn.commit()
cursor_setup.execute('DROP TABLE IF EXISTS movieGenres')
conn.commit()
cursor_setup.execute('CREATE TABLE movieGenres(title text, genre text)')
conn.commit()
cursor_setup.execute('DROP TABLE IF EXISTS viewedMovies')
conn.commit()
cursor_setup.execute('CREATE TABLE viewedMovies(title text, genre text)')
conn.commit()
cursor_setup.close()
'''
# External database connection

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'demo_db'


# Intialize MySQL
mysql.init_app(app)
'''

@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for("home"))


    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        session.permanent = True

        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if user exists using MySQL
        # conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))

        # Fetch one record and return result
        user = cursor.fetchone()
        print(user)

        # If user exists in users table in the database
        if user and check_password_hash(user[4], password):

            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['firstname'] = user[0]
            session['username'] = user[3]

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # user doesnt exist or username/password incorrect
            msg = 'Incorrect username/password! :/'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('firstname', None)
    session.pop('username', None)

    # Redirect to login page
    return redirect(url_for('welcome'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        # Create variables for easy access
        first = request.form['firstname']
        last = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hash = generate_password_hash(password)
        email = request.form['email']

        # Check if user exists using MySQL
        # conn = mysql.connect()    #MySql connector
        cursor = conn.cursor()

        #cursor.execute('SELECT * FROM users WHERE username = %s', (username,))  #MySql connect statement
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))   #SqLite Connect statement
        user = cursor.fetchone()

        # If user exists show error and validation checks
        if user:
            msg = 'Username/user already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # user doesnt exists and the form data is valid, now insert new user into users table
            # MySql Insert statement
            #cursor.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s)', (first, last, email, username, hash))

            # SqLite Insert Statement
            cursor.execute('INSERT INTO users (firstname, lastname, email, username, password) VALUES (?, ?, ?, ?, ?)',
                           (first, last, email, username, hash,))
            conn.commit()
            msg = 'You have successfully registered!'
            return render_template('index.html')

    elif request.method == "POST":
        # Form is empty... (no POST data)
        msg = 'Please fill all required fields!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/home', methods = ['POST', 'GET'])
def home():

    # Check if user is loggedin
    if 'loggedin' in session:

        cursor = conn.cursor()

        if request.method == 'POST' and 'username' and 'genrezz' in request.form:
            genre = request.form['genrezz']
            cursor.execute('SELECT title FROM movieGenres WHERE genre = ?', (genre,))
            moviez = cursor.fetchmany(100)
            return render_template('home.html', username=session['username'], genres=genresList, moviez=moviez)

        if request.method == 'POST' and 'titleSearched' in request.form:
            title = request.form['titleSearched']
            print(title)
            cursor.execute('SELECT genre FROM movieGenres WHERE title = ?', (title,))
            Xgenres = cursor.fetchall()
            print(Xgenres[0][0])
            for i in Xgenres:
                cursor.execute('INSERT INTO moviesSearched (title, genre) VALUES (?, ?)', (title, i[0],))
            conn.commit()
            return render_template('home.html', username=session['username'], genres=genresList)

        if request.method == 'POST' and 'moviezz' in request.form:
            moviezz = request.form['moviezz']
            print(moviezz)
            cursor.execute('SELECT genre FROM movieGenres WHERE title = ?', (moviezz,))
            Xmovies = cursor.fetchall()
            print(Xmovies[0][0])
            for i in Xmovies:
                cursor.execute('INSERT INTO viewedMovies (title, genre) VALUES (?, ?)', (moviezz, i[0],))
            conn.commit()
            return render_template('home.html', username=session['username'], genres=genresList)


        for i in range(1000):
            cast = ''
            genres = ''
            title = data[i]['title']
            year = data[i]['year']
            #cast = data[i]['cast']
            for j in data[i]['cast']:
                cast += j + ', '
            cast = cast[0:-2]
            cursor.execute('INSERT INTO movieCast (title, cast) VALUES (?, ?)', (title, cast))
            for j in data[i]['genres']:
                genres += j
                cursor.execute('INSERT INTO movieGenres (title, genre) VALUES (?,?)', (title, j))
            cursor.execute('INSERT INTO movies (title, year, cast, genres) VALUES (?, ?, ?, ?)',
                           (title, year, cast, genres))
        conn.commit()



    # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], genres=genresList)


    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the user info for the user so we can display it on the profile page
        #conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
        user = cursor.fetchone()

        # Show the profile page with user info
        return render_template('profile.html', user=user)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
