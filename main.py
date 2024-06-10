# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request,jsonify, g, make_response, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import imghdr
import uuid
from bs4 import BeautifulSoup
import requests
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key


csrf = CSRFProtect(app) 
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False,)
    description = db.Column(db.String(100), nullable=False, default='uzivatel nezadal popis')
    release_year = db.Column(db.Integer, nullable=False, )
    length = db.Column(db.Integer, nullable=False)
    actorId = db.Column(db.Integer, db.ForeignKey('actor.id'))
    categoryId = db.Column(db.Integer, db.ForeignKey('category.id'))
    directorId = db.Column(db.Integer, db.ForeignKey('director.id'))
    trailer = db.Column(db.String(100), nullable=False, default='https://www.youtube.com/watch?v=6hB3S9bIaco')
    image = db.Column(db.String(100), nullable=False, default='Untitled5.png')
    comment = db.relationship('Comment', backref='film', lazy=True)
    rating = db.Column(db.Float, nullable=True, default=0.0)
    def __repr__(self):
        return '<Film %r>' % self.title


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False )
    comment = db.relationship('Comment', backref='user', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username
    

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='actor', lazy=True)
    def __repr__(self):
        return '<Actor %r>' % self.name

class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='director', lazy=True)
    def __repr__(self):
        return '<Director %r>' % self.name


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='category', lazy=True)
    def __repr__(self):
        return '<Category %r>' % self.name



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = db.Column(db.String(100), nullable=False)
    filmId = db.Column(db.Integer, db.ForeignKey('film.id'))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    def __repr__(self):
        return '<Comment %r>' % self.text

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



def scraper(URL):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Ověření úspěšného načtení stránky

        # Vytvoření objektu BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Najděte hodnocení
        rating_element = soup.find('div', class_='film-rating-average')

        if rating_element:
            rating = rating_element.text.strip()
            return rating.split('%')[0]
        else:
            return False
    except Exception as e:
        return False


@app.route("/database/add_comment")
def add_comment_database():
    comment = Comment(text='This is a comment', filmId=1, userId=1)
    db.session.add(comment)
    db.session.commit()
    return 'Comment was added'

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
    film = Film(title='The Shawshank Redemption', description='Two imprisoned', release_year=1994, length=142, actorId=1, categoryId=1, directorId=1, trailer='https://www.youtube.com/watch?v=6hB3S9bIaco', image='Untitled5.png', rating=9.3)
    db.session.add(film)
    db.session.commit()
    return 'Film was added'

@app.route("/add_comment",methods=['POST'])
def add_comment():
    film_id = request.form['film_id']
    text = request.form['text']
    comment = Comment(text=text, filmId=film_id, userId=session['user_id'])
    db.session.add(comment)
    db.session.commit()
    return "ok"

@app.route("/delete_comment/<int:id>", methods=['DELETE'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.userId != session['user_id'] and not session.get('admin'):
        return 'You are not authorized to delete this comment', 403
    db.session.delete(comment)
    db.session.commit()
    return 'Comment was deleted', 200

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
      
                session['admin'] = user.admin

                session['user_id'] = user.id   
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

    film = Film.query.get_or_404(id)
    db.session.delete(film)
    db.session.commit()
    return 'Film was deleted', 200



@app.route('/film/<int:id>', methods=['GET'])
def filmDetail(id):
    if not session.get('username'):
        return redirect(url_for('home'))
    film = Film.query.get_or_404(id)

    return render_template('filmDetail.html', film=film)
# it doesnt remove old iamge from the folder, i am too lazy to fix it
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
        film.trailer = request.form['trailer']
        film.rating = request.form['rating']
        image = request.files.get("image")
    
        if image:

            filename = secure_filename(image.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in ['.jpg', '.png', '.jpeg'] or file_ext != validate_image(image.stream):
                return {"error": "File type not supported"}, 400
            unique_str = str(uuid.uuid4())[:8]
            image.filename = f"{unique_str}_{filename}"
            image.save(os.path.join(basedir, 'static/uploads', image.filename))
            del_image = os.path.join(basedir, 'static/uploads', film.image)
            if os.path.exists(del_image) and film.image != 'default.jpg':
                os.remove(del_image)
            film.image = image.filename
        director =  Director.query.filter_by(name=request.form['director']).first()
        if not director:
            director = Director(name=request.form['director'])
            db.session.add(director)
            db.session.commit()
        film.director = director
        actor =  Actor.query.filter_by(name=request.form['actor']).first()
        if not actor:
            actor = Actor(name=request.form['actor'])
            db.session.add(actor)
            db.session.commit()
        film.actor = actor
        category =  Category.query.filter_by(name=request.form['category']).first()
        if not category:
            category = Category(name=request.form['category'])
            db.session.add(category)
            db.session.commit()
        film.category = category
        db.session.commit()
        return redirect('/films')
    return render_template('edit_film.html', film=film)
@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    if not session.get('admin'):
        return 'You are not authorized to add a new film', 403
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        release_year = request.form['release_year']
        length = request.form['length']
        trailer = request.form['trailer']
        director_name = request.form['director']
        category_name = request.form['category']
        actor_name = request.form['actor']
        image = request.files.get("image")
        csfd = request.form['csfd']
        rating = scraper(csfd) if csfd else None
        if image:
            filename = secure_filename(image.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in ['.jpg', '.png', '.jpeg'] or file_ext != validate_image(image.stream):
                return {"error": "File type not supported"}, 400
            unique_str = str(uuid.uuid4())[:8]
            image.filename = f"{unique_str}_{filename}"
            image.save(os.path.join(basedir, 'static/uploads', image.filename))
        else:
            image.filename = 'default.jpg'
        
        director = Director.query.filter_by(name=director_name).first()
        if not director:
            director = Director(name=director_name)
            db.session.add(director)
            db.session.commit()

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        actor = Actor.query.filter_by(name=actor_name).first()
        if not actor:
            actor = Actor(name=actor_name)
            db.session.add(actor)
            db.session.commit()

        film = Film(title=title, description=description, release_year=release_year, length=length, trailer=trailer, image=image.filename, director=director, category=category, actor=actor, rating=rating)
        db.session.add(film)
        db.session.commit()
        return redirect('/films')
    return render_template('add_film.html')


@app.route('/logOut')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    session.pop('user_id', None)
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
@app.route("/userAPI/<int:id>", methods=['PUT', 'DELETE'])
def userAPI(id):
    if not session.get('admin'):
        return 'You are not authorized to see this page', 403
    user = User.query.get_or_404(id)
    if request.method == 'PUT':
        user.admin = not user.admin
        db.session.commit()
        session['admin'] = user.admin
    
        return 'User was updated', 200
    db.session.delete(user)
    db.session.commit()
    session.pop('username', None)
    session.pop('admin', None)
    session.pop('user_id', None)
    return 'User was deleted', 200



# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)