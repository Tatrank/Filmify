# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request,jsonify, g, make_response
import sqlite3
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt 
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

csrf = CSRFProtect(app) 

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
db = SQLAlchemy(app)

class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False,)
    description = db.Column(db.String(100), nullable=False, default='uzivatel nezadal popis')
    release_year = db.Column(db.Integer, nullable=False, )
    length = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return '<Film %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='USER')
    films = db.relationship('Film', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username
    

bcrypt = Bcrypt(app) 

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection
# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/create_db')
def create_db():
    try:
        db.create_all()
    except Exception as e:
        return str(e)
    return 'Database was created'


@app.route('/delete_db')
def delete_db():
    try:
        db.drop_all()
    except Exception as e:
        return str(e)
    return 'Database was deleted'

@app.route('/add_user')
def add_user():
    lol = User(username='admin', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='ADMIN')
    db.session.add(lol)
    db.session.commit()
    return 'User was added'

@app.route('/todolater')
# ‘/’ URL is bound with hello_world() function.
def todo():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM film').fetchall()
    conn.close()
        
    return render_template('index.html', films=data)


@app.route('/', methods=['GET', 'POST'])
# ‘/’ URL is bound with hello_world() function.
def home():
    if request.method == 'POST':
        password = request.form['Password']
        username = request.form['Username']
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                token = jwt.encode({           'user_id': username,'role': user.role,'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
                resp = make_response(jsonify(message='Login successful'))
                resp.set_cookie('jwt', token, httponly=True, samesite='Strict')
                return "Login successful"
            else:
                return 'error'
        else:
            user = User(username=username, password=hashedPassword)
            db.session.add(user)
            db.session.commit()
            token = jwt.encode({           'user_id': username,'role': "USER",'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
            resp = make_response(jsonify(message='Login successful'))
            resp.set_cookie('jwt', token, httponly=True, samesite='Strict')
            print(User.query.all())
            return "Login successful maded user"

    return render_template('authForm.html')

@app.route('/protected', methods=['GET'])
def protected():
    token = request.cookies.get('jwt')
    if not token:
        return jsonify(message='Token is missing'), 401
    
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify(message='This is a protected route', user_id=data['user_id'], role=data['role']), 200
    except jwt.ExpiredSignatureError:
        return jsonify(message='Token has expired'), 401
    except jwt.InvalidTokenError:
        return jsonify(message='Invalid token'), 401



@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        length = request.form['length']
        release_year = request.form['rel']

        conn = get_db_connection()
        conn.execute('INSERT INTO film (title, description, release_year, length) VALUES (?, ?, ?, ?)',
                     (title, description, release_year, length))
        conn.commit()
        conn.close()
        return 'Film was added'
    return render_template('form.html')





@app.route('/films', methods=['GET'])
def add_film():
    conn = get_db_connection()
    conn.execute('INSERT INTO film (title, description, release_year, length) VALUES (?, ?, ?, ?)',
                 ('The Big Fish', "lol",1235, 120 ))
    conn.commit()
    conn.close()
    return 'New film was added'
# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)