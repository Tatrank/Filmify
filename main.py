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
from flask_socketio import SocketIO, emit
import json
import requests
import uuid
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

socketio = SocketIO(app)
csrf = CSRFProtect(app) 
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False,)
    description = db.Column(db.String(100), nullable=False, default='uzivatel nezadal popis')
    release_year = db.Column(db.Integer, nullable=False, )
    length = db.Column(db.Integer, nullable=False)
    actorId = db.Column(db.Integer, db.ForeignKey('actor.id'))
    directorId = db.Column(db.Integer, db.ForeignKey('director.id'))
    trailer = db.Column(db.String(100), nullable=False, default='https://www.youtube.com/watch?v=6hB3S9bIaco')
    image = db.Column(db.String(100), nullable=False, default='PlaceholderFilm.png')
    comment = db.relationship('Comment', backref='film', lazy=True)
    rating = db.Column(db.Float, nullable=True, default=0.0)
    ratingUser = db.relationship('RatingUser', backref='film', lazy=True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<Film %r>' % self.title

category_film = db.Table('category_film',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('film_id', db.Integer, db.ForeignKey('film.id'), primary_key=True)
)








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
    admin = db.Column(db.Boolean(), nullable=False, default=True )
    comment = db.relationship('Comment', backref='user', lazy=True)
    ratingUser = db.relationship('RatingUser', backref='user', lazy=True)
    credits = db.Column(db.Integer, nullable=False, default=1000)
    api_key = db.Column(db.String(100), nullable=True, default=str(uuid.uuid4()))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<User %r>' % self.username
    

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='actor', lazy=True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<Actor %r>' % self.name

class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', backref='director', lazy=True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<Director %r>' % self.name



class RatingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    rating = db.Column(db.Float, nullable=False)
    filmId = db.Column(db.Integer, db.ForeignKey('film.id'))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<Rating %r>' % self.rating


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    film = db.relationship('Film', secondary=category_film, backref='category', lazy=True)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<Category %r>' % self.name



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = db.Column(db.String(100), nullable=False)
    filmId = db.Column(db.Integer, db.ForeignKey('film.id'))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return '<Comment %r>' % self.text

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/database/create_db')
def create_db():
    try:
        db.create_all()
        return 'Database was created'
    except Exception as e:
        return str(e)

@app.route('/pokus')
def pokus():
    return render_template('pokus.html')

@socketio.on("refresh")
def comments():
    emit("refreshComments", broadcast=True) 




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
        rating_element = soup.find('div', class_='film-rating-average').getText()
        title_element = soup.find('div', class_='film-header-name').find('h1').getText()
        description_element = soup.find('div', class_='plot-full').find('p').getText()
        lentgh_year = soup.find('div', class_='origin').getText().split(',')
        year = int(lentgh_year[1])
        time = (lentgh_year[2].split(' ')[1] )       
        if rating_element:
            rating = rating_element.text.strip()
            return rating.split('%')[0]
        else:
            return False
    except Exception as e:
        return False


@app.route('/scrapPokus')
def scrapPokus(
url

):

    
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ověření úspěšného načtení stránky
      
        # Vytvoření objektu BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
   
   
        rating_element = int(soup.find('div', class_='film-rating-average').text.strip().split('%')[0])
        title_element = soup.find('div', class_='film-header-name').find('h1').text.strip()
        description_element = soup.find('div', class_='plot-full').find('p').text.strip().strip()
        lentgh_year = soup.find('div', class_='origin').text.strip().split(',')
        year = int(lentgh_year[1].strip())
        time =int( lentgh_year[2].split(' ')[1]     )   
        director = soup.find('div', class_='creators').find('a').text.strip()
        category = soup.find('div', class_='genres').find_all('a')

        categories = [cat.text.strip() for cat in category]

        actor = soup.find('div', class_='creators').find_all('a')[4].text.strip()

        return {"title": title_element, "description": description_element, "release_year": year, "length": time, "director": director, "category": categories, "actor": actor,"rating": rating_element}




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    categoryList = ["action", "horror", "adventure" , "comedy", "drama", "thriller", "crime", "fantasy", "sci-fi", "mystery", "animation", "family", "romance", "biography", "history", "war", "western", "musical", "sport", "music", "documentary", "short", "film-noir", "adult"]
    #add bunch of normal names
    actorList = [  "Tom Hanks", "Morgan Freeman", "Tim Robbins", "Andy Dufresne", "William Sadler", "Clancy Brown", "Gil Bellows", "James Whitmore", "Bob Gunton", "Frank Darabont", "Stephen King", "Roger Deakins", "Thomas Newman", "Richard Francis-Bruce", "Terence Marsh", "Linda R. Chen", "Niki Marvin", "Castle Rock Entertainment", "Columbia Pictures", "Warner Bros."]
    directorList = ["Frank Darabont", "Stephen King", "Roger Deakins", "Thomas Newman", "Richard Francis-Bruce", "Terence Marsh", "Linda R. Chen", "Niki Marvin", "Castle Rock Entertainment", "Columbia Pictures", "Warner Bros."]
    for actor in actorList:
        if Actor.query.filter_by(name=actor).first():
            continue
        actor = Actor(name=actor)
        db.session.add(actor)
        db.session.commit()
    for director in directorList:
        if Director.query.filter_by(name=director).first():
            continue
        director = Director(name=director)
        db.session.add(director)
        db.session.commit()
    categories = []
    for category in categoryList:
        if Category.query.filter_by(name=category).first():
            categories.append(Category.query.filter_by(name=category).first())
            continue
        category = Category(name=category)
        db.session.add(category)
        db.session.commit()
        categories.append(category)

    film = Film(title='The Shawshank Redemption', description='Two imprisoned', release_year=1994, length=142, actorId=1, category=categories, directorId=1, trailer='https://www.youtube.com/watch?v=6hB3S9bIaco', image='PlaceholderFilm.png', rating=9.3)
    db.session.add(film)
    db.session.commit()

    for film in Film.query.all():
        print(film)

    return 'Film was added'

@app.route("/add_comment", methods=['POST'])
def add_comment():
    film_id = request.form['film_id']
    text = request.form['text']
    comment = Comment(text=text, filmId=film_id, userId=session['user_id'])
    db.session.add(comment)
    db.session.commit()
    
    user = User.query.filter_by(id=session['user_id']).first()
    socketio.emit("addComment", [comment.as_dict(), user.as_dict()])
    print("dfas")
    return "ok"

@app.route("/delete_comment/<int:id>", methods=['DELETE'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.userId != session['user_id'] and not session.get('admin'):
        return 'You are not authorized to delete this comment', 403
    db.session.delete(comment)
    db.session.commit()
    return 'Comment was deleted', 200




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
                return render_template('authForm.html', error=True)

    return render_template('authForm.html', error=False)

@app.route('/films', methods=['GET'])
def films():
    page = request.args.get('page', 1, type=int)
    if not session.get('username'):
        return redirect(url_for('home'))
    serche = request.args.get('search')
    category = request.args.get('category')
    categories = Category.query.all()
    if serche and category:
        films = Film.query.filter(Film.title.contains(serche), Film.category.any(Category.name == category)).paginate(page=page, per_page=8)
        return render_template('films.html', categories=categories,  films=films, admin=session['admin'], number_of_pages=range(films.pages))
    if serche:
        films = Film.query.filter(Film.title.contains(serche) ).paginate(page=page, per_page=8)
        return render_template('films.html',categories=categories , films=films, admin=session['admin'], number_of_pages=range(films.pages))
    if category:
        films = Film.query.filter(Film.category.any(Category.name == category)).paginate(page=page, per_page=8)
        return render_template('films.html', films=films, categories=categories , admin=session['admin'], number_of_pages=range(films.pages))
    films = Film.query.paginate(page=page, per_page=8)
    return render_template('films.html', films=films, categories=categories , admin=session['admin'], number_of_pages=range(films.pages))


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_film(id):
    if not session.get('admin'):
        return 'You are not authorized to delete this film', 403

    film = Film.query.get_or_404(id)
    db.session.delete(film)
    db.session.commit()
    return 'Film was deleted', 200

@app.route("/add_rating", methods=['POST'])
def add_rating():
    film_id = request.form['film_id']
    print(film_id)
    rating = request.form['rating']
    ratingExist = RatingUser.query.filter_by(filmId=film_id, userId=session['user_id']).first()
    if ratingExist:
        ratingExist.rating = rating
        db.session.commit()
        return "ok"
    ratingExist = RatingUser(rating=rating, filmId=film_id, userId=session['user_id'])
    db.session.add(ratingExist)
    db.session.commit()
    return "ok"

@app.route('/film/<int:id>', methods=['GET'])
def filmDetail(id):
    if not session.get('username'):
        return redirect(url_for('home'))
    film = Film.query.get_or_404(id)
    average = db.session.query(func.avg(RatingUser.rating)).filter(RatingUser.filmId == id).scalar()
    if not average:
        average = 0
    userRating = RatingUser.query.filter_by(filmId=id, userId=session['user_id']).first()
    return render_template('filmDetail.html', film=film, average=average, userRating=userRating)
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
        categoryList = request.form.getlist("category")
        category = []
        for cat in categoryList:
            categoryQueried = Category.query.filter_by(name=cat).first()
            if not categoryQueried:
                categoryQueried = Category(name=cat)
                db.session.add(categoryQueried)
                db.session.commit()
            category.append(categoryQueried)
        film.category = category
        db.session.commit()
        return redirect('/films')

    
    return render_template('edit_film.html', film=film)
@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    if not session.get('admin'):
        return 'You are not authorized to add a new film', 403
    if request.method == 'POST':

        #why it is string i dont know, but it is so i need to compare it with string 'true' not with boolean True 
        if request.form["csfdHidden"] == 'true':
            


            url = request.form["csfdUrl"]
            data = scrapPokus(url)
    
            title = data['title']
            description = data['description']
            release_year = data['release_year']
            length = data['length']
            trailer = request.form['trailer']
            director_name = data['director']
            category_name = data['category']
            actor_name = data['actor']
            image = request.files.get("image")
            if image:
                filename = secure_filename(image.filename)
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in ['.jpg', '.png', '.jpeg'] or file_ext != validate_image(image.stream):
                    return {"error": "File type not supported"}, 400
                unique_str = str(uuid.uuid4())[:8]
                image.filename = f"{unique_str}_{filename}"
                image.save(os.path.join(basedir, 'static/uploads', image.filename))
            else:
                image.filename = 'PlaceholderFilm.png'
            
            director = Director.query.filter_by(name=director_name).first()
            if not director:
                director = Director(name=director_name)
                db.session.add(director)
                db.session.commit()
            categoryList = []
            for category_name in data['category']:
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                        category = Category(name=category_name)
                        db.session.add(category)
                        db.session.commit()
                categoryList.append(category)
            
            actor = Actor.query.filter_by(name=actor_name).first()
            if not actor:
                actor = Actor(name=actor_name)
                db.session.add(actor)
                db.session.commit()

            film = Film(title=title, description=description, release_year=release_year, length=length, trailer=trailer, image=image.filename, director=director, category=categoryList, actor=actor, rating=data['rating'])
            db.session.add(film)
            db.session.commit()
        
        else:



            title = request.form['title']
            description = request.form['description']
            release_year = request.form['release_year']
            length = request.form['length']
            trailer = request.form['trailer']
            director_name = request.form['director']
            category_name = request.form['category']
            actor_name = request.form['actor']
            image = request.files.get("image")
            rating = request.form['rating']
            if image:
                filename = secure_filename(image.filename)
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in ['.jpg', '.png', '.jpeg'] or file_ext != validate_image(image.stream):
                    return {"error": "File type not supported"}, 400
                unique_str = str(uuid.uuid4())[:8]
                image.filename = f"{unique_str}_{filename}"
                image.save(os.path.join(basedir, 'static/uploads', image.filename))
            else:
                image.filename = 'PlaceholderFilm.png'
            
            director = Director.query.filter_by(name=director_name).first()
            if not director:
                director = Director(name=director_name)
                db.session.add(director)
                db.session.commit()

            actor = Actor.query.filter_by(name=actor_name).first()
            if not actor:
                actor = Actor(name=actor_name)
                db.session.add(actor)
                db.session.commit()
            categories = []
            for category_name in request.form.getlist("category"):
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                        category = Category(name=category_name)
                        db.session.add(category)
                        db.session.commit()
                categories.append(category)


            film = Film(title=title, description=description, release_year=release_year, length=length, trailer=trailer, image=image.filename, director=director, actor=actor, category=categories, rating=rating)
            db.session.add(film)
            db.session.commit()
        return redirect(url_for('filmDetail', id=film.id))
    return render_template('add_film.html')


@app.route('/logOut')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route("/api/user", methods=["GET"])
def user():
    user = request.args.get('search')
    user = User.query.filter_by(username=user).all()
    if not user:
        return jsonify({"user" : True})
    return jsonify({"user" : False})


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        password = request.form['Password']
        username = request.form['Username']
        user = User.query.filter_by(username=username).first()
        if user:
            return  render_template('signUp.html', error='User already exists')
        new_user = User(username=username, password=bcrypt.generate_password_hash(password).decode('utf-8'), api_key=str(uuid.uuid4()))
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

@app.route("/api/category", methods=["GET"])
def categorySearch():
    category = request.args.get('search')
    category = Category.query.filter(Category.name.contains(category)).all()
    category = [category.as_dict() for category in category]
 
 
    
    return jsonify(category)

@app.route("/api/actor", methods=["GET"])
def actorSearch():
    actor = request.args.get('search')
    actor = Actor.query.filter(Actor.name.contains(actor)).all()
    actor = [actor.as_dict() for actor in actor]
    return jsonify(actor)

@app.route("/api/director", methods=["GET"])
def directorSearch():
    director = request.args.get('search')
    director = Director.query.filter(Director.name.contains(director)).all()
    director = [director.as_dict() for director in director]
    return jsonify(director)

@app.route("/search", methods=['GET'])
def search():
    serche = request.args.get('search')

    if serche:
    
        #i want to retur films as a json but first i need to query them and after that i need to convert them to json
        films = Film.query.filter(Film.title.contains(serche)).limit(10)
        films = [film.as_dict() for film in films]
        return jsonify(films)
    return 'No films found', 404

@app.route("/api/public/films", methods=['GET'])
def filmsAPI():
    page = request.args.get('page', 1, type=int)
    serche = request.args.get('search')
    category = request.args.get('category')
    api_key = request.args.get('api_key')
    if not api_key:
        return 'You need to provide an api key', 403
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return 'Invalid api key', 403
    if user.credits <= 0:
        return 'You dont have enough credits', 403
    user.credits -= 1
    if serche and category:
        films = Film.query.filter(Film.title.contains(serche), Film.category.any(Category.name == category)).paginate(page=page, per_page=8)
        films = [film.as_dict() for film in films.items]
        return jsonify(films)
    if serche:
        films = Film.query.filter(Film.title.contains(serche)).paginate(page=page, per_page=8)
        films = [film.as_dict() for film in films.items]
        return jsonify(films)
    if category:
        films = Film.query.filter(Film.category.any(Category.name == category)).paginate(page=page, per_page=8)
        films = [film.as_dict() for film in films.items]
        return jsonify(films)
    films = Film.query.paginate(page=page, per_page=8)
    films = [film.as_dict() for film in films.items]
    return jsonify(films)




@app.route("/userOverwiev/<int:id>", methods=['GET'])
def userOverwiev(id):
    user = User.query.get_or_404(id)
    if not session.get('admin') and session['user_id'] != id:
        return 'You are not authorized to see this page', 403
    return render_template('userOverwiev.html', user=user)

@app.route("/changeAPIKey/<int:id>", methods=['PUT'])
def changeAPIKey(id):
    if not session.get('admin') and session['user_id'] != id:
        return 'You are not authorized to see this page', 403
    user = User.query.get_or_404(id)
    user.api_key = str(uuid.uuid4())
    db.session.commit()
    return 'API key was changed', 200
# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True,) 