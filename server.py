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

        for i in range(1000):
            cast = ''
            genres = ''
            title = data[i]['title']
            year = data[i]['year']
            for j in data[i]['cast']:
                cast += j + "   "
            for j in data[i]['genres']:
                genres += j + "   "
            cursor.execute('INSERT INTO movies (title, year, cast, genres) VALUES (?, ?, ?, ?)',
                           (title, year, cast, genres))
        conn.commit()

        actionMovies = '%Action%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (actionMovies,))
        actionMovies = cursor.fetchmany(100)
        conn.commit()

        adventureMovies = '%Adventure%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (adventureMovies,))
        adventureMovies = cursor.fetchmany(100)
        conn.commit()

        animatedMovies = '%Animated%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (animatedMovies,))
        animatedMovies = cursor.fetchmany(100)
        conn.commit()

        biographyMovies = '%Biography%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (biographyMovies,))
        biographyMovies = cursor.fetchmany(100)
        conn.commit()

        comedyMovies = '%Comedy%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (comedyMovies,))
        comedyMovies = cursor.fetchmany(100)
        conn.commit()

        crimeMovies = '%Crime%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (crimeMovies,))
        crimeMovies = cursor.fetchmany(100)
        conn.commit()

        danceMovies = '%Dance%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (danceMovies,))
        danceMovies = cursor.fetchmany(100)
        conn.commit()

        disasterMovies = '%Disaster%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (disasterMovies,))
        disasterMovies = cursor.fetchmany(100)
        conn.commit()

        documentaryMovies = '%Documentary%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (documentaryMovies,))
        documentaryMovies = cursor.fetchmany(100)
        conn.commit()

        dramaMovies = '%Drama%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (dramaMovies,))
        dramaMovies = cursor.fetchmany(100)
        conn.commit()

        eroticMovies = '%Erotic%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (eroticMovies,))
        eroticMovies = cursor.fetchmany(100)
        conn.commit()

        familyMovies = '%Family%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (familyMovies,))
        familyMovies = cursor.fetchmany(100)
        conn.commit()

        fantasyMovies = '%Fantasy%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (fantasyMovies,))
        fantasyMovies = cursor.fetchmany(100)
        conn.commit()

        foundFootageMovies = '%Found%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (foundFootageMovies,))
        foundFootageMovies = cursor.fetchmany(100)
        conn.commit()

        historicalMovies = '%Historical%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (historicalMovies,))
        historicalMovies = cursor.fetchmany(100)
        conn.commit()

        horrorMovies = '%Horror%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (horrorMovies,))
        horrorMovies = cursor.fetchmany(100)
        conn.commit()

        independentMovies = '%Independent%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (independentMovies,))
        independentMovies = cursor.fetchmany(100)
        conn.commit()

        legalMovies = '%Legal%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (legalMovies,))
        legalMovies = cursor.fetchmany(100)
        conn.commit()

        liveActionMovies = '%Live%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (liveActionMovies,))
        liveActionMovies = cursor.fetchmany(100)
        conn.commit()

        martialArtsMovies = '%Martial%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (martialArtsMovies,))
        martialArtsMovies = cursor.fetchmany(100)
        conn.commit()

        musicalMovies = '%Musical%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (musicalMovies,))
        musicalMovies = cursor.fetchmany(100)
        conn.commit()

        mysteryMovies = '%Mystery%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (mysteryMovies,))
        mysteryMovies = cursor.fetchmany(100)
        conn.commit()

        noirMovies = '%Noir%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (noirMovies,))
        noirMovies = cursor.fetchmany(100)
        conn.commit()

        performanceMovies = '%Performance%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (performanceMovies,))
        performanceMovies = cursor.fetchmany(100)
        conn.commit()

        politicalMovies = '%Political%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (politicalMovies,))
        politicalMovies = cursor.fetchmany(100)
        conn.commit()

        romanceMovies = '%Romance%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (romanceMovies,))
        romanceMovies = cursor.fetchmany(100)
        conn.commit()

        satireMovies = '%Satire%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (satireMovies,))
        satireMovies = cursor.fetchmany(100)
        conn.commit()

        scienceFictionMovies = '%Science%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (scienceFictionMovies,))
        scienceFictionMovies = cursor.fetchmany(100)
        conn.commit()

        shortMovies = '%Short%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (shortMovies,))
        shortMovies = cursor.fetchmany(100)
        conn.commit()

        silentMovies = '%Silent%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (silentMovies,))
        silentMovies = cursor.fetchmany(100)
        conn.commit()

        slasherMovies = '%Slasher%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (slasherMovies,))
        slasherMovies = cursor.fetchmany(100)
        conn.commit()

        sportsMovies = '%Sport%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (sportsMovies,))
        sportsMovies = cursor.fetchmany(100)
        conn.commit()

        spyMovies = '%Spy%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (spyMovies,))
        spyMovies = cursor.fetchmany(100)
        conn.commit()

        superheroMovies = '%Superhero%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (superheroMovies,))
        superheroMovies = cursor.fetchmany(100)
        conn.commit()

        supernaturalMovies = '%Supernatural%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (supernaturalMovies,))
        supernaturalMovies = cursor.fetchmany(100)
        conn.commit()

        suspenseMovies = '%Suspense%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (suspenseMovies,))
        suspenseMovies = cursor.fetchmany(100)
        conn.commit()

        teenMovies = '%Teen%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (teenMovies,))
        teenMovies = cursor.fetchmany(100)
        conn.commit()

        thrillerMovies = '%Thriller%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (thrillerMovies,))
        thrillerMovies = cursor.fetchmany(100)
        conn.commit()

        warMovies = '%War%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (warMovies,))
        warMovies = cursor.fetchmany(100)
        conn.commit()

        westernMovies = '%Western%'
        cursor.execute('SELECT * FROM movies WHERE genres LIKE ?', (westernMovies,))
        westernMovies = cursor.fetchmany(100)
        conn.commit()

        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], action=actionMovies, adventure=adventureMovies,
                               animated=animatedMovies, biography=biographyMovies, comedy=comedyMovies, crime=crimeMovies,
                               dance=danceMovies, disaster=disasterMovies, documentary=documentaryMovies, drama=dramaMovies,
                               family=familyMovies, fantasy=fantasyMovies, found=foundFootageMovies, historical=historicalMovies,
                               horror=horrorMovies, independent=independentMovies, legal=legalMovies, live=liveActionMovies,
                               martial=martialArtsMovies, musical=musicalMovies, mystery=mysteryMovies, noir=noirMovies,
                               performance=performanceMovies, political=politicalMovies, romance=romanceMovies, satire=satireMovies,
                               science=scienceFictionMovies, short=shortMovies, silent=silentMovies, slasher=slasherMovies,
                               sports=sportsMovies, spy=spyMovies, superhero=superheroMovies, supernatural=supernaturalMovies,
                               suspense=suspenseMovies, teen=teenMovies, thriller=thrillerMovies, war=warMovies,
                               western=westernMovies)


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
