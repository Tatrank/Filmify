# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request,jsonify, g, make_response, session, redirect, url_for, send_from_directory
import sqlite3
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt 
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import imghdr
from werkzeug.utils import secure_filename
import uuid
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)


app.config["UPLOAD_PATH"] = "image_uploads"

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key



def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")

#csrf = CSRFProtect(app) 
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False,)
    description = db.Column(db.String(100), nullable=False, default='uzivatel nezadal popis')
    release_year = db.Column(db.Integer, nullable=False, )
    length = db.Column(db.Integer, nullable=False)
    comment = db.relationship('Comment', backref='film', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'), nullable=False)
    actor = db.relationship('Actor', secondary='actor_film', backref='film', lazy=True)
    trailer = db.Column(db.String(100), nullable=False, default='https://www.youtube.com/watch?v=QdezFxHfatw')
    image = db.Column(db.String(100), nullable=False, default='https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.imdb.com%2Ftitle%2Ftt0133093%2F&psig=AOvVaw3')
    def __repr__(self):
        return '<Film %r>' % self.title





class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False )
    comment = db.relationship('Comment', backref='user', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username
    

class ActorFilm(db.Model):
    __tablename__ = 'actor_film'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    character = db.Column(db.String(50), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.id'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    def __repr__(self):
        return '<ActorFilm %r>' % self.id

class Actor(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', secondary='actor_film', backref='actor', lazy=True)
    def __repr__(self):
        return '<Actor %r>' % self.name

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='director', lazy=True)
    def __repr__(self):
        return '<Director %r>' % self.name


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    def __repr__(self):
        return '<Comment %r>' % self.text


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='category', lazy=True)
    def __repr__(self):
        return '<Category %r>' % self.name










def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/database/create_db')
def create_db():
    try:
        db.create_all()
    except Exception as e:
        return str(e)
    return 'Database was created'


@app.route('/database/delete_db')
def delete_db():
    try:
        db.drop_all()
    except Exception as e:
        return str(e)
    return 'Database was deleted'

@app.route('/database/add_user')
def add_user():
    admin = User(username="admin", password=bcrypt.generate_password_hash('admin').decode('utf-8'), admin=True)
    db.session.add(admin)
    user = User(username="user", password=bcrypt.generate_password_hash('user').decode('utf-8'), admin=False)
    db.session.add(user)
    db.session.commit()
    return 'User was added'
@app.route('/database/add_film')
def database_add_film():
    category = Category(name='Sci-fi')
    film = Film(title='Matrix', description='Film o tom jak se Neo stane vyvolenym', release_year=1999, length=136, category_id=1)
    db.session.add(film)
    db.session.add(category)
    db.session.commit()
    return 'Film was added'

@app.route('/database/add_film_lol')
def database_add_film2():

    film = Film(title='Matrix', description='Film o tom jak se Neo stane vyvolenym', release_year=1999, length=136, category_id=1)
    db.session.add(film)
    db.session.commit()
    return 'Film was added'

@app.route('/database/add_comment')
def database_add_comment():
    comment = Comment(text='nejlepsi film', user_id=1, film_id=1)
    db.session.add(comment)
    db.session.commit()
    return 'Comment was added'



@app.route("/pokus")
def pokus():
    return render_template('pokus.html')


@app.route('/', methods=['GET', 'POST'])
# ‘/’ URL is bound with hello_world() function.
def home():
    if request.method == 'POST':
        password = request.form['Password']
        username = request.form['Username']
        user = User.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                session['username'] = username
                print(session["username"])
                session['admin'] = user.admin
                print(session["username"])
                return redirect('/films')
            else:
                return 'error'

    return render_template('authForm.html')

@app.route('/films', methods=['GET'])
def films():
    if not session.get('username'):
        return redirect(url_for('home'))
    films = Film.query.all()
    return render_template('films.html', films=films, admin=session['admin'])


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_film(id):
    if not session.get('admin'):
        return 'You are not authorized to delete this film', 403
    print(id)
    film = Film.query.get_or_404(id)
    db.session.delete(film)
    db.session.commit()
    return 'Film was deleted', 200



@app.route('/film/<int:id>', methods=['GET'])
def filmDetail(id):
    film = Film.query.get_or_404(id)
    return render_template('filmDetail.html', film=film)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_film(id):
    if not session.get('admin'):
        return 'You are not authorized to edit this film', 403
    film = Film.query.get_or_404(id)
    if request.method == 'POST':
        film.title = request.form['title']
        film.description = request.form['description']
        film.release_year = request.form['release_year']
        film.length = request.form['length']
        db.session.commit()
        return redirect('/films')
    return render_template('edit_film.html', film=film)
@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    if not session.get('admin'):
        return 'You are not authorized to add new film', 403
    if request.method == 'POST':
        image = request.files["image"]

# check if filepath already exists. append random string if it does
        if secure_filename(image.filename) in [
            image for film in Film.query.all()
        ]:
            unique_str = str(uuid.uuid4())[:8]
            image.filename = f"{unique_str}_{image.filename}"


        #  handling file uploads
        filename = secure_filename(image.filename)
        if filename:
            file_ext = os.path.splitext(filename)[1]
            image_name = os.path.splitext(filename)[0]
            if file_ext not in [".jpg", ".png"] or file_ext != validate_image(image.stream):
                return {"error": "File type not supported"}, 400
            tit
            db.session.add(film)
            db.session.commit()
        return redirect('/films')
    return render_template('add_film.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    return redirect(url_for('home'))


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        password = request.form['Password']
        username = request.form['Username']
        user = User.query.filter_by(username=username).first()
        if user:
            return 'User already exists'
        new_user = User(username=username, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
        
    return render_template('signUp.html')

@app.route("/users", methods=['GET'])
def users():
    if not session.get('admin'):
        return 'You are not authorized to see this page', 403
    users = User.query.all()
    return render_template('users.html', users=users)

# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)